package main

var out_result uint8

// gf_multiplier computes the 4-bit Galois Field multiplication A * B
// using irreducible polynomial x^4 + x + 1 (0x13).
func gf_multiplier(A uint8, B uint8) {
	// Mask inputs to 4 bits
	A &= 0x0F
	B &= 0x0F

	multiplicand := A
	result := uint8(0)

	for i := 0; i < 4; i++ {
		// If current bit of B is 1, XOR multiplicand into result
		if (B>>i)&1 == 1 {
			result ^= multiplicand & 0x0F
		}
		// Shift multiplicand left
		multiplicand <<= 1
		// If overflow (bit 4 set), reduce with irreducible polynomial
		if multiplicand&0x10 != 0 {
			multiplicand ^= 0x13 // x^4 + x + 1
		}
	}

	out_result = result & 0x0F
}

func main() {}
