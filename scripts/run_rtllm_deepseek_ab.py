#!/usr/bin/env python3
"""Run RTLLM A/B evaluation with DeepSeek V4 Pro.

Path A: design_description -> SystemVerilog -> RTLLM testbench.
Path B: design_description -> restricted Go/MyGo DSL -> MyGo -> SystemVerilog -> RTLLM testbench.

The script is resumable and writes one artifact directory per task/path.
"""

from __future__ import annotations

import argparse
import csv
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
- Do not output Verilog. Return only Go source code.
- Every named return value must be assigned on every path, then end the function with an explicit bare return statement.
- Do not read a named return value before assigning it; use a local temporary then assign the return.
- Mask arithmetic back to intended widths when needed, e.g. x &= 0xff.
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

@dataclass
class Task:
    index: int
    rel: str
    dir: Path
    module: str
    ports: list[Port]
    description: str


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


def parse_width(raw: str) -> int:
    raw = raw.strip()
    m = re.search(r"\[\s*(\d+)\s*:\s*(\d+)\s*\]", raw)
    if m:
        return abs(int(m.group(1)) - int(m.group(2))) + 1
    m = re.search(r"(\d+)\s*-\s*bit", raw, flags=re.I)
    if m:
        return int(m.group(1))
    return 1


def parse_tasks(rtllm_root: Path) -> list[Task]:
    tasks: list[Task] = []
    for desc_path in sorted(rtllm_root.rglob("design_description.txt"), key=lambda p: str(p.relative_to(rtllm_root))):
        text = desc_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"Module name:\s*\r?\n\s*([A-Za-z_][A-Za-z0-9_]*)", text, flags=re.I)
        if not m:
            continue
        module = m.group(1)
        ports = parse_ports(text)
        tasks.append(Task(len(tasks) + 1, str(desc_path.parent.relative_to(rtllm_root)), desc_path.parent, module, ports, text))
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


