package main

var out_o_set_bit_count uint8
var prev_ready bool

func SetBitStreamCalculator(i_clk bool, i_rst_n bool, i_ready bool, i_bit_in bool) {
	if !i_rst_n {
		out_o_set_bit_count = 0
		prev_ready = false
	} else {
		rise := !prev_ready && i_ready
		if rise {
			out_o_set_bit_count = 0
		} else if i_ready {
			if i_bit_in && out_o_set_bit_count < 255 {
				out_o_set_bit_count++
			}
		}
		prev_ready = i_ready
	}
}

func main() {}
