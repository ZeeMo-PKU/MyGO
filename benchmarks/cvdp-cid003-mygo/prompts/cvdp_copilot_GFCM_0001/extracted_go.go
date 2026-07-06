package main

// Output clock
var out_clkout bool

// Internal enables
var clk1_en bool = true
var clk2_en bool = false

// Previous clock values for edge detection
var prevClk1 bool
var prevClk2 bool

// glitch_free_mux is the hardware entry function.
// It switches between clk1 and clk2 glitch-free based on sel.
// When rst_n is low, clkout is forced low.
func glitch_free_mux(clk1 bool, clk2 bool, sel bool, rst_n bool) {
	// Asynchronous active-low reset: force initial state immediately.
	if !rst_n {
		clk1_en = true
		clk2_en = false
	} else {
		// Edge-triggered updates
		// posedge clk1
		if clk1 && !prevClk1 {
			clk1_en = !sel && !clk2_en
		}
		// posedge clk2
		if clk2 && !prevClk2 {
			clk2_en = sel && !clk1_en
		}
	}

	// Store current clock values for next edge detection
	prevClk1 = clk1
	prevClk2 = clk2

	// Output generation: gated with rst_n to force low on reset
	out_clkout = rst_n && ((clk1 && clk1_en) || (clk2 && clk2_en))
}

func main() {}
