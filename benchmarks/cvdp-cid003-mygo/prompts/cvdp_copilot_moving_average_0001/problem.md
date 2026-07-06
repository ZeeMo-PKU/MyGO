Design a Verilog module that computes the **moving average** of an incoming **12-bit data stream**. The module should output the integer average of the last 8 input unsigned value samples. It continuously receives 12-bit input samples, stores them in a memory buffer, and outputs the average of the most recent 8 samples, updated on every clock cycle.

## Interface of the Module `moving_average`

### Inputs:
- **clk**: Clock signal.All operations are synchronized with the rising edge of the clock.
- **reset**: Synchronous reset, active high.
- **[11 : 0] data_in**: 12-bit input data.

### Output:
- **[11 : 0]  data_out**: 12-bit output representing the moving average of the last 8 input samples.

## Specifications:
1. **Sum Calculation**:
   - The internal sum register must have a sufficient bit-width to handle the full range of summed values. 

2. **Reset Behavior**:
   - When `reset` is asserted (active high), the output clears to zero. The memory buffer should also be cleared at reset and after reset is de-asserted, the moving average calculation should start fresh.
 
3. **Edge Conditions**:

   - After the reset is de-asserted, if the number of input samples is less than 8 the output is the sum of the available samples divided by 8.
  
## Assumptions:
- Assume that the input data is unsigned and bounded within 12 bits
- Assume that valid input data is available to the module when reset is de-asserted and that the design receives a continuous stream of inputs synchronous with the positive edge of the clock.