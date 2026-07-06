package main

const (
	DATA_WIDTH = 8
	FILO_DEPTH = 16
)

var (
	out_data_out uint8
	out_full     bool
	out_empty    bool

	mem     [FILO_DEPTH]uint8
	top     uint8
	prevClk bool
)

func FILO_RTL(clk bool, reset bool, push bool, pop bool, data_in uint8) {
	if reset {
		// Asynchronous active-HIGH reset
		out_empty = true
		out_full = false
		out_data_out = 0
		top = 0
	} else if clk && !prevClk {
		// Rising edge of clk
		if out_empty && push && pop {
			// Feedthrough: pass data_in directly to output, keep empty state
			out_data_out = data_in
			// out_empty and out_full remain unchanged (true and false)
		} else {
			// Handle pop operation
			if pop && !out_empty {
				top--
				out_data_out = mem[top]
				out_full = false
				if top == 0 {
					out_empty = true
				} else {
					out_empty = false
				}
			}
			// Handle push operation
			if push && !out_full {
				mem[top] = data_in
				top++
				out_empty = false
				if top == FILO_DEPTH {
					out_full = true
				} else {
					out_full = false
				}
			}
		}
	}
	prevClk = clk
}

func main() {}
