package main

// Constants for FSM states
const (
	IDLE    = 0
	COMPUTE = 1
	DONE    = 2
)

// Global registers (state and outputs)
var (
	state      uint8 = IDLE
	result1Reg int32
	result2Reg int32
	doneReg    bool
	prevClk    bool
)

// Output ports
var (
	out_result1 int32
	out_result2 int32
	out_done    bool
)

// fsm_linear_reg implements the top-level module.
// Inputs: clk (1-bit), reset (async, active high), start, x_in, w_in, b_in (signed DATA_WIDTH).
func fsm_linear_reg(clk bool, reset bool, start bool, x_in int16, w_in int16, b_in int16) {
	// Asynchronous reset
	if reset {
		state = IDLE
		result1Reg = 0
		result2Reg = 0
		doneReg = false
		prevClk = clk
		// Force outputs to zero
		out_result1 = 0
		out_result2 = 0
		out_done = false
		return
	}

	// Rising‑edge detection
	posEdge := clk && !prevClk
	if posEdge {
		// Next state and next register values
		var nextState uint8
		var nextResult1 int32
		var nextResult2 int32
		var nextDone bool

		switch state {
		case IDLE:
			if start {
				nextState = COMPUTE
			} else {
				nextState = IDLE
			}
			nextResult1 = 0
			nextResult2 = 0
			nextDone = false

		case COMPUTE:
			nextState = DONE
			// result1 = w_in * x_in >>> 1  (arithmetic right shift)
			nextResult1 = (int32(w_in) * int32(x_in)) >> 1
			// result2 = b_in + (x_in >>> 2)
			nextResult2 = int32(b_in) + (int32(x_in) >> 2)
			nextDone = false

		case DONE:
			nextState = IDLE
			nextResult1 = result1Reg
			nextResult2 = result2Reg
			nextDone = true

		default:
			nextState = IDLE
			nextResult1 = 0
			nextResult2 = 0
			nextDone = false
		}

		// Update sequential registers
		state = nextState
		result1Reg = nextResult1
		result2Reg = nextResult2
		doneReg = nextDone
	}

	// Continuous assignments (registered outputs)
	out_result1 = result1Reg
	out_result2 = result2Reg
	out_done = doneReg

	// Update previous clock value for edge detection
	prevClk = clk
}

func main() {}
