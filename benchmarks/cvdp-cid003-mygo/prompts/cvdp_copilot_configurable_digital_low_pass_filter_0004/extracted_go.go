package main

const N = 8
const DATA_WIDTH = 16
const DEC_FACTOR = 4

var out_valid_out bool
var out_data_out uint32
var out_peak_value uint16

// Internal state
var prev_clk bool
var valid_reg bool
var data_reg [2]uint64

func advanced_decimator_with_adaptive_peak_detection(clk bool, reset bool, valid_in bool, data_in [2]uint64) {
	posedge := clk && !prev_clk
	prev_clk = clk

	if reset {
		valid_reg = false
		data_reg = [2]uint64{0, 0}
	} else if posedge {
		valid_reg = valid_in
		data_reg = data_in
	}

	// Combinational unpack of N samples from registered data
	var samples [N]uint16
	for i := 0; i < N; i++ {
		bitPos := i * DATA_WIDTH
		wordIdx := bitPos / 64
		bitOff := bitPos % 64
		samples[i] = uint16((data_reg[wordIdx] >> uint(bitOff)) & 0xFFFF)
	}

	// Decimate: pick every DEC_FACTOR-th sample
	const OutCount = N / DEC_FACTOR
	var decimated [OutCount]uint16
	for i := 0; i < OutCount; i++ {
		decimated[i] = samples[i*DEC_FACTOR]
	}

	// Peak detection (signed comparison)
	peak := int16(decimated[0])
	for i := 1; i < OutCount; i++ {
		val := int16(decimated[i])
		if val > peak {
			peak = val
		}
	}

	// Pack decimated samples into output bus
	var packed uint32 = 0
	for i := 0; i < OutCount; i++ {
		packed |= uint32(decimated[i]) << uint(i * DATA_WIDTH)
	}

	out_valid_out = valid_reg
	out_data_out = packed
	out_peak_value = uint16(peak)
}

func main() {}
