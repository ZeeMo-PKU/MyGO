package main

// Parameters
const InWidth_g = 32
const InReg_g = true
const OutReg_g = true
const PlRegs_g = 1

// Output ports
var out_FirstBit uint8
var out_Found bool
var out_Valid bool

// Internal registers
var in_data_reg uint32
var in_valid_reg bool

// Pipeline stage registers (PlRegs_g = 1)
var pl_low_has_bit bool
var pl_low_first_bit uint8
var pl_high_has_bit bool
var pl_high_first_bit uint8
var pl_valid bool

// Output registers (OutReg_g = true)
var reg_out_FirstBit uint8
var reg_out_Found bool
var reg_out_Valid bool

// Priority encoder for 16-bit vector: returns (found, index)
func find_first_set_16(v uint16) (bool, uint8) {
	t := v
	for i := uint8(0); i < 16; i++ {
		if t&1 != 0 {
			return true, i
		}
		t >>= 1
	}
	return false, 0
}

// Hardware entry function
func cvdp_copilot_decode_firstbit(Clk bool, Rst bool, In_Data uint32, In_Valid bool) {
	if Rst {
		// Asynchronous reset
		in_data_reg = 0
		in_valid_reg = false
		pl_low_has_bit = false
		pl_low_first_bit = 0
		pl_high_has_bit = false
		pl_high_first_bit = 0
		pl_valid = false
		reg_out_FirstBit = 0
		reg_out_Found = false
		reg_out_Valid = false
		out_FirstBit = 0
		out_Found = false
		out_Valid = false
		return
	}

	// ---- Rising clock edge ----

	// Stage1 data selection: if InReg_g, use registered input; else use raw input
	var data_stage1 uint32
	var valid_stage1 bool
	if InReg_g {
		data_stage1 = in_data_reg
		valid_stage1 = in_valid_reg
	} else {
		data_stage1 = In_Data
		valid_stage1 = In_Valid
	}

	// Stage1: split into low/high 16-bit halves and find first set bit
	low16 := uint16(data_stage1 & 0xFFFF)
	high16 := uint16((data_stage1 >> 16) & 0xFFFF)
	low_found, low_idx := find_first_set_16(low16)
	high_found, high_idx := find_first_set_16(high16)

	// Next values for pipeline registers (PlRegs_g = 1)
	next_pl_low_has_bit := low_found
	next_pl_low_first_bit := low_idx
	next_pl_high_has_bit := high_found
	next_pl_high_first_bit := high_idx
	next_pl_valid := valid_stage1

	// Stage2: combine results using the current pipeline registers (previous cycle values)
	var stage2_firstBit uint8
	var stage2_found bool
	var stage2_valid bool
	if pl_low_has_bit {
		stage2_found = true
		stage2_firstBit = pl_low_first_bit
	} else if pl_high_has_bit {
		stage2_found = true
		stage2_firstBit = pl_high_first_bit + 16
	} else {
		stage2_found = false
		stage2_firstBit = 0
	}
	stage2_valid = pl_valid

	// Update pipeline registers with the next values
	pl_low_has_bit = next_pl_low_has_bit
	pl_low_first_bit = next_pl_low_first_bit
	pl_high_has_bit = next_pl_high_has_bit
	pl_high_first_bit = next_pl_high_first_bit
	pl_valid = next_pl_valid

	// Input register update (for next cycle)
	if InReg_g {
		in_data_reg = In_Data
		in_valid_reg = In_Valid
	}

	// Output stage
	if OutReg_g {
		// Register the output results
		reg_out_FirstBit = stage2_firstBit
		reg_out_Found = stage2_found
		reg_out_Valid = stage2_valid
		// Drive output ports from output registers
		out_FirstBit = reg_out_FirstBit
		out_Found = reg_out_Found
		out_Valid = reg_out_Valid
	} else {
		// Bypass output registers
		out_FirstBit = stage2_firstBit
		out_Found = stage2_found
		out_Valid = stage2_valid
	}
}

func main() {}
