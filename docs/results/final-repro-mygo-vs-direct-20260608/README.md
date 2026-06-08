# Final Reproduction: MyGo vs Direct Verilog

This directory records the final fresh reproduction run comparing the MyGo
tool flow against direct Verilog generation.

## Run Metadata

- Date: 2026-06-08
- Model: `deepseek/deepseek-v4-pro`
- Server artifact root:
  `/home/rongxv/work/final-repro-mygo-vs-direct-20260608-212521`
- Compared flows:
  - Direct Verilog: LLM directly generates Verilog/SystemVerilog.
  - MyGo: LLM generates Go-subset DSL, then MyGo lowers it to SystemVerilog.

## Final Scores

| Benchmark | Direct Verilog | MyGo | Difference (MyGo - Direct) |
| --- | ---: | ---: | ---: |
| CVDP cid003 | 51/78 (65.38%) | 48/78 (61.54%) | -3 |
| RTLLM | 26/50 (52.00%) | 5/50 (10.00%) | -21 |
| Verilog-Eval | 108/151 (71.52%) | 97/151 (64.24%) | -11 |

## Files

- `MyGo_final_repro_scores_20260608.pdf`: one-page report for presentation.
- `FINAL_SCORE_CARD.md`: compact score card.
- `final_scores.md`: detailed summary generated from the final run.
- `final_scores.json`: machine-readable score summary and job status.
- `manifest.txt`: server-side reproduction manifest.

## Notes

- CVDP Direct uses `results/cvdp_direct`.
- CVDP MyGo uses the environment-fixed rerun in `results/cvdp_mygo_envfix`.
- RTLLM uses `results/rtllm_both_rerun_envfix`.
- Verilog-Eval uses six sharded fresh runs under `results/verilog_eval_shard_*`.
- For Verilog-Eval, the current-case reference Verilog was not sent to the model.
- The earlier CVDP MyGo fresh token run was affected by `MODEL_ERROR` / API timeout
  noise, so the formal score uses the environment-fixed rerun.
