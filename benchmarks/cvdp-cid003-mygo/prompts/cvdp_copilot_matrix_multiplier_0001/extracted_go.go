package main

const (
	ROW_A            = 4
	COL_A            = 4
	ROW_B            = 4
	COL_B            = 4
	INPUT_DATA_WIDTH = 8
	// OUTPUT_DATA_WIDTH is chosen to hold the maximum possible dot‑product sum.
	// For unsigned 8‑bit inputs and COL_A = 4: max = 4 * 255² = 260100 → 18 bits.
	OUTPUT_DATA_WIDTH = 18
	MAT_A_ELEMENTS    = ROW_A * COL_A
	MAT_B_ELEMENTS    = ROW_B * COL_B
	OUTPUT_ELEMENTS   = ROW_A * COL_B
	OUTPUT_BITS       = OUTPUT_ELEMENTS * OUTPUT_DATA_WIDTH
	OUTPUT_BYTES      = (OUTPUT_BITS + 7) / 8
)

var out_matrix_c [OUTPUT_BYTES]uint8

// matrix_multiplier performs combinational matrix multiplication.
// Inputs are flattened in row‑major order with element (0,0) in the LSB.
// The output is flattened in the same way.
func matrix_multiplier(matrix_a [MAT_A_ELEMENTS]uint8, matrix_b [MAT_B_ELEMENTS]uint8) {
	var c [OUTPUT_ELEMENTS]uint32

	// Compute each output element as a dot product.
	for i := 0; i < ROW_A; i++ {
		for j := 0; j < COL_B; j++ {
			sum := uint32(0)
			for k := 0; k < COL_A; k++ {
				a_val := uint32(matrix_a[i*COL_A+k])
				b_val := uint32(matrix_b[k*COL_B+j])
				sum += a_val * b_val
			}
			// Mask to OUTPUT_DATA_WIDTH bits (overflow is impossible by construction).
			c[i*COL_B+j] = sum & ((1 << OUTPUT_DATA_WIDTH) - 1)
		}
	}

	// Clear output byte vector.
	for i := 0; i < OUTPUT_BYTES; i++ {
		out_matrix_c[i] = 0
	}

	// Tightly pack all elements into the output byte array.
	for n := 0; n < OUTPUT_ELEMENTS; n++ {
		val := c[n]
		bitPos := n * OUTPUT_DATA_WIDTH
		startByte := bitPos / 8
		endByte := (bitPos + OUTPUT_DATA_WIDTH - 1) / 8

		for b := startByte; b <= endByte; b++ {
			byteLSB := b * 8
			byteMSB := byteLSB + 7

			// Overlap between element bits and this byte.
			overlapStart := bitPos
			if byteLSB > overlapStart {
				overlapStart = byteLSB
			}
			overlapEnd := bitPos + OUTPUT_DATA_WIDTH - 1
			if byteMSB < overlapEnd {
				overlapEnd = byteMSB
			}

			if overlapStart <= overlapEnd {
				// Slice of val that contributes to this byte.
				lowBit := overlapStart - bitPos
				numBits := overlapEnd - overlapStart + 1
				mask := uint8((1 << numBits) - 1)
				bits := uint8((val >> lowBit) & uint32(mask))

				// Align within the byte.
				shift := overlapStart - byteLSB
				out_matrix_c[b] |= bits << shift
			}
		}
	}
}

func main() {}
