package main

var out_data_out uint8

func hamming_code_receiver(data_in uint8) {
	// Compute even-parity syndrome bits
	c3 := ((data_in >> 1) & 1) ^ ((data_in >> 3) & 1) ^ ((data_in >> 5) & 1) ^ ((data_in >> 7) & 1)
	c2 := ((data_in >> 2) & 1) ^ ((data_in >> 3) & 1) ^ ((data_in >> 6) & 1) ^ ((data_in >> 7) & 1)
	c1 := ((data_in >> 4) & 1) ^ ((data_in >> 5) & 1) ^ ((data_in >> 6) & 1) ^ ((data_in >> 7) & 1)
	syndrome := (c1 << 2) | (c2 << 1) | c3

	corrected := data_in
	if syndrome != 0 {
		// Flip the erroneous bit at position syndrome (1‑7)
		corrected = data_in ^ (1 << syndrome)
	}

	// Extract data bits from corrected word: bits 7,6,5,3 → data_out[3:0]
	out_data_out = ((corrected >> 7) & 1) << 3 |
		((corrected >> 6) & 1) << 2 |
		((corrected >> 5) & 1) << 1 |
		((corrected >> 3) & 1)
}

func main() {}
