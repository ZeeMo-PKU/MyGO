# MyGO-CVDP cid003 Non-Agentic Failure Analysis

This file contains the reviewed per-case failure classification for all non-PASS cases in the envfix single-shot/pass@1 run.

## Reviewed Category Counts

- `VERILOG_INTERFACE_ERROR` (Verilog/CVDP interface contract mismatch): 55
- `TIMEOUT` (stage timeout): 10
- `GO_SYNTAX_ERROR` (generated Go static error): 4
- `MYGO_CIRCT_BACKEND_ERROR` (MyGO/CIRCT backend error): 3
- `FUNCTIONAL_FAIL` (true functional assertion mismatch): 2
- `MYGO_IR_LOWERING_ERROR` (MyGO IR lowering error): 2
- `VERILOG_COMPILE_ERROR` (Verilog compile/runtime error): 1
- `PASS`: 1

## Reviewed Subcategory Counts

- `PORT_OR_SIGNAL_MISSING`: 20
- `PORT_NAME_MISMATCH_OUT_PREFIX`: 18
- `PARAMETER_MISSING`: 11
- `LLM_TIMEOUT`: 7
- `INTERNAL_SIGNAL_OR_OBSERVABILITY_MISSING`: 5
- `MYGO_COMPILE_TIMEOUT`: 3
- `CIRCT_SSA_OR_TYPE_ERROR`: 3
- `GO_TYPE_ERROR`: 3
- `ASSERTION_VALUE_MISMATCH`: 2
- `MALFORMED_MLIR`: 2
- `PORT_NAME_MISSING`: 1
- `VVP_RUNTIME_ERROR`: 1
- `GO_PARSE_ERROR`: 1

## Per-Case Analysis

### 11. `cvdp_copilot_axi_stream_upscale_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `INTERNAL_SIGNAL_OR_OBSERVABILITY_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `axis_upscale`
- Go function: `axis_upscale`
- Verilog module: `axis_upscale`

Meaning:

cocotb ?? `m_axis_data` ????? RTL ?? benchmark ??????????

Why this category:

???? testbench ??? RTL ???????????????????

Key log excerpt:

```text
AttributeError: axis_upscale contains no child object named m_axis_data. Did you mean: 's_axis_data'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_axis_upscale[0] - SystemExit: 1
```

### 16. `cvdp_copilot_bcd_to_excess_3_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `INTERNAL_SIGNAL_OR_OBSERVABILITY_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `bcd_to_excess_3`
- Go function: `bcd_to_excess_3`
- Verilog module: `bcd_to_excess_3`

Meaning:

cocotb ?? `excess3` ????? RTL ?? benchmark ??????????

Why this category:

???? testbench ??? RTL ???????????????????

Key log excerpt:

```text
AttributeError: bcd_to_excess_3 contains no child object named excess3
assert dut.excess3.value == expected_value, f"Error: BCD {bcd_value} should convert to {expected_value}, got {dut.excess3.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_areg_param[0] - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_areg_param[1] - SystemExit: 1
```

### 58. `cvdp_copilot_perf_counters_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `INTERNAL_SIGNAL_OR_OBSERVABILITY_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `cvdp_copilot_perf_counters`
- Go function: `cvdp_copilot_perf_counters`
- Verilog module: `cvdp_copilot_perf_counters`

Meaning:

cocotb ?? `p_count_o` ????? RTL ?? benchmark ??????????

Why this category:

???? testbench ??? RTL ???????????????????

Key log excerpt:

```text
AttributeError: cvdp_copilot_perf_counters contains no child object named p_count_o. Did you mean: 'count_q'?
Failed 2 of 2 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 59. `cvdp_copilot_perfect_squares_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `INTERNAL_SIGNAL_OR_OBSERVABILITY_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `perfect_squares_generator`
- Go function: `perfect_squares_generator`
- Verilog module: `perfect_squares_generator`

Meaning:

cocotb ?? `sqr_o` ????? RTL ?? benchmark ??????????

Why this category:

???? testbench ??? RTL ???????????????????

Key log excerpt:

```text
AttributeError: perfect_squares_generator contains no child object named sqr_o
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 74. `cvdp_copilot_ttc_lite_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `INTERNAL_SIGNAL_OR_OBSERVABILITY_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `ttc_counter_lite`
- Go function: `ttc_counter_lite`
- Verilog module: `ttc_counter_lite`

Meaning:

cocotb ?? `axi_rdata` ????? RTL ?? benchmark ??????????

Why this category:

???? testbench ??? RTL ???????????????????

Key log excerpt:

```text
AttributeError: ttc_counter_lite contains no child object named axi_rdata. Did you mean: 'axi_wdata'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_areg_param[0] - SystemExit: 1
```

