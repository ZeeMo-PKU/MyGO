package main

var out_sqr_o uint32
var n uint32 = 1
var prev_clk bool

func perfect_squares_generator(clk bool, reset bool) {
	if reset {
		n = 1
		out_sqr_o = 1
	} else if clk && !prev_clk {
		next_n := n + 1
		if next_n > 65535 {
			out_sqr_o = 0xFFFFFFFF
		} else {
			out_sqr_o = next_n * next_n
			n = next_n
		}
	}
	prev_clk = clk
}

func main() {}
