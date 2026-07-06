package main

var out_excess3 uint8 // 4-bit Excess-3 output
var out_error   bool  // error flag, true for invalid BCD

func bcd_to_excess_3(bcd uint8) {
	if bcd > 9 {
		out_excess3 = 0
		out_error = true
	} else {
		out_excess3 = bcd + 3
		out_error = false
	}
}

func main() {}
