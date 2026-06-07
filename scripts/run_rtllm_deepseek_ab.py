#!/usr/bin/env python3
"""Run RTLLM A/B evaluation with DeepSeek V4 Pro.

Path A: design_description -> SystemVerilog -> RTLLM testbench.
Path B: design_description -> restricted Go/MyGo DSL -> MyGo -> SystemVerilog -> RTLLM testbench.

The script is resumable and writes one artifact directory per task/path.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import os
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from openai import OpenAI

DEFAULT_MODEL = "deepseek/deepseek-v4-pro"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MAX_TOKENS = 16384
DEFAULT_REASONING_EFFORT = "none"

SYSTEM_VERILOG_PROMPT = """You are a professional RTL designer.
Return only complete synthesizable Verilog/SystemVerilog source code, including all submodules used by the top module.
Do not include markdown fences, explanations, or comments outside the code.
Define the exact requested module name and ports from the task description.
Do not include a testbench.
"""

MYGO_RULES = """MyGo restricted Go rules for this RTLLM run:
- Use package main.
- Include exactly one hardware top function plus an empty func main() {}.
- Use the requested RTLLM module name as the Go function name when it is a valid Go identifier.
- Function parameters are hardware inputs. Named return values are hardware outputs.
- Use exact port names whenever they are valid Go identifiers. If a name is a Go keyword, add a safe suffix.
- Use bool for 1-bit signals, uint8/uint16/uint32/uint64 for wider unsigned signals.
- Use local variables, assignments, +, -, *, &, |, ^, <<, >>, comparisons, explicit casts, if/else, and simple for loops only when the bounds are small constants.
- Prefer direct algebraic and bitwise formulas for combinational logic.
- For sequential logic, use package-level variables as registers. Handle reset first, then compute/update state on clock calls.
- Do not use arrays, slices, maps, structs, interfaces, pointers, recursion, goroutines, channels, imports, fmt, or helper packages.
- Do not define helper functions unless the task structurally needs a tiny pure combinational helper.
- Every named return value must be assigned on every path, then end the function with an explicit bare return statement.
- Do not read a named return value before assigning it; use a local temporary then assign the return.
- Mask arithmetic back to intended widths when needed, e.g. x &= 0xff.
- Do not output Verilog. Return only Go source code.
"""

SYSTEM_MYGO_PROMPT = """You convert RTL design descriptions into the restricted Go subset accepted by MyGo.
Return only complete Go source code.
Do not include markdown fences, SystemVerilog, explanations, or reasoning.
Start with package main.
"""

GO_KEYWORDS = {
    "break", "default", "func", "interface", "select", "case", "defer", "go", "map", "struct",
    "chan", "else", "goto", "package", "switch", "const", "fallthrough", "if", "range", "type",
    "continue", "for", "import", "return", "var",
}

@dataclass
class Port:
    direction: str
    name: str
    width: int
    range: str = ""

@dataclass
class Parameter:
    name: str
    default: str = "1"

@dataclass
class Task:
    index: int
    rel: str
    dir: Path
    module: str
    ports: list[Port]
    description: str
    tb_module: str = ""
    tb_ports: list[Port] | None = None
    tb_params: list[Parameter] | None = None
    tb_positional: bool = False


def sanitize_path(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    text = text.strip("._")
    return text[:160] or "task"


def go_ident(name: str) -> str:
    name = re.sub(r"\W", "_", name)
    if not name or not re.match(r"^[A-Za-z_]", name):
        name = "x_" + name
    if name in GO_KEYWORDS:
        name = name + "_port"
    return name


def go_type(width: int) -> str:
    if width <= 1:
        return "bool"
    if width <= 8:
        return "uint8"
    if width <= 16:
        return "uint16"
    if width <= 32:
        return "uint32"
    return "uint64"


def eval_sv_int_expr(expr: str, params: dict[str, int] | None = None) -> int | None:
    params = params or {}
    expr = expr.strip()
    expr = re.sub(
        r"\b(\d+)'([bodhBODH])([0-9a-fA-F_xXzZ]+)\b",
        lambda m: str(int(
            m.group(3).replace("_", "").replace("x", "0").replace("X", "0").replace("z", "0").replace("Z", "0"),
            {"b": 2, "o": 8, "d": 10, "h": 16}[m.group(2).lower()],
        )),
        expr,
    )
    for name, value in sorted(params.items(), key=lambda kv: -len(kv[0])):
        expr = re.sub(rf"\b{re.escape(name)}\b", str(value), expr)
    if not re.fullmatch(r"[0-9+\-*/%() <<>>]+", expr):
        return None
    try:
        value = eval(expr, {"__builtins__": {}}, {})
    except Exception:
        return None
    return int(value)


def parse_width(raw: str, params: dict[str, int] | None = None) -> int:
    raw = raw.strip()
    m = re.search(r"\[\s*([^:\]]+)\s*:\s*([^\]]+)\s*\]", raw)
    if m:
        high = eval_sv_int_expr(m.group(1), params)
        low = eval_sv_int_expr(m.group(2), params)
        if high is not None and low is not None:
            return abs(high - low) + 1
        if m.group(1).strip().isdigit() and m.group(2).strip().isdigit():
            return abs(int(m.group(1)) - int(m.group(2))) + 1
    m = re.search(r"(\d+)\s*-\s*bit", raw, flags=re.I)
    if m:
        return int(m.group(1))
    return 1


def strip_sv_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def extract_balanced(text: str, open_pos: int) -> tuple[str, int]:
    depth = 0
    start = open_pos + 1
    for i in range(open_pos, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start:i], i
    return "", open_pos


def split_top_level_commas(text: str) -> list[str]:
    items: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch in "({[":
            depth += 1
        elif ch in ")}]" and depth:
            depth -= 1
        elif ch == "," and depth == 0:
            items.append(text[start:i].strip())
            start = i + 1
    tail = text[start:].strip()
    if tail:
        items.append(tail)
    return items


def parse_signal_decls(tb_text: str) -> dict[str, tuple[str, int, str]]:
    decls: dict[str, tuple[str, int, str]] = {}
    text = strip_sv_comments(tb_text)
    params = parse_parameter_values(text)
    for m in re.finditer(r"\b(input|output|wire|reg|logic)\b\s*(?:signed\s+|unsigned\s+)?(\[[^\]]+\])?\s*([^;]+);", text):
        kind = m.group(1)
        rng = (m.group(2) or "").strip()
        width = parse_width(rng, params) if rng else 1
        for part in split_top_level_commas(m.group(3)):
            name_m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_$]*)", part)
            if name_m:
                decls[name_m.group(1)] = (kind, width, rng)
    return decls


def parse_parameter_values(text: str) -> dict[str, int]:
    params: dict[str, int] = {}
    for m in re.finditer(r"\b(?:localparam|parameter)\b\s+(?:integer\s+)?([A-Za-z_][A-Za-z0-9_$]*)\s*=\s*([^;,\n]+)", text):
        val = eval_sv_int_expr(m.group(2), params)
        if val is not None:
            params[m.group(1)] = val
    return params


def infer_direction(port_name: str, connected_signal: str, decls: dict[str, tuple[str, int, str]]) -> str:
    name = port_name.lower()
    if re.search(r"(res_valid|rempty|empty|full|valid_out|data_out|rdata|dout|out|result|sum|quotient|remainder|done|valid_o|^o_|_o$|flag|zero|carry|borrow|overflow|clk_div|detected|cout|co$|^s$|^y$)", name):
        return "output"
    if re.search(r"(clk|clock|rst|reset|en|load|start|ready|data_in|din|wdata|^in|_in$|addr|we|wr|rd|sel|op|opcode|a$|b$|x$|y$)", name):
        return "input"
    sig_kind = decls.get(connected_signal, ("", 1, ""))[0]
    if sig_kind in {"reg", "logic"}:
        return "input"
    return "output"


def names_close(a: str, b: str) -> bool:
    aa = re.sub(r"[^a-z0-9]", "", a.lower())
    bb = re.sub(r"[^a-z0-9]", "", b.lower())
    return bool(aa and bb and (aa == bb or aa in bb or bb in aa or difflib.SequenceMatcher(None, aa, bb).ratio() >= 0.72))


def module_instantiation_candidates(text: str, fallback_module: str) -> list[tuple[int, str, int, bool]]:
    candidates: list[tuple[int, str, int, bool]] = []
    forbidden = {
        "module", "if", "for", "while", "case", "assign", "always", "initial", "begin", "end",
        "repeat", "wait", "forever", "posedge", "negedge", "task", "function", "display",
        "monitor", "finish", "fopen", "fclose", "fwrite", "readmemh", "random",
    }
    for m in re.finditer(
        r"(?m)^\s*(?!\$)([A-Za-z_][A-Za-z0-9_$]*)\s*(?:#\s*\(|[A-Za-z_][A-Za-z0-9_$]*\s*\()",
        text,
    ):
        mod = m.group(1)
        if mod.lower() in forbidden:
            continue
        if not names_close(mod, fallback_module):
            continue
        pos = text.find("(", m.end() - 1)
        if pos >= 0:
            candidates.append((m.start(), mod, pos, bool(re.search(r"#\s*$", text[m.start():pos]))))
    return candidates


def parse_testbench_interface(task_dir: Path, fallback_module: str) -> tuple[str, list[Port], list[Parameter], bool]:
    tb_path = task_dir / "testbench.v"
    if not tb_path.exists():
        return fallback_module, [], [], False
    tb = tb_path.read_text(encoding="utf-8", errors="ignore")
    text = strip_sv_comments(tb)
    decls = parse_signal_decls(tb)
    param_values = parse_parameter_values(text)
    best: tuple[int, str, list[Parameter], list[Port], bool] | None = None
    for _, mod, pos, has_param_list in module_instantiation_candidates(text, fallback_module):
        params: list[Parameter] = []
        if has_param_list:
            param_body, close = extract_balanced(text, pos)
            for item in split_top_level_commas(param_body):
                pm = re.search(r"\.\s*([A-Za-z_][A-Za-z0-9_$]*)\s*\(\s*([^)]+?)\s*\)", item, flags=re.S)
                if pm:
                    raw_default = pm.group(2).strip()
                    val = eval_sv_int_expr(raw_default, param_values)
                    params.append(Parameter(pm.group(1), str(val) if val is not None else raw_default))
            inst_m = re.search(r"\s*[A-Za-z_][A-Za-z0-9_$]*\s*\(", text[close + 1 :])
            if not inst_m:
                continue
            pos = close + 1 + inst_m.end() - 1
        body, close = extract_balanced(text, pos)
        if close <= pos or close + 1 >= len(text) or text[close + 1] != ";":
            continue
        ports: list[Port] = []
        items = split_top_level_commas(body)
        named = any(re.search(r"^\s*\.", item) for item in items)
        for idx, item in enumerate(items):
            pm = re.search(r"\.\s*([A-Za-z_][A-Za-z0-9_$]*)\s*\(\s*([^)]+?)\s*\)", item, flags=re.S)
            if pm:
                pname = pm.group(1)
                raw_conn = pm.group(2).strip()
            elif not named:
                raw_conn = item.strip()
                pname = re.sub(r"\W+", " ", raw_conn).strip().split(" ")[0] if raw_conn else f"pos{idx}"
            else:
                continue
            conn = re.sub(r"\W+", " ", raw_conn).strip().split(" ")[0] if raw_conn else ""
            width = decls.get(conn, ("", 1, ""))[1]
            rng = decls.get(conn, ("", 1, ""))[2]
            ports.append(Port(infer_direction(pname, conn, decls), pname, width, rng))
        score = len(ports) + 2 * len(params) + (20 if mod == fallback_module else 0)
        if ports and (best is None or score > best[0]):
            best = (score, mod, params, ports, not named)
    if not best:
        return fallback_module, [], [], False
    return best[1], best[3], best[2], best[4]


def parse_tasks(rtllm_root: Path) -> list[Task]:
    tasks: list[Task] = []
    for desc_path in sorted(rtllm_root.rglob("design_description.txt"), key=lambda p: str(p.relative_to(rtllm_root))):
        text = desc_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"Module name:\s*\r?\n\s*([A-Za-z_][A-Za-z0-9_]*)", text, flags=re.I)
        if not m:
            continue
        module = m.group(1)
        ports = parse_ports(text)
        tb_module, tb_ports, tb_params, tb_positional = parse_testbench_interface(desc_path.parent, module)
        tasks.append(Task(len(tasks) + 1, str(desc_path.parent.relative_to(rtllm_root)), desc_path.parent, module, ports, text, tb_module, tb_ports, tb_params, tb_positional))
    return tasks


def parse_ports(text: str) -> list[Port]:
    ports: list[Port] = []
    direction: str | None = None
    seen: set[tuple[str, str]] = set()
    for raw in text.splitlines():
        line = raw.strip()
        low = line.lower()
        if re.match(r"input ports?:", low):
            direction = "input"
            continue
        if re.match(r"output ports?:", low):
            direction = "output"
            continue
        if direction and re.match(r"(implementation|function|operation|description|give me|requirements?)\b", low):
            direction = None
        if not direction or not line:
            continue
        # Examples: a[7:0]: ..., input [7:0] a, b, or cin: Carry-in.
        before = line.split(":", 1)[0].strip().strip("-*")
        before = re.sub(r"\b(input|output|wire|reg|logic|signed|unsigned)\b", " ", before, flags=re.I).strip()
        width = parse_width(line)
        before_no_width = re.sub(r"\[\s*\d+\s*:\s*\d+\]", " ", before)
        names: list[str] = []
        # Prefer name[msb:lsb] forms.
        for nm in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*\d+\s*:\s*\d+\]", before):
            names.append(nm)
        if not names:
            for part in re.split(r"[,/]", before_no_width):
                part = part.strip()
                if not part:
                    continue
                toks = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", part)
                if toks:
                    names.append(toks[-1])
        for name in names:
            if name.lower() in {"input", "output", "port", "ports"}:
                continue
            key = (direction, name)
            if key in seen:
                continue
            seen.add(key)
            ports.append(Port(direction, name, width))
    return ports


def suggested_go_signature(task: Task) -> str:
    params = []
    returns = []
    used_inputs = set()
    for p in task.ports:
        name = go_ident(p.name)
        typ = go_type(p.width)
        if p.direction == "input":
            used_inputs.add(name)
            params.append(f"{name} {typ}")
    for p in task.ports:
        if p.direction != "output":
            continue
        name = go_ident(p.name)
        if name in used_inputs:
            name = "out_" + name
        returns.append(f"{name} {go_type(p.width)}")
    ret = ""
    if returns:
        ret = " (" + ", ".join(returns) + ")"
    return f"func {go_ident(task.module)}({', '.join(params)}){ret}"


def effective_module(task: Task) -> str:
    return task.tb_module or task.module


def validate_go_code(code: str, task: Task) -> str | None:
    if not re.search(r"^\s*package\s+main\b", code, flags=re.M):
        return "missing package main"
    if "mygo:verilog begin" in code and "mygo:verilog end" in code:
        if re.search(r"\bmodule\s+" + re.escape(task.module) + r"\b", code):
            return None
        return f"inline verilog missing module {task.module}"
    funcs = re.findall(r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", code)
    hardware_funcs = [name for name in funcs if name != "main"]
    if not hardware_funcs:
        return "missing hardware function"
    wanted = go_ident(effective_module(task))
    if wanted not in hardware_funcs and go_ident(task.module) not in hardware_funcs:
        return f"missing target hardware function {wanted}"
    if re.search(r"\b(import|unsafe|fmt\.|go\s+func|chan\b|map\[|\[\]\w)", code):
        return "uses unsupported Go/MyGo construct"
    return None


def hardware_function_names(code: str) -> list[str]:
    return [name for name in re.findall(r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", code) if name != "main"]


def select_mygo_target(code: str, task: Task) -> str:
    funcs = hardware_function_names(code)
    for wanted in [go_ident(effective_module(task)), go_ident(task.module)]:
        if wanted in funcs:
            return wanted
    return funcs[0] if funcs else go_ident(effective_module(task))


def extract_inline_verilog(text: str) -> str | None:
    m = re.search(r"mygo:verilog\s+begin\s*(.*?)\s*mygo:verilog\s+end", text, flags=re.S | re.I)
    if m:
        return m.group(1).strip()
    first = re.search(r"\bmodule\s+[A-Za-z_][A-Za-z0-9_$]*\b", text)
    last = text.rfind("endmodule")
    if first and last >= first.start():
        return text[first.start() : last + len("endmodule")].strip()
    return None


def wrap_inline_verilog(verilog: str) -> str:
    return "\n".join([
        "package main",
        "",
        "/*",
        "mygo:verilog begin",
        verilog.strip(),
        "mygo:verilog end",
        "*/",
        "",
        "func main() {}",
        "",
    ])


def normalize_sv_for_iverilog(verilog: str) -> str:
    text = verilog
    text = re.sub(r"\balways_comb\b", "always @*", text)
    text = re.sub(r"\b(input|inout)\s+logic\b", r"\1 wire", text)
    text = re.sub(r"\boutput\s+logic\b", "output reg", text)
    text = hoist_simple_block_decls(text)
    return text


def hoist_simple_block_decls(verilog: str) -> str:
    def rewrite_module(match: re.Match[str]) -> str:
        module_text = match.group(0)
        decls: list[str] = []
        seen: set[str] = set()
        lines = module_text.splitlines()
        rewritten_lines: list[str] = []
        in_proc = False
        depth = 0

        for line in lines:
            stripped = line.strip()
            starts_proc = bool(re.match(r"(always|initial)\b", stripped))
            if starts_proc:
                in_proc = True
            if in_proc:
                dm = re.match(r"^(\s+)(logic|wire|reg)\s+(\[[^\]]+\]\s+)?([^;\n]+);", line)
                if dm:
                    _, _, rng, names = dm.groups()
                    simple_names = [name.strip() for name in split_top_level_commas(names)]
                    if all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", name) for name in simple_names):
                        for name in simple_names:
                            if name not in seen:
                                seen.add(name)
                                decls.append(f"  reg {rng or ''}{name};")
                        continue
            rewritten_lines.append(line)
            if in_proc:
                depth += len(re.findall(r"\bbegin\b", stripped))
                depth -= len(re.findall(r"\bend\b", stripped))
                if starts_proc and "begin" not in stripped:
                    in_proc = False
                elif depth <= 0 and not starts_proc:
                    in_proc = False

        rewritten = "\n".join(rewritten_lines)
        if not decls:
            return rewritten
        insert_at = rewritten.find("\n);")
        if insert_at < 0:
            return rewritten
        insert_after = rewritten.find("\n", insert_at + 3)
        if insert_after < 0:
            return rewritten
        return rewritten[:insert_after + 1] + "\n".join(decls) + "\n" + rewritten[insert_after + 1:]

    return re.sub(r"\bmodule\b.*?\bendmodule\b", rewrite_module, verilog, flags=re.S)


def extract_code(text: str, kind: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:systemverilog|verilog|sv|go|golang)?\s*(.*?)```", text, flags=re.S | re.I)
    if m:
        text = m.group(1).strip()
    if kind == "go":
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and isinstance(obj.get("go_source"), str):
                text = obj["go_source"].strip()
        except json.JSONDecodeError:
            jm = re.search(r"\{.*\}", text, flags=re.S)
            if jm:
                try:
                    obj = json.loads(jm.group(0))
                    if isinstance(obj, dict) and isinstance(obj.get("go_source"), str):
                        text = obj["go_source"].strip()
                except json.JSONDecodeError:
                    pass
        if "mygo:verilog begin" in text and "package main" in text:
            verilog = extract_inline_verilog(text)
            if verilog:
                return wrap_inline_verilog(verilog)
        if not re.search(r"^\s*package\s+main\b", text, flags=re.M):
            verilog = extract_inline_verilog(text)
            if verilog:
                return wrap_inline_verilog(verilog)
        m = re.search(r"(package\s+main\b.*)", text, flags=re.S)
        if m:
            text = m.group(1).strip()
        else:
            text = "package main\n\n" + text.lstrip()
        if "func main" not in text:
            text = text.rstrip() + "\n\nfunc main() {}\n"
        return text.rstrip() + "\n"
    verilog = extract_inline_verilog(text)
    if verilog:
        text = verilog
    return normalize_sv_for_iverilog(text).rstrip() + "\n"


def call_model(
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
) -> tuple[str, dict[str, Any]]:
    t0 = time.time()
    extra_body: dict[str, Any] | None = None
    if reasoning_effort != "default":
        extra_body = {"reasoning": {"effort": reasoning_effort, "exclude": True}}
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.1,
        max_tokens=max_tokens,
        extra_body=extra_body,
        timeout=360,
    )
    choice = resp.choices[0]
    content = choice.message.content or ""
    meta = {
        "model": model,
        "elapsed_seconds": time.time() - t0,
        "finish_reason": choice.finish_reason,
        "usage": resp.usage.model_dump() if getattr(resp, "usage", None) else None,
    }
    return content, meta


def repair_mygo_source(
    client: OpenAI,
    model: str,
    task: Task,
    prompt: str,
    bad_source: str,
    error: str,
) -> tuple[str, dict[str, Any]]:
    user = "\n\n".join([
        "Repair the generated Go/MyGo source so it follows the requested restricted MyGo format.",
        f"Validation or compiler error: {error}",
        "Original generation prompt:", prompt,
        "Bad Go/MyGo source:", bad_source,
        "Return only corrected complete Go source code. Start with package main.",
    ])
    return call_model(client, model, SYSTEM_MYGO_PROMPT, user)


def run_cmd(cmd: list[str], cwd: Path, timeout: float, env: dict[str, str] | None = None) -> dict[str, Any]:
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, env=env)
        return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "elapsed_seconds": time.time() - t0, "timeout": False}
    except subprocess.TimeoutExpired as exc:
        return {"returncode": None, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "elapsed_seconds": time.time() - t0, "timeout": True}


def normalize_testbench_for_iverilog(task_dir: Path) -> dict[str, Any]:
    tb_path = task_dir / "testbench.v"
    if not tb_path.exists():
        return {"changed": False, "reason": "missing testbench"}
    text = tb_path.read_text(encoding="utf-8", errors="ignore")
    changes: list[str] = []

    def rewrite_array_init(match: re.Match[str]) -> str:
        indent, kind, width, name, lo, hi, values = match.groups()
        vals = split_top_level_commas(values)
        assigns = "\n".join(f"{indent}    {name}[{int(lo) + i}] = {val.strip()};" for i, val in enumerate(vals))
        changes.append(f"array_init:{name}")
        return f"{indent}{kind} {width or ''}{name} [{lo}:{hi}];\n{indent}initial begin\n{assigns}\n{indent}end"

    text2 = re.sub(
        r"(?m)^(\s*)(reg|logic)\s+(\[[^\]]+\]\s+)?([A-Za-z_][A-Za-z0-9_$]*)\s*\[(\d+)\s*:\s*(\d+)\]\s*=\s*'?\{(.*?)\}\s*;",
        rewrite_array_init,
        text,
        flags=re.S,
    )
    if text2 != text:
        tb_path.write_text(text2, encoding="utf-8")
    return {"changed": bool(changes), "changes": changes}


def simulate(task_dir: Path, design_file: Path, timeout: float = 60) -> tuple[str, str, dict[str, Any]]:
    sim_out = task_dir / "sim.out"
    if sim_out.exists():
        sim_out.unlink()
    tb_detail = normalize_testbench_for_iverilog(task_dir)
    comp = run_cmd(["iverilog", "-g2012", "-o", str(sim_out), str(design_file), "testbench.v"], task_dir, timeout)
    if comp["timeout"]:
        return "COMPILE_TIMEOUT", "iverilog timeout", {"compile": comp, "testbench_normalize": tb_detail}
    if comp["returncode"] != 0:
        return "COMPILE_FAIL", (comp["stdout"] + comp["stderr"]).strip(), {"compile": comp, "testbench_normalize": tb_detail}
    run = run_cmd(["vvp", str(sim_out)], task_dir, timeout)
    out = (run["stdout"] + run["stderr"]).strip()
    if run["timeout"]:
        return "TIMEOUT", out or "simulation timeout", {"compile": comp, "simulation": run, "testbench_normalize": tb_detail}
    if "Your Design Passed" in out or re.search(r"\bPassed\b", out):
        return "PASS", out, {"compile": comp, "simulation": run, "testbench_normalize": tb_detail}
    if run["returncode"] != 0:
        return "SIM_ERROR", out, {"compile": comp, "simulation": run, "testbench_normalize": tb_detail}
    return "FAIL", out, {"compile": comp, "simulation": run, "testbench_normalize": tb_detail}


def parse_sv_module_headers(sv_text: str) -> list[tuple[str, list[Port]]]:
    modules: list[tuple[str, list[Port]]] = []
    for m in re.finditer(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_$]*)\s*(?:#\s*\([^;]*?\)\s*)?\((.*?)\)\s*;", sv_text, flags=re.S):
        module = m.group(1)
        body = m.group(2)
        ports: list[Port] = []
        current_dir = "input"
        current_width = 1
        current_range = ""
        for item in split_top_level_commas(body):
            part = " ".join(item.split())
            dm = re.search(r"\b(input|output|inout)\b", part)
            if dm:
                current_dir = "output" if dm.group(1) == "output" else "input"
            rm = re.search(r"(\[[^\]]+\])", part)
            if rm:
                current_range = rm.group(1)
                current_width = parse_width(current_range)
            name_m = re.search(r"([A-Za-z_][A-Za-z0-9_$]*)\s*$", part)
            if name_m:
                ports.append(Port(current_dir, name_m.group(1), current_width, current_range))
        modules.append((module, ports))
    return modules


def parse_sv_module_header(sv_text: str, preferred: str = "") -> tuple[str, list[Port]]:
    modules = parse_sv_module_headers(sv_text)
    if not modules:
        return "", []
    for module in modules:
        if module[0] == preferred:
            return module
    return modules[-1]


def wire_decl(port: Port) -> str:
    rng = port.range or (f"[{port.width - 1}:0]" if port.width > 1 else "")
    return f"wire {rng} {port.name};".replace("  ", " ").strip()


def choose_inner_port(wrapper_port: Port, inner_ports: list[Port], used: set[str]) -> str | None:
    names = [p.name for p in inner_ports if p.name not in used]
    if wrapper_port.name in names:
        return wrapper_port.name
    norm = wrapper_port.name.lower()
    norm_stripped = re.sub(r"(^tb_|_tb$|^test_|_test$)", "", norm)
    for name in names:
        inner_norm = re.sub(r"(^tb_|_tb$|^test_|_test$)", "", name.lower())
        if inner_norm == norm_stripped:
            return name
    aliases = {
        "rst_n": ["reset_n", "rst", "reset"],
        "reset_n": ["rst_n", "rst", "reset"],
        "rst_tb": ["rst", "reset", "rst_n", "reset_n"],
        "reset_tb": ["reset", "rst", "rst_n", "reset_n"],
        "clk_tb": ["clk", "clock"],
        "clock_tb": ["clk", "clock"],
        "clk_div": ["clkdiv", "clk_div_out", "out", "clock_out"],
        "clk_div_tb": ["clk_div", "clkdiv", "out"],
        "data_out": ["dout", "out", "q"],
        "dout": ["data_out", "out", "q"],
        "data_in": ["din", "in", "d"],
        "din": ["data_in", "in", "d"],
        "out_tb": ["out", "dout", "data_out", "q"],
        "in_tb": ["in", "din", "data_in", "d"],
    }
    for alias in aliases.get(norm, []):
        for name in names:
            if name.lower() == alias:
                return name
    match = difflib.get_close_matches(wrapper_port.name, names, n=1, cutoff=0.78)
    if match:
        return match[0]
    same_dir = [p.name for p in inner_ports if p.name not in used and p.direction == wrapper_port.direction and p.width == wrapper_port.width]
    if len(same_dir) == 1:
        return same_dir[0]
    return None


def ports_compatible(wrapper_ports: list[Port], inner_ports: list[Port]) -> bool:
    if len(wrapper_ports) != len(inner_ports):
        return False
    by_name = {p.name: p for p in inner_ports}
    for wp in wrapper_ports:
        ip = by_name.get(wp.name)
        if not ip or ip.direction != wp.direction:
            return False
    return True


def apply_compat_wrapper(sv_path: Path, task: Task) -> dict[str, Any]:
    sv_text = sv_path.read_text(encoding="utf-8", errors="ignore")
    inner_module, inner_ports = parse_sv_module_header(sv_text, task.module)
    wrapper_module = effective_module(task)
    wrapper_ports = task.tb_ports or []
    params = task.tb_params or []
    if not inner_module or not wrapper_ports:
        return {"wrapped": False, "reason": "missing inner module or tb ports"}
    needs_wrapper = bool(params) or task.tb_positional or inner_module != wrapper_module or not ports_compatible(wrapper_ports, inner_ports)
    if not needs_wrapper:
        return {"wrapped": False, "reason": "already compatible"}

    original_inner = inner_module + "__mygo_impl"
    sv_text = re.sub(rf"\bmodule\s+{re.escape(inner_module)}\b", f"module {original_inner}", sv_text, count=1)
    param_text = ""
    if params:
        param_text = " #(\n" + ",\n".join(f"  parameter {p.name} = {p.default}" for p in params) + "\n)"
    lines = [sv_text.rstrip(), "", f"module {wrapper_module}{param_text}("]
    for i, p in enumerate(wrapper_ports):
        comma = "," if i + 1 < len(wrapper_ports) else ""
        rng = p.range or (f"[{p.width - 1}:0] " if p.width > 1 else "")
        lines.append(f"  {p.direction} {rng}{p.name}{comma}")
    lines.append(");")
    used: set[str] = set()
    conns: list[tuple[str, str]] = []
    passthrough: list[str] = []
    for wp in wrapper_ports:
        ip = choose_inner_port(wp, inner_ports, used)
        if ip:
            used.add(ip)
            conns.append((ip, wp.name))
        else:
            if wp.direction == "output":
                lines.append(f"  assign {wp.name} = '0;")
            else:
                passthrough.append(wp.name)
    lines.append(f"  {original_inner} u_mygo_impl (")
    for i, (ip, wp) in enumerate(conns):
        comma = "," if i + 1 < len(conns) else ""
        lines.append(f"    .{ip}({wp}){comma}")
    lines.append("  );")
    lines.append("endmodule")
    sv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "wrapped": True,
        "inner_module": inner_module,
        "wrapper_module": wrapper_module,
        "params": [asdict(p) for p in params],
        "connections": [{"inner": ip, "wrapper": wp} for ip, wp in conns],
        "unmapped_inputs": passthrough,
    }


def copy_task_files(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    module = None
    desc = src / "design_description.txt"
    if desc.exists():
        match = re.search(
            r"Module name:\s*\r?\n\s*([A-Za-z_][A-Za-z0-9_]*)",
            desc.read_text(encoding="utf-8", errors="ignore"),
            flags=re.I,
        )
        if match:
            module = match.group(1)

    skip_names = {"sim.out"}
    if module:
        skip_names.add(f"{module}.v")

    for item in src.iterdir():
        if not item.is_file():
            continue
        name = item.name
        lower = name.lower()
        if name in skip_names or lower.startswith("verified_") or lower == "makefile":
            continue
        if lower.endswith((".v", ".sv")) and lower not in {"testbench.v", "testbench.sv"}:
            continue
        shutil.copy2(item, dst / name)


def run_direct(task: Task, out_root: Path, client: OpenAI, model: str, reuse: bool, max_tokens: int, path_name: str = "direct_verilog") -> dict[str, Any]:
    out = out_root / f"{task.index:03d}_{sanitize_path(task.rel)}" / path_name
    out.mkdir(parents=True, exist_ok=True)
    copy_task_files(task.dir, out)
    raw_path = out / "model_raw.txt"
    sv_path = out / f"{task.module}.v"
    meta_path = out / "model_meta.json"
    prompt_path = out / "prompt_sent.txt"
    prompt = task.description.strip() + "\n\nReturn only the complete Verilog/SystemVerilog module."
    prompt_path.write_text(SYSTEM_VERILOG_PROMPT + "\n--- USER ---\n" + prompt, encoding="utf-8")
    try:
        if reuse and raw_path.exists():
            raw = raw_path.read_text(encoding="utf-8", errors="ignore")
            meta = {"source": "cache"}
        else:
            raw, meta = call_model(client, model, SYSTEM_VERILOG_PROMPT, prompt, max_tokens=max_tokens)
            raw_path.write_text(raw, encoding="utf-8")
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        code = extract_code(raw, "verilog")
        sv_path.write_text(code, encoding="utf-8")
        wrap_detail = apply_compat_wrapper(sv_path, task)
        status, reason, detail = simulate(out, sv_path)
        detail["compat_wrapper"] = wrap_detail
    except Exception as exc:
        status, reason, detail = "MODEL_ERROR", f"{type(exc).__name__}: {exc}", {}
    result = {"task_index": task.index, "task": task.rel, "module": task.module, "path": path_name, "status": status, "reason": reason, "artifacts": str(out), "detail": detail}
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def compile_mygo_source(task: Task, out: Path, out_root: Path, mygo_bin: Path, circt_opt: Path, go_path: Path, sv_path: Path, target: str) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("GOTOOLCHAIN", "local")
    env["GOCACHE"] = str(out_root / ".gocache")
    env["GOMODCACHE"] = str(out_root / ".gomodcache")
    cmd = [str(mygo_bin), "compile", "-emit", "verilog", "-target", target, "-circt-opt", str(circt_opt), "-o", str(sv_path), str(go_path)]
    return run_cmd(cmd, out, 180, env)


def run_direct_mygo_inline(task: Task, out_root: Path, client: OpenAI, model: str, mygo_bin: Path, circt_opt: Path, reuse: bool, max_tokens: int) -> dict[str, Any]:
    out = out_root / f"{task.index:03d}_{sanitize_path(task.rel)}" / "direct_mygo_inline"
    out.mkdir(parents=True, exist_ok=True)
    copy_task_files(task.dir, out)
    raw_path = out / "model_raw.txt"
    go_path = out / "main.go"
    gomod_path = out / "go.mod"
    sv_path = out / f"{task.module}.v"
    meta_path = out / "model_meta.json"
    prompt_path = out / "prompt_sent.txt"
    prompt = task.description.strip() + "\n\nReturn only the complete Verilog/SystemVerilog module."
    prompt_path.write_text(SYSTEM_VERILOG_PROMPT + "\n--- USER ---\n" + prompt, encoding="utf-8")
    try:
        if reuse and raw_path.exists():
            raw = raw_path.read_text(encoding="utf-8", errors="ignore")
            meta = {"source": "cache"}
        else:
            raw, meta = call_model(client, model, SYSTEM_VERILOG_PROMPT, prompt, max_tokens=max_tokens)
            raw_path.write_text(raw, encoding="utf-8")
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        verilog = normalize_sv_for_iverilog(extract_code(raw, "verilog"))
        if not re.search(r"\bmodule\s+" + re.escape(task.module) + r"\b", verilog):
            # Keep the model output unchanged, but wrap obvious close-name module mismatches.
            pass
        go_path.write_text(wrap_inline_verilog(verilog), encoding="utf-8")
        gomod_path.write_text("module rtllm_direct_inline_task\n\ngo 1.25.4\n", encoding="utf-8")
        comp = compile_mygo_source(task, out, out_root, mygo_bin, circt_opt, go_path, sv_path, go_ident(task.module))
        if comp["timeout"]:
            status, reason, detail = "MYGO_TIMEOUT", "MyGo compile timeout", {"mygo_compile": comp}
        elif comp["returncode"] != 0:
            status, reason, detail = "MYGO_COMPILE_ERROR", (comp["stdout"] + comp["stderr"]).strip(), {"mygo_compile": comp}
        else:
            wrap_detail = apply_compat_wrapper(sv_path, task)
            status, reason, detail = simulate(out, sv_path)
            detail["mygo_compile"] = comp
            detail["compat_wrapper"] = wrap_detail
    except Exception as exc:
        status, reason, detail = "MODEL_ERROR", f"{type(exc).__name__}: {exc}", {}
    result = {"task_index": task.index, "task": task.rel, "module": task.module, "path": "direct_mygo_inline", "status": status, "reason": reason, "artifacts": str(out), "detail": detail}
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def run_mygo(task: Task, out_root: Path, client: OpenAI, model: str, mygo_bin: Path, circt_opt: Path, reuse: bool, repair: bool, max_tokens: int) -> dict[str, Any]:
    out = out_root / f"{task.index:03d}_{sanitize_path(task.rel)}" / "mygo"
    out.mkdir(parents=True, exist_ok=True)
    copy_task_files(task.dir, out)
    raw_path = out / "model_raw.txt"
    go_path = out / "main.go"
    gomod_path = out / "go.mod"
    sv_path = out / f"{task.module}.v"
    meta_path = out / "model_meta.json"
    repair_raw_path = out / "repair_raw.txt"
    repair_meta_path = out / "repair_meta.json"
    prompt_path = out / "prompt_sent.txt"
    iface = "\n".join(f"- {p.direction} {p.name}[{p.width}]" for p in task.ports) or "- Could not parse ports; infer from description."
    prompt = "\n\n".join([
        f"RTLLM requested module name: {task.module}",
        f"Suggested Go signature: {suggested_go_signature(task)}",
        "Parsed ports:", iface,
        MYGO_RULES,
        "Critical output format requirements:",
        "- The first non-whitespace text must be package main.",
        "- Either include the suggested hardware function, or include an inline Verilog block with mygo:verilog begin/end.",
        "- If using inline Verilog, put the complete synthesizable module inside the block comment and keep func main() {} after it.",
        "- Do not include unsafe, imports, arrays, slices, or explanatory text outside comments.",
        "RTLLM design description:", task.description.strip(),
    ])
    prompt_path.write_text(SYSTEM_MYGO_PROMPT + "\n--- USER ---\n" + prompt, encoding="utf-8")
    try:
        if reuse and raw_path.exists():
            raw = raw_path.read_text(encoding="utf-8", errors="ignore")
            meta = {"source": "cache"}
        else:
            raw, meta = call_model(client, model, SYSTEM_MYGO_PROMPT, prompt, max_tokens=max_tokens)
            raw_path.write_text(raw, encoding="utf-8")
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        go_code = extract_code(raw, "go")
        validation_error = validate_go_code(go_code, task)
        repair_reason = ""
        if validation_error and repair:
            repair_reason = validation_error
            if reuse and repair_raw_path.exists():
                repaired_raw = repair_raw_path.read_text(encoding="utf-8", errors="ignore")
                repair_meta = {"source": "cache"}
            else:
                repaired_raw, repair_meta = repair_mygo_source(client, model, task, prompt, go_code, repair_reason)
                repair_raw_path.write_text(repaired_raw, encoding="utf-8")
                repair_meta_path.write_text(json.dumps(repair_meta, ensure_ascii=False, indent=2), encoding="utf-8")
            go_code = extract_code(repaired_raw, "go")
            validation_error = validate_go_code(go_code, task)
            if validation_error:
                raise ValueError(f"invalid MyGo source after repair: {validation_error}")
        elif validation_error:
            raise ValueError(f"invalid MyGo source: {validation_error}")
        go_path.write_text(go_code, encoding="utf-8")
        gomod_path.write_text("module rtllm_mygo_task\n\ngo 1.25.4\n", encoding="utf-8")
        mygo_target = select_mygo_target(go_code, task)
        comp = compile_mygo_source(task, out, out_root, mygo_bin, circt_opt, go_path, sv_path, mygo_target)
        if comp["returncode"] != 0 and not comp["timeout"] and repair:
            repair_reason = (comp["stdout"] + comp["stderr"]).strip()
            if reuse and repair_raw_path.exists() and not validation_error:
                repaired_raw = repair_raw_path.read_text(encoding="utf-8", errors="ignore")
            else:
                repaired_raw, repair_meta = repair_mygo_source(client, model, task, prompt, go_code, repair_reason)
                repair_raw_path.write_text(repaired_raw, encoding="utf-8")
                repair_meta_path.write_text(json.dumps(repair_meta, ensure_ascii=False, indent=2), encoding="utf-8")
            repaired_code = extract_code(repaired_raw, "go")
            validation_error = validate_go_code(repaired_code, task)
            if not validation_error:
                go_path.write_text(repaired_code, encoding="utf-8")
                mygo_target = select_mygo_target(repaired_code, task)
                comp = compile_mygo_source(task, out, out_root, mygo_bin, circt_opt, go_path, sv_path, mygo_target)
        if comp["timeout"]:
            status, reason, detail = "MYGO_TIMEOUT", "MyGo compile timeout", {"mygo_compile": comp}
        elif comp["returncode"] != 0:
            status, reason, detail = "MYGO_COMPILE_ERROR", (comp["stdout"] + comp["stderr"]).strip(), {"mygo_compile": comp}
        else:
            wrap_detail = apply_compat_wrapper(sv_path, task)
            status, reason, detail = simulate(out, sv_path)
            detail["mygo_compile"] = comp
            detail["compat_wrapper"] = wrap_detail
            if repair_reason:
                detail["repair_reason"] = repair_reason[:2000]
    except Exception as exc:
        status, reason, detail = "MODEL_ERROR", f"{type(exc).__name__}: {exc}", {}
    result = {"task_index": task.index, "task": task.rel, "module": task.module, "path": "mygo", "status": status, "reason": reason, "artifacts": str(out), "detail": detail}
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def summarize(results: list[dict[str, Any]], out_root: Path, rtllm_root: Path, model: str, mygo_commit: str, rtllm_commit: str) -> None:
    results = sorted(results, key=lambda r: (r["task_index"], r["path"]))
    counts: dict[str, dict[str, int]] = {}
    for r in results:
        counts.setdefault(r["path"], {})[r["status"]] = counts.setdefault(r["path"], {}).get(r["status"], 0) + 1
    with (out_root / "results.json").open("w", encoding="utf-8") as f:
        json.dump({"model": model, "rtllm_root": str(rtllm_root), "rtllm_commit": rtllm_commit, "mygo_commit": mygo_commit, "counts": counts, "results": results}, f, ensure_ascii=False, indent=2)
    with (out_root / "results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_index", "task", "module", "path", "status", "reason", "artifacts"])
        writer.writeheader()
        for r in results:
            row = {k: r.get(k, "") for k in writer.fieldnames}
            writer.writerow(row)
    lines = [
        "# RTLLM DeepSeek V4 Pro A/B Results",
        "",
        f"- Model: `{model}`",
        f"- RTLLM root: `{rtllm_root}`",
        f"- RTLLM commit/snapshot: `{rtllm_commit}`",
        f"- MyGo commit: `{mygo_commit}`",
        f"- Tasks: {len({r['task'] for r in results})}",
        "- Sampling: pass@1 style, one model output per task per path",
        "- Leakage guard: prompts contain only `design_description.txt` plus parsed interface hints; testbench/reference files are not sent to the model.",
        "",
        "## Summary",
        "",
        "| Path | PASS | Total | Pass rate | Status counts |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for path in sorted(counts):
        c = counts.get(path, {})
        total = sum(c.values())
        passed = c.get("PASS", 0)
        rate = (100.0 * passed / total) if total else 0.0
        count_text = ", ".join(f"{k}={v}" for k, v in sorted(c.items()))
        lines.append(f"| {path} | {passed} | {total} | {rate:.2f}% | {count_text} |")
    paths = sorted(counts)
    lines.extend([
        "",
        "## Per Task",
        "",
        "| # | Task | Module | " + " | ".join(paths) + " |",
        "| ---: | --- | --- | " + " | ".join("---" for _ in paths) + " |",
    ])
    by_task: dict[str, dict[str, Any]] = {}
    for r in results:
        by_task.setdefault(r["task"], {"index": r["task_index"], "module": r["module"]})[r["path"]] = r
    for task, entry in sorted(by_task.items(), key=lambda kv: kv[1]["index"]):
        statuses = [entry.get(path, {}).get("status", "-") for path in paths]
        lines.append(f"| {entry['index']} | `{task}` | `{entry['module']}` | " + " | ".join(statuses) + " |")
    (out_root / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_root / "SUMMARY.txt").write_text(json.dumps(counts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summarize_token_usage(out_root)


def summarize_token_usage(out_root: Path) -> None:
    rows: list[dict[str, Any]] = []
    totals: dict[str, float] = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "reasoning_tokens": 0,
        "cost": 0.0,
    }
    for meta_path in sorted(out_root.glob("*/*/model_meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        usage = meta.get("usage") or {}
        details = usage.get("completion_tokens_details") or {}
        row = {
            "task_dir": meta_path.parent.parent.name,
            "path": meta_path.parent.name,
            "model": meta.get("model", ""),
            "finish_reason": meta.get("finish_reason", ""),
            "elapsed_seconds": meta.get("elapsed_seconds", ""),
            "prompt_tokens": usage.get("prompt_tokens", 0) or 0,
            "completion_tokens": usage.get("completion_tokens", 0) or 0,
            "total_tokens": usage.get("total_tokens", 0) or 0,
            "reasoning_tokens": details.get("reasoning_tokens", 0) or 0,
            "cost": usage.get("cost", 0.0) or 0.0,
        }
        rows.append(row)
        for key in totals:
            value = row.get(key, 0)
            if isinstance(value, (int, float)):
                totals[key] += value
    with (out_root / "token_usage_per_task.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "task_dir",
            "path",
            "model",
            "finish_reason",
            "elapsed_seconds",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "reasoning_tokens",
            "cost",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "model_calls": len(rows),
        "totals": {
            "prompt_tokens": int(totals["prompt_tokens"]),
            "completion_tokens": int(totals["completion_tokens"]),
            "total_tokens": int(totals["total_tokens"]),
            "reasoning_tokens": int(totals["reasoning_tokens"]),
            "cost": totals["cost"],
        },
    }
    (out_root / "token_usage_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rtllm-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--mygo-root", type=Path, required=True)
    ap.add_argument("--mygo-bin", type=Path, required=True)
    ap.add_argument("--circt-opt", type=Path, required=True)
    ap.add_argument("--key-file", type=Path, default=Path("/home/rongxv/work/secrets/openrouter_key.txt"))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--task-filter", default="", help="Run only tasks whose relative path contains this substring.")
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    ap.add_argument("--path", choices=["direct", "mygo", "direct-inline", "both", "all"], default="both")
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--repair", action="store_true", help="Allow one extra model call to repair invalid MyGo source. Do not use for strict pass@1.")
    ap.add_argument("--rtllm-commit", default="41b26896e33b536940116a975626455eed3de65e")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key and args.key_file.exists():
        api_key = args.key_file.read_text(encoding="utf-8").strip()
    if not api_key:
        raise RuntimeError("Missing OpenRouter/DeepSeek API key")
    client = OpenAI(api_key=api_key, base_url=args.base_url)

    tasks = parse_tasks(args.rtllm_root)
    if args.task_filter:
        tasks = [t for t in tasks if args.task_filter.lower() in t.rel.lower()]
    if args.limit:
        tasks = tasks[: args.limit]
    (args.out / "tasks.json").write_text(json.dumps([asdict(t) | {"dir": str(t.dir)} for t in tasks], ensure_ascii=False, indent=2), encoding="utf-8")

    results: list[dict[str, Any]] = []
    futures = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        for task in tasks:
            if args.path in {"direct", "both", "all"}:
                futures.append(ex.submit(run_direct, task, args.out, client, args.model, args.reuse, args.max_tokens))
            if args.path in {"mygo", "both", "all"}:
                futures.append(ex.submit(run_mygo, task, args.out, client, args.model, args.mygo_bin, args.circt_opt, args.reuse, args.repair, args.max_tokens))
            if args.path in {"direct-inline", "all"}:
                futures.append(ex.submit(run_direct_mygo_inline, task, args.out, client, args.model, args.mygo_bin, args.circt_opt, args.reuse, args.max_tokens))
        total = len(futures)
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            results.append(r)
            print(f"[{i}/{total}] {r['path']} {r['task']} -> {r['status']}", flush=True)
            # incremental summary
            try:
                mygo_commit = subprocess.check_output(
                    ["git", "-C", str(args.mygo_root), "rev-parse", "HEAD"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
            except Exception:
                mygo_commit = "unknown"
            summarize(results, args.out, args.rtllm_root, args.model, mygo_commit, args.rtllm_commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
