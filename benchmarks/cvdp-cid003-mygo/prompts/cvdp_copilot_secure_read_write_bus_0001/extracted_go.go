package main

const (
	p_addr_width       = 8
	p_data_width       = 8
	p_configurable_key uint8 = 0xAA
)

var (
	mem [1 << p_addr_width]uint8
	out_data_out uint8
	out_error    bool
	prev_capture_pulse bool
)

func secure_read_write_bus_interface(i_addr uint8, i_data_in uint8, i_key_in uint8, i_read_write_enable bool, i_capture_pulse bool, i_reset_bar bool) {
	// asynchronous active-low reset
	if !i_reset_bar {
		// clear memory and outputs
		for i := range mem {
			mem[i] = 0
		}
		out_data_out = 0
		out_error = false
		prev_capture_pulse = i_capture_pulse
		return
	}

	// rising-edge detection of i_capture_pulse
	if i_capture_pulse && !prev_capture_pulse {
		if i_key_in == p_configurable_key {
			if !i_read_write_enable { // write operation
				mem[i_addr] = i_data_in
				out_data_out = 0
				out_error = false
			} else { // read operation
				out_data_out = mem[i_addr]
				out_error = false
			}
		} else {
			out_error = true
			out_data_out = 0
		}
	}

	prev_capture_pulse = i_capture_pulse
}

func main() {}
