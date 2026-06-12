#!/usr/bin/env python3
"""A/B evaluation harness: LLM→Verilog (Path A) vs LLM→Go→MyGO→Verilog (Path B).

Usage:
    export PATH="/home/node/go-install/go/bin:/workspace/feiyang/mygo/circt/bin:$PATH"
    python3 tests/verilog-eval/eval_ab_harness.py --output-dir /tmp/eval_ab --limit 5
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMPTS_DIR = REPO_ROOT / "verilog-eval" / "historical" / "dataset_spec-to-rtl" / "prompts"
REF_DIR = REPO_ROOT / "tests" / "verilog-eval" / "reference_verilog"
TEST_DIR = REPO_ROOT / "tests" / "verilog-eval" / "test_verilog"
GO_SOLUTIONS_DIR = REPO_ROOT / "tests" / "verilog-eval" / "current_go_156"

API_BASE = "http://localhost:3000/v1"
API_KEY = "proxy-b99682656cc61f944a632d41e5e58c524ec3187c95e5faa069afbe18a1615a2e"
MODEL = "deepseek/deepseek-v4-pro"
TEMPERATURE = 0.0

FEWSHOT_CASES = ["Prob001_zero", "Prob041_dff8r", "Prob109_fsm1", "Prob038_count15", "Prob025_reduction"]

# ---------------------------------------------------------------------------
# Tutorials (comparable size for fairness)
# ---------------------------------------------------------------------------
VERILOG_TUTORIAL = """\
SystemVerilog quick reference for this task:

1. Define exactly one module named TopModule with the same ports as RefModule.
2. Use `assign` for simple combinational outputs.
3. Use `always_comb` (or `always @(*)`) for complex combinational logic.
4. Use `always @(posedge clk)` for sequential (clocked) logic.
5. In sequential blocks use non-blocking `<=` for flip-flop assignments.
6. In combinational blocks use blocking `=`.
7. Bit operations: `&` (and), `|` (or), `^` (xor), `~` (not), `<<` (shift left), `>>` (shift right).
8. Concatenation: `{a, b}`. Replication: `{4{a}}`.
9. Part-select: `data[7:0]`, `data[15:8]`.
10. Conditional: `cond ? true_val : false_val`.
11. For synchronous reset: `always @(posedge clk) if (reset) q <= 0; else q <= d;`
12. For active-high async reset: `always @(posedge clk or posedge areset) if (areset) ...`
13. Declare `reg` for anything assigned inside `always`. Outputs driven by `assign` are `wire`.
14. Use `logic` or explicit `reg`/`wire` — both are accepted.

IMPORTANT — common mistakes to avoid:

15. Always add `initial` blocks for registers that must start at zero.
    BAD:  output reg [7:0] q; always @(posedge clk) q <= d;  // q starts undefined
    GOOD: output reg [7:0] q; initial q = 8'h0; always @(posedge clk) q <= d;

16. Match the reference Verilog's behavior EXACTLY. Do not add extra pipeline stages
    or delay registers unless the problem specifically asks for them.
    BAD:  always @(posedge clk) begin a_dly <= a; q <= ~a_dly; end  // adds 1-cycle delay
    GOOD: always @(posedge clk) q <= ~a;  // direct, no extra delay

17. Use `reg` instead of `logic` for compatibility with iverilog.
    BAD:  output logic [7:0] q;  // may cause iverilog issues
    GOOD: output reg [7:0] q;

18. Do NOT use `typedef enum logic` — iverilog doesn't support it well.
    BAD:  typedef enum logic[3:0] { S0, S1, S2 } state_t;
    GOOD: localparam S0=0, S1=1, S2=2; reg [3:0] state;

19. For FSMs, use `localparam` for state encoding and `reg` for state registers.
    Use `always_comb` or `always @(*)` for next-state logic and `always @(posedge clk)` for state update.

20. For circuits described by waveforms, analyze carefully: does the output change
    on the same cycle as the input, or one cycle later? Match the exact timing.
"""

GO_DSL_SUMMARY = """\
MyGO Go DSL — complete reference:

