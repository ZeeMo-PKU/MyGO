package main

// Shift register holds the previous two input bits.
// sr1 is the most recent previous bit (delayed by 1 clock).
// sr2 is the bit delayed by 2 clocks.
var sr1, sr2 bool

// Encoded output bits.
var out_encoded_bit1, out_encoded_bit2 bool

// convolutional_encoder implements a constraint length 3 convolutional encoder
// with generator polynomials:
//   g1 = 111 (x² + x + 1)  → encoded_bit1 = data_in XOR sr1 XOR sr2
//   g2 = 101 (x² + 1)      → encoded_bit2 = data_in XOR sr2
// The function is called on every positive clock edge.
func convolutional_encoder(clk bool, rst bool, data_in bool) {
	if rst {
		// Asynchronous reset: clear shift register and outputs.
		sr1 = false
		sr2 = false
		out_encoded_bit1 = false
		out_encoded_bit2 = false
	} else {
		// Compute outputs combinatorially using current data_in and current state.
		out_encoded_bit1 = data_in != sr1 != sr2
		out_encoded_bit2 = data_in != sr2

		// Update the shift register for the next clock cycle.
		sr2 = sr1
		sr1 = data_in
	}
}

func main() {}