### 1. `cvdp_copilot_16qam_mapper_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `qam16_mapper_interpolated`
- Go function: `qam16_mapper_interpolated`
- Verilog module: `qam16_mapper_interpolated`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `N` not found in `qam16_mapper_interpolated`.
error: parameter `N` not found in `qam16_mapper_interpolated`.
returned non-zero exit status 2
FAILED ../../harness/src/test_runner.py::test_data[0-2] - subprocess.CalledPr...
FAILED ../../harness/src/test_runner.py::test_data[0-4_0] - subprocess.Called...
FAILED ../../harness/src/test_runner.py::test_data[0-8_0] - subprocess.Called...
FAILED ../../harness/src/test_runner.py::test_data[0-4_1] - subprocess.Called...
```

### 8. `cvdp_copilot_apb_gpio_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP elaboration
- CVDP TOPLEVEL: `cvdp_copilot_apb_gpio`
- Go function: `cvdp_copilot_apb_gpio`
- Verilog module: `cvdp_copilot_apb_gpio`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `GPIO_WIDTH` not found in `cvdp_copilot_apb_gpio`.
error: parameter `GPIO_WIDTH` not found in `cvdp_copilot_apb_gpio`.
AssertionError: Simulation failed for GPIO_WIDTH = 8: Command '['iverilog', '-o', '<RUN_DIR>/logs/cvdp_copilot_apb_gpio_0001/cvdp/host_rundir/harness/sim_build/sim.vvp', '-s', 'cvdp_copilot_apb_gpio', '-g2012', '-Pcvdp_copilot_apb_gpio.GPIO_WIDTH=8', '-f', '/home/rongxv/work/...
AssertionError: Simulation failed for GPIO_WIDTH = 11: Command '['iverilog', '-o', '<RUN_DIR>/logs/cvdp_copilot_apb_gpio_0001/cvdp/host_rundir/harness/sim_build/sim.vvp', '-s', 'cvdp_copilot_apb_gpio', '-g2012', '-Pcvdp_copilot_apb_gpio.GPIO_WIDTH=11', '-f', '/home/rongxv/wor...
AssertionError: Simulation failed for GPIO_WIDTH = 30: Command '['iverilog', '-o', '<RUN_DIR>/logs/cvdp_copilot_apb_gpio_0001/cvdp/host_rundir/harness/sim_build/sim.vvp', '-s', 'cvdp_copilot_apb_gpio', '-g2012', '-Pcvdp_copilot_apb_gpio.GPIO_WIDTH=30', '-f', '/home/rongxv/wor...
E AssertionError: Simulation failed for GPIO_WIDTH = 8: Command '['iverilog', '-o', '<RUN_DIR>/logs/cvdp_copilot_apb_gpio_0001/cvdp/host_rundir/harness/sim_build/sim.vvp', '-s', 'cvdp_copilot_apb_gpio', '-g2012', '-Pcvdp_copilot_apb_gpio.GPIO_WIDTH=8', '-f', '/home/rongxv/wor...
E AssertionError: Simulation failed for GPIO_WIDTH = 11: Command '['iverilog', '-o', '<RUN_DIR>/logs/cvdp_copilot_apb_gpio_0001/cvdp/host_rundir/harness/sim_build/sim.vvp', '-s', 'cvdp_copilot_apb_gpio', '-g2012', '-Pcvdp_copilot_apb_gpio.GPIO_WIDTH=11', '-f', '/home/rongxv/w...
```

### 10. `cvdp_copilot_axi_register_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `axi_register`
- Go function: `axi_register`
- Verilog module: `axi_register`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `ADDR_WIDTH` not found in `axi_register`.
:0: error: parameter `DATA_WIDTH` not found in `axi_register`.
error: parameter `ADDR_WIDTH` not found in `axi_register`.
error: parameter `DATA_WIDTH` not found in `axi_register`.
returned non-zero exit status 3
FAILED ../../harness/src/test_runner.py::test_axi_reg[8-12-0] - subprocess.Ca...
FAILED ../../harness/src/test_runner.py::test_axi_reg[8-16-0] - subprocess.Ca...
```

### 19. `cvdp_copilot_car_parking_management_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `car_parking_system`
- Go function: `sevenSeg`
- Verilog module: `car_parking_system`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `TOTAL_SPACES` not found in `car_parking_system`.
error: parameter `TOTAL_SPACES` not found in `car_parking_system`.
returned non-zero exit status 2
FAILED ../../harness/src/test_runner.py::test_runner - subprocess.CalledProce...
FAILED ../../harness/src/test_runner.py::test_car_parking_system[14] - subpro...
FAILED ../../harness/src/test_runner.py::test_car_parking_system[12] - subpro...
FAILED ../../harness/src/test_runner.py::test_car_parking_system[9] - subproc...
```

### 25. `cvdp_copilot_configurable_digital_low_pass_filter_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `low_pass_filter`
- Go function: `low_pass_filter`
- Verilog module: `low_pass_filter`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `COEFF_WIDTH` not found in `low_pass_filter`.
:0: error: parameter `DATA_WIDTH` not found in `low_pass_filter`.
:0: error: parameter `NUM_TAPS` not found in `low_pass_filter`.
error: parameter `COEFF_WIDTH` not found in `low_pass_filter`.
error: parameter `DATA_WIDTH` not found in `low_pass_filter`.
error: parameter `NUM_TAPS` not found in `low_pass_filter`.
returned non-zero exit status 4
```

### 27. `cvdp_copilot_configurable_digital_low_pass_filter_0014`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `fsm_linear_reg`
- Go function: `fsm_linear_reg`
- Verilog module: `fsm_linear_reg`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `DATA_WIDTH` not found in `fsm_linear_reg`.
error: parameter `DATA_WIDTH` not found in `fsm_linear_reg`.
returned non-zero exit status 2
FAILED ../../harness/src/test_runner.py::test_data[0-2] - subprocess.CalledPr...
FAILED ../../harness/src/test_runner.py::test_data[0-16_0] - subprocess.Calle...
FAILED ../../harness/src/test_runner.py::test_data[0-15] - subprocess.CalledP...
FAILED ../../harness/src/test_runner.py::test_data[0-8] - subprocess.CalledPr...
```

