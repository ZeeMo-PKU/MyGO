# Direct DeepSeek CVDP Token Multishard Run 2026-06-07

This directory records a fresh direct-SystemVerilog CVDP run used to measure token usage without MyGo.

Run setup:

- Dataset subset: `cid003`, `nonagentic_no_commercial`, 78 tasks.
- Flow: direct SystemVerilog generation; no MyGo compile or MyGo prompt path.
- Model: `deepseek/deepseek-v4-pro` through OpenRouter.
- Server: Trifoliate.
- Parallelism: 6 independent shard processes, 13 tasks each.
- Freshness: the server output root was deleted and recreated before launch; no `--skip-existing`; no old model output was reused.
- Prompt isolation: each task used one independent chat request containing only the system prompt and that task's prompt/context/expected output filenames.

Result:

- PASS: 51 / 78
- FAIL: 27 / 78
- Pass rate: 65.38%

Token usage:

- Input tokens (`prompt_tokens`): 101909
- Output tokens (`completion_tokens`): 88138
- Total tokens: 190047
- Cached prompt tokens: 0
- Reasoning tokens: 0
- OpenRouter reported cost: 0.136443636 USD

Artifacts:

- `DIRECT_FRESH_MULTISHARD_TOKEN_REPORT.md`: human-readable summary.
- `token_usage_summary.json`: full summary plus per-task rows.
- `token_usage_per_task.csv`: compact per-task token/status table.

Raw model responses, API keys, and temporary CVDP harness directories are intentionally excluded.
