Design RTL for generating 8-bit data continuously in an incremental manner through a Parallel In Serial Out (PISO) shift register. This module has to generate 1-bit during every clock cycle and to complete the generation of a new 8-bit value at the end of every 8 clock cycles. Could you ensure the patterns are generated in MSB to LSB order? For example, the first 8-bit pattern generated will be 8'b0000_0001, in which the first clock has to create '0' and the eighth clock will produce '1' as output. The pattern generation has to be controlled by a clock and asynchronous active LOW reset. The RTL module `piso_8bit` must have the following design consideration and interface.

## Design considerations
- One-bit serial data has to be generated during every clock cycle based on the value of 8-bit internal register `tmp`
- The value of `tmp` has to be initialized to a value 0000_0001 when the reset is at active LOW and it gets incremented by 1 after every eight clock cycles when the reset is at HIGH
- When all the eight bits of `tmp` value 1111_1111 have been transmitted, it gets incremented by 1 to have a value of 0000_0000 and the shifting process continues

## Interface

### Inputs:
•	`clk (1-bit)` : This is a single-bit input clock. It is required for the operation of a shift register as the data movement is controlled at the positive edge of this clock. The clock normally operates at a 50:50 duty cycle. 
•	`rst (1-bit)`: This input is a control signal that resets the internal register value to zero and the shift register operation. This is an asynchronous active LOW reset, which when maintaining active LOW, keeps the `serial_out` data at logic LOW.

### Output:
•	`serial_out (1-bit)`: This signal represents the output of the PISO shift register. When the reset is at logic HIGH, a new value is asserted at this output during every positive edge of the clock cycle. The value at `serial_out` is controlled by the contents of the internal 8-bit register which keeps changing every 8th clock cycle. 
