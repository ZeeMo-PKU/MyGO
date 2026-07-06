package main

// State encoding (3-bit): S0=0 ... S7=7
var state uint8 = 0
var out_seq_detected bool
var prev_clk bool

func fsm_seq_detector(clk_in bool, rst_in bool, seq_in bool) {
    // Asynchronous active-high reset
    if rst_in {
        state = 0
        out_seq_detected = false
        prev_clk = clk_in
        return
    }

    // Detect rising edge of clk_in
    if !prev_clk && clk_in {
        var next_state uint8
        var detected bool

        // Default keep current state, output low
        next_state = state
        detected = false

        // Next state and output combinational logic
        switch state {
        case 0: // S0
            if seq_in {
                next_state = 1 // S1
            } else {
                next_state = 0 // S0
            }
        case 1: // S1 (matched '1')
            if seq_in {
                next_state = 1 // stay S1 (overlapping)
            } else {
                next_state = 2 // S2 (matched "10")
            }
        case 2: // S2 (matched "10")
            if seq_in {
                next_state = 3 // S3 ("101")
            } else {
                next_state = 0 // back to S0
            }
        case 3: // S3 (matched "101")
            if seq_in {
                next_state = 4 // S4 ("1011")
            } else {
                next_state = 2 // S2 ("10")
            }
        case 4: // S4 (matched "1011")
            if seq_in {
                next_state = 1 // S1 (overlapping '1')
            } else {
                next_state = 5 // S5 ("10110")
            }
        case 5: // S5 (matched "10110")
            if seq_in {
                next_state = 3 // S3 ("101")
            } else {
                next_state = 6 // S6 ("101100")
            }
        case 6: // S6 (matched "101100")
            if seq_in {
                next_state = 1 // S1
            } else {
                next_state = 7 // S7 ("1011000")
            }
        case 7: // S7 (matched "1011000")
            if seq_in {
                next_state = 1 // overlapping start after full sequence
                detected = true
            } else {
                next_state = 0
                detected = false
            }
        default:
            next_state = 0
        }

        // Update state and registered output on rising edge
        state = next_state
        out_seq_detected = detected
    }

    // Store current clk_in to detect next rising edge
    prev_clk = clk_in
}

func main() {}
