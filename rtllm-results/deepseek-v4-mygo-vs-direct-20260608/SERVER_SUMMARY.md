# RTLLM DeepSeek V4 Pro A/B Results

- Model: `deepseek/deepseek-v4-pro`
- RTLLM root: `/home/rongxv/work/rtllm-runs/dsv4-mygo-vs-direct-20260608-005901/RTLLM-41b2689`
- RTLLM commit/snapshot: `41b26896e33b536940116a975626455eed3de65e`
- MyGo commit: `9699ebdf84ace8daa67388d8197099d7d12c044b`
- Tasks: 50
- Sampling: pass@1 style, one model output per task per path
- Leakage guard: prompts contain only `design_description.txt` plus parsed interface hints; testbench/reference files are not sent to the model.

## Summary

| Path | PASS | Total | Pass rate | Status counts |
| --- | ---: | ---: | ---: | --- |
| direct_verilog | 29 | 50 | 58.00% | COMPILE_FAIL=15, FAIL=5, PASS=29, TIMEOUT=1 |
| mygo | 21 | 50 | 42.00% | COMPILE_FAIL=7, FAIL=11, MYGO_COMPILE_ERROR=10, PASS=21, TIMEOUT=1 |

## Per Task

| # | Task | Module | Direct | MyGo |
| ---: | --- | --- | --- | --- |
| 1 | `Arithmetic/Accumulator/accu` | `accu` | PASS | PASS |
| 2 | `Arithmetic/Adder/adder_16bit` | `adder_16bit` | PASS | PASS |
| 3 | `Arithmetic/Adder/adder_32bit` | `adder_32bit` | PASS | MYGO_COMPILE_ERROR |
| 4 | `Arithmetic/Adder/adder_8bit` | `adder_8bit` | PASS | FAIL |
| 5 | `Arithmetic/Adder/adder_bcd` | `adder_bcd` | PASS | PASS |
| 6 | `Arithmetic/Adder/adder_pipe_64bit` | `adder_pipe_64bit` | COMPILE_FAIL | COMPILE_FAIL |
| 7 | `Arithmetic/Comparator/comparator_3bit` | `comparator_3bit` | PASS | PASS |
| 8 | `Arithmetic/Comparator/comparator_4bit` | `comparator_4bit` | PASS | PASS |
| 9 | `Arithmetic/Divider/div_16bit` | `div_16bit` | PASS | FAIL |
| 10 | `Arithmetic/Divider/radix2_div` | `radix2_div` | COMPILE_FAIL | MYGO_COMPILE_ERROR |
| 11 | `Arithmetic/Multiplier/multi_16bit` | `multi_16bit` | PASS | MYGO_COMPILE_ERROR |
| 12 | `Arithmetic/Multiplier/multi_8bit` | `multi_8bit` | PASS | PASS |
| 13 | `Arithmetic/Multiplier/multi_booth_8bit` | `multi_booth_8bit` | PASS | PASS |
| 14 | `Arithmetic/Multiplier/multi_pipe_4bit` | `multi_pipe_4bit` | PASS | COMPILE_FAIL |
| 15 | `Arithmetic/Multiplier/multi_pipe_8bit` | `multi_pipe_8bit` | COMPILE_FAIL | PASS |
| 16 | `Arithmetic/Other/fixed_point_adder` | `fixed_point_adder` | COMPILE_FAIL | COMPILE_FAIL |
| 17 | `Arithmetic/Other/fixed_point_substractor` | `fixed_point_subtractor` | PASS | MYGO_COMPILE_ERROR |
| 18 | `Arithmetic/Other/float_multi` | `float_multi` | COMPILE_FAIL | MYGO_COMPILE_ERROR |
| 19 | `Arithmetic/Substractor/sub_64bit` | `sub_64bit` | PASS | PASS |
| 20 | `Control/Counter/JC_counter` | `JC_counter` | PASS | FAIL |
| 21 | `Control/Counter/counter_12` | `counter_12` | PASS | PASS |
| 22 | `Control/Counter/ring_counter` | `ring_counter` | COMPILE_FAIL | COMPILE_FAIL |
| 23 | `Control/Counter/up_down_counter` | `up_down_counter` | PASS | PASS |
| 24 | `Control/Finite State Machine/fsm` | `fsm` | PASS | PASS |
| 25 | `Control/Finite State Machine/sequence_detector` | `sequence_detector` | COMPILE_FAIL | COMPILE_FAIL |
| 26 | `Memory/FIFO/asyn_fifo` | `asyn_fifo` | FAIL | MYGO_COMPILE_ERROR |
| 27 | `Memory/LIFO/LIFObuffer` | `LIFObuffer` | PASS | PASS |
| 28 | `Memory/Shifter/LFSR` | `LFSR` | COMPILE_FAIL | COMPILE_FAIL |
| 29 | `Memory/Shifter/barrel_shifter` | `barrel_shifter` | FAIL | FAIL |
| 30 | `Memory/Shifter/right_shifter` | `right_shifter` | PASS | MYGO_COMPILE_ERROR |
| 31 | `Miscellaneous/Frequency divider/freq_div` | `freq_div` | PASS | FAIL |
| 32 | `Miscellaneous/Frequency divider/freq_divbyeven` | `freq_diveven` | COMPILE_FAIL | COMPILE_FAIL |
| 33 | `Miscellaneous/Frequency divider/freq_divbyfrac` | `freq_divbyfrac` | COMPILE_FAIL | MYGO_COMPILE_ERROR |
| 34 | `Miscellaneous/Frequency divider/freq_divbyodd` | `freq_divbyodd` | COMPILE_FAIL | FAIL |
| 35 | `Miscellaneous/Others/calendar` | `calendar` | PASS | FAIL |
| 36 | `Miscellaneous/Others/edge_detect` | `edge_detect` | PASS | PASS |
| 37 | `Miscellaneous/Others/parallel2serial` | `parallel2serial` | COMPILE_FAIL | PASS |
| 38 | `Miscellaneous/Others/pulse_detect` | `pulse_detect` | FAIL | FAIL |
| 39 | `Miscellaneous/Others/serial2parallel` | `serial2parallel` | TIMEOUT | TIMEOUT |
| 40 | `Miscellaneous/Others/synchronizer` | `synchronizer` | PASS | PASS |
| 41 | `Miscellaneous/Others/traffic_light` | `traffic_light` | COMPILE_FAIL | MYGO_COMPILE_ERROR |
| 42 | `Miscellaneous/Others/width_8to16` | `width_8to16` | PASS | MYGO_COMPILE_ERROR |
| 43 | `Miscellaneous/RISC-V/RAM` | `RAM` | COMPILE_FAIL | PASS |
| 44 | `Miscellaneous/RISC-V/ROM` | `ROM` | PASS | PASS |
| 45 | `Miscellaneous/RISC-V/alu` | `alu` | COMPILE_FAIL | FAIL |
| 46 | `Miscellaneous/RISC-V/clkgenerator` | `clkgenerator` | FAIL | FAIL |
| 47 | `Miscellaneous/RISC-V/instr_reg` | `instr_reg` | PASS | PASS |
| 48 | `Miscellaneous/RISC-V/pe` | `pe` | PASS | PASS |
| 49 | `Miscellaneous/Signal generation/signal_generator` | `signal_generator` | FAIL | FAIL |
| 50 | `Miscellaneous/Signal generation/square_wave` | `square_wave` | PASS | PASS |
