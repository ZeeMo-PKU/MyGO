# DeepSeek V4 direct Verilog CVDP server rerun, 2026-06-06

This directory records a fresh from-scratch server rerun of the CVDP `cid003` benchmark without MyGo.

## Setup

- Model: `deepseek/deepseek-v4-pro` via OpenRouter
- Flow: DeepSeek -> direct SystemVerilog -> Icarus/CVDP cocotb
- Server: `Trifoliate`, `/home/rongxv`
- Dataset: CVDP v1.1.0 non-agentic code generation, public no-commercial `cid003` subset
- Execution: fresh 78-task run, 4 shards; invalid empty model outputs were rerun with a non-empty RTL guard

## Result

- Total: 78
- PASS: 67
- FAIL: 11
- MODEL_ERROR: 0
- Pass rate: 85.90%
- Empty Verilog outputs after rerun: 0

`FAIL` means direct-generated SystemVerilog reached the CVDP host harness but did not produce a passing result. Some FAIL cases are functional assertion failures, while others are Icarus/SystemVerilog compile or elaboration failures.

## Compared With MyGo Server Run

| Metric | Direct Verilog | MyGo route |
| --- | ---: | ---: |
| PASS / 78 | 67 | 56 |
| Pass rate | 85.90% | 71.79% |

| Transition | Count | Meaning |
| --- | ---: | --- |
| both_pass | 55 | Both direct and MyGo pass |
| mygo_improved | 1 | Direct fails, MyGo passes |
| direct_only | 12 | Direct passes, MyGo does not pass |
| both_failed | 10 | Neither route passes |

## Failed Tasks

| # | Task | Category | Evidence |
| ---: | --- | --- | --- |
| 7 | `cvdp_copilot_apb_dsp_unit_0001` | CVDP_FUNCTION_FAIL | assert 0 == 85 |
| 9 | `cvdp_copilot_apb_history_shift_register_0001` | CVDP_FUNCTION_FAIL | 181.00ns WARNING  ..er.test_APBGlobalHistoryRegister control_register readback mismatch: Expected 0xb, got 0x0 |
| 24 | `cvdp_copilot_concatenate_0001` | CVDP_FUNCTION_FAIL | assert LogicArray('10', Range(1, 'downto', 0)) == 1 |
| 28 | `cvdp_copilot_convolutional_encoder_0001` | CVDP_FUNCTION_FAIL | 33.00ns WARNING  ..ding.test_convolutional_encoding Encoded bit1 mismatch at cycle 1: got 0, expected 1 |
| 33 | `cvdp_copilot_digital_dice_roller_0001` | CVDP_FUNCTION_FAIL | raise AttributeError(f"{self._path} contains no child object named {name}") |
| 36 | `cvdp_copilot_ethernet_packet_parser_0001` | VERILOG_COMPILE_FAIL | raise CalledProcessError(retcode, process.args, |
| 39 | `cvdp_copilot_fibonacci_series_0001` | CVDP_FUNCTION_FAIL | assert 2 == 1 |
| 40 | `cvdp_copilot_fifo_async_0001` | VERILOG_COMPILE_FAIL | /home/rongxv/work/cvdp-runs/direct-deepseek-v4-server-fresh-20260606/40_cvdp_copilot_fifo_async_0001/harness/rtl/fifo_async.sv:91: error: 'w_full' is not a v... |
| 65 | `cvdp_copilot_secure_read_write_register_bank_0001` | CVDP_FUNCTION_FAIL | assert LogicArray('00000010', Range(7, 'downto', 0)) == 0 |
| 66 | `cvdp_copilot_sequencial_binary_to_one_hot_decoder_0001` | VERILOG_COMPILE_FAIL | raise CalledProcessError(retcode, process.args, |
| 70 | `cvdp_copilot_static_branch_predict_0001` | CVDP_FUNCTION_FAIL | raise AttributeError(f"{self._path} contains no child object named {name}") |

## Files

- `direct_server_summary.md`: this human-readable report.
- `direct_server_summary.csv`: per-task direct run table.
- `direct_server_summary.json`: structured summary and rows.
- `direct_vs_mygo_server_detailed.csv`: per-task comparison against the MyGo server run.
- `direct_server_summary.txt`: compact status counts.

API keys, raw model responses, and temporary CVDP harness work directories are intentionally not included.
