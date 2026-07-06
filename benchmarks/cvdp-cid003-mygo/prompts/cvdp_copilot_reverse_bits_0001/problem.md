## Problem Description
Design a Verilog module named `reverse_bits` to reverse the bits of a 32-bit unsigned input number. The module should take a 32-bit input bus and produce a 32-bit output bus where the input bits are reversed. For example, if the input is `32'b00000000000000000000000000000001` (decimal 1), the output should be `32'b10000000000000000000000000000000`.

## Specifications

### Inputs
- **`input [31:0] num_in`**: The 32-bit unsigned number to be reversed.

### Outputs
- **`output [31:0] num_out`**: The bit-reversed 32-bit number.

## Behavioral Description
The module should process the input `num_in` such that:
- The least significant bit (LSB) of `num_in` becomes the most significant bit (MSB) of `num_out`.
- The second least significant bit of `num_in` becomes the second most significant bit of `num_out`, and so on.

### Constraints and Edge Cases
- Ensure that all input bits are reversed correctly without errors.
- Special cases to test include:
  - **All bits set to `1`**: `32'b11111111111111111111111111111111`.
  - **All bits set to `0`**: `32'b00000000000000000000000000000000`.
  - **Alternating pattern**: `32'b10101010101010101010101010101010`.
- Undefined or high-impedance inputs (`x` or `z`) are not considered valid and will not be given as input.

## Implementation Guidelines
- The module must be implemented in synthesizable Verilog.
- The solution should be combinational and free of clocked elements and resets.
- Clear comments and intuitive naming conventions should enhance readability and maintainability.