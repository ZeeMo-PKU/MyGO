Design an **8-bit Serial In Parallel Out (SIPO) shift register** that captures one bit of serial data on each rising edge of the clock signal and shifts this data into an 8-bit parallel output register. The design specification for the **8-bit SIPO shift register** is outlined below:

## Design Specification:

A **Serial In Parallel Out (SIPO) Shift Register** is a digital circuit that accepts a serial bitstream as input and outputs the data in parallel form after a series of clock cycles. It is often used in communication systems to convert data from a serial format (bit-by-bit) into a parallel format (multiple bits at once), which is useful for interfacing with parallel buses, memory systems, or storing data in registers.

### Module Name:
`serial_in_parallel_out_8bit`

### Edge Cases:
- **Initial State**: The initial content of the `parallel_out` register can be all x (unknown logic level), assuming no serial data has been shifted in yet. The system should handle this cleanly and shift in new data from the serial input as soon as clock pulses are received.
- **Continuous Data Stream**: After the initial 8 clock cycles, new data from the serial input will continue to overwrite the oldest bits in the `parallel_out` register. The most significant bit (MSB) will be shifted out, and new data will shift in from the LSB.

### Example Operations:

#### Example 1: Serial Input Sequence (First 8 Bits)
- **Serial Input Sequence**: `1, 0, 1, 1, 0, 0, 1, 0`
- **Initial `parallel_out`**: `00000000`
- **Clock Cycles**:
  - After the first clock cycle: `parallel_out = 8'b00000001` (serial_in = 1)
  - After the second clock cycle: `parallel_out = 8'b00000010` (serial_in = 0)
  - After the third clock cycle: `parallel_out = 8'b00000101` (serial_in = 1)
  - After the fourth clock cycle: `parallel_out = 8'b00001011` (serial_in = 1)
  - After the fifth clock cycle: `parallel_out = 8'b00010110` (serial_in = 0)
  - After the sixth clock cycle: `parallel_out = 8'b00101100` (serial_in = 0)
  - After the seventh clock cycle: `parallel_out = 8'b01011001` (serial_in = 1)
  - After the eighth clock cycle: `parallel_out = 8'b10110010` (serial_in = 0)

At the end of this 8-bit sequence, the `parallel_out` register will hold the value `10110010`.