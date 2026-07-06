Could you please implement a clock divider RTL module using SystemVerilog that divides an input clock by a factor of 2,4 or 8? The module `clock_divider` should take an input clock (`clk`) and generate an output clock (`clk_out`) with a reduced frequency based on a selection input (`sel`).

### Requirements:

**Inputs:**
- `clk`: The primary clock input that needs to be divided.  The module operates on the rising edge of this clock .
- `rst_n`: An active-low asynchronous reset signal. 
- `[1:0] sel`: A 2-bit signal that determines the clock division factor, determining whether the input clock will be divided by 2, 4, or 8.

**Output:**
- `clk_out`: The divided clock signal output.

### Functionality:
1. **Clock Division:**
- The output clock frequency should change based on the `sel` input:
  - `sel = 2'b00`: Divide by 2.
  - `sel = 2'b01`: Divide by 4.
  - `sel = 2'b10`: Divide by 8.

2. **Reset Behavior:**
- When `rst_n` is asserted,`clk_out` should be zero.
- After `rst_n` is de-asserted, the design will output the divided clock based on the `sel`.

3. **Edge Cases**:
- **Out-of-range `sel`**: If `sel` takes any value other than `2'b00`, `2'b01`, or `2'b10`, the output `clk_out` should be held at 0 until a valid `sel` is applied.

4. **Assumptions on `sel`:**
- The `sel` signal is expected to remain stable during normal operation. Assume that the `sel` value is always provided synchronized with reset (`rst_n`).