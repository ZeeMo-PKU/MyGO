package main

const BINARY_WIDTH = 5
const OUTPUT_WIDTH = 32

var out_o_one_hot_out uint32  // output
var one_hot_reg uint32        // internal register
var prev_clk bool             // for rising-edge detection

func binary_to_one_hot_decoder_sequential(i_binary_in uint8, i_clk bool, i_rstb bool) {
	// Asynchronous active-low reset
	if !i_rstb {
		one_hot_reg = 0
		out_o_one_hot_out = 0
		prev_clk = i_clk
		return
	}

	// Rising edge of clock
	if i_clk && !prev_clk {
		bin := i_binary_in & ((1 << BINARY_WIDTH) - 1)
		one_hot_reg = 1 << bin
	}

	// Output always follows the register
	out_o_one_hot_out = one_hot_reg

	// Update clock history
	prev_clk = i_clk
}

func main() {}
