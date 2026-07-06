package main

var out_o_data_out uint8

// Register bank memory: 256 bytes (address width 8, data width 8)
var mem [256]uint8

// State for edge detection and unlock sequence
var prev_capture_pulse bool
var unlocked bool
var unlock_stage uint8 // 0: need code0, 1: code0 done, need code1

func secure_read_write_register_bank(i_addr uint8, i_data_in uint8, i_read_write_enable bool, i_capture_pulse bool, i_rst_n bool) {
	// Asynchronous active-low reset: resets unlock state machine only
	if !i_rst_n {
		prev_capture_pulse = i_capture_pulse
		unlocked = false
		unlock_stage = 0
		out_o_data_out = 0
		return
	}

	// Positive edge detection on i_capture_pulse
	if i_capture_pulse && !prev_capture_pulse {
		if i_read_write_enable {
			// Read operation
			// Addresses 0 and 1 are write-only and always output 0
			// Also, before unlock, all other addresses output 0
			if i_addr == 0 || i_addr == 1 || !unlocked {
				out_o_data_out = 0
			} else {
				out_o_data_out = mem[i_addr]
			}
		} else {
			// Write operation
			// Output is 0 during writes
			out_o_data_out = 0
			if unlocked {
				// Unlocked: write any address freely
				// But note: writes to 0 or 1 with wrong code still trigger re-lock
				if i_addr == 0 {
					mem[i_addr] = i_data_in
					if i_data_in == 0xAB { // p_unlock_code_0
						unlock_stage = 1
					} else {
						unlocked = false
						unlock_stage = 0
					}
				} else if i_addr == 1 {
					mem[i_addr] = i_data_in
					if unlock_stage == 1 && i_data_in == 0xCD { // p_unlock_code_1
						unlocked = true // already true
						unlock_stage = 0
					} else {
						unlocked = false
						unlock_stage = 0
					}
				} else {
					mem[i_addr] = i_data_in
				}
			} else {
				// Locked: only addresses 0 and 1 can be written, used for unlocking
				if i_addr == 0 {
					mem[i_addr] = i_data_in
					if i_data_in == 0xAB {
						unlock_stage = 1
					} else {
						// Wrong code resets sequence
						unlock_stage = 0
					}
				} else if i_addr == 1 {
					mem[i_addr] = i_data_in
					if unlock_stage == 1 && i_data_in == 0xCD {
						unlocked = true
						unlock_stage = 0
					} else {
						// Wrong code or wrong sequence resets
						unlocked = false
						unlock_stage = 0
					}
				}
				// Other addresses are blocked; no write occurs
			}
		}
	}

	// Update previous capture_pulse for next edge detection
	prev_capture_pulse = i_capture_pulse
}

func main() {}
