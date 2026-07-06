package main

var state uint8 = 0
var a_ff uint8 = 0
var b_ff uint8 = 0
var out_OUT uint8 = 0
var out_done bool = false
var prev_clk bool = false

// gcd_top computes the GCD of two unsigned integers A and B using the Euclidean algorithm.
// It implements a combined control path / datapath Finite State Machine (FSM).
func gcd_top(clk bool, rst bool, A uint8, B uint8, go bool) {
	rising := clk && !prev_clk
	prev_clk = clk
	if !rising {
		return
	}

	var nxt_state uint8
	var nxt_a, nxt_b, nxt_OUT uint8
	var nxt_done bool

	if rst {
		// Synchronous reset: clear all registers and outputs
		nxt_state = 0
		nxt_a = 0
		nxt_b = 0
		nxt_OUT = 0
		nxt_done = false
	} else {
		// Default: keep current values
		nxt_state = state
		nxt_a = a_ff
		nxt_b = b_ff
		nxt_OUT = out_OUT
		nxt_done = out_done

		switch state {
		case 0: // S0: IDLE
			if go {
				nxt_a = A
				nxt_b = B
				if A == B {
					nxt_state = 1
					nxt_done = true
					nxt_OUT = A
				} else if A > B {
					nxt_state = 2
				} else {
					nxt_state = 3
				}
			}
		case 1: // S1: DONE
			nxt_state = 0
			nxt_done = false
		case 2: // S2: A > B, subtract B from A
			tmp := a_ff - b_ff
			nxt_a = tmp
			nxt_b = b_ff
			if tmp == b_ff {
				nxt_state = 1
				nxt_done = true
				nxt_OUT = tmp
			} else if tmp > b_ff {
				nxt_state = 2
			} else {
				nxt_state = 3
			}
		case 3: // S3: B > A, subtract A from B
			tmp := b_ff - a_ff
			nxt_b = tmp
			nxt_a = a_ff
			if a_ff == tmp {
				nxt_state = 1
				nxt_done = true
				nxt_OUT = a_ff
			} else if a_ff > tmp {
				nxt_state = 2
			} else {
				nxt_state = 3
			}
		default:
			nxt_state = 0
			nxt_a = 0
			nxt_b = 0
			nxt_OUT = 0
			nxt_done = false
		}
	}

	state = nxt_state
	a_ff = nxt_a
	b_ff = nxt_b
	out_OUT = nxt_OUT
	out_done = nxt_done
}

func main() {}
