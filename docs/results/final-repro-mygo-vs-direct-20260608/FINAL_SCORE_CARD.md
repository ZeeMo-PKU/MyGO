# Final Score Card

- Model: `deepseek/deepseek-v4-pro`
- Root: `/home/rongxv/work/final-repro-mygo-vs-direct-20260608-212521`
- Fresh run date: 2026-06-08

| Benchmark | Route | Score | Pass rate |
| --- | --- | ---: | ---: |
| CVDP cid003 78 tasks | LLM direct Verilog | 51/78 | 65.38% |
| CVDP cid003 78 tasks | LLM -> MyGo DSL -> Verilog | 48/78 | 61.54% |
| RTLLM 50 tasks | LLM direct Verilog | 26/50 | 52.00% |
| RTLLM 50 tasks | LLM -> MyGo DSL -> Verilog | 5/50 | 10.00% |
| Verilog-Eval 151 tasks | LLM direct Verilog | 108/151 | 71.52% |
| Verilog-Eval 151 tasks | LLM -> MyGo DSL -> Verilog | 97/151 | 64.24% |

Notes:
- CVDP Direct result is from `results/cvdp_direct`; CVDP MyGo result is from env-fixed rerun `results/cvdp_mygo_envfix`.
- RTLLM result is from env-fixed rerun `results/rtllm_both_rerun_envfix`.
- Verilog-Eval result is from 6 sharded runs under `results/verilog_eval_shard_*`; current-case reference Verilog was not sent to the model.
