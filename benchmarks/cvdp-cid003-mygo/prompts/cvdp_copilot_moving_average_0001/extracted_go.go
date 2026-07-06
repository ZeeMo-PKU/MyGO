package main

var out_data_out uint16

var buffer [8]uint16
var sum uint32
var count uint8
var pos uint8

// moving_average computes the integer moving average of the last 8 12-bit unsigned samples.
func moving_average(clk bool, reset bool, data_in uint16) {
	if clk {
		if reset {
			for i := 0; i < 8; i++ {
				buffer[i] = 0
			}
			sum = 0
			count = 0
			pos = 0
			out_data_out = 0
		} else {
			if count < 8 {
				// Buffer not yet full, just add new sample.
				sum += uint32(data_in)
				buffer[pos] = data_in
				pos = (pos + 1) & 7
				count++
			} else {
				// Subtract the oldest sample (at pos) and add the new one.
				sum = sum - uint32(buffer[pos]) + uint32(data_in)
				buffer[pos] = data_in
				pos = (pos + 1) & 7
			}
			out_data_out = uint16(sum / 8)
		}
	}
}

func main() {}
