# MyGo vs Direct Fresh Reproduction Scores

- Root: `/home/rongxv/work/final-repro-mygo-vs-direct-20260608-212521`
- Model: `deepseek/deepseek-v4-pro`
- Direct route: LLM directly generates Verilog/SystemVerilog.
- MyGo route: LLM generates restricted Go DSL, then MyGo compiles to Verilog; runners may use compiler-feedback repair when configured.

## Final Scores

| Benchmark | Route | PASS | Total | Rate | Status counts |
| --- | --- | ---: | ---: | ---: | --- |
| CVDP cid003 | direct | 51 | 78 | 65.38% | FAIL=27, PASS=51 |
| CVDP cid003 | mygo | 48 | 78 | 61.54% | FAIL=26, MODEL_ERROR=1, MYGO_COMPILE_ERROR=3, PASS=48 |
| RTLLM | direct_verilog | 26 | 50 | 52.00% | FAIL=22, PASS=26, TIMEOUT=2 |
| RTLLM | mygo | 5 | 50 | 10.00% | FAIL=43, MYGO_COMPILE_ERROR=1, PASS=5, TIMEOUT=1 |
| Verilog-Eval | path_a | 108 | 151 | 71.52% | equivalent=108, iverilog_failed=26, not_equivalent=17 |
| Verilog-Eval | path_b | 97 | 151 | 64.24% | equivalent=97, go_compile_failed=26, go_compile_timeout=1, not_equivalent=27 |

## Jobs

| Job | PID | Alive |
| --- | ---: | --- |
| cvdp_direct_cvdp_shard_00 | 2831334 | False |
| cvdp_direct_cvdp_shard_01 | 2831336 | False |
| cvdp_direct_cvdp_shard_02 | 2831338 | False |
| cvdp_direct_cvdp_shard_03 | 2831340 | False |
| cvdp_direct_cvdp_shard_04 | 2831342 | False |
| cvdp_direct_cvdp_shard_05 | 2831344 | False |
| cvdp_mygo_cvdp_shard_00 | 2831346 | False |
| cvdp_mygo_cvdp_shard_01 | 2831348 | False |
| cvdp_mygo_cvdp_shard_02 | 2831350 | False |
| cvdp_mygo_cvdp_shard_03 | 2831352 | False |
| cvdp_mygo_cvdp_shard_04 | 2831354 | False |
| cvdp_mygo_cvdp_shard_05 | 2831356 | False |
| cvdp_mygo_envfix_shard_00 | 2915728 | False |
| cvdp_mygo_envfix_shard_01 | 2915731 | False |
| cvdp_mygo_envfix_shard_02 | 2915734 | False |
| cvdp_mygo_envfix_shard_03 | 2915737 | False |
| cvdp_mygo_envfix_shard_04 | 2915740 | False |
| cvdp_mygo_envfix_shard_05 | 2915743 | False |
| rtllm_both | 2831357 | False |
| rtllm_both_rerun_envfix | 2862601 | False |
| verilog_eval_both | 2874340 | False |
| verilog_eval_shard_00 | 2937887 | False |
| verilog_eval_shard_01 | 2937890 | False |
| verilog_eval_shard_02 | 2937893 | False |
| verilog_eval_shard_03 | 2937896 | False |
| verilog_eval_shard_04 | 2937899 | False |
| verilog_eval_shard_05 | 2937902 | False |
