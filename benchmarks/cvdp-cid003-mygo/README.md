# MyGO-CVDP cid003 Non-Agentic Experiment Artifacts

This directory records a lightweight, reviewable artifact set for a MyGO evaluation on the CVDP cid003 Non-Agentic code-generation subset.

## Scope

- Dataset slice: CVDP v1.1.0 Non-Agentic `cid003`, 78 cases.
- Model provider: OpenRouter.
- Model: `deepseek/deepseek-v4-pro`.
- Protocol: single-shot/pass@1. Each case calls the LLM once.
- No retry, no fallback, no automatic repair.
- Parallelism: `--jobs 4`.
- Timeouts: LLM 180s, MyGO compile 120s, CVDP host stage 420s, total 600s.
- MyGO commit recorded by the run: `125084e4dffcc3f859e44652cde986b7e229fcf0`.

## Results

- Total cases: 78
- PASS: 1
- Non-PASS: 77

Reviewed category counts:

- `VERILOG_INTERFACE_ERROR`: 55
- `TIMEOUT`: 10
- `GO_SYNTAX_ERROR`: 4
- `MYGO_CIRCT_BACKEND_ERROR`: 3
- `FUNCTIONAL_FAIL`: 2
- `MYGO_IR_LOWERING_ERROR`: 2
- `VERILOG_COMPILE_ERROR`: 1
- `PASS`: 1

## Files

- `results.csv`: complete 78-case result table with reviewed categories merged in.
- `error_taxonomy.json`: machine-readable reviewed failure taxonomy.
- `error_analysis.md`: per-case analysis for all non-PASS cases.
- `teacher_report.html`: human-readable summary report.
- `run_manifest.redacted.json`: redacted run environment metadata.
- `cid003_non_agentic_whitelist.txt`: case whitelist used by the run.
- `prompts/<case_id>/problem.md`: original problem text saved for the case.
- `prompts/<case_id>/prompt.txt`: full prompt sent to the LLM.
- `prompts/<case_id>/extracted_go.go`: Go code extracted from the LLM response, or a placeholder when no code was extracted.

## Omitted Raw Artifacts

The full raw run directory, Verilog outputs, CVDP simulation logs, and packaged tarball are intentionally not committed here because they are large and noisy for code review. This PR keeps the artifact set small enough for normal repository review while preserving the prompt, generated Go, result table, and reviewed failure analysis.

## Redaction

The artifact set is redacted to avoid committing local user paths, server secret paths, API-key locations, authorization headers, or large archives.