def extract_code(text: str, kind: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:systemverilog|verilog|sv|go|golang)?\s*(.*?)```", text, flags=re.S | re.I)
    if m:
        text = m.group(1).strip()
    if kind == "go":
        m = re.search(r"(package\s+main\b.*)", text, flags=re.S)
        if m:
            text = m.group(1).strip()
        if "func main" not in text:
            text = text.rstrip() + "\n\nfunc main() {}\n"
        return text.rstrip() + "\n"
    first = re.search(r"\bmodule\s+[A-Za-z_][A-Za-z0-9_$]*\b", text)
    last = text.rfind("endmodule")
    if first and last >= first.start():
        text = text[first.start() : last + len("endmodule")].strip()
    return text.rstrip() + "\n"


def call_model(client: OpenAI, model: str, system: str, user: str) -> tuple[str, dict[str, Any]]:
    t0 = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.1,
        max_tokens=8192,
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


def run_cmd(cmd: list[str], cwd: Path, timeout: float, env: dict[str, str] | None = None) -> dict[str, Any]:
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, env=env)
        return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "elapsed_seconds": time.time() - t0, "timeout": False}
    except subprocess.TimeoutExpired as exc:
        return {"returncode": None, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "elapsed_seconds": time.time() - t0, "timeout": True}


def simulate(task_dir: Path, design_file: Path, timeout: float = 60) -> tuple[str, str, dict[str, Any]]:
    sim_out = task_dir / "sim.out"
    if sim_out.exists():
        sim_out.unlink()
    comp = run_cmd(["iverilog", "-g2012", "-o", str(sim_out), str(design_file), "testbench.v"], task_dir, timeout)
    if comp["timeout"]:
        return "COMPILE_TIMEOUT", "iverilog timeout", {"compile": comp}
    if comp["returncode"] != 0:
        return "COMPILE_FAIL", (comp["stdout"] + comp["stderr"]).strip(), {"compile": comp}
    run = run_cmd(["vvp", str(sim_out)], task_dir, timeout)
    out = (run["stdout"] + run["stderr"]).strip()
    if run["timeout"]:
        return "TIMEOUT", out or "simulation timeout", {"compile": comp, "simulation": run}
    if "Your Design Passed" in out or re.search(r"\bPassed\b", out):
        return "PASS", out, {"compile": comp, "simulation": run}
    if run["returncode"] != 0:
        return "SIM_ERROR", out, {"compile": comp, "simulation": run}
    return "FAIL", out, {"compile": comp, "simulation": run}


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


def run_direct(task: Task, out_root: Path, client: OpenAI, model: str, reuse: bool) -> dict[str, Any]:
    out = out_root / f"{task.index:03d}_{sanitize_path(task.rel)}" / "direct_verilog"
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
            raw, meta = call_model(client, model, SYSTEM_VERILOG_PROMPT, prompt)
            raw_path.write_text(raw, encoding="utf-8")
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        code = extract_code(raw, "verilog")
        sv_path.write_text(code, encoding="utf-8")
        status, reason, detail = simulate(out, sv_path)
    except Exception as exc:
        status, reason, detail = "MODEL_ERROR", f"{type(exc).__name__}: {exc}", {}
    result = {"task_index": task.index, "task": task.rel, "module": task.module, "path": "direct_verilog", "status": status, "reason": reason, "artifacts": str(out), "detail": detail}
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def run_mygo(task: Task, out_root: Path, client: OpenAI, model: str, mygo_bin: Path, circt_opt: Path, reuse: bool) -> dict[str, Any]:
    out = out_root / f"{task.index:03d}_{sanitize_path(task.rel)}" / "mygo"
    out.mkdir(parents=True, exist_ok=True)
    copy_task_files(task.dir, out)
    raw_path = out / "model_raw.txt"
    go_path = out / "main.go"
    gomod_path = out / "go.mod"
    sv_path = out / f"{task.module}.v"
    meta_path = out / "model_meta.json"
    prompt_path = out / "prompt_sent.txt"
    iface = "\n".join(f"- {p.direction} {p.name}[{p.width}]" for p in task.ports) or "- Could not parse ports; infer from description."
    prompt = "\n\n".join([
        f"RTLLM module name: {task.module}",
        f"Suggested Go signature: {suggested_go_signature(task)}",
        "Parsed ports:", iface,
        MYGO_RULES,
        "RTLLM design description:", task.description.strip(),
    ])
    prompt_path.write_text(SYSTEM_MYGO_PROMPT + "\n--- USER ---\n" + prompt, encoding="utf-8")
    try:
        if reuse and raw_path.exists():
            raw = raw_path.read_text(encoding="utf-8", errors="ignore")
            meta = {"source": "cache"}
        else:
            raw, meta = call_model(client, model, SYSTEM_MYGO_PROMPT, prompt)
            raw_path.write_text(raw, encoding="utf-8")
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        go_code = extract_code(raw, "go")
        go_path.write_text(go_code, encoding="utf-8")
        gomod_path.write_text("module rtllm_mygo_task\n\ngo 1.25.4\n", encoding="utf-8")
        env = os.environ.copy()
        env.setdefault("GOTOOLCHAIN", "local")
        env["GOCACHE"] = str(out_root / ".gocache")
        env["GOMODCACHE"] = str(out_root / ".gomodcache")
        cmd = [str(mygo_bin), "compile", "-emit", "verilog", "-target", go_ident(task.module), "-circt-opt", str(circt_opt), "-o", str(sv_path), str(go_path)]
        comp = run_cmd(cmd, out, 180, env)
        if comp["timeout"]:
            status, reason, detail = "MYGO_TIMEOUT", "MyGo compile timeout", {"mygo_compile": comp}
        elif comp["returncode"] != 0:
            status, reason, detail = "MYGO_COMPILE_ERROR", (comp["stdout"] + comp["stderr"]).strip(), {"mygo_compile": comp}
        else:
            status, reason, detail = simulate(out, sv_path)
            detail["mygo_compile"] = comp
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
    for path in ["direct_verilog", "mygo"]:
        c = counts.get(path, {})
        total = sum(c.values())
        passed = c.get("PASS", 0)
        rate = (100.0 * passed / total) if total else 0.0
        count_text = ", ".join(f"{k}={v}" for k, v in sorted(c.items()))
        lines.append(f"| {path} | {passed} | {total} | {rate:.2f}% | {count_text} |")
    lines.extend(["", "## Per Task", "", "| # | Task | Module | Direct | MyGo |", "| ---: | --- | --- | --- | --- |"])
    by_task: dict[str, dict[str, Any]] = {}
    for r in results:
        by_task.setdefault(r["task"], {"index": r["task_index"], "module": r["module"]})[r["path"]] = r
    for task, entry in sorted(by_task.items(), key=lambda kv: kv[1]["index"]):
        da = entry.get("direct_verilog", {}).get("status", "-")
        mb = entry.get("mygo", {}).get("status", "-")
        lines.append(f"| {entry['index']} | `{task}` | `{entry['module']}` | {da} | {mb} |")
    (out_root / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_root / "SUMMARY.txt").write_text(json.dumps(counts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    ap.add_argument("--path", choices=["direct", "mygo", "both"], default="both")
    ap.add_argument("--reuse", action="store_true")
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
    if args.limit:
        tasks = tasks[: args.limit]
    (args.out / "tasks.json").write_text(json.dumps([asdict(t) | {"dir": str(t.dir)} for t in tasks], ensure_ascii=False, indent=2), encoding="utf-8")

    results: list[dict[str, Any]] = []
    futures = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        for task in tasks:
            if args.path in {"direct", "both"}:
                futures.append(ex.submit(run_direct, task, args.out, client, args.model, args.reuse))
            if args.path in {"mygo", "both"}:
                futures.append(ex.submit(run_mygo, task, args.out, client, args.model, args.mygo_bin, args.circt_opt, args.reuse))
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
