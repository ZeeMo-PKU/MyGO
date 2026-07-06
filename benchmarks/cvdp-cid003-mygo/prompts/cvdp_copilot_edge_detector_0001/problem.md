Design a System Verilog module named "`sync_pos_neg_edge_detector` that detects both positive and negative edges on a glitch-free and debounced input signal. The module should output a signal indicating the detection of a positive or negative edge. Each detection signal should be asserted for **one clock cycle** when an edge is detected. The module should also incorporate asynchronous reset functionality.

## Input/Output Specifications

### Inputs:
- `i_clk`: Clock signal (active on rising edge).
- `i_rstb`: Asynchronous reset signal (active low).
- `i_detection_signal`: Glitch-free, debounced signal whose edges are to be detected.

### Outputs:
- `o_positive_edge_detected`: Asserted for one clock cycle when a positive edge is detected on `i_detection_signal`.
- `o_negative_edge_detected`: Asserted for one clock cycle when a negative edge is detected on `i_detection_signal`.

## Behavioral Definition
- When the module detects a **positive edge** (rising transition) on `i_detection_signal`, the output `o_positive_edge_detected` should be asserted high for **one clock cycle**.
- When the module detects a **negative edge** (falling transition) on `i_detection_signal`, the output `o_negative_edge_detected` should be asserted high for **one clock cycle**.
- The design assumes that `i_detection_signal` is **glitch-free and debounced**, so no additional debouncing logic is required.

## Reset Behavior
- When the asynchronous reset (`i_rstb`) is active (low), all outputs (`o_positive_edge_detected` and `o_negative_edge_detected`) should be reset to `0`, and internal state should be cleared.
- When the reset is de-asserted, normal edge detection should resume.