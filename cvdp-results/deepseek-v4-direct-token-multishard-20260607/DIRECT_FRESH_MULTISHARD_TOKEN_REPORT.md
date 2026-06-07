# Direct Verilog Fresh Multishard CVDP Run - 2026-06-07

- Run root: `/home/rongxv/work/cvdp-runs/direct-deepseek-v4-server-fresh-20260607-token-mt`
- Flow: direct SystemVerilog generation, no MyGo
- Model: `deepseek/deepseek-v4-pro` via OpenRouter
- Parallelism: 6 independent shard processes x 13 tasks
- Freshness: output root deleted/recreated; no `--skip-existing`; no old model output reused
- Prompt isolation: one independent chat request per task; no cross-task conversation history

## Result

- Total tasks: 78
- FAIL: 27
- PASS: 51
- PASS rate: 51/78 (65.38%)

## Token Usage

- Input tokens (`prompt_tokens`): 101909
- Output tokens (`completion_tokens`): 88138
- Total tokens: 190047
- Cached prompt tokens: 0
- Reasoning tokens: 0
- OpenRouter reported cost: $0.136444

Average per task:

- Input tokens/task: 1306.53
- Output tokens/task: 1129.97
- Total tokens/task: 2436.50
- Cost/task: $0.001749

## Non-PASS Tasks

- 03 `cvdp_copilot_64b66b_encoder_0001`: FAIL
- 07 `cvdp_copilot_apb_dsp_unit_0001`: FAIL
- 09 `cvdp_copilot_apb_history_shift_register_0001`: FAIL
- 14 `cvdp_copilot_barrel_shifter_0001`: FAIL
- 17 `cvdp_copilot_binary_to_one_hot_decoder_0001`: FAIL
- 18 `cvdp_copilot_caesar_cipher_0001`: FAIL
- 22 `cvdp_copilot_comparator_0001`: FAIL
- 24 `cvdp_copilot_concatenate_0001`: FAIL
- 28 `cvdp_copilot_convolutional_encoder_0001`: FAIL
- 30 `cvdp_copilot_data_width_converter_0003`: FAIL
- 33 `cvdp_copilot_digital_dice_roller_0001`: FAIL
- 35 `cvdp_copilot_edge_detector_0001`: FAIL
- 36 `cvdp_copilot_ethernet_packet_parser_0001`: FAIL
- 39 `cvdp_copilot_fibonacci_series_0001`: FAIL
- 40 `cvdp_copilot_fifo_async_0001`: FAIL
- 44 `cvdp_copilot_gf_multiplier_0001`: FAIL
- 52 `cvdp_copilot_morse_code_0001`: FAIL
- 60 `cvdp_copilot_piso_0001`: FAIL
- 63 `cvdp_copilot_reverse_bits_0001`: FAIL
- 64 `cvdp_copilot_secure_read_write_bus_0001`: FAIL
- 65 `cvdp_copilot_secure_read_write_register_bank_0001`: FAIL
- 66 `cvdp_copilot_sequencial_binary_to_one_hot_decoder_0001`: FAIL
- 67 `cvdp_copilot_serial_in_parallel_out_0004`: FAIL
- 68 `cvdp_copilot_set_bit_calculator_0001`: FAIL
- 70 `cvdp_copilot_static_branch_predict_0001`: FAIL
- 73 `cvdp_copilot_thermostat_0001`: FAIL
- 75 `cvdp_copilot_unpacker_one_hot_0001`: FAIL

## Artifacts

- `token_usage_summary.json`
- `token_usage_per_task.csv`
- Per-task `llm_meta.json` files remain under the server run root and contain the raw OpenRouter `usage` objects.
