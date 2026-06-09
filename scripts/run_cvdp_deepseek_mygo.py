import argparse
import ast
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent if (SCRIPT_DIR.parent / "go.mod").exists() else SCRIPT_DIR
ASSET_ROOT = (
    SCRIPT_DIR
    if (SCRIPT_DIR / "cvdp_v1.1.0_nonagentic_code_generation_no_commercial.jsonl").exists()
    else REPO_ROOT.parent
)
DEFAULT_DATASET = ASSET_ROOT / "cvdp_v1.1.0_nonagentic_code_generation_no_commercial.jsonl"
DEFAULT_CSV = ASSET_ROOT / "cvdp_code_generation_649_tasks.csv"
DEFAULT_MYGO_ROOT = REPO_ROOT
DEFAULT_OUT = Path.home() / "Desktop" / "CVDP_MyGo_Deepseek_v4"
DEFAULT_KEY_FILE = Path.home() / "Desktop" / "API KEY" / "CVDP测试用-API Key.txt"
DEFAULT_MYGO = DEFAULT_MYGO_ROOT / "bin" / ("mygo.exe" if os.name == "nt" else "mygo")
DEFAULT_CIRCT_OPT = (
    Path(r"C:\tools\circt\firtool-1.146.0\bin\circt-opt.exe")
    if os.name == "nt"
    else Path("/home/rongxv/work/tools/circt/firtool-1.146.0/bin/circt-opt")
)
DEFAULT_MODEL = "deepseek/deepseek-v4-pro"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


MYGO_LIMITS = """MyGo restricted Go rules for this run:
- Use package main.
- Include the requested top function and an empty func main() {}.
- The top function's parameters are hardware inputs; named return values are hardware outputs.
- Use exactly the requested top function name when it is a valid Go identifier.
- Use exact CVDP port names for function parameters and named return values whenever they are valid Go identifiers.
- Never use Go reserved keywords as identifiers. If a CVDP port is named `go`, `type`, `range`, etc., rename the Go parameter safely, for example `go_in`; the wrapper reconnects ports by position.
- If an input port and an output port have the same name, keep the input parameter name exact and give the named return value a safe suffix such as out_<name>. The wrapper can reconnect by position, but Go cannot compile duplicate parameter/result names.
- Use only scalar bool, int8/int16/int32/int64, uint8/uint16/uint32/uint64 values.
- Use local variables, assignments, +, -, *, &, |, ^, <<, >>, comparisons, explicit casts, and if/else.
- Prefer algebraic and bitwise formulas over long if/else chains. Long repeated if/else chains can make MyGo MLIR generation too large.
- For this CVDP wrapper flow, do not use for loops. Manually unroll repeated logic for the default parameter values.
- Do not use division or modulo; use shifts/masks for powers of two.
- Do not use arrays, slices, maps, structs, interfaces, methods, pointers, recursion, select, switch, dynamic loops, goroutines, channels, packages other than main, imports, fmt, or comments explaining the solution.
- Do not define helper functions. Put every operation inside the requested top function plus only an empty func main() {}.
- Do not use switch/case. Use if/else chains.
- Every named return value must be assigned on every path. End the top function's final fallthrough path with an explicit bare return; do not rely on implicit named-return exit.
- For APB/AXI-style tasks, always drive all ready/error/output ports to deterministic default values before protocol-specific branches.
- For sequential tasks, use package-level state variables and update them once per TopModule call. Handle reset first, then compute outputs from the current state, then update next state.
- For active-low reset ports named resetn/rst_n/reset_n/aresetn/areset_n, reset when the value is false. For reset/rst/areset/arst, reset when true.
- After arithmetic, shifts, counters, or concatenation-like logic, mask values back to the intended width, for example `x &= 0xff`.
- For a full-width 64-bit mask, use `^uint64(0)` instead of `1 << 64`; Go rejects `1 << 64` when it is converted to uint64.
- Do not read a named return value before assigning it in the same call. Use a local temporary variable, then assign the return value.
- Avoid declaring a local variable with the same name as any port or named return value.
- For one-hot, encoder, decoder, and set-bit tasks, initialize the output to zero first, then set individual bits with masks.
- For width-converter/packer/unpacker tasks, build outputs with explicit shifts and masks; do not rely on implicit truncation.
- Do not output SystemVerilog. Return only JSON with target_function and go_code.
- The go_code JSON string must contain actual newline characters, not literal backslash-n or backslash-t text.
- If a CVDP parameterized width cannot be represented exactly in MyGo, implement the default parameter behavior with the nearest scalar integer type. The local harness wrapper will expose the CVDP interface.
"""


SYSTEM_PROMPT = """You convert CVDP RTL specifications into the restricted Go subset accepted by MyGo.
Return only a JSON object with:
{
  "target_function": "<Go top function name>",
  "go_code": "<complete Go source>"
}
Do not include markdown fences or SystemVerilog.
Do not assume access to hidden tests or reference answers.
Do not include reasoning, analysis, explanations, or comments outside the JSON object.
"""


GO_RESERVED = {
    "break",
    "case",
    "chan",
    "const",
    "continue",
    "default",
    "defer",
    "else",
    "fallthrough",
    "for",
    "func",
    "go",
    "goto",
    "if",
    "import",
    "interface",
    "map",
    "package",
    "range",
    "return",
    "select",
    "struct",
    "switch",
    "type",
    "var",
}


@dataclass
class PortSpec:
    direction: str
    name: str
    width: str
    bits: int | None


@dataclass
class GoArg:
    name: str
    typ: str

    @property
    def bits(self) -> int:
        return go_type_bits(self.typ)


def sanitize_name(name: str, max_len: int = 96) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", "_", name).strip("._ ")
    return name[:max_len] or "item"


def is_go_identifier(name: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name)) and name not in GO_RESERVED


def go_identifier(name: str) -> str:
    candidate = re.sub(r"\W", "_", name)
    if not candidate or not re.match(r"^[A-Za-z_]", candidate) or candidate in GO_RESERVED:
        candidate = "mygo_" + candidate
    return candidate


def sv_identifier(name: str) -> str:
    candidate = re.sub(r"\W", "_", name)
    if not candidate or not re.match(r"^[A-Za-z_]", candidate):
        candidate = "sv_" + candidate
    return candidate


def read_key(path: Path) -> str:
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return key.strip()
    key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError(f"API key file is empty: {path}")
    return key


def selected_ids(csv_path: Path) -> set[str]:
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)
        return {
            row["id"]
            for row in rows
            if row["split"] == "nonagentic_no_commercial"
            and row["categories"].split(";")[0] == "cid003"
        }


def load_tasks(dataset_path: Path, csv_path: Path) -> list[dict]:
    ids = selected_ids(csv_path)
    tasks = []
    with dataset_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("id") not in ids:
                continue
            output = row.get("output", {})
            if output.get("response"):
                raise RuntimeError(f"Non-empty output.response found for {row['id']}")
            for file_name, content in output.get("context", {}).items():
                if content:
                    raise RuntimeError(f"Non-empty output.context found for {row['id']}:{file_name}")
            tasks.append(row)
    tasks.sort(key=lambda r: r["id"])
    if len(tasks) != 78:
        raise RuntimeError(f"Expected 78 cid003 tasks, got {len(tasks)}")
    return tasks


