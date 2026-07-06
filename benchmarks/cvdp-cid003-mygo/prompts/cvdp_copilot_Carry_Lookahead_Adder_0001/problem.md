Design a **Generate/Propagate (GP) module** in Verilog .v format for use in a **carry lookahead adder** design.The **Generate/Propagate (GP)** module is an essential part of the **carry lookahead adder** (CLA) architecture, which is designed to speed up the process of adding binary numbers by precomputing the carry signals in parallel. 


## Interface

### Outputs:
- **generate** signal (`o_generate`) : 1-bit signal, true if both `i_A` and `i_B` are 1 (indicates carry generation).
- **propagate** signal (`o_propagate`) : 1-bit signal, true if either `i_A` or `i_B` is 1 (indicates carry propagation).
- **carry-out** signal (`o_Cout `) : 1-bit carry-out signal, computed using the generate, propagate, and carry-in signals.

### Inputs:
- **i_A** : 1-bit input signal representing one operand bit.
- **i_B** : 1-bit input signal representing the other operand bit.
- **i_Cin** : 1-bit carry-in signal from the previous stage.


## Truth Table:
| i_A   | i_B   | i_Cin| o_generate | o_propagate | o_Cout (carry-out) |
| --- | --- | --- | ------------ | ------------- | ---------------- |
|  0  |  0  |  0  |      0       |       0       |        0         |
|  0  |  0  |  1  |      0       |       0       |        0         |
|  0  |  1  |  0  |      0       |       1       |        0         |
|  0  |  1  |  1  |      0       |       1       |        1         |
|  1  |  0  |  0  |      0       |       1       |        0         |
|  1  |  0  |  1  |      0       |       1       |        1         |
|  1  |  1  |  0  |      1       |       1       |        1         |
|  1  |  1  |  1  |      1       |       1       |        1         |