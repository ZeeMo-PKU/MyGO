Design a circuit in SystemVerilog which takes an input stream 'bit_stream' at every clock cycle and assert an output  'palindrome_detetcted' when there is found palindrome in incoming stream. The length of the palindrome should be 3. Your design should be fully synthesizable.
## Port list:
### Parameter:
- N: Determines the width of the Palindrome. For this particular circuit as we are detecting 3bit palindrome so its value should be 3

### Inputs:
- clk: Clock signal used to synchronize all operations with the rising edge of the clock.
- reset: Synchronous reset, active High.
- bit_stream: A single bit input signal which provided a randomized bit stream at every clock cycle.

### Output:
- palindrome_detected: An output signals which indicates whether the Palindrome is detected in incoming bit stream or not.

## Module Definition:
```verilog
module palindrome_detect #( 
parameter N=3
) (
input clk,
input reset,
input bit_stream,
output palindrome_detected
);
//Your Code
endmodule
```