def expected_files(task: dict) -> list[str]:
    files = list(task.get("output", {}).get("context", {}).keys())
    if not files:
        raise RuntimeError(f"No expected output file listed for {task['id']}")
    return files


def env_map(task: dict) -> dict[str, str]:
    raw = (task.get("harness", {}).get("files", {}) or {}).get("src/.env", "")
    env = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def parse_parameter_defaults(prompt: str) -> dict[str, str]:
    params: dict[str, str] = {}
    in_param_table = False
    in_param_section = False
    for line in prompt.splitlines():
        if re.match(r"^\s*#{1,6}\s+", line):
            in_param_section = bool(re.search(r"\bparameters?\b", section_label(line)))
        if "|" not in line:
            in_param_table = False
            if in_param_section:
                bullet = re.search(
                    r"\s*[-*]\s*`?([A-Za-z_][A-Za-z0-9_]*)`?.*?\bdefault\b\s*(?:=|is|:)?\s*([-]?\d+)",
                    line,
                    flags=re.I,
                )
                if bullet:
                    params[bullet.group(1)] = bullet.group(2)
            continue
        if re.search(r"-{3,}", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        headers = [strip_md(c).lower() for c in cells]
        if any(h in {"parameter", "parameter name", "param", "name"} for h in headers) and any(
            "default" in h or "value" in h for h in headers
        ):
            in_param_table = True
            continue
        if not in_param_table:
            continue
        name = strip_md(cells[0])
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            continue
        if name.lower() in {"parameter", "name", "signal", "port"}:
            continue
        default = ""
        for cell in cells[1:]:
            value = strip_md(cell)
            if re.search(r"[-]?\d+", value):
                default = value
                break
        num = re.search(r"[-]?\d+", default)
        if num:
            params[name] = num.group(0)
    return params


def strip_md(text: str) -> str:
    text = text.strip()
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    return text.strip()


def section_label(line: str) -> str:
    text = re.sub(r"^\s*#{1,6}\s*", "", line.strip())
    text = text.lstrip("-*").strip().rstrip(":")
    text = strip_md(text).strip().lower()
    text = text.strip("* :")
    return re.sub(r"\s+", " ", text)


def infer_width_from_port_text(text: str) -> str:
    m = re.search(r"\[[^\]]+:[^\]]+\]", text)
    if m:
        return m.group(0)
    m = re.search(r"\(\s*`?([A-Za-z_][A-Za-z0-9_]*)`?\s+bits?\s*\)", text, flags=re.I)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d+)\s*[- ]?\s*bits?\b", text, flags=re.I)
    if m:
        bits = int(m.group(1))
        return "[0:0]" if bits <= 1 else f"[{bits - 1}:0]"
    return "[0:0]"


def matched_width(match: re.Match[str] | None) -> str | None:
    if not match or not match.lastindex:
        return None
    for idx in range(match.lastindex, 0, -1):
        value = match.group(idx)
        if value and value.startswith("["):
            return value
    return None


def refine_port_width(name: str, width: str, params: dict[str, str]) -> str:
    if width != "[0:0]":
        return width
    if "DATA_WIDTH" in params and re.search(r"data", name, flags=re.I):
        return "DATA_WIDTH"
    return width


