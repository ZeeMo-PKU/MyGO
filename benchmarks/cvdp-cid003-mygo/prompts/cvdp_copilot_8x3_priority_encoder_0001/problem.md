Design and implement an 8x3 priority encoder using Verilog. The priority encoder should take 8-bit input signal and output a 3-bit binary code representing the position of the highest-priority active input. The encoder should follow the priority order from the highest bit (bit 7) to the lowest bit (bit 0).

**Specifications for module `priority_encoder_8x3 ` :**

- Inputs:
    - [7:0] in: An 8-bit input vector. The priority of the inputs decreases from bit 7 to bit 0.

- Output:
    - [2:0] out: A 3-bit output vector that represents the binary code corresponding to the highest-priority active input.

**Priority Rules:**

- The priority encoder should output the binary index of the highest active input line.
    - For example, if in[7] is high, the output should be 3'b111 regardless of the state of the lower-priority bits.
    - If none of the input lines are active (in is all zeros), the output should default to 3'b000.

**Additional Details:**

- Ensure that the output is updated immediately whenever there is a change in the input.