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
| direct_mygo_inline | 32 | 50 | 64.00% | COMPILE_FAIL=1, FAIL=14, PASS=32, TIMEOUT=3 |

## Per Task

| # | Task | Module | direct_mygo_inline |
| ---: | --- | --- | --- |
| 1 | `Arithmetic/Accumulator/accu` | `accu` | PASS |
| 2 | `Arithmetic/Adder/adder_16bit` | `adder_16bit` | PASS |
| 3 | `Arithmetic/Adder/adder_32bit` | `adder_32bit` | PASS |
| 4 | `Arithmetic/Adder/adder_8bit` | `adder_8bit` | PASS |
| 5 | `Arithmetic/Adder/adder_bcd` | `adder_bcd` | PASS |
| 6 | `Arithmetic/Adder/adder_pipe_64bit` | `adder_pipe_64bit` | PASS |
| 7 | `Arithmetic/Comparator/comparator_3bit` | `comparator_3bit` | PASS |
| 8 | `Arithmetic/Comparator/comparator_4bit` | `comparator_4bit` | PASS |
| 9 | `Arithmetic/Divider/div_16bit` | `div_16bit` | FAIL |
| 10 | `Arithmetic/Divider/radix2_div` | `radix2_div` | TIMEOUT |
| 11 | `Arithmetic/Multiplier/multi_16bit` | `multi_16bit` | PASS |
| 12 | `Arithmetic/Multiplier/multi_8bit` | `multi_8bit` | PASS |
| 13 | `Arithmetic/Multiplier/multi_booth_8bit` | `multi_booth_8bit` | FAIL |
| 14 | `Arithmetic/Multiplier/multi_pipe_4bit` | `multi_pipe_4bit` | PASS |
| 15 | `Arithmetic/Multiplier/multi_pipe_8bit` | `multi_pipe_8bit` | FAIL |
| 16 | `Arithmetic/Other/fixed_point_adder` | `fixed_point_adder` | FAIL |
| 17 | `Arithmetic/Other/fixed_point_substractor` | `fixed_point_subtractor` | COMPILE_FAIL |
| 18 | `Arithmetic/Other/float_multi` | `float_multi` | FAIL |
| 19 | `Arithmetic/Substractor/sub_64bit` | `sub_64bit` | PASS |
| 20 | `Control/Counter/JC_counter` | `JC_counter` | PASS |
| 21 | `Control/Counter/counter_12` | `counter_12` | PASS |
| 22 | `Control/Counter/ring_counter` | `ring_counter` | FAIL |
| 23 | `Control/Counter/up_down_counter` | `up_down_counter` | PASS |
| 24 | `Control/Finite State Machine/fsm` | `fsm` | PASS |
| 25 | `Control/Finite State Machine/sequence_detector` | `sequence_detector` | PASS |
| 26 | `Memory/FIFO/asyn_fifo` | `asyn_fifo` | TIMEOUT |
| 27 | `Memory/LIFO/LIFObuffer` | `LIFObuffer` | FAIL |
| 28 | `Memory/Shifter/LFSR` | `LFSR` | PASS |
| 29 | `Memory/Shifter/barrel_shifter` | `barrel_shifter` | FAIL |
| 30 | `Memory/Shifter/right_shifter` | `right_shifter` | PASS |
| 31 | `Miscellaneous/Frequency divider/freq_div` | `freq_div` | PASS |
| 32 | `Miscellaneous/Frequency divider/freq_divbyeven` | `freq_diveven` | FAIL |
| 33 | `Miscellaneous/Frequency divider/freq_divbyfrac` | `freq_divbyfrac` | FAIL |
| 34 | `Miscellaneous/Frequency divider/freq_divbyodd` | `freq_divbyodd` | PASS |
| 35 | `Miscellaneous/Others/calendar` | `calendar` | PASS |
| 36 | `Miscellaneous/Others/edge_detect` | `edge_detect` | PASS |
| 37 | `Miscellaneous/Others/parallel2serial` | `parallel2serial` | PASS |
| 38 | `Miscellaneous/Others/pulse_detect` | `pulse_detect` | FAIL |
| 39 | `Miscellaneous/Others/serial2parallel` | `serial2parallel` | TIMEOUT |
| 40 | `Miscellaneous/Others/synchronizer` | `synchronizer` | PASS |
| 41 | `Miscellaneous/Others/traffic_light` | `traffic_light` | FAIL |
| 42 | `Miscellaneous/Others/width_8to16` | `width_8to16` | PASS |
| 43 | `Miscellaneous/RISC-V/RAM` | `RAM` | PASS |
| 44 | `Miscellaneous/RISC-V/ROM` | `ROM` | PASS |
| 45 | `Miscellaneous/RISC-V/alu` | `alu` | PASS |
| 46 | `Miscellaneous/RISC-V/clkgenerator` | `clkgenerator` | FAIL |
| 47 | `Miscellaneous/RISC-V/instr_reg` | `instr_reg` | PASS |
| 48 | `Miscellaneous/RISC-V/pe` | `pe` | PASS |
| 49 | `Miscellaneous/Signal generation/signal_generator` | `signal_generator` | FAIL |
| 50 | `Miscellaneous/Signal generation/square_wave` | `square_wave` | PASS |