### 34. `cvdp_copilot_digital_stopwatch_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `dig_stopwatch`
- Go function: `dig_stopwatch`
- Verilog module: `dig_stopwatch`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `CLK_FREQ` not found in `dig_stopwatch`.
error: parameter `CLK_FREQ` not found in `dig_stopwatch`.
returned non-zero exit status 2
FAILED ../../harness/src/test_runner.py::test_dig_stop[3-0] - subprocess.Call...
FAILED ../../harness/src/test_runner.py::test_dig_stop[50-0] - subprocess.Cal...
FAILED ../../harness/src/test_runner.py::test_dig_stop[63-0] - subprocess.Cal...
```

### 50. `cvdp_copilot_matrix_multiplier_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `matrix_multiplier`
- Go function: `matrix_multiplier`
- Verilog module: `matrix_multiplier`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `COL_A` not found in `matrix_multiplier`.
:0: error: parameter `COL_B` not found in `matrix_multiplier`.
:0: error: parameter `INPUT_DATA_WIDTH` not found in `matrix_multiplier`.
:0: error: parameter `ROW_A` not found in `matrix_multiplier`.
:0: error: parameter `ROW_B` not found in `matrix_multiplier`.
error: parameter `COL_A` not found in `matrix_multiplier`.
error: parameter `COL_B` not found in `matrix_multiplier`.
```

### 54. `cvdp_copilot_nbit_swizzling_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `nbit_swizzling`
- Go function: `reverse8`
- Verilog module: `nbit_swizzling`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `DATA_WIDTH` not found in `nbit_swizzling`.
error: parameter `DATA_WIDTH` not found in `nbit_swizzling`.
returned non-zero exit status 2
FAILED ../../harness/src/test_runner.py::test_nbit_sizling[16] - subprocess.C...
FAILED ../../harness/src/test_runner.py::test_nbit_sizling[32] - subprocess.C...
FAILED ../../harness/src/test_runner.py::test_nbit_sizling[40] - subprocess.C...
FAILED ../../harness/src/test_runner.py::test_nbit_sizling[48] - subprocess.C...
```

### 62. `cvdp_copilot_restoring_division_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `restoring_division`
- Go function: `restoring_division`
- Verilog module: `restoring_division`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `WIDTH` not found in `restoring_division`.
error: parameter `WIDTH` not found in `restoring_division`.
returned non-zero exit status 2
FAILED ../../harness/src/test_runner.py::test_areg_param[3-0] - subprocess.Ca...
FAILED ../../harness/src/test_runner.py::test_areg_param[3-1] - subprocess.Ca...
FAILED ../../harness/src/test_runner.py::test_areg_param[4-0] - subprocess.Ca...
FAILED ../../harness/src/test_runner.py::test_areg_param[4-1] - subprocess.Ca...
```

### 71. `cvdp_copilot_sync_lifo_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PARAMETER_MISSING`
- First failing stage: CVDP harness
- CVDP TOPLEVEL: `sync_lifo`
- Go function: `sync_lifo`
- Verilog module: `sync_lifo`

Meaning:

CVDP testbench ?? iverilog -P ?????????????? Verilog parameter?

Why this category:

????????????? RTL ??????? benchmark ???????? pytest/cocotb ?????

Key log excerpt:

```text
:0: error: parameter `ADDR_WIDTH` not found in `sync_lifo`.
:0: error: parameter `DATA_WIDTH` not found in `sync_lifo`.
error: parameter `ADDR_WIDTH` not found in `sync_lifo`.
error: parameter `DATA_WIDTH` not found in `sync_lifo`.
returned non-zero exit status 3
FAILED ../../harness/src/test_runner.py::test_areg_param[4] - subprocess.Call...
FAILED ../../harness/src/test_runner.py::test_areg_param[8] - subprocess.Call...
```

### 5. `cvdp_copilot_Carry_Lookahead_Adder_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `GP`
- Go function: `GP`
- Verilog module: `GP`

Meaning:

cocotb ?? `o_generate` ????? RTL ????? `out_o_generate`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: GP contains no child object named o_generate. Did you mean: 'out_o_generate'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_gp_test - SystemExit: 1
```

### 9. `cvdp_copilot_apb_history_shift_register_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `APBGlobalHistoryRegister`
- Go function: `APBGlobalHistoryRegister`
- Verilog module: `APBGlobalHistoryRegister`

Meaning:

cocotb ?? `history_empty` ????? RTL ????? `out_history_empty`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: APBGlobalHistoryRegister contains no child object named history_empty. Did you mean: 'out_history_empty'?
assert dut.history_empty.value == 1, "history_empty should be 1 after reset"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 17. `cvdp_copilot_binary_to_one_hot_decoder_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `binary_to_one_hot_decoder`
- Go function: `binary_to_one_hot_decoder`
- Verilog module: `binary_to_one_hot_decoder`

Meaning:

cocotb ?? `one_hot_out` ????? RTL ????? `out_one_hot_out`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: binary_to_one_hot_decoder contains no child object named one_hot_out. Did you mean: 'out_one_hot_out'?
assert dut.one_hot_out.value==1, f"output should not be {dut.one_hot_out.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 22. `cvdp_copilot_comparator_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `signed_unsigned_comparator`
- Go function: `signed_unsigned_comparator`
- Verilog module: `signed_unsigned_comparator`

Meaning:

cocotb ?? `o_greater` ????? RTL ????? `out_o_greater`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: signed_unsigned_comparator contains no child object named o_greater. Did you mean: 'out_o_greater'?
assert dut.o_greater.value==0, f"output should not be {dut.o_greater.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 23. `cvdp_copilot_complex_multiplier_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `complex_multiplier`
- Go function: `complex_multiplier`
- Verilog module: `complex_multiplier`

Meaning:

cocotb ?? `result_real` ????? RTL ????? `out_result_real`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: complex_multiplier contains no child object named result_real. Did you mean: 'out_result_real'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_palindrome_detect - SystemExit: 1
```

### 24. `cvdp_copilot_concatenate_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP elaboration
- CVDP TOPLEVEL: `enhanced_fsm_signal_processor`
- Go function: `enhanced_fsm_signal_processor`
- Verilog module: `enhanced_fsm_signal_processor`

Meaning:

cocotb ?? `o_fsm_status` ????? RTL ????? `out_o_fsm_status`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: enhanced_fsm_signal_processor contains no child object named o_fsm_status. Did you mean: 'out_o_fsm_status'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 30. `cvdp_copilot_data_width_converter_0003`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `data_width_converter`
- Go function: `data_width_converter`
- Verilog module: `data_width_converter`

Meaning:

