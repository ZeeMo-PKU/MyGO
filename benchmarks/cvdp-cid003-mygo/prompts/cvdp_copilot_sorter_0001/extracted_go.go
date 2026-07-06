package main

const N = 8
const WIDTH = 8
const MASK = (1 << WIDTH) - 1

var out_done bool
var out_data uint64

var prev_clk bool
var state uint8 // 0 = IDLE, 1 = SORTING, 2 = DONE
var step uint8
var arr_reg uint64

func sorting_engine(clk bool, rst bool, start bool, in_data uint64) {
	out_done = false
	if rst {
		state = 0
		step = 0
		prev_clk = clk
		return
	}
	if clk && !prev_clk {
		next_state := state
		switch state {
		case 0: // IDLE
			if start {
				next_state = 1 // SORTING
				arr_reg = in_data
				step = 0
			}
		case 1: // SORTING
			if N == 1 {
				next_state = 2 // DONE
			} else {
				j := step % (N - 1)
				shiftA := uint(j) * WIDTH
				shiftB := uint(j+1) * WIDTH
				a := (arr_reg >> shiftA) & MASK
				b := (arr_reg >> shiftB) & MASK
				if a > b {
					clearMaskA := ^(MASK << shiftA)
					clearMaskB := ^(MASK << shiftB)
					arr_reg &= clearMaskA
					arr_reg &= clearMaskB
					arr_reg |= (b << shiftA) | (a << shiftB)
				}
				step++
				if step == uint8(N*(N-1)) {
					next_state = 2 // DONE
				}
			}
		case 2: // DONE
			out_done = true
			out_data = arr_reg
			next_state = 0 // back to IDLE
		}
		state = next_state
	}
	prev_clk = clk
}

func main() {}
