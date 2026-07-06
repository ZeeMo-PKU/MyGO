package main

var out_encoder_data_out [66]bool
var prev_clk bool

// encoder_64b66b implements a 64b/66b encoder.
// It samples encoder_data_in and encoder_control_in on the rising edge of clk_in,
// and updates out_encoder_data_out one cycle later.
func encoder_64b66b(clk_in bool, rst_in bool, encoder_data_in uint64, encoder_control_in uint8) {
	if rst_in {
		out_encoder_data_out = [66]bool{}
	} else if !prev_clk && clk_in {
		if encoder_control_in == 0 {
			// Pure data encoding: sync = 2'b01
			out_encoder_data_out[64] = true
			out_encoder_data_out[65] = false
			for i := 0; i < 64; i++ {
				out_encoder_data_out[i] = ((encoder_data_in >> uint(i)) & 1) == 1
			}
		} else {
			// Control word present: sync = 2'b10, data = 0
			out_encoder_data_out[64] = false
			out_encoder_data_out[65] = true
			for i := 0; i < 64; i++ {
				out_encoder_data_out[i] = false
			}
		}
	}
	prev_clk = clk_in
}

func main() {}
