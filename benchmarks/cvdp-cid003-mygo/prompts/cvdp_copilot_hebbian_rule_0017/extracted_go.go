package main

// Outputs
var out_w1, out_w2, out_bias uint8
var out_present_state, out_next_state uint8

// Internal registers
var present_state uint8
var iteration_counter uint8 // 2-bit: 0..3
var x1, x2 uint8           // captured inputs (4-bit signed)
var target uint8           // gate target (4-bit signed)
var w1, w2, bias uint8     // weight and bias registers (4-bit signed, clk-driven)
var old_clk bool

// computeTarget returns the target for the given gate selection (0=AND,1=OR,2=NAND,3=NOR)
// x1, x2 are expected to be bipolar (1 or -1 as 0xF). Returns 1 for true, 0xF (-1) for false.
func computeTarget(x1Val, x2Val, gate uint8) uint8 {
	x1True := x1Val == 1
	x2True := x2Val == 1
	andResult := x1True && x2True
	orResult := x1True || x2True

	var result bool
	switch gate & 0x3 {
	case 0: // AND
		result = andResult
	case 1: // OR
		result = orResult
	case 2: // NAND
		result = !andResult
	case 3: // NOR
		result = !orResult
	default:
		result = false
	}
	if result {
		return 1
	}
	return 0xF // -1 in 4-bit two's complement
}

// hebb_gates implements the Hebbian learning FSM
func hebb_gates(clk bool, rst bool, start bool, a uint8, b uint8, gate_select uint8) {
	// Combinational next‑state logic
	var next_state uint8
	switch present_state {
	case 0: // IDLE
		if start {
			next_state = 1 // CAPTURE
		} else {
			next_state = 0
		}
	case 1: // CAPTURE
		next_state = 2 // TARGET_ASSIGN
	case 2: // TARGET_ASSIGN
		next_state = 3
	case 3:
		next_state = 4
	case 4:
		next_state = 5
	case 5:
		next_state = 6
	case 6:
		next_state = 7 // COMPUTE_DELTA (abstract)
	case 7:
		next_state = 8 // UPDATE_WEIGHTS
	case 8:
		next_state = 9 // LOOP_CHECK
	case 9: // LOOP_CHECK
		if iteration_counter < 3 {
			next_state = 1 // next input pair
		} else {
			next_state = 10 // RETURN_IDLE
		}
	case 10: // RETURN_IDLE
		next_state = 0
	default:
		next_state = 0
	}

	// Assign outputs from registers / combinational
	out_w1 = w1
	out_w2 = w2
	out_bias = bias
	out_present_state = present_state
	out_next_state = next_state

	// Asynchronous active‑low reset
	if !rst {
		present_state = 0
		iteration_counter = 0
		x1 = 0
		x2 = 0
		target = 0
		w1 = 0
		w2 = 0
		bias = 0
		old_clk = clk // prevent false posedge after reset
		return
	}

	// Rising‑edge detection
	posedge := clk && !old_clk
	old_clk = clk

	if posedge {
		// Capture inputs during CAPTURE state (state 1)
		if present_state == 1 {
			x1 = a & 0xF
			x2 = b & 0xF
		}

		// Compute gate target during TARGET_ASSIGN state (state 2)
		if present_state == 2 {
			target = computeTarget(x1, x2, gate_select)
		}

		// Update weights and bias during UPDATE_WEIGHTS state (state 8)
		if present_state == 8 {
			// delta_w1 = x1 * target  →  +1 if equal, -1 otherwise
			if x1 == target {
				w1 = (w1 + 1) & 0xF
			} else {
				w1 = (w1 - 1) & 0xF
			}
			// delta_w2
			if x2 == target {
				w2 = (w2 + 1) & 0xF
			} else {
				w2 = (w2 - 1) & 0xF
			}
			// delta_bias = target
			if target == 1 {
				bias = (bias + 1) & 0xF
			} else {
				bias = (bias - 1) & 0xF
			}
		}

		// Increment iteration counter when leaving LOOP_CHECK back to CAPTURE
		if present_state == 9 && next_state == 1 {
			iteration_counter = (iteration_counter + 1) & 0x3 // 2‑bit counter
		}

		// State update
		present_state = next_state
	}
}

func main() {}