cocotb ?? `o_data_out` ????? RTL ????? `out_o_data_out`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: data_width_converter contains no child object named o_data_out. Did you mean: 'out_o_data_out'?
assert dut.o_data_out.value == expected_output, f"Output mismatch: Expected {hex(expected_output)}, got {hex(dut.o_data_out.value)}"
Expected {hex(expected_output)}, got {hex(dut.o_data_out.value)}"
Expected output: 0x11111111222222223333333344444444
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 35. `cvdp_copilot_edge_detector_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `sync_pos_neg_edge_detector`
- Go function: `sync_pos_neg_edge_detector`
- Verilog module: `sync_pos_neg_edge_detector`

Meaning:

cocotb ?? `o_positive_edge_detected` ????? RTL ????? `out_o_positive_edge_detected`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: sync_pos_neg_edge_detector contains no child object named o_positive_edge_detected. Did you mean: 'out_o_positive_edge_detected'?
assert dut.o_positive_edge_detected.value==1, f"output should be 1 not {dut.o_positive_edge_detected.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 37. `cvdp_copilot_events_to_apb_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `apb_controller`
- Go function: `apb_controller`
- Verilog module: `apb_controller`

Meaning:

cocotb ?? `apb_psel_o` ????? RTL ????? `out_apb_psel_o`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: apb_controller contains no child object named apb_psel_o. Did you mean: 'out_apb_psel_o'?
assert dut.apb_psel_o.value == 0, "APB select should be 0 at a reset"
Failed 4 of 4 tests
FAILED ../../harness/src/test_runner.py::test_apb - SystemExit: 1
```

### 42. `cvdp_copilot_fsm_seq_detector_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `fsm_seq_detector`
- Go function: `fsm_seq_detector`
- Verilog module: `fsm_seq_detector`

Meaning:

cocotb ?? `seq_detected` ????? RTL ????? `out_seq_detected`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: fsm_seq_detector contains no child object named seq_detected. Did you mean: 'out_seq_detected'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_detection_at_start - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_detection_at_end - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_multiple_occurrences - SystemEx...
FAILED ../../harness/src/test_runner.py::test_noise_before_after - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_seq_overlapping - SystemExit: 1
```

### 52. `cvdp_copilot_morse_code_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `morse_encoder`
- Go function: `morse_encoder`
- Verilog module: `morse_encoder`

Meaning:

cocotb ?? `morse_out` ????? RTL ????? `out_morse_out`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: morse_encoder contains no child object named morse_out. Did you mean: 'out_morse_out'?
assert int(dut.morse_out.value) == expected_morse, f"Test failed for {ascii_char}: Expected Morse {bin(expected_morse)}, got {bin(int(dut.morse_out.value))}"
Expected Morse {bin(expected_morse)}, got {bin(int(dut.morse_out.value))}"
Failed 3 of 3 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 56. `cvdp_copilot_palindrome_3b_0002`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `palindrome_detect`
- Go function: `palindrome_detect`
- Verilog module: `palindrome_detect`

Meaning:

cocotb ?? `palindrome_detected` ????? RTL ????? `out_palindrome_detected`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: palindrome_detect contains no child object named palindrome_detected. Did you mean: 'out_palindrome_detected'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_palindrome_detect - SystemExit: 1
```

### 60. `cvdp_copilot_piso_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `piso_8bit`
- Go function: `piso_8bit`
- Verilog module: `piso_8bit`

Meaning:

cocotb ?? `serial_out` ????? RTL ????? `out_serial_out`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: piso_8bit contains no child object named serial_out. Did you mean: 'out_serial_out'?
assert int(dut.serial_out.value) == 0, "serial_out value didn't reset properly"
Failed 5 of 5 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 66. `cvdp_copilot_sequencial_binary_to_one_hot_decoder_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `binary_to_one_hot_decoder_sequential`
- Go function: `binary_to_one_hot_decoder_sequential`
- Verilog module: `binary_to_one_hot_decoder_sequential`

Meaning:

cocotb ?? `o_one_hot_out` ????? RTL ????? `out_o_one_hot_out`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: binary_to_one_hot_decoder_sequential contains no child object named o_one_hot_out. Did you mean: 'out_o_one_hot_out'?
assert dut.o_one_hot_out.value==1, f"output should not be {dut.o_one_hot_out.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 67. `cvdp_copilot_serial_in_parallel_out_0004`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `serial_in_parallel_out_8bit`
- Go function: `serial_in_parallel_out_8bit`
- Verilog module: `serial_in_parallel_out_8bit`

Meaning:

cocotb ?? `parallel_out` ????? RTL ????? `out_parallel_out`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: serial_in_parallel_out_8bit contains no child object named parallel_out. Did you mean: 'out_parallel_out'?
Failed 3 of 3 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 68. `cvdp_copilot_set_bit_calculator_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `SetBitStreamCalculator`
- Go function: `SetBitStreamCalculator`
- Verilog module: `SetBitStreamCalculator`

Meaning:

cocotb ?? `o_set_bit_count` ????? RTL ????? `out_o_set_bit_count`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: SetBitStreamCalculator contains no child object named o_set_bit_count. Did you mean: 'out_o_set_bit_count'?
assert dut.o_set_bit_count.value==8, f"output should not be {dut.o_set_bit_count.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 73. `cvdp_copilot_thermostat_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `thermostat`
- Go function: `thermostat`
- Verilog module: `thermostat`

Meaning:

cocotb ?? `o_state` ????? RTL ????? `out_state`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: thermostat contains no child object named o_state. Did you mean: 'out_state'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 76. `cvdp_copilot_vending_machine_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISMATCH_OUT_PREFIX`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `vending_machine`
- Go function: `vending_machine`
- Verilog module: `vending_machine`

Meaning:

cocotb ?? `dispense_item` ????? RTL ????? `out_dispense_item`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: vending_machine contains no child object named dispense_item. Did you mean: 'out_dispense_item'?
assert dut.dispense_item.value == 1, f"Expected item to be dispensed!"
Expected item to be dispensed!"
expected price: 20
expected price: 10
expected price: 15
Failed 1 of 1 tests
```

### 18. `cvdp_copilot_caesar_cipher_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_NAME_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `caesar_cipher`
- Go function: `caesar_cipher`
- Verilog module: `caesar_cipher`

Meaning:

CVDP ??????????????

Why this category:

????? cocotb ?? DUT ?????????????

Key log excerpt:

