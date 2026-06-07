# RTLLM DeepSeek V4 Pro Direct vs MyGo, 2026-06-08

This directory records a server-side RTLLM A/B run comparing:

- Direct path: `design_description.txt -> DeepSeek V4 Pro -> Verilog/SystemVerilog -> RTLLM testbench`
- MyGo path: `design_description.txt -> DeepSeek V4 Pro -> restricted Go/MyGo DSL -> MyGo -> Verilog/SystemVerilog -> RTLLM testbench`

## Setup

- Model: `deepseek/deepseek-v4-pro` via OpenRouter
- Server: `Trifoliate`, `/home/rongxv`
- Run root: `/home/rongxv/work/rtllm-runs/dsv4-mygo-vs-direct-20260608-005901/full`
- Runner: `scripts/run_rtllm_deepseek_ab.py`
- RTLLM snapshot: `41b26896e33b536940116a975626455eed3de65e`
- MyGo commit: `9699ebdf84ace8daa67388d8197099d7d12c044b`
- Parallelism: `--jobs 6`
- Sampling: pass@1 style, one model output per task per path
- Simulator: `iverilog -g2012` plus `vvp`

## Leakage Guard

The model prompts contain only `design_description.txt` plus parsed interface hints. The runner does not send `testbench.v`, verified reference files, or generated answers to the model.

For judging, the runner copies the task testbench and non-Verilog data files into the work directory after generation, then compiles and simulates the generated design.

## Result

| Path | PASS | Total | Pass rate | Status counts |
| --- | ---: | ---: | ---: | --- |
| Direct Verilog | 29 | 50 | 58.00% | `PASS=29`, `COMPILE_FAIL=15`, `FAIL=5`, `TIMEOUT=1` |
| MyGo | 21 | 50 | 42.00% | `PASS=21`, `MYGO_COMPILE_ERROR=10`, `FAIL=11`, `COMPILE_FAIL=7`, `TIMEOUT=1` |

Per-task comparison:

| Bucket | Count |
| --- | ---: |
| Both pass | 18 |
| Direct-only pass | 11 |
| MyGo-only pass | 3 |
| Neither pass | 18 |
| Union pass | 32 |

The direct Verilog path is stronger in this pass@1 RTLLM run. MyGo is not better overall here, but it does recover three tasks where direct Verilog failed to pass.

## Comparison With RTLCoder Paper

Reference: RTLCoder, arXiv:2312.08617, Table II.

The paper's RTLLM numbers are not directly apples-to-apples with this run:

- The paper reports RTLLM V1.1 with 29 tasks. This run uses the 50-task RTLLM snapshot.
- The paper reports pass@5: each task has 5 trials, and a task counts as success if any trial passes. This run is pass@1 style: one model output per task per path.
- The paper uses Synopsys VCS. This run uses `iverilog -g2012` plus `vvp`.
- The paper sweeps `top_p=0.95` and temperatures `{0.2, 0.5, 0.8}`, then reports the best setting. This run uses one fixed low-temperature setting in the runner.

With those caveats, the functional pass rates line up as follows:

| Source | Setting | Functional pass |
| --- | --- | ---: |
| RTLCoder paper: GPT-3.5 | RTLLM V1.1, pass@5 | 37.9% |
| RTLCoder paper: GPT-4 | RTLLM V1.1, pass@5 | 65.5% |
| RTLCoder paper: DeepSeek-Coder-6.7B base | RTLLM V1.1, pass@5 | 34.5% |
| RTLCoder paper: RTLCoder-DeepSeek-Direct | RTLLM V1.1, pass@5 | 44.8% |
| RTLCoder paper: RTLCoder-DeepSeek | RTLLM V1.1, pass@5 | 48.3% |
| This run: Direct Verilog with DS V4 Pro | RTLLM 50 tasks, pass@1 | 58.0% |
| This run: MyGo with DS V4 Pro | RTLLM 50 tasks, pass@1 | 42.0% |
| This run: Direct or MyGo union | RTLLM 50 tasks, two path attempts | 64.0% |

Interpretation:

- Direct DS V4 Pro is numerically above the RTLCoder paper's RTLCoder-DeepSeek RTLLM functional result, but the comparison favors neither side cleanly because dataset, simulator, sampling, and decoding are different.
- MyGo DS V4 Pro is numerically above the paper's GPT-3.5 and DeepSeek-Coder-6.7B base RTLLM results, but below the paper's RTLCoder-DeepSeek result.
- The union result is close to the paper's GPT-4 RTLLM functional score, but it is a two-pipeline complementarity number, not the same metric as a single model's pass@5.
- To make this publishable, rerun the exact RTLLM V1.1 29-task set with 5 samples per task and report both syntax and functional pass@5 under one simulator.

## MyGo-Only Passes

| # | Task | Direct | MyGo |
| ---: | --- | --- | --- |
| 15 | `Arithmetic/Multiplier/multi_pipe_8bit` | `COMPILE_FAIL` | `PASS` |
| 37 | `Miscellaneous/Others/parallel2serial` | `COMPILE_FAIL` | `PASS` |
| 43 | `Miscellaneous/RISC-V/RAM` | `COMPILE_FAIL` | `PASS` |

## Direct-Only Passes

| # | Task | Direct | MyGo |
| ---: | --- | --- | --- |
| 3 | `Arithmetic/Adder/adder_32bit` | `PASS` | `MYGO_COMPILE_ERROR` |
| 4 | `Arithmetic/Adder/adder_8bit` | `PASS` | `FAIL` |
| 9 | `Arithmetic/Divider/div_16bit` | `PASS` | `FAIL` |
| 11 | `Arithmetic/Multiplier/multi_16bit` | `PASS` | `MYGO_COMPILE_ERROR` |
| 14 | `Arithmetic/Multiplier/multi_pipe_4bit` | `PASS` | `COMPILE_FAIL` |
| 17 | `Arithmetic/Other/fixed_point_substractor` | `PASS` | `MYGO_COMPILE_ERROR` |
| 20 | `Control/Counter/JC_counter` | `PASS` | `FAIL` |
| 30 | `Memory/Shifter/right_shifter` | `PASS` | `MYGO_COMPILE_ERROR` |
| 31 | `Miscellaneous/Frequency divider/freq_div` | `PASS` | `FAIL` |
| 35 | `Miscellaneous/Others/calendar` | `PASS` | `FAIL` |
| 42 | `Miscellaneous/Others/width_8to16` | `PASS` | `MYGO_COMPILE_ERROR` |

## Reproduce

On `Trifoliate`, from a MyGo checkout with the runner script:

```bash
export PATH=/home/rongxv/work/tools/bin:/home/rongxv/work/tools/circt/firtool-1.146.0/bin:$PATH
export GOTOOLCHAIN=local

/home/rongxv/venvs/cvdp-test/bin/python scripts/run_rtllm_deepseek_ab.py \
  --rtllm-root /home/rongxv/work/rtllm-runs/dsv4-mygo-vs-direct-20260608-005901/RTLLM-41b2689 \
  --out /home/rongxv/work/rtllm-runs/dsv4-mygo-vs-direct-20260608-005901/full \
  --mygo-root /home/rongxv/work/rtllm-runs/dsv4-mygo-vs-direct-20260608-005901/MyGO \
  --mygo-bin /home/rongxv/work/rtllm-runs/dsv4-mygo-vs-direct-20260608-005901/MyGO/bin/mygo \
  --circt-opt /home/rongxv/work/tools/circt/firtool-1.146.0/bin/circt-opt \
  --model deepseek/deepseek-v4-pro \
  --jobs 6 \
  --path both \
  --reuse
```

`--reuse` reuses cached `model_raw.txt` files if they already exist. Omit it for a fully fresh model-call run.

## Files

- `README.md`: this experiment note.
- `SERVER_SUMMARY.md`: generated per-task Markdown summary from the runner.
- `SUMMARY.txt`: compact status counts.
- `results.csv`: per-task/path table.
- `results.json`: structured result data with command details.
- `run3.log`: final authoritative run log.

Raw model responses and per-task temporary work directories are retained on the server and are not included here.

## Caveats

- This is an RTLLM 50-task snapshot run, not the CVDP benchmark and not a pass@k estimate.
- Earlier dry runs exposed two runner bugs: truncating generated Verilog after the first `endmodule`, and not copying non-Verilog data files needed by some testbenches. The numbers here come from the corrected `run3`.
- `COMPILE_FAIL`, `MYGO_COMPILE_ERROR`, functional `FAIL`, and `TIMEOUT` are intentionally separated. They should not be collapsed into a single model-quality bucket.
