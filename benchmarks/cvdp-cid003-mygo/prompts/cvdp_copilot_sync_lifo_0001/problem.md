Design a System Verilog module that implements a **synchronous LIFO (Last-In, First-Out)** memory with configurable data width and depth. The design allows data to be written to and read from the LIFO structure based on specific control signals. 

### Interface of the Module `sync_lifo`
2. **Parameter Definitions**:
   - `DATA_WIDTH` (default = 8): Specifies the bit-width of the data to be stored in the LIFO.
   - `ADDR_WIDTH` (default = 3): Specifies the number of address bits, determining the depth of the LIFO. The depth is ( 2^{ADDR_WIDTH} ). 
   
3. **Input Ports**:
   - `clock` (1 bit): Clock signal. All operations are synchronized with the rising edge of the clock.
   - `reset` (1 bit): Synchronous reset, active high.
   - `write_en` (1 bit): Write enable signal. When asserted high, new data is written into the LIFO if it is not full.
   - `read_en` (1 bit): Read enable signal. When asserted high, data is read from the LIFO if it is not empty.
   - `data_in` (DATA_WIDTH bits): The data input that will be written to the LIFO when `write_en` is active.

4. **Output Ports**:
   - `empty` (1 bit): High when the LIFO is empty, indicating no data is available to be read.
   - `full` (1 bit): High when the LIFO is full, indicating no more data can be written.
   - `data_out` (DATA_WIDTH bits): The output data that is read from the LIFO when `read_en` is active.

### Specifications:

1. **Write Operation**: 
	- On the rising edge of the clock, if `write_en` is high and the LIFO is not full, the `data_in` is written to the memory array. 
	
2. **Read Operation**: 
	- On the rising edge of the clock, if `read_en` is high and the LIFO is not empty, the data from the top of the LIFO (the last written value) should be read and output through `data_out`. 
	
3. **Reset Behavior**:
   	-  When reset is asserted (active high), the output clears to zero. The memory should also be cleared at reset and after reset is de-asserted, the LIFO write operation should start fresh.

 4. **Edge Cases**:
   	-  Overflow: If write_en is asserted while the LIFO is full, no new data will be written, and the contents and pointer remain unchanged.
   	-  Underflow: If read_en is asserted while the LIFO is empty, data_out will hold its previous value, and the LIFO pointer and memory remain unchanged.
### Assumptions:
-    Assume that the input data is bounded within DATA_WIDTH bits
	