```text
DUT does not have an 'output_char' output.
DUT does not have an 'output_char' output."
AssertionError: DUT does not have an 'output_char' output.
assert False
assert hasattr(dut, "output_char"), "DUT does not have an 'output_char' output."
Failed 4 of 4 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 3. `cvdp_copilot_64b66b_encoder_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `encoder_64b66b`
- Go function: `encoder_64b66b`
- Verilog module: `encoder_64b66b`

Meaning:

cocotb ?? `encoder_data_out` ????? RTL ????? `encoder_data_in`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: encoder_64b66b contains no child object named encoder_data_out. Did you mean: 'encoder_data_in'?
Expected data output is zero
Failed 7 of 7 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 4. `cvdp_copilot_8x3_priority_encoder_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `priority_encoder_8x3`
- Go function: `priority_encoder_8x3`
- Verilog module: `priority_encoder_8x3`

Meaning:

cocotb ?? `out` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: priority_encoder_8x3 contains no child object named out
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_moving_run[0] - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_moving_run[1] - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_moving_run[2] - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_moving_run[3] - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_moving_run[4] - SystemExit: 1
```

### 6. `cvdp_copilot_GFCM_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `glitch_free_mux`
- Go function: `glitch_free_mux`
- Verilog module: `glitch_free_mux`

Meaning:

cocotb ?? `clkout` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: glitch_free_mux contains no child object named clkout
assert dut.clkout.value == 0, f"Glitch detected, clkout is {dut.clkout.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_gfcm - SystemExit: 1
```

### 14. `cvdp_copilot_barrel_shifter_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `barrel_shifter_8bit`
- Go function: `barrel_shifter_8bit`
- Verilog module: `barrel_shifter_8bit`

Meaning:

cocotb ?? `data_out` ????? RTL ????? `data_in`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: barrel_shifter_8bit contains no child object named data_out. Did you mean: 'data_in'?
Failed 3 of 3 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 21. `cvdp_copilot_clock_divider_0003`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `clock_divider`
- Go function: `clock_divider`
- Verilog module: `clock_divider`

Meaning:

cocotb ?? `clk_out` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: clock_divider contains no child object named clk_out
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_clock_divider_run[0] - SystemEx...
```

### 28. `cvdp_copilot_convolutional_encoder_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `convolutional_encoder`
- Go function: `convolutional_encoder`
- Verilog module: `convolutional_encoder`

Meaning:

cocotb ?? `shift_reg` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: convolutional_encoder contains no child object named shift_reg
AttributeError: convolutional_encoder contains no child object named encoded_bit1. Did you mean: 'out_encoded_bit1'?
assert dut.shift_reg.value == 0, f"Shift register is not reset properly: {dut.shift_reg.value}"
Expected encoded bits: bit1=1, bit2=1
Expected encoded bits: bit1=0, bit2=0
Failed 3 of 3 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 33. `cvdp_copilot_digital_dice_roller_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `digital_dice_roller`
- Go function: `digital_dice_roller`
- Verilog module: `digital_dice_roller`

Meaning:

cocotb ?? `DICE_MAX` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: digital_dice_roller contains no child object named DICE_MAX
AttributeError: digital_dice_roller contains no child object named reset. Did you mean: 'reset_n'?
Failed 3 of 3 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 36. `cvdp_copilot_ethernet_packet_parser_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `field_extract`
- Go function: `field_extract`
- Verilog module: `field_extract`

Meaning:

cocotb ?? `field` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: field_extract contains no child object named field
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 38. `cvdp_copilot_factorial_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `factorial`
- Go function: `factorial`
- Verilog module: `factorial`

Meaning:

cocotb ?? `busy` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: factorial contains no child object named busy
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_factorial - SystemExit: 1
```

### 39. `cvdp_copilot_fibonacci_series_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `fibonacci_series`
- Go function: `fibonacci_series`
- Verilog module: `fibonacci_series`

Meaning:

cocotb ?? `fib_out` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: fibonacci_series contains no child object named fib_out
Failed 2 of 2 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 44. `cvdp_copilot_gf_multiplier_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `gf_multiplier`
- Go function: `gf_multiplier`
- Verilog module: `gf_multiplier`

Meaning:

cocotb ?? `result` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: gf_multiplier contains no child object named result
Failed 2 of 2 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 45. `cvdp_copilot_hamming_code_tx_and_rx_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `hamming_code_tx_for_4bit`
- Go function: `hamming_code_tx_for_4bit`
- Verilog module: `hamming_code_tx_for_4bit`

Meaning:

cocotb ?? `data_out` ????? RTL ????? `data_in`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: hamming_code_tx_for_4bit contains no child object named data_out. Did you mean: 'data_in'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test[0] - SystemExit: 1
```

### 46. `cvdp_copilot_hamming_code_tx_and_rx_0003`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `hamming_code_receiver`
- Go function: `hamming_code_receiver`
- Verilog module: `hamming_code_receiver`

Meaning:

cocotb ?? `data_out` ????? RTL ????? `data_in`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: hamming_code_receiver contains no child object named data_out. Did you mean: 'data_in'?
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test[0] - SystemExit: 1
```

### 53. `cvdp_copilot_moving_average_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `moving_average`
- Go function: `moving_average`
- Verilog module: `moving_average`

Meaning:

cocotb ?? `data_out` ????? RTL ????? `data_in`?

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: moving_average contains no child object named data_out. Did you mean: 'data_in'?
assert dut.data_out.value == 0, f"[ERROR] data_out is not zero after reset: {dut.data_out.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_moving_rndm[0] - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_moving_rndm[1] - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_moving_rndm[2] - SystemExit: 1
FAILED ../../harness/src/test_runner.py::test_moving_rndm[3] - SystemExit: 1
```

### 63. `cvdp_copilot_reverse_bits_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `reverse_bits`
- Go function: `reverse_bits`
- Verilog module: `reverse_bits`

Meaning:

cocotb ?? `num_out` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: reverse_bits contains no child object named num_out
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 64. `cvdp_copilot_secure_read_write_bus_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP elaboration
- CVDP TOPLEVEL: `secure_read_write_bus_interface`
- Go function: `secure_read_write_bus_interface`
- Verilog module: `secure_read_write_bus_interface`

Meaning:

cocotb ?? `o_error` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: secure_read_write_bus_interface contains no child object named o_error
assert dut.o_error.value==0, f"output should not be {dut.o_error.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 65. `cvdp_copilot_secure_read_write_register_bank_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `secure_read_write_register_bank`
- Go function: `secure_read_write_register_bank`
- Verilog module: `secure_read_write_register_bank`

Meaning:

cocotb ?? `o_data_out` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: secure_read_write_register_bank contains no child object named o_data_out
assert dut.o_data_out.value==2, f"output should not be {dut.o_data_out.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 70. `cvdp_copilot_static_branch_predict_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `static_branch_predict`
- Go function: `static_branch_predict`
- Verilog module: `static_branch_predict`

Meaning:

cocotb ?? `register_addr_i` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: static_branch_predict contains no child object named register_addr_i
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 75. `cvdp_copilot_unpacker_one_hot_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `unpack_one_hot`
- Go function: `unpack_one_hot`
- Verilog module: `unpack_one_hot`

Meaning:

cocotb ?? `destination_reg` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: unpack_one_hot contains no child object named destination_reg
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_runner - SystemExit: 1
```

### 78. `cvdp_copilot_wb2ahb_0001`

- Status: `FAIL`
- Reviewed category: `VERILOG_INTERFACE_ERROR`
- Subcategory: `PORT_OR_SIGNAL_MISSING`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `wishbone_to_ahb_bridge`
- Go function: `trailing_ones`
- Verilog module: `wishbone_to_ahb_bridge`

Meaning:

cocotb ?? `hwrite` ????? RTL ???????

Why this category:

??????????????? testbench ???????/????????????????

Key log excerpt:

```text
AttributeError: wishbone_to_ahb_bridge contains no child object named hwrite
assert dut.hwrite.value == 1, f"ERROR: hwrite should be 1, got {dut.hwrite.value}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_areg_param[0] - SystemExit: 1
```

### 2. `cvdp_copilot_16qam_mapper_0006`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `LLM_TIMEOUT`
- First failing stage: LLM/Go generation
- CVDP TOPLEVEL: `qam16_demapper_interpolated`
- Go function: ``
- Verilog module: ``

Meaning:

LLM ???? 180 ???????? MyGO ? Go ???

Why this category:

LLM ??????MyGO/CVDP ???????????? Go?MyGO ? Verilog?

Key log excerpt:

```text

```

### 7. `cvdp_copilot_apb_dsp_unit_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `LLM_TIMEOUT`
- First failing stage: LLM/Go generation
- CVDP TOPLEVEL: `apb_dsp_unit`
- Go function: ``
- Verilog module: ``

Meaning:

LLM ???? 180 ???????? MyGO ? Go ???

Why this category:

LLM ??????MyGO/CVDP ???????????? Go?MyGO ? Verilog?

Key log excerpt:

```text

```

### 12. `cvdp_copilot_axil_precision_counter_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `LLM_TIMEOUT`
- First failing stage: LLM/Go generation
- CVDP TOPLEVEL: `precision_counter_axi`
- Go function: ``
- Verilog module: ``

Meaning:

LLM ???? 180 ???????? MyGO ? Go ???

Why this category:

LLM ??????MyGO/CVDP ???????????? Go?MyGO ? Verilog?

Key log excerpt:

```text

```

### 20. `cvdp_copilot_cascaded_adder_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `LLM_TIMEOUT`
- First failing stage: LLM/Go generation
- CVDP TOPLEVEL: `cascaded_adder`
- Go function: ``
- Verilog module: ``

Meaning:

LLM ???? 180 ???????? MyGO ? Go ???

Why this category:

LLM ??????MyGO/CVDP ???????????? Go?MyGO ? Verilog?

Key log excerpt:

```text

```

### 49. `cvdp_copilot_load_store_unit_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `LLM_TIMEOUT`
- First failing stage: LLM/Go generation
- CVDP TOPLEVEL: `load_store_unit`
- Go function: ``
- Verilog module: ``

Meaning:

LLM ???? 180 ???????? MyGO ? Go ???

Why this category:

LLM ??????MyGO/CVDP ???????????? Go?MyGO ? Verilog?

Key log excerpt:

```text

```

### 51. `cvdp_copilot_microcode_sequencer_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `LLM_TIMEOUT`
- First failing stage: LLM/Go generation
- CVDP TOPLEVEL: `microcode_sequencer`
- Go function: ``
- Verilog module: ``

Meaning:

LLM ???? 180 ???????? MyGO ? Go ???

Why this category:

LLM ??????MyGO/CVDP ???????????? Go?MyGO ? Verilog?

Key log excerpt:

```text

```

### 57. `cvdp_copilot_perceptron_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `LLM_TIMEOUT`
- First failing stage: LLM/Go generation
- CVDP TOPLEVEL: `perceptron_gates`
- Go function: ``
- Verilog module: ``

Meaning:

LLM ???? 180 ???????? MyGO ? Go ???

Why this category:

LLM ??????MyGO/CVDP ???????????? Go?MyGO ? Verilog?

Key log excerpt:

```text

```

### 13. `cvdp_copilot_axis_joiner_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `MYGO_COMPILE_TIMEOUT`
- First failing stage: MyGO compile
- CVDP TOPLEVEL: `axis_joiner`
- Go function: `axis_joiner`
- Verilog module: ``

Meaning:

MyGO ???? 120 ???????? Verilog/CVDP?

Why this category:

MyGO ????????????? RTL????? CVDP ?????

Key log excerpt:

```text
TIMEOUT after 120s while running: <RUN_DIR>/tools/mygo compile -emit=verilog --target axis_joiner --circt-mlir <RUN_DIR>/logs/cvdp_copilot_axis_joiner_0001/mygo/design.mlir -o /home/rongxv/work/c...
```

