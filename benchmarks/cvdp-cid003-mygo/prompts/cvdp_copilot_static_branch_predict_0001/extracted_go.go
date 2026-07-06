package main

var out_predict_branch_taken_o bool
var out_predict_branch_pc_o uint32

// static_branch_predict implements a static branch predictor for RISC-V.
// It receives a 32-bit instruction (uncompressed), the program counter, and a valid flag.
// It predicts whether a branch/jump is taken and computes the target address.
func static_branch_predict(fetch_rdata_i uint32, fetch_pc_i uint32, fetch_valid_i bool) {
	// Extract opcode (bits 6:0)
	opcode := fetch_rdata_i & 0x7F

	// Initialize outputs
	taken := false
	target := uint32(0)

	if fetch_valid_i {
		if opcode == 0x6F { // JAL
			// Build J-type immediate (21-bit value, bits 20:0)
			imm20_0 := uint32(0)
			imm20_0 |= ((fetch_rdata_i >> 31) & 1) << 20
			imm20_0 |= ((fetch_rdata_i >> 12) & 0xFF) << 12
			imm20_0 |= ((fetch_rdata_i >> 20) & 1) << 11
			imm20_0 |= ((fetch_rdata_i >> 21) & 0x3FF) << 1
			// Sign-extend from bit 20
			var imm uint32
			if (imm20_0 & 0x100000) != 0 {
				imm = imm20_0 | 0xFFE00000
			} else {
				imm = imm20_0
			}
			taken = true
			target = fetch_pc_i + imm

		} else if opcode == 0x67 { // JALR
			// Extract 12-bit immediate and sign-extend
			imm12 := (fetch_rdata_i >> 20) & 0xFFF
			var imm uint32
			if (imm12 & 0x800) != 0 {
				imm = imm12 | 0xFFFFF000
			} else {
				imm = imm12
			}
			taken = true
			target = fetch_pc_i + imm

		} else if opcode == 0x63 { // branch (B-type)
			// Build B-type immediate (13-bit value, bits 12:0)
			imm12_0 := uint32(0)
			imm12_0 |= ((fetch_rdata_i >> 31) & 1) << 12
			imm12_0 |= ((fetch_rdata_i >> 7) & 1) << 11
			imm12_0 |= ((fetch_rdata_i >> 25) & 0x3F) << 5
			imm12_0 |= ((fetch_rdata_i >> 8) & 0xF) << 1
			// Sign-extend from bit 12
			var imm uint32
			if (imm12_0 & 0x1000) != 0 {
				imm = imm12_0 | 0xFFFFE000
			} else {
				imm = imm12_0
			}
			// Branch taken if immediate is negative (sign bit = 1)
			if (imm & 0x80000000) != 0 {
				taken = true
				target = fetch_pc_i + imm
			}
		}
	}

	out_predict_branch_taken_o = taken
	out_predict_branch_pc_o = target
}

func main() {}