=== BASICS ===
- File: package main ... func TopModule(...) { ... } ... func main() {}
- Inputs = TopModule parameters. Outputs = package-level `var out_* type` globals.
- Types: bool (1 bit), uint8 (2-8 bits), uint16 (9-16 bits), uint32 (17-32 bits).
- Wide vectors: [N]bool for 100+ bit ports. Index 0 = LSB.
- No return values, pointers, structs, interfaces, maps, select, recursion.

=== GLOBAL GENERATION GUARDRAILS ===
- Do not use imports, fmt, unsafe, goroutines, channels, pointers, dynamic slices, maps, structs, recursion, or software-style helpers.
- Keep `TopModule` as the only hardware function. Helper stubs are allowed only for MyGO builtins listed below: Latch, NegEdgeFF, BitsAnd/BitsOr/BitsXor/BitsNot/BitsShiftLeft/BitsShiftRight/BitsAnd3/BitsOr3.
- Do not use arrays as memories, register banks, queues, or lookup tables. Fixed `[N]bool` arrays are allowed only when the port itself is a very wide bit-vector or when calling the listed wide-vector helper stubs.
- Avoid `for`/`range` loops in generated logic. For wide vector operations use the Bits* helper stubs; for small decoders use direct bitwise/arithmetic expressions or a short explicit if/else chain.
- For adders/subtractors/comparators up to 64 bits, use integer arithmetic directly. Do not expand every bit into separate bool carry variables; that can make MyGO/CIRCT compilation explode.
- Example 8-bit adder: `tmp := uint16(a) + uint16(b); if cin { tmp++ }; out_sum = uint8(tmp & 0xff); out_cout = (tmp >> 8) != 0`.
- For sequential designs, use package-level registers. Handle reset first, then update every related register in one clocked block. Do not keep persistent state in local variables.
- If the clock input is bool, use `if reset { ... } else if clk { ... }`; if the clock input is numeric, use `if reset != 0 { ... } else if clk != 0 { ... }`.
- Do not assign persistent outputs only inside `if clk`; assign `out_*` from package-level output registers after the clocked block so sampled outputs remain stable.
- Avoid overflowing masks: cast to a wider unsigned type before masking, e.g. `tmp := uint32(a) + uint32(b); out_sum = uint16(tmp & 0xffff)`.