### 31. `cvdp_copilot_dbi_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `MYGO_COMPILE_TIMEOUT`
- First failing stage: MyGO compile
- CVDP TOPLEVEL: `dbi_enc`
- Go function: `dbi_enc`
- Verilog module: ``

Meaning:

MyGO ???? 120 ???????? Verilog/CVDP?

Why this category:

MyGO ????????????? RTL????? CVDP ?????

Key log excerpt:

```text
TIMEOUT after 120s while running: <RUN_DIR>/tools/mygo compile -emit=verilog --target dbi_enc --circt-mlir <RUN_DIR>/logs/cvdp_copilot_dbi_0001/mygo/design.mlir -o /home/rongxv/work/cvdp-runs/myg...
```

### 72. `cvdp_copilot_sync_serial_communication_0001`

- Status: `TIMEOUT`
- Reviewed category: `TIMEOUT`
- Subcategory: `MYGO_COMPILE_TIMEOUT`
- First failing stage: MyGO compile
- CVDP TOPLEVEL: `sync_serial_communication_tx_rx`
- Go function: `sync_serial_communication_tx_rx`
- Verilog module: `sync_serial_communication_tx_rx`

Meaning:

MyGO ???? 120 ???????? Verilog/CVDP?

Why this category:

MyGO ????????????? RTL????? CVDP ?????

Key log excerpt:

```text
TIMEOUT after 120s while running: <RUN_DIR>/tools/mygo compile -emit=verilog --target sync_serial_communication_tx_rx --circt-mlir <RUN_DIR>/logs/cvdp_copilot_sync_serial_communication_0001/mygo/...
```

### 43. `cvdp_copilot_gcd_0001`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `GO_SYNTAX_ERROR`
- Subcategory: `GO_PARSE_ERROR`
- First failing stage: MyGO frontend
- CVDP TOPLEVEL: `gcd_top`
- Go function: `gcd_top`
- Verilog module: ``

Meaning:

???? Go ???????????????/????????

Why this category:

??????? main.go ? Go ???????????? MyGO IR/Verilog?

Key log excerpt:

```text
expected ')', found 'go' (and 1 more errors)
```

### 55. `cvdp_copilot_packet_controller_0001`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `GO_SYNTAX_ERROR`
- Subcategory: `GO_TYPE_ERROR`
- First failing stage: MyGO frontend
- CVDP TOPLEVEL: `packet_controller`
- Go function: `packet_controller`
- Verilog module: ``

Meaning:

Go ??????????????/????/????????

Why this category:

??????? main.go??? LLM ?? Go ?????????? MyGO ??? CVDP?

Key log excerpt:

```text
error: <RUN_DIR>/logs/cvdp_copilot_packet_controller_0001/extracted_go/main.go:110:20: 0xAB + 0xCD (untyped int constant 376) overflows uint8
```

### 61. `cvdp_copilot_prbs_gen_0003`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `GO_SYNTAX_ERROR`
- Subcategory: `GO_TYPE_ERROR`
- First failing stage: MyGO frontend
- CVDP TOPLEVEL: `cvdp_prbs_gen`
- Go function: `cvdp_prbs_gen`
- Verilog module: ``

Meaning:

Go ??????????????/????/????????

Why this category:

??????? main.go??? LLM ?? Go ?????????? MyGO ??? CVDP?

Key log excerpt:

```text
error: <RUN_DIR>/logs/cvdp_copilot_prbs_gen_0003/extracted_go/main.go:44:31: invalid operation: inBit ^ expected (mismatched types uint16 and uint32)
expected (mismatched types uint16 and uint32)
```

### 69. `cvdp_copilot_sorter_0001`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `GO_SYNTAX_ERROR`
- Subcategory: `GO_TYPE_ERROR`
- First failing stage: MyGO frontend
- CVDP TOPLEVEL: `sorting_engine`
- Go function: `sorting_engine`
- Verilog module: ``

Meaning:

Go ??????????????/????/????????

Why this category:

??????? main.go??? LLM ?? Go ?????????? MyGO ??? CVDP?

Key log excerpt:

```text
error: <RUN_DIR>/logs/cvdp_copilot_sorter_0001/extracted_go/main.go:44:6: invalid operation: arr_reg &= clearMaskA (mismatched types uint64 and int)
error: <RUN_DIR>/logs/cvdp_copilot_sorter_0001/extracted_go/main.go:45:6: invalid operation: arr_reg &= clearMaskB (mismatched types uint64 and int)
```

### 26. `cvdp_copilot_configurable_digital_low_pass_filter_0004`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `MYGO_CIRCT_BACKEND_ERROR`
- Subcategory: `CIRCT_SSA_OR_TYPE_ERROR`
- First failing stage: MyGO CIRCT backend
- CVDP TOPLEVEL: `advanced_decimator_with_adaptive_peak_detection`
- Go function: `advanced_decimator_with_adaptive_peak_detection`
- Verilog module: ``

Meaning:

CIRCT ???? SSA ????SSA ?????? SSA ???????? MyGO ??? CIRCT/MLIR ??????

Why this category:

????? circt-opt/firtool ????????? Verilog??? CVDP harness ??????

Key log excerpt:

```text
<RUN_DIR>/logs/cvdp_copilot_configurable_digital_low_pass_filter_0004/extracted_go/.mygo-tmp/.mygo-circt-882420740/design.mlir:820:113: error: use of value '%t52_127' expects different type than prior uses: 'i16' vs '!hw.inout<i16>'
backend: circt-opt --pass-pipeline failed: exit status 1
```

### 40. `cvdp_copilot_fifo_async_0001`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `MYGO_CIRCT_BACKEND_ERROR`
- Subcategory: `CIRCT_SSA_OR_TYPE_ERROR`
- First failing stage: MyGO CIRCT backend
- CVDP TOPLEVEL: `fifo_async`
- Go function: `binToGray`
- Verilog module: ``

Meaning:

CIRCT ???? SSA ????SSA ?????? SSA ???????? MyGO ??? CIRCT/MLIR ??????

Why this category:

????? circt-opt/firtool ????????? Verilog??? CVDP harness ??????

Key log excerpt:

```text
<RUN_DIR>/logs/cvdp_copilot_fifo_async_0001/extracted_go/.mygo-tmp/.mygo-circt-2603216313/design.mlir:431:38: error: use of undeclared SSA value name
backend: circt-opt --pass-pipeline failed: exit status 1
```

### 48. `cvdp_copilot_hill_cipher_0001`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `MYGO_CIRCT_BACKEND_ERROR`
- Subcategory: `CIRCT_SSA_OR_TYPE_ERROR`
- First failing stage: MyGO CIRCT backend
- CVDP TOPLEVEL: `hill_cipher`
- Go function: `hill_cipher`
- Verilog module: ``

Meaning:

CIRCT ???? SSA ????SSA ?????? SSA ???????? MyGO ??? CIRCT/MLIR ??????

Why this category:

????? circt-opt/firtool ????????? Verilog??? CVDP harness ??????

Key log excerpt:

```text
<RUN_DIR>/logs/cvdp_copilot_hill_cipher_0001/extracted_go/.mygo-tmp/.mygo-circt-1019206835/design.mlir:573:5: error: redefinition of SSA value '%c0'
backend: circt-opt --pass-pipeline failed: exit status 1
```

### 15. `cvdp_copilot_bcd_counter_0001`

- Status: `FAIL`
- Reviewed category: `FUNCTIONAL_FAIL`
- Subcategory: `ASSERTION_VALUE_MISMATCH`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `bcd_counter`
- Go function: `bcd_counter`
- Verilog module: `bcd_counter`

Meaning:

RTL ??????????CVDP ????????????????

Why this category:

??/?????????????????????????????????????

Key log excerpt:

```text
AssertionError: Counter incorrect for hours after reset
assert int(dut.ms_hr) == 0 and int(dut.ls_hr) == 0, "24-hour reset failed"
assert int(dut.ms_min) == 0 and int(dut.ls_min) == 0, "24-hour reset failed"
assert int(dut.ms_sec) == 0 and int(dut.ls_sec) == 0, "24-hour reset failed"
assert int(dut.ms_hr) == 1 and int(dut.ls_hr) == 0, "Counter incorrect for hours after reset"
assert (0 == 1)
Failed 1 of 1 tests
```

### 47. `cvdp_copilot_hebbian_rule_0017`

- Status: `FAIL`
- Reviewed category: `FUNCTIONAL_FAIL`
- Subcategory: `ASSERTION_VALUE_MISMATCH`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `hebb_gates`
- Go function: `computeTarget`
- Verilog module: `hebb_gates`

Meaning:

RTL ??????????CVDP ????????????????

Why this category:

??/?????????????????????????????????????

Key log excerpt:

```text
AssertionError: Expected w1=1, but got 0
assert dut.w1.value.signed_integer == 2, f"Expected w1=1, but got {dut.w1.value.signed_integer}"
assert 0 == 2
Expected w1=1, but got 0
Expected w1=1, but got {dut.w1.value.signed_integer}"
Failed 1 of 1 tests
FAILED ../../harness/src/test_runner.py::test_hebb_gates - SystemExit: 1
```

### 29. `cvdp_copilot_data_bus_controller_0001`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `MYGO_IR_LOWERING_ERROR`
- Subcategory: `MALFORMED_MLIR`
- First failing stage: MyGO frontend
- CVDP TOPLEVEL: `data_bus_controller`
- Go function: `data_bus_controller`
- Verilog module: ``

Meaning:

MyGO ? Go lowering ??? MLIR ??????CIRCT ???? expected operation name in quotes?

Why this category:

Go ?????? MyGO?????? design.mlir/CIRCT ??????? CVDP???? Verilog ???

Key log excerpt:

```text
<RUN_DIR>/logs/cvdp_copilot_data_bus_controller_0001/extracted_go/.mygo-tmp/.mygo-circt-833160785/design.mlir:50:27: error: expected operation name in quotes
expected operation name in quotes
backend: circt-opt --pass-pipeline failed: exit status 1
```

### 32. `cvdp_copilot_decode_firstbit_0001`

- Status: `MODEL_OR_MYGO_ERROR`
- Reviewed category: `MYGO_IR_LOWERING_ERROR`
- Subcategory: `MALFORMED_MLIR`
- First failing stage: MyGO frontend
- CVDP TOPLEVEL: `cvdp_copilot_decode_firstbit`
- Go function: `find_first_set_16`
- Verilog module: ``

Meaning:

MyGO ? Go lowering ??? MLIR ??????CIRCT ???? expected operation name in quotes?

Why this category:

Go ?????? MyGO?????? design.mlir/CIRCT ??????? CVDP???? Verilog ???

Key log excerpt:

```text
<RUN_DIR>/logs/cvdp_copilot_decode_firstbit_0001/extracted_go/.mygo-tmp/.mygo-circt-2992803055/design.mlir:95:27: error: expected operation name in quotes
expected operation name in quotes
backend: circt-opt --pass-pipeline failed: exit status 1
```

### 41. `cvdp_copilot_filo_0005`

- Status: `FAIL`
- Reviewed category: `VERILOG_COMPILE_ERROR`
- Subcategory: `VVP_RUNTIME_ERROR`
- First failing stage: CVDP simulation/assertion
- CVDP TOPLEVEL: `FILO_RTL`
- Go function: `FILO_RTL`
- Verilog module: `FILO_RTL`

Meaning:

vvp ??????? 3???????????????/??????

Why this category:

?????????? Verilog/CVDP ???????? Go ?????

Key log excerpt:

```text
returned non-zero exit status 3
FAILED ../../harness/src/test_runner.py::test_runner - subprocess.CalledProce...
FAILED ../../harness/src/test_runner.py::test_filo[12-10] - subprocess.Called...
FAILED ../../harness/src/test_runner.py::test_filo[12-12] - subprocess.Called...
FAILED ../../harness/src/test_runner.py::test_filo[16-10] - subprocess.Called...
FAILED ../../harness/src/test_runner.py::test_filo[16-12] - subprocess.Called...
```