def parse_ports(prompt: str, params: dict[str, str]) -> list[PortSpec]:
    ports: list[PortSpec] = []
    seen: set[tuple[str, str]] = set()
    direction = None
    for line in prompt.splitlines():
        low = line.lower()
        label = section_label(line)
        is_heading = bool(re.match(r"^\s*#{1,6}\s+", line))
        if (
            (re.match(r"^#{1,6}\s*\*{0,2}inputs?\b", low) and "output" not in low)
            or re.fullmatch(r"inputs?(?:\s+(?:signals?|ports?|specifications?))?", label)
        ):
            direction = "input"
            continue
        if (
            (re.match(r"^#{1,6}\s*\*{0,2}outputs?\b", low) and "input" not in low)
            or re.fullmatch(r"outputs?(?:\s+(?:signals?|ports?|specifications?))?", label)
        ):
            direction = "output"
            continue
        if direction and is_heading:
            direction = None
        if direction and re.fullmatch(r"-{3,}", line.strip()):
            direction = None
        if not direction:
            continue
        if "|" in line and not re.search(r"-{3,}", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            name = strip_md(cells[0])
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
                continue
            if name.lower() in {"name", "signal", "input", "output"}:
                continue
            width = strip_md(cells[1])
            key = (direction, name)
            if key in seen:
                continue
            seen.add(key)
            width = refine_port_width(name, width, params)
            ports.append(PortSpec(direction, name, width, width_bits(width, params)))
            continue
        m = re.match(r"\s*(?:[-*]|\d+\.)\s*(?:\*\*)?\s*`?([A-Za-z_][A-Za-z0-9_]*)`?", line)
        code_width = None
        if m and m.group(1).lower() not in {"input", "inputs", "output", "outputs"}:
            code_width = re.search(r"`\s*" + re.escape(m.group(1)) + r"\s*(\[[^\]]+\])?\s*`", line)
        if (not m or m.group(1).lower() in {"input", "inputs", "output", "outputs"}) and re.match(r"\s*(?:[-*]|\d+\.)", line):
            code = re.search(r"`\s*([A-Za-z_][A-Za-z0-9_]*)\s*(\[[^\]]+\])?\s*`", line)
            if code:
                m = code
                code_width = code
        if not m:
            continue
        name = strip_md(m.group(1))
        if name in params:
            continue
        if name.lower() in {"input", "inputs", "output", "outputs"}:
            continue
        if "_" not in name and name not in {"clk", "clock", "reset", "rst", "button"} and name[:1].isupper():
            continue
        has_code_name = bool(re.match(r"\s*[-*]\s*(?:\*\*)?\s*`[A-Za-z_][A-Za-z0-9_]*`", line))
        has_width = bool(re.search(r"\([^\)]*(?:\[|\bbit|\bbits)[^\)]*\)|\b\d+\s*-\s*bit\b", line, flags=re.I))
        signalish = "_" in name or name.lower() in {"clk", "clock", "reset", "rst", "button"}
        if not (has_code_name or has_width or signalish):
            continue
        width = matched_width(code_width) or infer_width_from_port_text(line)
        key = (direction, name)
        if key in seen:
            continue
        seen.add(key)
        width = refine_port_width(name, width, params)
        ports.append(PortSpec(direction, name, width, width_bits(width, params)))
    return ports


def safe_eval_int(expr: str, params: dict[str, str]) -> int | None:
    expr = strip_md(expr)
    for k, v in params.items():
        expr = re.sub(rf"\b{re.escape(k)}\b", str(v), expr)
    expr = expr.replace(" ", "")
    expr = expr.replace("/", "//")
    if not re.fullmatch(r"[0-9+\-*/()<>]+", expr):
        return None
    try:
        node = ast.parse(expr, mode="eval")
        for sub in ast.walk(node):
            if not isinstance(
                sub,
                (
                    ast.Expression,
                    ast.BinOp,
                    ast.UnaryOp,
                    ast.Constant,
                    ast.Add,
                    ast.Sub,
                    ast.Mult,
                    ast.FloorDiv,
                    ast.USub,
                    ast.UAdd,
                ),
            ):
                return None
        val = eval(compile(node, "<expr>", "eval"), {"__builtins__": {}}, {})
        return int(val)
    except Exception:
        return None


def width_bits(width: str, params: dict[str, str]) -> int | None:
    raw = strip_md(width)
    if not raw:
        return 1
    m = re.search(r"\[\s*(.*?)\s*:\s*(.*?)\s*\]", raw)
    if m:
        left = safe_eval_int(m.group(1), params)
        right = safe_eval_int(m.group(2), params)
        if left is not None and right is not None:
            return abs(left - right) + 1
    if raw.lower() in {"bit", "logic", "wire", "bool"}:
        return 1
    val = safe_eval_int(raw, params)
    if val is not None and val > 0:
        return val
    nums = [int(x) for x in re.findall(r"\d+", raw)]
    if len(nums) == 1 and nums[0] > 0:
        return nums[0]
    return None


def go_type_for_bits(bits: int | None) -> str:
    if bits is None:
        return "uint64"
    if bits <= 8:
        return "uint8"
    if bits <= 16:
        return "uint16"
    if bits <= 32:
        return "uint32"
    return "uint64"


def go_type_bits(typ: str) -> int:
    typ = typ.strip()
    if typ == "bool":
        return 1
    m = re.search(r"(\d+)$", typ)
    if m:
        return int(m.group(1))
    return 32


def suggested_signature(module_name: str, ports: list[PortSpec]) -> str:
    target = go_identifier(module_name)
    params = []
    returns = []
    for port in ports:
        name = go_identifier(port.name)
        typ = go_type_for_bits(port.bits)
        if port.direction == "input":
            params.append(f"{name} {typ}")
        elif port.direction == "output":
            returns.append(f"{name} {typ}")
    ret = ""
    if returns:
        ret = " (" + ", ".join(returns) + ")"
    return f"func {target}({', '.join(params)}){ret}"


def build_prompt(task: dict) -> tuple[str, dict]:
    prompt = task.get("input", {}).get("prompt", "")
    if not prompt:
        raise RuntimeError(f"Empty prompt for {task['id']}")
    env = env_map(task)
    module_name = env.get("TOPLEVEL") or find_module_name(prompt) or go_identifier(task["id"])
    params = parse_parameter_defaults(prompt)
    ports = parse_ports(prompt, params)
    sig = suggested_signature(module_name, ports)
    files = expected_files(task)
    context = task.get("input", {}).get("context", {}) or {}
    parts = [
        f"Problem ID: {task['id']}",
        f"CVDP top module name: {module_name}",
        f"Suggested MyGo top signature: {sig}",
        "Expected output file(s):",
        "\n".join(f"- {name}" for name in files),
        "",
        MYGO_LIMITS,
        "",
        "CVDP specification:",
        prompt,
    ]
    if context:
        parts.extend(["", "Public input context files needed for the problem:"])
        for name, content in context.items():
            parts.append(f"\nFile: {name}\n```systemverilog\n{content}\n```")
    meta = {
        "module_name": module_name,
        "params": params,
        "ports": [p.__dict__ for p in ports],
        "suggested_signature": sig,
    }
    return "\n".join(parts), meta


def find_module_name(prompt: str) -> str | None:
    m = re.search(r"Module Name:\s*\n\s*`?([A-Za-z_][A-Za-z0-9_]*)`?", prompt, flags=re.I)
    if m:
        return m.group(1)
    m = re.search(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)\b", prompt)
    if m:
        return m.group(1)
    return None


def strip_code_fence(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json|go|golang)?\s*(.*?)```", text, flags=re.I | re.S)
    if match:
        return match.group(1).strip()
    return text


def normalize_go_source_text(code: str) -> str:
    code = strip_code_fence(code).strip()
    if code.count("\n") <= 1 and code.count(r"\n") >= 2:
        candidate = (
            code.replace(r"\r\n", "\n")
            .replace(r"\n", "\n")
            .replace(r"\t", "\t")
        )
        if "package main" in candidate and "\n" in candidate:
            code = candidate
    return code


def parse_model_response(text: str, default_target: str) -> tuple[str, str]:
    raw = strip_code_fence(text)
    try:
        obj = json.loads(raw)
        target = obj.get("target_function") or default_target
        code = obj.get("go_code") or ""
        if code.strip():
            return target, normalize_go_source_text(code)
    except Exception:
        pass
    go_match = re.search(r"(package\s+main\b.*)", raw, flags=re.S)
    code = normalize_go_source_text(go_match.group(1).strip() if go_match else raw.strip())
    target = find_go_function(code) or default_target
    return target, code


def find_go_function(code: str) -> str | None:
    funcs = re.findall(r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", code)
    for name in funcs:
        if name != "main":
            return name
    return funcs[0] if funcs else None


def call_model(client: OpenAI, model: str, prompt: str, timeout: float) -> tuple[str, dict]:
    start = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=20000,
        timeout=timeout,
        extra_body={"reasoning": {"max_tokens": 1024}},
        extra_headers={
            "HTTP-Referer": "https://localhost/cvdp-mygo",
            "X-Title": "CVDP MyGo DeepSeek evaluation",
        },
    )
    elapsed = time.time() - start
    msg = resp.choices[0].message
    text = msg.content or ""
    meta = {
        "model": model,
        "elapsed_seconds": elapsed,
        "response_id": getattr(resp, "id", None),
        "finish_reason": getattr(resp.choices[0], "finish_reason", None),
        "usage": getattr(resp, "usage", None).model_dump() if getattr(resp, "usage", None) else {},
    }
    return text, meta


def run_cmd(cmd: list[str], cwd: Path, timeout: float, env: dict | None = None) -> dict:
    start = time.time()
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=merged_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
        )
        stdout, _ = proc.communicate(timeout=timeout)
        output = decode_output(stdout)
        return {
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "returncode": proc.returncode,
            "elapsed_seconds": time.time() - start,
            "command": cmd,
            "output_log": output,
        }
    except subprocess.TimeoutExpired as exc:
        output = decode_output(exc.stdout)
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            proc.kill()
        try:
            more_stdout, _ = proc.communicate(timeout=5)
            output += decode_output(more_stdout)
        except Exception:
            pass
        return {
            "status": "TIMEOUT",
            "elapsed_seconds": time.time() - start,
            "command": cmd,
            "output_log": output,
        }
    except Exception as exc:
        return {
            "status": "ERROR",
            "elapsed_seconds": time.time() - start,
            "command": cmd,
            "output_log": f"{type(exc).__name__}: {exc}",
        }


def make_ascii_work_dir(mygo_root: Path, label: str) -> Path:
    if os.name == "nt":
        root = Path(r"C:\temp\mygo_cvdp_work")
    else:
        root = Path(os.environ.get("TMPDIR", "/tmp")) / "mygo_cvdp_work"
    root.mkdir(parents=True, exist_ok=True)
    base = sanitize_name(label, 64)
    stamp = f"{int(time.time() * 1000)}_{os.getpid()}"
    work_dir = root / f"{base}_{stamp}"
    work_dir.mkdir(parents=True, exist_ok=False)
    return work_dir


def decode_output(data) -> str:
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return data.decode(enc)
        except Exception:
            pass
    return data.decode("utf-8", errors="replace")


def compile_mygo(
    mygo: Path,
    circt_opt: Path,
    mygo_root: Path,
    source: Path,
    target: str,
    out_dir: Path,
    timeout: float,
) -> dict:
    env = {
        "GOCACHE": str(mygo_root / ".gocache-agent"),
        "GOMODCACHE": str(mygo_root / ".gomodcache-agent"),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    ascii_dir = make_ascii_work_dir(mygo_root, out_dir.parent.name)
    ascii_source = ascii_dir / "main.go"
    ascii_source.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (ascii_dir / "go.mod").write_text("module cvdp_mygo_task\n\ngo 1.25.4\n", encoding="utf-8")
    ir_path = out_dir / "mygo.ir"
    mlir_path = out_dir / "mygo.mlir"
    sv_path = out_dir / "mygo_raw.sv"
    for old_path in (ir_path, mlir_path, sv_path):
        old_path.unlink(missing_ok=True)
    for old_log in ("ir_log.txt", "mlir_log.txt", "verilog_log.txt"):
        (out_dir / old_log).unlink(missing_ok=True)
    ascii_outputs = {
        "ir": ascii_dir / "mygo.ir",
        "mlir": ascii_dir / "mygo.mlir",
        "verilog": ascii_dir / "mygo_raw.sv",
    }
    steps = []
    for emit, path in [("ir", ir_path), ("mlir", mlir_path), ("verilog", sv_path)]:
        ascii_path = ascii_outputs[emit]
        cmd = [str(mygo), "compile", "-target", target, "-emit", emit, "-o", str(ascii_path)]
        if emit == "verilog":
            cmd.extend(["--circt-opt", str(circt_opt)])
        cmd.append(str(ascii_source))
        res = run_cmd(cmd, ascii_dir, timeout, env)
        if ascii_path.exists():
            shutil.copyfile(ascii_path, path)
        res["emit"] = emit
        res["output_path"] = str(path)
        res["ascii_output_path"] = str(ascii_path)
        (out_dir / f"{emit}_log.txt").write_text(res.get("output_log", ""), encoding="utf-8")
        steps.append(res)
        if res["status"] != "PASS":
            return {
                "status": "FAIL",
                "steps": steps,
                "ir_path": str(ir_path) if ir_path.exists() else None,
                "mlir_path": str(mlir_path) if mlir_path.exists() else None,
                "sv_path": str(sv_path) if sv_path.exists() else None,
                "error_log": res.get("output_log", ""),
            }
    return {
        "status": "PASS",
        "steps": steps,
        "ir_path": str(ir_path),
        "mlir_path": str(mlir_path),
        "sv_path": str(sv_path),
        "error_log": "",
    }


def mygo_failure_reason(compile_info: dict, context: str) -> str:
    for step in compile_info.get("steps", []):
        if step.get("status") == "PASS":
            continue
        emit = step.get("emit") or "unknown"
        status = step.get("status") or "FAIL"
        elapsed = step.get("elapsed_seconds")
        log = (step.get("output_log") or compile_info.get("error_log") or "").strip()
        if log:
            return f"{context}: MyGo {emit} {status}. {log}"
        if isinstance(elapsed, (int, float)):
            return f"{context}: MyGo {emit} {status} after {elapsed:.1f}s"
        return f"{context}: MyGo {emit} {status}"
    log = (compile_info.get("error_log") or "").strip()
    if log:
        return f"{context}: {log}"
    return f"{context}: MyGo compile failed"


def fallback_failure_status(reason: str) -> str:
    text = reason.lower()
    if "no_model mode enabled" in text:
        return "NO_MODEL_ERROR"
    if "restricted go" in text:
        return "MODEL_STATIC_ERROR"
    if "model returned empty response" in text or "api" in text or "timeout" in text:
        return "MODEL_ERROR"
    if "mygo" in text:
        return "MYGO_COMPILE_ERROR"
    return "MODEL_ERROR"


def sim_mygo(
    mygo: Path,
    circt_opt: Path,
    mygo_root: Path,
    source: Path,
    target: str,
    out_dir: Path,
    timeout: float,
) -> dict:
    env = {
        "GOCACHE": str(mygo_root / ".gocache-agent"),
        "GOMODCACHE": str(mygo_root / ".gomodcache-agent"),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    ascii_dir = make_ascii_work_dir(mygo_root, out_dir.parent.name + "_sim")
    ascii_source = ascii_dir / "main.go"
    ascii_source.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (ascii_dir / "go.mod").write_text("module cvdp_mygo_task\n\ngo 1.25.4\n", encoding="utf-8")
    sim_verilog = ascii_dir / "mygo_sim_design.sv"
    cmd = [
        str(mygo),
        "sim",
        "-target",
        target,
        "--circt-opt",
        str(circt_opt),
        "--verilog-out",
        str(sim_verilog),
        "--sim-max-cycles",
        "64",
        "--keep-artifacts",
        "true",
        str(ascii_source),
    ]
    res = run_cmd(cmd, ascii_dir, timeout, env)
    res["ascii_work_dir"] = str(ascii_dir)
    res["verilog_out"] = str(sim_verilog)
    res["note"] = (
        "This is MyGo's own built-in simulation of the generated Go/DSL source. "
        "It is separate from CVDP harness grading. On Windows, Verilator launcher issues "
        "may make this fail even when MyGo compile succeeds."
    )
    if sim_verilog.exists():
        try:
            shutil.copyfile(sim_verilog, out_dir / "mygo_sim_design.sv")
            res["copied_verilog_out"] = str(out_dir / "mygo_sim_design.sv")
        except Exception as exc:
            res["copy_warning"] = f"{type(exc).__name__}: {exc}"
    (out_dir / "MyGo仿真结果.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"status: {res.get('status')}",
        f"returncode: {res.get('returncode')}",
        f"elapsed_seconds: {res.get('elapsed_seconds')}",
        f"ascii_work_dir: {res.get('ascii_work_dir')}",
        f"verilog_out: {res.get('verilog_out')}",
        "",
        res.get("note", ""),
        "",
        "---- MyGo sim log ----",
        res.get("output_log", ""),
    ]
    (out_dir / "MyGo仿真结果.txt").write_text("\n".join(lines), encoding="utf-8")
    return res


def split_go_fields(raw: str) -> list[GoArg]:
    raw = raw.strip()
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    result: list[GoArg] = []
    pending_names: list[str] = []
    for part in parts:
        tokens = part.split()
        if len(tokens) == 1:
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", tokens[0]) and tokens[0] not in {
                "bool",
                "int8",
                "int16",
                "int32",
                "int64",
                "uint8",
                "uint16",
                "uint32",
                "uint64",
            }:
                pending_names.append(tokens[0])
            else:
                result.append(GoArg(f"out{len(result)}", tokens[0]))
            continue
        typ = tokens[-1]
        names = pending_names + tokens[:-1]
        pending_names = []
        for name in names:
            result.append(GoArg(name.strip(), typ))
    for name in pending_names:
        result.append(GoArg(name, "uint64"))
    return result


def parse_go_signature(code: str, target: str) -> tuple[list[GoArg], list[GoArg]]:
    m = re.search(
        rf"\bfunc\s+{re.escape(target)}\s*\((?P<params>[^)]*)\)\s*(?P<returns>\([^)]*\)|[A-Za-z_][A-Za-z0-9_]*)?",
        code,
        flags=re.S,
    )
    if not m:
        return [], []
    params = split_go_fields(m.group("params") or "")
    raw_returns = (m.group("returns") or "").strip()
    if raw_returns.startswith("(") and raw_returns.endswith(")"):
        raw_returns = raw_returns[1:-1]
    returns = split_go_fields(raw_returns)
    return params, returns


def go_function_body(code: str, target: str) -> str | None:
    m = re.search(rf"\bfunc\s+{re.escape(target)}\s*\(", code)
    if not m:
        return None
    open_idx = code.find("{", m.end())
    if open_idx < 0:
        return None
    depth = 0
    for idx in range(open_idx, len(code)):
        ch = code[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return code[open_idx + 1 : idx]
    return None


def restricted_go_check(code: str, target: str) -> str | None:
    scan = re.sub(r"//.*", "", code)
    scan = re.sub(r"/\*.*?\*/", "", scan, flags=re.S)
    funcs = re.findall(r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", code)
    extra = [name for name in funcs if name not in {target, "main"}]
    if extra:
        return "Do not define helper functions; extra functions found: " + ", ".join(extra)
    if not re.search(rf"\bfunc\s+{re.escape(target)}\s*\(", code):
        return f"Missing requested target function {target}."
    params, returns = parse_go_signature(code, target)
    reserved = sorted({arg.name for arg in params + returns if arg.name in GO_RESERVED})
    if reserved:
        return "Do not use Go reserved keywords as identifiers; rename by position: " + ", ".join(reserved)
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for scope, args in (("input", params), ("output", returns)):
        for arg in args:
            if not arg.name:
                continue
            if arg.name in seen and arg.name not in duplicates:
                duplicates.append(arg.name)
            seen[arg.name] = scope
    if duplicates:
        return "Do not reuse the same Go identifier for multiple ports/results; rename outputs with out_<name>: " + ", ".join(duplicates)
    body = go_function_body(code, target)
    if returns and body is not None:
        body_scan = re.sub(r"//.*", "", body)
        body_scan = re.sub(r"/\*.*?\*/", "", body_scan, flags=re.S).rstrip()
        if not re.search(r"\breturn\s*$", body_scan):
            return "End the requested top function's final fallthrough path with an explicit bare return."
    if re.search(r"\b1\s*<<\s*64\b", scan):
        return "Do not use 1 << 64; use ^uint64(0) for a 64-bit all-ones mask."
    banned_patterns = [
        (r"\bimport\b", "Do not use imports."),
        (r"\bswitch\b|\bcase\b", "Do not use switch/case; use if/else."),
        (r"\bfor\b", "Do not use for loops; manually unroll repeated logic."),
        (r"\bstruct\b|\binterface\b|\bmap\b|\bchan\b|\bgo\b|\bselect\b", "Do not use unsupported Go constructs."),
        (r"(?<!/)/(?!/)", "Do not use division; use shifts for powers of two."),
        (r"%", "Do not use modulo; use masks."),
    ]
    for pattern, message in banned_patterns:
        if re.search(pattern, scan):
            return message
    if not re.search(r"\bfunc\s+main\s*\(\s*\)\s*\{\s*\}", code):
        return "Include exactly an empty func main() {}."
    return None


def sv_range_from_width(width: str) -> str:
    raw = strip_md(width)
    if not raw:
        return ""
    raw = raw.replace("×", "*")
    if re.search(r"\[\s*.*?:.*?\s*\]", raw):
        return re.search(r"\[\s*.*?:.*?\s*\]", raw).group(0)
    if raw.lower() in {"1", "1 bit", "bit", "logic", "wire", "bool"}:
        return ""
    if re.search(r"[A-Za-z0-9_()*/+\-]", raw):
        expr = re.sub(r"[^A-Za-z0-9_()*/+\- ]", "", raw).strip()
        if expr and expr != "1":
            return f"[({expr})-1:0]"
    return ""


def split_return_sort_key(output_name: str, arg: GoArg) -> tuple[int, str]:
    suffix = arg.name[len(output_name) :].lstrip("_").lower() if arg.name.startswith(output_name) else arg.name.lower()
    high_words = ("sync", "header", "high", "msb", "upper")
    low_words = ("data", "low", "lsb", "lower")
    if any(word in suffix for word in high_words):
        return (0, arg.name)
    if any(word in suffix for word in low_words):
        return (2, arg.name)
    return (1, arg.name)


def split_return_suffix(output_name: str, arg: GoArg) -> str:
    return arg.name[len(output_name) :].lstrip("_").lower() if arg.name.startswith(output_name) else ""


def is_split_return_candidate(output_name: str, arg: GoArg) -> bool:
    suffix = split_return_suffix(output_name, arg)
    if not suffix:
        return False
    if any(word in suffix.split("_") for word in ("valid", "ready", "enable", "done", "flag", "error")):
        return False
    return bool(re.search(r"(sync|header|high|hi|msb|upper|data|low|lo|lsb|lower|\d+)$", suffix))


def split_concat_expr(port: PortSpec, bindings: list[tuple[GoArg, str]]) -> str:
    if len(bindings) == 1:
        return bindings[0][1]
    port_bits = port.bits or sum(arg.bits for arg, _ in bindings)
    low_idx = None
    canonical = go_identifier(port.name)
    for i, (arg, _) in enumerate(bindings):
        suffix = arg.name[len(canonical) :].lstrip("_").lower() if arg.name.startswith(canonical) else arg.name.lower()
        if any(word in suffix for word in ("data", "low", "lsb", "lower")):
            low_idx = i
    if low_idx is not None:
        low_arg, low_wire = bindings[low_idx]
        high_bits = max(port_bits - low_arg.bits, 0)
        high_parts = []
        for i, (arg, wire) in enumerate(bindings):
            if i == low_idx or high_bits <= 0:
                continue
            take = min(arg.bits, high_bits)
            high_bits -= take
            high_parts.append(f"{wire}[{take - 1}:0]" if take > 1 else wire)
        return "{" + ", ".join(high_parts + [low_wire]) + "}" if high_parts else low_wire
    return "{" + ", ".join(wire for _, wire in bindings) + "}"


def adapt_verilog(
    raw_sv: str,
    module_name: str,
    prompt_ports: list[PortSpec],
    params: dict[str, str],
    go_params: list[GoArg],
    go_returns: list[GoArg],
) -> tuple[str, str]:
    if not raw_sv.strip():
        return raw_sv, "No MyGo Verilog was available to adapt."
    top = sv_identifier(module_name)
    core = "__mygo_core_" + top
    adapted = re.sub(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)\b", f"module {core}", raw_sv, count=1)
    input_ports = [p for p in prompt_ports if p.direction == "input"]
    output_ports = [p for p in prompt_ports if p.direction == "output"]
    if not input_ports and go_params:
        input_ports = [PortSpec("input", p.name, str(p.bits), p.bits) for p in go_params]
    if not output_ports and go_returns:
        output_ports = [PortSpec("output", p.name, str(p.bits), p.bits) for p in go_returns]

    param_items = [(k, v) for k, v in params.items() if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k)]
    lines = []
    if param_items:
        lines.append(f"module {top} #(")
        for i, (name, value) in enumerate(param_items):
            comma = "," if i < len(param_items) - 1 else ""
            lines.append(f"  parameter integer {name} = {value}{comma}")
        lines.append(")(")
    else:
        lines.append(f"module {top}(")
    port_lines = []
    all_ports = input_ports + output_ports
    for i, port in enumerate(all_ports):
        direction = "input" if port.direction == "input" else "output"
        rng = sv_range_from_width(port.width)
        rng_text = f" {rng}" if rng else ""
        comma = "," if i < len(all_ports) - 1 else ""
        port_lines.append(f"  {direction}{rng_text} {sv_identifier(port.name)}{comma}")
    lines.extend(port_lines)
    lines.append(");")

    return_map = {arg.name: arg for arg in go_returns}
    output_bindings: dict[str, list[tuple[GoArg, str]]] = {}
    for idx, port in enumerate(output_ports):
        canonical = go_identifier(port.name)
        binding_args: list[GoArg] = []
        arg = return_map.get(port.name) or return_map.get(canonical)
        if arg is not None:
            binding_args = [arg]
        elif port.bits and port.bits > 64:
            candidates = [
                item
                for item in go_returns
                if (
                    (item.name.startswith(canonical + "_") or item.name.startswith(port.name + "_"))
                    and is_split_return_candidate(canonical, item)
                )
            ]
            binding_args = sorted(candidates, key=lambda item: split_return_sort_key(canonical, item))
        if binding_args:
            output_bindings[port.name] = [
                (item, "__mygo_" + sv_identifier(item.name if len(binding_args) > 1 else port.name))
                for item in binding_args
            ]
    for idx, port in enumerate(output_ports):
        bindings = output_bindings.get(port.name, [])
        if not bindings:
            bits = port.bits or 64
            rng = f"[{max(bits, 1)-1}:0] " if bits > 1 else ""
            lines.append(f"  wire {rng}__mygo_{sv_identifier(port.name)};")
            continue
        for arg, wire in bindings:
            bits = arg.bits
            rng = f"[{max(bits, 1)-1}:0] " if bits > 1 else ""
            lines.append(f"  wire {rng}{wire};")

    conns = []
    input_by_name = {p.name: p for p in input_ports}
    for idx, arg in enumerate(go_params):
        port = input_by_name.get(arg.name)
        if port is None and idx < len(input_ports):
            port = input_ports[idx]
        if port is not None:
            conns.append((arg.name, sv_identifier(port.name)))
    for idx, arg in enumerate(go_returns):
        wire = None
        for bindings in output_bindings.values():
            for bound_arg, bound_wire in bindings:
                if bound_arg.name == arg.name:
                    wire = bound_wire
                    break
            if wire is not None:
                break
        if wire is None and idx < len(output_ports):
            candidate = output_ports[idx]
            if arg.name == candidate.name or arg.name == go_identifier(candidate.name):
                wire = "__mygo_" + sv_identifier(candidate.name)
        if wire is not None:
            conns.append((arg.name, wire))
    lines.append(f"  {core} __mygo_inst (")
    for i, (core_port, wrapper_signal) in enumerate(conns):
        comma = "," if i < len(conns) - 1 else ""
        lines.append(f"    .{sv_identifier(core_port)}({wrapper_signal}){comma}")
    lines.append("  );")
    for idx, port in enumerate(output_ports):
        bindings = output_bindings.get(port.name)
        expr = split_concat_expr(port, bindings) if bindings else "__mygo_" + sv_identifier(port.name)
        lines.append(f"  assign {sv_identifier(port.name)} = {expr};")
    lines.append("endmodule")
    note = (
        "Adapted by renaming the MyGo module to a core module and adding a CVDP-facing wrapper. "
        "The wrapper exposes prompt-derived parameters and ports; width mismatches are left for SystemVerilog truncation/extension."
    )
    return adapted + "\n\n" + "\n".join(lines) + "\n", note


def restore_harness(task_dir: Path, task: dict, rtl_outputs: dict[str, str]) -> Path:
    harness_dir = task_dir / "harness"
    if harness_dir.exists():
        shutil.rmtree(harness_dir)
    harness_dir.mkdir(parents=True)
    for rel, content in (task.get("harness", {}).get("files", {}) or {}).items():
        dest = harness_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = content.replace("__OSS_SIM_IMAGE__", "nvidia/cvdp-sim:v1.0.0")
        content = content.replace("__OSS_PNR_IMAGE__", "nvidia/cvdp-sim:v1.0.0")
        dest.write_text(content, encoding="utf-8")
    for rel, content in (task.get("input", {}).get("context", {}) or {}).items():
        dest = harness_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    for rel, content in rtl_outputs.items():
        dest = harness_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    return harness_dir


def run_host_harness(task_dir: Path, task: dict, rtl_outputs: dict[str, str], timeout: float) -> dict:
    harness_dir = restore_harness(task_dir, task, rtl_outputs)
    env_file = harness_dir / "src" / ".env"
    test_runner = harness_dir / "src" / "test_runner.py"
    if not env_file.exists() or not test_runner.exists():
        return {"status": "NOT_RUN", "reason": "No src/.env or src/test_runner.py in public harness."}
    env_vars = env_map(task)
    env = os.environ.copy()

    def remap(value: str) -> str:
        return (
            value.replace("/code/", str(harness_dir).replace("\\", "/") + "/")
            .replace("/src/", str((harness_dir / "src")).replace("\\", "/") + "/")
            .replace("/rundir/", str((harness_dir / "rundir")).replace("\\", "/") + "/")
        )

    for key, value in env_vars.items():
        env[key] = remap(value)
    env["PYTHONPATH"] = str(harness_dir / "src")
    rundir = harness_dir / "rundir"
    rundir.mkdir(exist_ok=True)
    return run_cmd([sys.executable, str(test_runner)], rundir, timeout, env)


def write_task_inputs(task_dir: Path, task: dict, prompt: str, prompt_meta: dict) -> None:
    (task_dir / "题目.json").write_text(
        json.dumps(
            {
                "id": task["id"],
                "categories": task.get("categories"),
                "input": task.get("input"),
                "expected_output_files": expected_files(task),
                "prompt_meta": prompt_meta,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (task_dir / "题目.txt").write_text(task.get("input", {}).get("prompt", ""), encoding="utf-8")
    (task_dir / "发送给DeepSeek的提示.txt").write_text(
        SYSTEM_PROMPT + "\n\n--- USER PROMPT ---\n" + prompt,
        encoding="utf-8",
    )


def write_result(task_dir: Path, result: dict) -> None:
    (task_dir / "测试结果.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"id: {result.get('id')}",
        f"status: {result.get('status')}",
    ]
    if result.get("reason"):
        lines.append(f"reason: {result['reason']}")
    if result.get("returncode") is not None:
        lines.append(f"returncode: {result['returncode']}")
    if result.get("elapsed_seconds") is not None:
        lines.append(f"elapsed_seconds: {result['elapsed_seconds']:.2f}")
    if result.get("output_log"):
        lines.extend(["", "---- CVDP harness log ----", result["output_log"]])
    (task_dir / "测试结果.txt").write_text("\n".join(lines), encoding="utf-8")


def is_valid_exam_result(result: dict) -> bool:
    status = result.get("status")
    if status in {"PASS", "FAIL", "MODEL_STATIC_ERROR", "MYGO_STATIC_ERROR", "MYGO_COMPILE_ERROR"}:
        return True
    if status == "NO_MODEL_ERROR":
        return False
    if status not in {"MODEL_ERROR", "MODEL_OR_MYGO_ERROR"}:
        return False
    reason = str(result.get("reason") or "")
    transient_markers = [
        "NoneType: None",
        "no_model mode enabled",
        "Model returned empty response",
        "APITimeoutError",
        "APIConnectionError",
        "RateLimitError",
        "InternalServerError",
        "BadGateway",
        "ServiceUnavailable",
    ]
    return not any(marker in reason for marker in transient_markers)


def build_mygo_if_needed(mygo_root: Path, mygo_path: Path, rebuild: bool = False) -> None:
    if mygo_path.exists() and not rebuild:
        return
    env = os.environ.copy()
    env["GOCACHE"] = str(mygo_root / ".gocache-agent")
    env["GOMODCACHE"] = str(mygo_root / ".gomodcache-agent")
    mygo_path.parent.mkdir(parents=True, exist_ok=True)
    res = run_cmd(["go", "build", "-o", str(mygo_path), "./cmd/mygo"], mygo_root, 180, env)
    if res["status"] != "PASS":
        raise RuntimeError("Failed to build mygo.exe:\n" + res.get("output_log", ""))


def find_existing_go_dir(task_dir: Path) -> Path | None:
    for candidate in task_dir.iterdir():
        if candidate.is_dir() and (candidate / "main.go").exists():
            return candidate
    return None


def read_task_id_file(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for part in re.split(r"[\s,]+", line):
            part = part.strip()
            if part:
                ids.append(part)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--mygo-root", type=Path, default=DEFAULT_MYGO_ROOT)
    parser.add_argument("--mygo", type=Path, default=DEFAULT_MYGO)
    parser.add_argument("--circt-opt", type=Path, default=DEFAULT_CIRCT_OPT)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--task-id", action="append", default=[])
    parser.add_argument("--task-id-file", type=Path, default=None)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--reuse-model-output", action="store_true")
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--no-harness", action="store_true")
    parser.add_argument("--no-mygo-sim", action="store_true")
    parser.add_argument("--rebuild-mygo", action="store_true")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--go-attempts", type=int, default=3)
    parser.add_argument("--model-timeout", type=float, default=300)
    parser.add_argument("--mygo-timeout", type=float, default=90)
    parser.add_argument("--mygo-sim-timeout", type=float, default=120)
    parser.add_argument("--harness-timeout", type=float, default=180)
    args = parser.parse_args()

    build_mygo_if_needed(args.mygo_root, args.mygo, args.rebuild_mygo)
    tasks = load_tasks(args.dataset, args.csv)
    for original_idx, task in enumerate(tasks, 1):
        task["_exam_idx"] = original_idx
    selected_task_ids = set(args.task_id or [])
    if args.task_id_file is not None:
        selected_task_ids.update(read_task_id_file(args.task_id_file))
    if selected_task_ids:
        available_ids = {task["id"] for task in tasks}
        missing_ids = sorted(selected_task_ids - available_ids)
        if missing_ids:
            raise RuntimeError("Unknown task id(s): " + ", ".join(missing_ids))
        tasks = [task for task in tasks if task["id"] in selected_task_ids]
    if args.limit is not None:
        tasks = tasks[: args.limit]

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "README.txt").write_text(
        "CVDP cid003 run using DeepSeek to generate restricted Go, MyGo to generate Verilog, and local CVDP harnesses for testing.\n"
        "Leakage guard: prompts use only input.prompt, input.context, expected output filenames, and MyGo restrictions. Dataset output.response/output.context are checked empty before use. Harness files are not sent to the model.\n"
        "The CVDP-facing Verilog is a local wrapper around MyGo-generated Verilog when wrapper adaptation is needed.\n",
        encoding="utf-8",
    )

    client = None
    if not args.no_model:
        client = OpenAI(api_key=read_key(args.key_file), base_url=OPENROUTER_BASE_URL)

    summary = []
    total_tasks = len(tasks)
    for run_idx, task in enumerate(tasks, 1):
        idx = int(task.get("_exam_idx") or run_idx)
        task_name = f"{idx:02d}_{sanitize_name(task['id'])}"
        task_dir = args.out / task_name
        task_dir.mkdir(parents=True, exist_ok=True)
        result_path = task_dir / "测试结果.json"
        if args.skip_existing and result_path.exists():
            try:
                existing = json.loads(result_path.read_text(encoding="utf-8"))
                if is_valid_exam_result(existing):
                    summary.append({"idx": idx, "run_idx": run_idx, "id": task["id"], "status": existing.get("status"), "reason": existing.get("reason")})
                    print(f"[{run_idx}/{total_tasks} idx={idx}] {task['id']} -> skipped {existing.get('status')}", flush=True)
                    continue
            except Exception:
                pass

        prompt, prompt_meta = build_prompt(task)
        write_task_inputs(task_dir, task, prompt, prompt_meta)
        files = expected_files(task)
        module_name = prompt_meta["module_name"]
        default_target = go_identifier(module_name)

        model_error = None
        error_status = None
        target = default_target
        go_code = ""
        llm_meta = {}
        go_source_path = None
        mygo_dir = task_dir / "MyGo输出"

        existing_go_dir = find_existing_go_dir(task_dir) if args.reuse_model_output else None
        if existing_go_dir is not None:
            go_source_path = existing_go_dir / "main.go"
            original_go_code = go_source_path.read_text(encoding="utf-8")
            go_code = normalize_go_source_text(original_go_code)
            if go_code != original_go_code:
                go_source_path.write_text(go_code, encoding="utf-8")
            try:
                llm_meta = json.loads((task_dir / "llm_meta.json").read_text(encoding="utf-8"))
            except Exception:
                llm_meta = {}
            target = llm_meta.get("target_function") or find_go_function(go_code) or default_target
            if not is_go_identifier(target):
                target = default_target
            static_error = restricted_go_check(go_code, target)
            if static_error:
                model_error = static_error
                error_status = "MODEL_STATIC_ERROR"
            else:
                compile_info = compile_mygo(args.mygo, args.circt_opt, args.mygo_root, go_source_path, target, mygo_dir, args.mygo_timeout)
                (mygo_dir / "mygo_compile_result.json").write_text(json.dumps(compile_info, ensure_ascii=False, indent=2), encoding="utf-8")
                if compile_info["status"] != "PASS":
                    model_error = mygo_failure_reason(compile_info, "MyGo compile failed for reused model output")
                    error_status = "MYGO_COMPILE_ERROR"
        elif args.no_model:
            model_error = "no_model mode enabled"
            error_status = "NO_MODEL_ERROR"
        else:
            compile_status = None
            compile_info = None
            feedback = ""
            for attempt in range(1, args.go_attempts + 1):
                attempt_prompt = prompt
                if feedback:
                    attempt_prompt += "\n\nPrevious MyGo compile failed. Revise only the restricted Go code. Compiler log:\n" + feedback[-6000:]
                (task_dir / f"发送给DeepSeek的提示_attempt{attempt}.txt").write_text(
                    SYSTEM_PROMPT + "\n\n--- USER PROMPT ---\n" + attempt_prompt,
                    encoding="utf-8",
                )
                last_exc = None
                raw_text = ""
                for retry in range(1, args.retries + 1):
                    try:
                        raw_text, meta = call_model(client, args.model, attempt_prompt, args.model_timeout)
                        meta["attempt"] = attempt
                        meta["retry"] = retry
                        llm_meta = meta
                        if not raw_text.strip():
                            (task_dir / f"llm_empty_response_attempt{attempt}_retry{retry}.json").write_text(
                                json.dumps(meta, ensure_ascii=False, indent=2),
                                encoding="utf-8",
                            )
                            last_exc = RuntimeError("Model returned empty response")
                            if retry < args.retries:
                                time.sleep(min(10 * retry, 30))
                                continue
                        break
                    except Exception as exc:
                        last_exc = exc
                        if retry < args.retries:
                            time.sleep(min(10 * retry, 30))
                if not raw_text:
                    if last_exc is None:
                        model_error = "Model returned empty response"
                    else:
                        model_error = f"{type(last_exc).__name__}: {last_exc}"
                    error_status = "MODEL_ERROR"
                    break
                (task_dir / f"DeepSeek原始回复_attempt{attempt}.txt").write_text(raw_text, encoding="utf-8")
                target, go_code = parse_model_response(raw_text, default_target)
                if not is_go_identifier(target):
                    target = default_target
                go_dir = task_dir / "DeepSeek生成的Go"
                go_dir.mkdir(exist_ok=True)
                attempts_dir = go_dir / "attempts"
                attempts_dir.mkdir(exist_ok=True)
                (attempts_dir / f"main_attempt{attempt}.go").write_text(go_code, encoding="utf-8")
                (go_dir / "main.go").write_text(go_code, encoding="utf-8")
                (go_dir / "go.mod").write_text("module cvdp_mygo_task\n\ngo 1.25.4\n", encoding="utf-8")
                go_source_path = go_dir / "main.go"
                llm_meta["target_function"] = target
                (task_dir / "llm_meta.json").write_text(json.dumps(llm_meta, ensure_ascii=False, indent=2), encoding="utf-8")

                static_error = restricted_go_check(go_code, target)
                if static_error:
                    error_status = "MODEL_STATIC_ERROR"
                    feedback = static_error
                    (task_dir / f"restricted_go_check_attempt{attempt}.txt").write_text(static_error, encoding="utf-8")
                    continue

                compile_info = compile_mygo(args.mygo, args.circt_opt, args.mygo_root, go_source_path, target, mygo_dir, args.mygo_timeout)
                (mygo_dir / "mygo_compile_result.json").write_text(json.dumps(compile_info, ensure_ascii=False, indent=2), encoding="utf-8")
                compile_status = compile_info["status"]
                if compile_status == "PASS":
                    break
                feedback = compile_info.get("error_log") or json.dumps(compile_info, ensure_ascii=False)

            if model_error is None and compile_status != "PASS":
                model_error = mygo_failure_reason(compile_info or {}, "MyGo compile failed after DeepSeek revision attempts")
                error_status = "MYGO_COMPILE_ERROR" if compile_info else (error_status or "MODEL_ERROR")

        if model_error:
            error_status = error_status or fallback_failure_status(model_error)
            result = {
                "id": task["id"],
                "status": error_status,
                "reason": model_error,
                "expected_output_files": files,
                "target_function": target,
            }
            write_result(task_dir, result)
        else:
            mygo_sv_path = mygo_dir / "mygo_raw.sv"
            raw_sv = mygo_sv_path.read_text(encoding="utf-8") if mygo_sv_path.exists() else ""
            go_params, go_returns = parse_go_signature(go_code, target)
            adapted_sv, note = adapt_verilog(
                raw_sv,
                module_name,
                [PortSpec(**p) for p in prompt_meta["ports"]],
                prompt_meta["params"],
                go_params,
                go_returns,
            )
            (task_dir / "适配说明.txt").write_text(note, encoding="utf-8")
            (task_dir / "CVDP测试用Verilog.sv").write_text(adapted_sv, encoding="utf-8")
            if not args.no_mygo_sim:
                sim_dir = task_dir / "MyGo仿真"
                if go_source_path is not None:
                    sim_mygo(args.mygo, args.circt_opt, args.mygo_root, go_source_path, target, sim_dir, args.mygo_sim_timeout)
            rtl_outputs = {files[0]: adapted_sv}
            if args.no_harness:
                result = {
                    "id": task["id"],
                    "status": "NOT_RUN",
                    "reason": "no_harness mode enabled",
                    "expected_output_files": files,
                    "target_function": target,
                }
            else:
                result = run_host_harness(task_dir, task, rtl_outputs, args.harness_timeout)
                result.update({"id": task["id"], "expected_output_files": files, "target_function": target})
            write_result(task_dir, result)

        summary.append({"idx": idx, "run_idx": run_idx, "id": task["id"], "status": result.get("status"), "reason": result.get("reason")})
        (args.out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        counts = {}
        for item in summary:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        (args.out / "summary.txt").write_text(
            "\n".join([f"{k}: {v}" for k, v in sorted(counts.items())]) + "\n",
            encoding="utf-8",
        )
        print(f"[{run_idx}/{total_tasks} idx={idx}] {task['id']} -> {result.get('status')}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