=== RESET PATTERNS (critical — #1 source of errors) ===
Synchronous reset (param named "reset"):
    if clk { if reset { state = 0 } else { state = next } }

Asynchronous reset (param named "areset"):
    if areset { state = initVal } else if clk { state = next }
    NEVER: if clk { if areset { ... } }  ← WRONG, makes areset synchronous!

=== FSM PATTERN ===
    next := state                              // 1. snapshot
    switch state { case 0: ...; case 1: ... }  // 2. compute next
    if areset { state = 0 } else if clk { state = next }  // 3. update
    out_val = (state == 1)                     // 4. outputs AFTER update

=== MULTI-STATE UPDATES ===
Update ALL registers in ONE if-clk block using snapshots of old values:
    oldState := state; oldCnt := counter
    if areset { state=0; counter=0 } else if clk { state=nextState; counter=nextCnt }

=== OUTPUT RULES ===
- NEVER read back from out_* after writing. Use a local var, assign to out_* once.
    BAD:  if x { out_a = 1 }; out_b = out_a + 1
    GOOD: var a uint8; if x { a = 1 }; out_a = a; out_b = a + 1
- For combinational FSMs (state is INPUT param): assign out_* directly in each case.
- Outputs go AFTER the if-clk block, reading the updated state.
- NEVER add extra state variables or pipeline stages unless the spec requires them.
  If the spec says "output = f(input)", write out_x = f(input) directly.
  Do NOT create a saved_x variable and copy to out_x — this adds unintended delay.

=== LATCHES & NEGEDGE (critical — #2 source of errors) ===
MyGO provides built-in Latch and NegEdgeFF helper functions. Define stubs and use them:

    func Latch(enable, data bool) bool { return data }      // stub
    func NegEdgeFF(clock, data bool) bool { return data }   // stub

    out_p = Latch(clock, a)        // transparent latch: follows a when clock=1, holds when clock=0
    out_q = NegEdgeFF(clock, a)    // negedge FF: captures a on falling edge of clock

These compile to correct hardware. ALWAYS prefer these over manual implementations.

Manual alternatives (if not using builtins):
    Transparent latch: out_p = (clock && a) || (!clock && saved_val)  ← ONE expression
    D-latch with enable: if ena { out_q = d }  ← direct assign, NO intermediate variable
    Negedge FF: if prev_clock && !clock { q_reg = a }; out_q = q_reg; prev_clock = clock

    NEVER: if clock { latch = a }; out_p = latch  ← WRONG, creates unwanted register
    NEVER: if ena { saved = d }; out_q = saved    ← WRONG, adds unnecessary state

=== WIDE BIT-VECTOR HELPERS (for 100+ bit operations) ===
MyGO provides built-in helper functions for [N]bool bitwise operations.
Define stub functions in your file, then use them — the compiler intercepts them:

    func BitsAnd(a, b [N]bool) [N]bool { return a }   // stub
    func BitsOr(a, b [N]bool) [N]bool  { return a }
    func BitsXor(a, b [N]bool) [N]bool { return a }
    func BitsNot(a [N]bool) [N]bool    { return a }
    func BitsShiftLeft(a [N]bool, n int) [N]bool  { return a }
    func BitsShiftRight(a [N]bool, n int) [N]bool { return a }
    func BitsAnd3(a, b, c [N]bool) [N]bool { return a }
    func BitsOr3(a, b, c [N]bool) [N]bool  { return a }

Each compiles to a SINGLE Verilog vector operation (e.g. comb.and on i512).
These work with ANY [N]bool size: [100]bool, [256]bool, [512]bool, etc.
Use for ANY problem with 100+ bit vectors — neighbor detection, shifts, cellular automata.
Example: 100-bit neighbor AND: out_both = BitsAnd(in, BitsShiftRight(in, 1))
Example (rule110 in 15 lines):

    var out_q [512]bool
    func BitsAnd(a, b [512]bool) [512]bool { return a }
    func BitsOr(a, b [512]bool) [512]bool  { return a }
    func BitsNot(a [512]bool) [512]bool    { return a }
    func BitsShiftLeft(a [512]bool, n int) [512]bool  { return a }
    func BitsShiftRight(a [512]bool, n int) [512]bool { return a }
    func TopModule(clk bool, load bool, data [512]bool) {
        if clk {
            if load { out_q = data } else {
                left := BitsShiftRight(out_q, 1)
                right := BitsShiftLeft(out_q, 1)
                out_q = BitsNot(BitsOr(BitsOr(
                    BitsAnd(BitsAnd(left, out_q), right),
                    BitsAnd(BitsAnd(BitsNot(left), BitsNot(out_q)), BitsNot(right))),
                    BitsAnd(BitsAnd(left, BitsNot(out_q)), BitsNot(right))))
            }
        }
    }

For 2D grids (Conway's Life 16x16): use uint16 per row + bitwise neighbor counting.
Count neighbors in parallel: sum_bit0 = a^b^c; sum_bit1 = (a&b)|(a&c)|(b&c).

=== WIDE SEQUENTIAL REGISTERS (100-bit shift/rotate) ===
Use 100 individual package-level bool vars (q_0..q_99) for state.
Copy to out_* array at end. This produces 500+ lines — that is expected.

=== COUNTERS ===
- BCD counters: pack all digits into uint16/uint32. Extract with shifts/masks.
- Cascaded counters: use enable chains where each digit's enable depends on all
  lower digits being at their max value.
- Count-to-N: use `if count == N-1 { count = 0 } else { count++ }` pattern.
- Always initialize counter state in the reset path.

=== WAVEFORM / CIRCUIT INFERENCE ===
When the problem gives a waveform and asks you to infer the circuit:
- Analyze timing carefully: does output change on same cycle as input, or next cycle?
- Combinational: output changes immediately with input (same time step)
- Sequential: output changes on clock edge (one cycle after input change)
- Check if the output is a simple gate, a flip-flop, or a latch
- Match the EXACT timing shown — do not add extra delay

=== COUNTER-EXAMPLES (BAD → GOOD) ===

BAD: if clock { out_p = a } else { out_p = saved_a }  // latch with if/else
GOOD: out_p = (clock && a) || (!clock && saved_val)    // single combinational mux

BAD: out_x = a + b; out_y = out_x == 0   // reading back out_* after write
GOOD: r := a + b; out_x = r; out_y = r == 0  // local var, assign out_* once

BAD: if clk { state = next }; if clk { counter++ }  // two clk blocks
GOOD: if areset { state=0; counter=0 } else if clk { state=next; counter=newCnt }

BAD: if clk { if areset { state = 0 } else { ... } }  // areset inside clk = synchronous!
GOOD: if areset { state = 0 } else if clk { ... }      // areset before clk = asynchronous

BAD: var q [100]bool  // using array for sequential state
GOOD: var q_0, q_1, ..., q_99 bool  // individual vars for 100-bit register

BAD: func TopModule(data0, data1, data2 uint64)  // separate wide input params
GOOD: func TopModule(data [3]uint64)               // array param = single port

=== NEVER ===
- Never use `...` or `// similar` — write every line explicitly.
- Never use [N]bool for internal state when Bits* helpers are available.
- Never use separate parameters (data0, data1...) for wide inputs — use [N]type array.
- Never add extra pipeline delay registers unless the problem explicitly asks for them.
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_cases():
    prompts = sorted(PROMPTS_DIR.glob("*_prompt.txt"))
    cases = []
    for p in prompts:
        case = p.name[: -len("_prompt.txt")]
        ref = REF_DIR / f"{case}_ref.sv"
        test = TEST_DIR / f"{case}_test.sv"
        if ref.exists() and test.exists():
            cases.append({"case": case, "prompt": p, "ref": ref, "test": test})
    return cases


def strip_code_fence(text):
    m = re.search(r"```(?:systemverilog|verilog|sv|go|golang)?\s*(.*?)```", text, flags=re.S)
    if m:
        return m.group(1).strip() + "\n"
    # Fallback: find code embedded in reasoning text
    # Look for "package main" as anchor for Go code
    pm = re.search(r"(package\s+main\b.*)", text, flags=re.S)
    if pm:
        code = pm.group(1).strip()
        # Trim trailing non-code text after the last closing brace
        brace_depth = 0
        last_brace = -1
        for i, ch in enumerate(code):
            if ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
                if brace_depth == 0:
                    last_brace = i
        if last_brace > 0:
            code = code[:last_brace + 1]
        return code.strip() + "\n"
    # Look for "module " as anchor for Verilog code
    vm = re.search(r"(module\s+TopModule\b.*?endmodule)", text, flags=re.S)
    if vm:
        return vm.group(1).strip() + "\n"
    return text.strip() + "\n"


def ref_to_top_solution(ref_sv):
    return re.sub(r"\bRefModule\b", "TopModule", ref_sv)


def ensure_main_stub(go_src):
    if re.search(r"\bfunc\s+main\s*\(", go_src):
        return go_src
    return go_src.rstrip() + "\n\nfunc main() {}\n"


def build_fewshot(target):
    examples = []
    for case_id in FEWSHOT_CASES:
        prompt_path = PROMPTS_DIR / f"{case_id}_prompt.txt"
        ref_path = REF_DIR / f"{case_id}_ref.sv"
        go_path = GO_SOLUTIONS_DIR / case_id / "main.go"
        if not all(p.exists() for p in [prompt_path, ref_path]):
            continue
        prompt_text = prompt_path.read_text().strip()
        ref_sv = ref_path.read_text().strip()
        if target == "verilog":
            solution = ref_to_top_solution(ref_sv)
        else:
            if go_path.exists():
                solution = go_path.read_text().strip()
            else:
                continue
        examples.append(f"--- Example ---\nTask:\n{prompt_text}\n\nReference Verilog:\n{ref_sv}\n\nSolution:\n{solution}\n--- End Example ---")
    return "\n\n".join(examples)


def call_llm(system_prompt, user_prompt, timeout=1200):
    import urllib.request
    import urllib.error
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": 65536,
    }
    req = urllib.request.Request(
        API_BASE.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode())
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e
    content = payload["choices"][0]["message"].get("content") or ""
    if not content:
        reasoning = payload["choices"][0]["message"].get("reasoning") or ""
        if reasoning:
            content = reasoning
    return content


def run_cmd(cmd, cwd, timeout=120):
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return {"ok": proc.returncode == 0, "rc": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "timeout": False}
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": None, "stdout": "", "stderr": "timeout", "timeout": True}


def classify_sim(result):
    if result["timeout"]:
        return "sim_timeout", -1, -1
    out = result["stdout"] + result["stderr"]
    m = re.search(r"Mismatches:\s*(\d+)\s*in\s*(\d+)\s*samples", out)
    if m:
        mm, ss = int(m.group(1)), int(m.group(2))
        return ("equivalent" if mm == 0 else "not_equivalent"), mm, ss
    if "Mismatches:" in out:
        return "not_equivalent", -1, -1
    if result["ok"]:
        return "equivalent", 0, 0
    return "sim_error", -1, -1


def rewrite_module_main_to_top(sv_path):
    text = Path(sv_path).read_text()
    if "module TopModule" in text:
        return
    text = re.sub(r"\bmodule\s+main\b", "module TopModule", text)
    Path(sv_path).write_text(text)


# ---------------------------------------------------------------------------
# Path A: LLM → Verilog → test
# ---------------------------------------------------------------------------

def run_path_a(case_info, fewshot, output_dir):
    case = case_info["case"]
    d = Path(output_dir) / case / "path_a"
    d.mkdir(parents=True, exist_ok=True)

    prompt_text = case_info["prompt"].read_text().strip()
    ref_sv = case_info["ref"].read_text().strip()

    system_prompt = (
        "You are a code generator. Output ONLY valid SystemVerilog source code. "
        "Do NOT include any explanations, reasoning, or comments outside the code. "
        "The very first line of your response MUST be `module TopModule`. "
        "Define exactly one module named TopModule with the same port interface as RefModule in the reference. "
        "Do not include RefModule."
    )
    user_prompt = (
        "Generate one complete SystemVerilog file defining module TopModule.\n"
        "Return SystemVerilog code only.\n\n"
        f"SystemVerilog reference:\n{VERILOG_TUTORIAL}\n\n"
        f"{fewshot}\n\n"
        f"Task:\n{prompt_text}\n\n"
        f"Reference Verilog (interface to match):\n{ref_sv}\n"
    )

    t0 = time.time()
    try:
        raw = call_llm(system_prompt, user_prompt)
        sv_code = strip_code_fence(raw)
    except Exception as e:
        return {"status": "llm_failed", "error": str(e), "time_s": time.time() - t0}
    llm_time = time.time() - t0

    if len(sv_code.strip()) < 10:
        return {"status": "llm_empty", "error": "empty response", "time_s": llm_time}

    sv_path = d / "TopModule.sv"
    sv_path.write_text(sv_code)

    sim_out = d / "sim.out"
    r = run_cmd(["iverilog", "-g2012", "-o", str(sim_out), str(sv_path), str(case_info["ref"]), str(case_info["test"])], cwd=d, timeout=60)
    if not r["ok"]:
        return {"status": "iverilog_failed", "error": r["stderr"][:500], "time_s": llm_time}

    r = run_cmd(["vvp", str(sim_out)], cwd=d, timeout=60)
    status, mm, ss = classify_sim(r)
    return {"status": status, "mismatches": mm, "samples": ss, "time_s": llm_time, "sv_file": str(sv_path)}


# ---------------------------------------------------------------------------
# Path B: LLM → Go → MyGO → Verilog → test
# ---------------------------------------------------------------------------

def run_path_b(case_info, fewshot, output_dir):
    case = case_info["case"]
    d = Path(output_dir) / case / "path_b"
    d.mkdir(parents=True, exist_ok=True)

    prompt_text = case_info["prompt"].read_text().strip()
    ref_sv = case_info["ref"].read_text().strip()

    system_prompt = (
        "You are a code generator. Output ONLY valid Go source code. "
        "Do NOT explain, reason, or think step by step. "
        "Do NOT include any text before or after the code. "
        "Start your response with `package main` immediately. "
        "Follow the MyGO DSL exactly. "
        "Outputs must use out_* package globals. "
        "Do not use pointer outputs or return-value outputs. "
        "IMPORTANT RULES: "
        "(1) For D-latches with enable: write `if ena { out_q = d }` directly — do NOT create an intermediate saved variable. "
        "(2) For combinational FSMs where state is an INPUT: assign out_next_state directly inside each switch case — do NOT use a local `next` variable. "
        "(3) For transparent latches: use `out_p = Latch(clock, a)` builtin. For negedge FF: use `out_q = NegEdgeFF(clock, a)` builtin. "
        "(4) For wide [N]bool bitwise ops (100+ bits): use BitsAnd/BitsOr/BitsNot/BitsShiftLeft/BitsShiftRight helper stubs. "
        "(5) NEVER add intermediate state variables or extra pipeline stages unless the spec explicitly requires them. "
        "(6) Do not use arrays as memories/register banks; fixed [N]bool arrays are only for wide vector ports and Bits* helper stubs. "
        "(7) Avoid for/range loops; use direct expressions, short if/else chains, or Bits* helpers. "
        "(8) For small adders/subtractors/comparators use integer arithmetic with a wider temporary, not bit-by-bit bool carry expansion. "
        "(9) For numeric clocks use `clk != 0`; for bool clocks use `clk`."
    )
    user_prompt = (
        "Generate one complete Go source file for the MyGO compiler.\n"
        "Return Go code only.\n\n"
        f"Follow this DSL summary exactly:\n{GO_DSL_SUMMARY}\n\n"
        f"{fewshot}\n\n"
        f"Task:\n{prompt_text}\n\n"
        f"Reference Verilog (interface to match):\n{ref_sv}\n"
    )

    t0 = time.time()
    try:
        raw = call_llm(system_prompt, user_prompt)
        go_code = strip_code_fence(raw)
        go_code = ensure_main_stub(go_code)
    except Exception as e:
        return {"status": "llm_failed", "error": str(e), "time_s": time.time() - t0}
    llm_time = time.time() - t0

    if len(go_code.strip()) < 10:
        return {"status": "llm_empty", "error": "empty response", "time_s": llm_time}

    go_path = d / "main.go"
    go_path.write_text(go_code)
    gomod = d / "go.mod"
    if not gomod.exists():
        gomod.write_text("module tmpeval\n\ngo 1.25\n")

    sv_path = d / "TopModule.sv"
    compile_cmd = [
        "go", "run", "./cmd/mygo", "compile",
        "-emit", "verilog",
        "--circt-lowering-options", "locationInfoStyle=none,omitVersionComment",
        "--benchmark-ref-path", str(case_info["ref"]),
        "-o", str(sv_path),
        str(go_path),
    ]
    t1 = time.time()
    r = run_cmd(compile_cmd, cwd=str(REPO_ROOT), timeout=180)
    compile_time = time.time() - t1
    if not r["ok"]:
        # Repair loop: feed error back to LLM for one retry
        repair_prompt = (
            "The following Go code failed to compile. Fix it and return ONLY the corrected Go code.\n"
            "Start with `package main` immediately. No explanations.\n\n"
            "Keep the same MyGO subset guardrails: no imports/pointers/slices/maps/structs; no helper functions except the documented builtins; no arrays as memories/register banks; fixed [N]bool arrays only for wide vector ports; avoid for/range loops; cast to wider unsigned types before applying large masks.\n\n"
            f"Original task:\n{prompt_text}\n\n"
            f"Reference Verilog:\n{ref_sv}\n\n"
            f"Broken Go code:\n{go_code}\n\n"
            f"Compiler error:\n{r['stderr'][:800]}\n\n"
            f"DSL rules:\n{GO_DSL_SUMMARY}\n"
        )
        try:
            raw2 = call_llm(system_prompt, repair_prompt)
            go_code2 = strip_code_fence(raw2)
            go_code2 = ensure_main_stub(go_code2)
            if len(go_code2.strip()) > 10:
                go_path.write_text(go_code2)
                r2 = run_cmd(compile_cmd, cwd=str(REPO_ROOT), timeout=180)
                compile_time += time.time() - t1
                if r2["ok"]:
                    r = r2  # repair succeeded
        except Exception:
            pass
        if not r["ok"]:
            tag = "go_compile_timeout" if r["timeout"] else "go_compile_failed"
            return {"status": tag, "error": r["stderr"][:500], "time_s": llm_time, "compile_time_s": compile_time, "go_file": str(go_path)}

    rewrite_module_main_to_top(sv_path)

    sim_out = d / "sim.out"
    r = run_cmd(["iverilog", "-g2012", "-o", str(sim_out), str(sv_path), str(case_info["ref"]), str(case_info["test"])], cwd=d, timeout=60)
    if not r["ok"]:
        return {"status": "iverilog_failed", "error": r["stderr"][:500], "time_s": llm_time, "compile_time_s": compile_time}

    r = run_cmd(["vvp", str(sim_out)], cwd=d, timeout=60)
    status, mm, ss = classify_sim(r)
    return {"status": status, "mismatches": mm, "samples": ss, "time_s": llm_time, "compile_time_s": compile_time, "go_file": str(go_path), "sv_file": str(sv_path)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="A/B verilog-eval benchmark")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--limit", type=int, default=0, help="max problems to run (0=all)")
    parser.add_argument("--start-from", default="", help="skip until this case ID")
    parser.add_argument("--path", default="both", choices=["a", "b", "both"], help="which path(s) to run")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = load_cases()
    print(f"Loaded {len(cases)} problems, {len(FEWSHOT_CASES)} excluded as few-shot examples")

    fewshot_verilog = build_fewshot("verilog")
    fewshot_go = build_fewshot("go")

    results = []
    results_path = out_dir / "results.json"

    skipping = bool(args.start_from)
    count = 0

    for ci in cases:
        case = ci["case"]
        if skipping:
            if case == args.start_from:
                skipping = False
            else:
                continue

        if case in FEWSHOT_CASES:
            results.append({"case": case, "path_a": {"status": "skipped"}, "path_b": {"status": "skipped"}})
            continue

        count += 1
        if args.limit and count > args.limit:
            break

        print(f"\n[{count}] {case}")
        entry = {"case": case}

        if args.path in ("a", "both"):
            print(f"  Path A (Verilog)...", end=" ", flush=True)
            entry["path_a"] = run_path_a(ci, fewshot_verilog, out_dir)
            print(entry["path_a"]["status"])
        else:
            entry["path_a"] = {"status": "skipped"}

        if args.path in ("b", "both"):
            print(f"  Path B (MyGO)...", end=" ", flush=True)
            entry["path_b"] = run_path_b(ci, fewshot_go, out_dir)
            print(entry["path_b"]["status"])
        else:
            entry["path_b"] = {"status": "skipped"}

        results.append(entry)
        results_path.write_text(json.dumps(results, indent=2))

    # Summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    for label, key in [("Path A (LLM→Verilog)", "path_a"), ("Path B (LLM→Go→MyGO→Verilog)", "path_b")]:
        statuses = [r[key]["status"] for r in results if key in r]
        total = len([s for s in statuses if s != "skipped"])
        equiv = statuses.count("equivalent")
        ne = statuses.count("not_equivalent")
        llm_f = statuses.count("llm_failed") + statuses.count("llm_empty")
        compile_f = statuses.count("go_compile_failed") + statuses.count("go_compile_timeout")
        iv_f = statuses.count("iverilog_failed")
        sim_f = statuses.count("sim_timeout") + statuses.count("sim_error")
        print(f"\n{label}:")
        print(f"  Equivalent (pass): {equiv}/{total} ({100*equiv/total:.1f}%)" if total else "  No results")
        print(f"  Not equivalent:    {ne}")
        print(f"  LLM failed:        {llm_f}")
        if compile_f:
            print(f"  Compile failed:    {compile_f}")
        print(f"  iverilog failed:   {iv_f}")
        print(f"  Sim timeout/error: {sim_f}")

    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps({"results": results}, indent=2))
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
