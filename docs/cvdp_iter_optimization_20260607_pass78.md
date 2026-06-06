# CVDP MyGo Iteration 2026-06-07

Goal: push the 78-task MyGo-backed CVDP subset beyond 74 PASS.

Starting point after the 2026-06-06 iteration was 69/78 PASS by latest validated per-task result. The remaining 9 non-PASS tasks were rerun on Trifoliate in three shards with the updated MyGo emitter and the CVDP runner using 4 Go-generation attempts, 2 model retries, harness execution enabled, and MyGo internal simulation disabled.

## Result

Latest validated per-task result: 78/78 PASS.

This is a per-task merged result, not a single monolithic 78-task rerun. It combines the earlier validated PASS set with the 9 previously failing tasks listed below, all of which passed in the 2026-06-07 targeted rerun.

## Newly Recovered Tasks

| Index | Task | Status | Evidence shard |
| --- | --- | --- | --- |
| 07 | cvdp_copilot_apb_dsp_unit_0001 | PASS | remaining-shard-a |
| 09 | cvdp_copilot_apb_history_shift_register_0001 | PASS | remaining-shard-a |
| 24 | cvdp_copilot_concatenate_0001 | PASS | remaining-shard-a |
| 28 | cvdp_copilot_convolutional_encoder_0001 | PASS | remaining-shard-b |
| 33 | cvdp_copilot_digital_dice_roller_0001 | PASS | remaining-shard-b |
| 39 | cvdp_copilot_fibonacci_series_0001 | PASS | remaining-shard-b |
| 40 | cvdp_copilot_fifo_async_0001 | PASS | remaining-shard-c |
| 65 | cvdp_copilot_secure_read_write_register_bank_0001 | PASS | remaining-shard-c |
| 70 | cvdp_copilot_static_branch_predict_0001 | PASS | remaining-shard-c |

## Evidence Paths

Server run root:

```text
/home/rongxv/work/cvdp-runs/iter-mygo-fixes-20260607
```

Shard directories:

```text
/home/rongxv/work/cvdp-runs/iter-mygo-fixes-20260607/remaining-shard-a
/home/rongxv/work/cvdp-runs/iter-mygo-fixes-20260607/remaining-shard-b
/home/rongxv/work/cvdp-runs/iter-mygo-fixes-20260607/remaining-shard-c
```

Verification summary from the server:

```json
{
  "count": 9,
  "counts": {
    "PASS": 9
  }
}
```

## Runner Status Cleanup

The runner no longer writes the ambiguous `MODEL_OR_MYGO_ERROR` status for new results. New runs classify failures into more actionable buckets:

- `MODEL_ERROR`
- `MODEL_STATIC_ERROR`
- `MYGO_COMPILE_ERROR`
- `NO_MODEL_ERROR`

The reader still accepts old `MODEL_OR_MYGO_ERROR` files so existing run directories remain reusable.
