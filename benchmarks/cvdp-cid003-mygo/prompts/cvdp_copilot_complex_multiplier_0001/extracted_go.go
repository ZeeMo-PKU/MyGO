package main

var out_result_real uint32
var out_result_imag uint32
var prev_clk bool

func complex_multiplier(clk bool, arst_n bool, a_real int16, a_imag int16, b_real int16, b_imag int16) {
	// Asynchronous active-low reset: clear outputs immediately
	if !arst_n {
		out_result_real = 0
		out_result_imag = 0
	} else if clk && !prev_clk { // rising edge
		// One-cycle latency: compute product
		a := int32(a_real)
		b := int32(a_imag)
		c := int32(b_real)
		d := int32(b_imag)
		out_result_real = uint32(a*c - b*d)
		out_result_imag = uint32(a*d + b*c)
	}
	prev_clk = clk
}

func main() {}
