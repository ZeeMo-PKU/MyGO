package main

var out_data_out uint8

// barrel_shifter_8bit is a combinational 8-bit barrel shifter.
// data_in : 8-bit input data.
// shift_bits : 3-bit value specifying shift amount (0 to 7).
// left_right : direction; true = left shift, false = right shift.
func barrel_shifter_8bit(data_in uint8, shift_bits uint8, left_right bool) {
	if left_right {
		out_data_out = data_in << shift_bits
	} else {
		out_data_out = data_in >> shift_bits
	}
}

func main() {}
