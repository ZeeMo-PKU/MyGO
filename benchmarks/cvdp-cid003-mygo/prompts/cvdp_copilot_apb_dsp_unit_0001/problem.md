Design a **`apb_dsp_unit`** module in Verilog that serves as an APB interface for configuring internal registers. These registers specify which memory addresses are used for arithmetic operations (addition or multiplication). The computed result is then made available through a designated register.

---

## Register Descriptions

1. **`r_operand_1`**  
   - **Address:** 0x0  
   - **Function:** Holds the memory address of the first operand.

2. **`r_operand_2`**  
   - **Address:** 0x1  
   - **Function:** Holds the memory address of the second operand.

3. **`r_Enable`**  
   - **Address:** 0x2  
   - **Values:**  
     - `0`: DSP disabled  
     - `1`: Addition mode  
     - `2`: Multiplication mode  
     - `3`: Data Writing mode  

4. **`r_write_address`**  
   - **Address:** 0x3  
   - **Function:** Specifies the address in memory where data will be written.  
   - **Default Value:** 0x00000000  
   - **Usage:** If `r_Enable` = 3, the data in the `r_write_data` register is written to the address specified by this register.

5. **`r_write_data`**  
   - **Address:** 0x4  
   - **Function:** Specifies the data to be written into memory.  
   - **Default Value:** 0x00000000  
   - **Usage:** If `r_Enable` = 3, the data in this register is written to the address specified by `r_write_address`.

---

## APB Interface: 
### Clock & Reset Signals
- `pclk`: APB clock input for synchronous operations.  
- `presetn`: Active-low asynchronous reset signal for system initialization.

### APB Signals
- `paddr` (input, 10 bits): Address bus for accessing internal CSR registers and Memory.  
- `pselx` (input): APB select signal, indicating CSR and Memory selection.  
- `penable` (input): APB enable signal, marking transaction progression.  
- `pwrite` (input): Write-enable signal, distinguishing read from write operations, high for write and low for read operation.
- `pwdata` (input, 8 bits): Write data bus for sending data to CSR registers and Memory.  
- `pready` (output, reg): Ready signal, indicating the completion of a transaction.  
- `prdata` (output, reg, 8 bits): Read data bus for retrieving data.  
- `pslverr` (output, reg): Error signal for invalid addresses or unsupported operations.

## SRAM Interface:
- `sram_valid`: At positive edge of this signal, data in `r_write_data` is latched to address in `r_write_address`.

---

## APB Protocol

1. **Read Operations**  
   - In the **READ_STATE**, drive `prdata` with the register value corresponding to `paddr`.
   - After operation, return to **IDLE**.

2. **Write Operations**  
   - In the **WRITE_STATE**, update the register selected by `paddr` with `pwdata`.  
   - After updating the register, return to **IDLE**.

3. **Reset Behavior**  
   - When `presetn` is deasserted (active-low), reset all outputs and internal registers to their default values:
     - Set `pready` and `pslverr` to 0.  
     - Clear `prdata`.  
     - Initialize `r_operand_1`, `r_operand_2`, `r_Enable`, `r_write_address`, and `r_write_data` to 0.

---

## Functional Behavior

1. **APB Interface Control**  
   - Memory is accessed via the APB interface.  
   - The operational mode is controlled by **`r_Enable`**:
     - **Default (0x0):** DSP is disabled.  
     - **Write Mode (0x3):** Data can be written to memory.  
     - **Addition Mode (0x1):** Values at the addresses specified by **`r_operand_1`** and **`r_operand_2`** are added. The result is stored at address **0x5**.  
     - **Multiplication Mode (0x2):** Values at the addresses specified by **`r_operand_1`** and **`r_operand_2`** are multiplied. The result is stored at address **0x5**.  
   - To read computed data directly via APB, use address **0x5** and retrieve it through **`PRDATA`**.

2. **Error Handling**  
   - If a read or write operation is attempted on an address outside the defined registers, **`PSLVERR`** is driven high (`1'b1`).

3. **Wait States**  
   - This design does not support wait states. All APB read/write operations complete in two clock cycles, with **`PREADY`** always driven high (`1'b1`).

4. **Memory Interface**  
   - A 1 KB SRAM module serves as the memory.

**Note:** Addresses from **0x00** to **0x05** are reserved for configuration registers.