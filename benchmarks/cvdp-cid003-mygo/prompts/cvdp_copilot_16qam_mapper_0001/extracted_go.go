package main

var out_I uint32
var out_Q uint32

func qam16_mapper_interpolated(bits uint16) {
	const N = 4
	const IN_WIDTH = 4
	const OUT_WIDTH = 3

	out_I = 0
	out_Q = 0

	for k := 0; k < N/2; k++ {
		// Extract two consecutive input symbols (each 4 bits)
		sym0 := uint8((bits >> uint((2*k)*IN_WIDTH)) & 0xF)
		sym1 := uint8((bits >> uint((2*k+1)*IN_WIDTH)) & 0xF)

		// Decode MSBs (bits 3:2) for I, LSBs (bits 1:0) for Q
		msbs0 := (sym0 >> 2) & 0x3
		lsbs0 := sym0 & 0x3
		msbs1 := (sym1 >> 2) & 0x3
		lsbs1 := sym1 & 0x3

		i0 := map2To3(msbs0)
		q0 := map2To3(lsbs0)
		i1 := map2To3(msbs1)
		q1 := map2To3(lsbs1)

		// Interpolated values: arithmetic mean of two adjacent symbols
		interp_i := interpolate(i0, i1)
		interp_q := interpolate(q0, q1)

		// Pack outputs: first symbol, interpolated, second symbol
		// Each sample occupies OUT_WIDTH bits (3 bits)
		// Base bit position for this pair
		base := k * (3 * OUT_WIDTH) // 9*k for N=4
		out_I |= (uint32(i0) & 0x7) << uint(base)
		out_I |= (uint32(interp_i) & 0x7) << uint(base + OUT_WIDTH)
		out_I |= (uint32(i1) & 0x7) << uint(base + 2*OUT_WIDTH)

		out_Q |= (uint32(q0) & 0x7) << uint(base)
		out_Q |= (uint32(interp_q) & 0x7) << uint(base + OUT_WIDTH)
		out_Q |= (uint32(q1) & 0x7) << uint(base + 2*OUT_WIDTH)
	}
}

// map2To3 converts a 2-bit value (0..3) to its 3-bit two's complement
// QAM16 mapping: 00 → -3 (101), 01 → -1 (111), 10 → 1 (001), 11 → 3 (011)
func map2To3(v uint8) uint8 {
	switch v {
	case 0:
		return 5 // -3
	case 1:
		return 7 // -1
	case 2:
		return 1 // 1
	case 3:
		return 3 // 3
	default:
		return 0
	}
}

// interpolate computes the arithmetic mean of two 3-bit signed values.
// Sum is performed in 4‑bit signed precision, then shifted right by 1
// (arithmetic).  The result is returned as a 3-bit unsigned value.
func interpolate(a, b uint8) uint8 {
	// Convert 3‑bit unsigned to signed 8‑bit
	aSigned := int8(a)
	if a >= 4 {
		aSigned = int8(a) - 8
	}
	bSigned := int8(b)
	if b >= 4 {
		bSigned = int8(b) - 8
	}

	sum := aSigned + bSigned
	shifted := sum >> 1 // arithmetic shift

	// Convert back to 3‑bit unsigned representation
	if shifted < 0 {
		return uint8(shifted+8) & 0x7
	}
	return uint8(shifted) & 0x7
}

func main() {}
