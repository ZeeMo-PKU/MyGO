package main

var out_data_out uint8

func hamming_code_tx_for_4bit(data_in uint8) {
	// Extract input bits
	d0 := data_in & 1
	d1 := (data_in >> 1) & 1
	d2 := (data_in >> 2) & 1
	d3 := (data_in >> 3) & 1

	// Calculate parity bits
	p1 := d0 ^ d1 ^ d3 // parity for positions 0,1,3 of data_in; placed at output bit 1
	p2 := d0 ^ d2 ^ d3 // parity for positions 0,2,3 of data_in; placed at output bit 2
	p3 := d1 ^ d2 ^ d3 // parity for positions 1,2,3 of data_in; placed at output bit 4

	// Assemble output byte
	out_data_out = (d3 << 7) | (d2 << 6) | (d1 << 5) | (p3 << 4) | (d0 << 3) | (p2 << 2) | (p1 << 1) | 0
}

func main() {}
