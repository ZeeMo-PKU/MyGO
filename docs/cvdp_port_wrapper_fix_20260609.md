# CVDP MyGo port-wrapper fix evidence (2026-06-09)

## Scope

This fix targets CVDP MyGo-route failures where cocotb could not find expected top-level ports, for example:

```text
encoder_64b66b contains no child object named encoder_data_out
```

The change is in the CVDP runner/wrapper layer, not in the MyGo compiler core.

## Runner changes

- Parse CVDP bullet-list interfaces, not only Markdown tables.
- Recognize headings such as `### **Inputs**`, `Input Signals`, `Outputs`, and numbered port lists.
- Parse widths from forms such as `64-bit`, `128-bits,[127:0]`, and backtick names like `o_state[2:0]`.
- Restrict parameter-default parsing to parameter sections, avoiding false parameters like `o_ready = 0`.
- Reassemble MyGo split wide outputs into the CVDP top-level output, e.g.:

```systemverilog
assign encoder_data_out = {__mygo_encoder_data_out_sync[1:0], __mygo_encoder_data_out_data};
```

- Avoid treating sideband outputs such as `*_valid` as chunks of a wide data output.
- Avoid unsafe positional fallback for output ports when names do not match.

## Smoke result

Case: `03_cvdp_copilot_64b66b_encoder_0001`

- Before: cocotb failed with missing `encoder_data_out`.
- After: `PASS`, `TESTS=7 PASS=7 FAIL=0 SKIP=0`.
- Evidence path:
  `/home/rongxv/work/cvdp-runs/portfix-smoke-20260609-64b66b-fullharness/portfix_harness_result_envmapped.json`

## Batch rerun of previous missing-port failures

Input set: the 9 CVDP MyGo env-fixed cases whose previous `test_result.json` contained `contains no child object named`.

Rerun path:
`/home/rongxv/work/cvdp-runs/portfix-rerun-missingports-v3-20260609`

Summary:

Attribution note: remaining `contains no child object named ...` failures are reported as answer errors, not formatting mismatches. They mean the generated/wrapped design does not provide a signal or hierarchy object required by the benchmark test contract.

| Case | Result after fix | Remaining issue |
|---|---:|---|
| `03_cvdp_copilot_64b66b_encoder_0001` | PASS | Fixed by split-output wrapper. |
| `73_cvdp_copilot_thermostat_0001` | PASS | Fixed by better numbered-list port parsing. |
| `24_cvdp_copilot_concatenate_0001` | FAIL | Port compile issue fixed; now real functional failure: FSM status expected 2, got 1. |
| `30_cvdp_copilot_data_width_converter_0003` | FAIL | Port compile issue fixed; now real functional failure: output remains 0. |
| `68_cvdp_copilot_set_bit_calculator_0001` | FAIL | Parameter/input confusion fixed; now real functional failure: count remains 0. |
| `28_cvdp_copilot_convolutional_encoder_0001` | FAIL | Answer error: missing required signal. The test expects internal `shift_reg`, but the generated/wrapped design does not provide it. |
| `33_cvdp_copilot_digital_dice_roller_0001` | FAIL | Answer error: missing required signal. The test expects a parameter/internal object such as `DICE_MAX`, but the generated/wrapped design does not expose it. |
| `40_cvdp_copilot_fifo_async_0001` | FAIL | Answer error: missing required signal. The test expects a parameter/internal object such as `DEPTH`, but the generated/wrapped design does not expose it. |
| `70_cvdp_copilot_static_branch_predict_0001` | FAIL | Answer error: missing required signal. The test drives `register_addr_i`, but the generated/wrapped design does not provide that required signal. |

Projected CVDP MyGo env-fixed score if these rerun results replace the original missing-port failures:

```text
56/78 -> 58/78
```

## Patched files on server

- `/home/rongxv/work/MyGo-PR21-repro-20260607-165808/scripts/run_cvdp_deepseek_mygo.py`
- `/home/rongxv/work/cvdp-runs/run_cvdp_deepseek_mygo_go124_local.py`

The existing MyGo compiler files `internal/mlir/emitter.go` and `internal/mlir/emitter_test.go` were already dirty and were not modified by this port-wrapper fix.

