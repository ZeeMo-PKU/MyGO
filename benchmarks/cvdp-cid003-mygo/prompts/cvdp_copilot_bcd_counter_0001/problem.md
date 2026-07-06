Design a System Verilog module named `bcd_counter` that implements a 24-hour clock using Binary-Coded Decimal (BCD) counters. The clock should display hours, minutes, and seconds in a 24-hour format (`00:00:00` to `23:59:59`) and reset automatically.

## Design Specifications

**Module Name**:  
`bcd_counter`

### Inputs:
- `clk`: Clock input signal for synchronizing the counters.
- `rst`: Active-high reset signal that resets all counters to `00:00:00` when asserted.

### Outputs:
- `ms_hr` (4-bit) — Most significant digit of the hour counter, representing the tens place.
- `ls_hr` (4-bit) — Least significant digit of the hour counter, representing the units place.
- `ms_min` (4-bit) — Most significant digit of the minute counter, representing the tens place.
- `ls_min` (4-bit) — Least significant digit of the minute counter, representing the units place.
- `ms_sec` (4-bit) — Most significant digit of the second counter, representing the tens place.
- `ls_sec` (4-bit) — Least significant digit of the second counter, representing the units place.

### Functional Requirements:
1. The module operates as a 24-hour clock, displaying hours in a 24-hour format from `00:00:00` to `23:59:59`.
2. When `rst` is high, all outputs (`ms_hr`, `ls_hr`, `ms_min`, `ls_min`, `ms_sec`, `ls_sec`) reset to `0`.
3. On each positive edge of `clk`, increment the seconds counter:
   - Increment `ls_sec` until it reaches 9. On reaching 9, reset `ls_sec` to `0` and increment `ms_sec`.
   - Increment `ms_sec` until it reaches 5. When `ms_sec` reaches 5 and `ls_sec` reaches 9, reset both to `0` and increment `ls_min`.
4. Apply similar logic for `ms_min`, `ls_min`, `ms_hr`, and `ls_hr`, ensuring each counter resets appropriately at its upper limit for hours, minutes, or seconds.
5. The hour counter resets to `00:00:00` after reaching `23:59:59`.

### Edge Cases:
- Ensure the counter resets exactly at 24 hours (`23:59:59` to `00:00:00`) to simulate a 24-hour clock format.
