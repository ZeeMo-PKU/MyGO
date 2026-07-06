Develop a SystemVerilog module called `perfect_squares_generator` that outputs a sequence of perfect squares based on an initial reset state. This module should meet the following specifications:

### **Module Specifications**

1. **Sequential Square Generation:**
   - On each positive clock edge, the module outputs the next perfect square, beginning from 1.
   - The sequence of perfect squares is represented on the `sqr_o` output, progressing as 1, 4, 9, 16, etc., with each square calculated using incremental steps.

2. **Inputs and Outputs:**
   - **Inputs:**
     - `clk`: 1-bit clock input, active on the positive edge.
     - `reset`: 1-bit asynchronous, active-high reset input. On activation, the module resets and begins the sequence anew.
   - **Outputs:**
     - `sqr_o [31:0]`: 32-bit output for the current perfect square.

3. **Internal Operation and Edge Case Handling:**
   - The module uses an internal counter to maintain a sequence of base numbers for calculating squares. 
   - **Overflow Protection**: If `sqr_o` exceeds the 32-bit maximum (`32'hFFFFFFFF`), it saturates at this maximum value, preventing any overflow in the output.

4. **Reset Behavior:**
   - When `reset` is high, the module initializes to produce the first square (1) on the following clock edge. The sequence then continues with each positive clock edge.

### **Example Output Sequence:**
After an active-high reset, `sqr_o` will output the next perfect square on each positive clock edge:
   - After reset: `sqr_o` = 1
   - First clock cycle: `sqr_o` = 4
   - Second clock cycle: `sqr_o` = 9
   - Third clock cycle: `sqr_o` = 16