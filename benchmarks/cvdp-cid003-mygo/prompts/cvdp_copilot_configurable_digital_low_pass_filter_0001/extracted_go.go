package main

const DATA_WIDTH = 16
const COEFF_WIDTH = 16
const NUM_TAPS = 8
const NBW_MULT = DATA_WIDTH + COEFF_WIDTH
const OUT_WIDTH = NBW_MULT + 3 // $clog2(8) = 3

var reg_data [NUM_TAPS]int16
var reg_coeffs [NUM_TAPS]int16
var reg_valid_in bool

var out_valid_out bool
var out_data_out [OUT_WIDTH]bool // index 0 = LSB

func low_pass_filter(clk bool, reset bool, data_in [NUM_TAPS]int16, valid_in bool, coeffs [NUM_TAPS]int16) {
	// synchronous reset and data/coefficient loading
	if reset {
		reg_data = [NUM_TAPS]int16{}
		reg_coeffs = [NUM_TAPS]int16{}
		reg_valid_in = false
	} else {
		if valid_in {
			reg_data = data_in
			reg_coeffs = coeffs
		}
		reg_valid_in = valid_in
	}

	// combinational convolution sum
	var sum int64 = 0
	for i := 0; i < NUM_TAPS; i++ {
		sum += int64(reg_data[i]) * int64(reg_coeffs[NUM_TAPS-1-i])
	}

	// convert sum to OUT_WIDTH bits, LSB at index 0
	mask := uint64((1 << OUT_WIDTH) - 1)
	u := uint64(sum) & mask
	for i := 0; i < OUT_WIDTH; i++ {
		out_data_out[i] = (u>>uint(i))&1 != 0
	}

	out_valid_out = reg_valid_in
}

func main() {}
