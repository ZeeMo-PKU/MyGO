package main

var out_parallel_out uint8
var state uint8
var prev_clock bool

func serial_in_parallel_out_8bit(clock bool, serial_in bool) {
	// Positive-edge detection and shift
	if clock && !prev_clock {
		var bit uint8
		if serial_in {
			bit = 1
		} else {
			bit = 0
		}
		state = ((state << 1) & 0xFF) | bit
	}
	// Continuous assignment of output
	out_parallel_out = state
	// Store current clock for next edge detection
	prev_clock = clock
}

func main() {}
