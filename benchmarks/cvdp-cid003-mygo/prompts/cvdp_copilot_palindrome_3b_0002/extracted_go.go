package main

var sr0 bool
var sr1 bool
var sr2 bool
var out_palindrome_detected bool

// palindrome_detect detects a 3-bit palindrome in the incoming bit stream.
// It shifts in each new bit and asserts palindrome_detected when the oldest
// bit equals the newest bit in the 3-bit shift register.
func palindrome_detect(clk bool, reset bool, bit_stream bool) {
	if reset {
		sr0 = false
		sr1 = false
		sr2 = false
		out_palindrome_detected = false
	} else {
		// Shift register update
		sr2 = sr1
		sr1 = sr0
		sr0 = bit_stream
		// Palindrome condition: newest bit matches the bit from two cycles ago
		out_palindrome_detected = sr0 == sr2
	}
}

func main() {}
