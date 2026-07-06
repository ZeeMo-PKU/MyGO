package main

var (
	memory       [8]uint8 // LIFO storage, 2^ADDR_WIDTH = 8
	pointer      uint8    // number of stored elements (0 to 8)
	data_out_reg uint8    // registered output data
	prev_clock   bool     // for rising-edge detection
	out_empty    bool
	out_full     bool
	out_data_out uint8
)

func sync_lifo(clock bool, reset bool, write_en bool, read_en bool, data_in uint8) {
	// Detect rising edge of clock
	if !prev_clock && clock {
		if reset {
			// Synchronous reset: clear all state
			for i := 0; i < 8; i++ {
				memory[i] = 0
			}
			pointer = 0
			data_out_reg = 0
		} else {
			not_full := pointer < 8
			not_empty := pointer > 0

			// Perform concurrent read/write operations
			if write_en && not_full {
				memory[pointer] = data_in
			}
			if read_en && not_empty {
				data_out_reg = memory[pointer-1]
			}

			// Update pointer based on enables and previous state
			if write_en && not_full {
				pointer++
			}
			if read_en && not_empty {
				pointer--
			}
		}
	}
	prev_clock = clock

	// Combinatorial outputs
	out_empty = pointer == 0
	out_full = pointer == 8
	out_data_out = data_out_reg
}

func main() {
}
