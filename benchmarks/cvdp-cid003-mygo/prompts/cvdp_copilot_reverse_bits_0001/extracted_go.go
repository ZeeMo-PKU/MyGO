package main

var out_num_out uint32

// reverse_bits reverses the bits of a 32-bit unsigned input number.
// It implements a combinational bit-reversal using a series of swaps.
func reverse_bits(num_in uint32) {
	// Swap adjacent 16-bit halves.
	n := (num_in >> 16) | (num_in << 16)
	// Swap adjacent bytes.
	n = ((n & 0xff00ff00) >> 8) | ((n & 0x00ff00ff) << 8)
	// Swap adjacent nibbles (4 bits).
	n = ((n & 0xf0f0f0f0) >> 4) | ((n & 0x0f0f0f0f) << 4)
	// Swap adjacent pairs of bits.
	n = ((n & 0xcccccccc) >> 2) | ((n & 0x33333333) << 2)
	// Swap adjacent bits.
	n = ((n & 0xaaaaaaaa) >> 1) | ((n & 0x55555555) << 1)
	out_num_out = n
}

func main() {}
