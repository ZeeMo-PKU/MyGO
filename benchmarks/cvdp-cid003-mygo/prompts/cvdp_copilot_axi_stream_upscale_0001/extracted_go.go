package main

var (
	out_s_axis_ready bool
	out_m_axis_valid bool
	out_m_axis_data uint32
)

var (
	valid_reg bool
	data_reg  uint32
)

func axis_upscale(clk bool, resetn bool, dfmt_enable bool, dfmt_type bool, dfmt_se bool, s_axis_valid bool, s_axis_data uint32, m_axis_ready bool) {
	// Outputs based on current registered state
	out_s_axis_ready = m_axis_ready
	out_m_axis_valid = valid_reg
	out_m_axis_data = data_reg

	// Next-state logic with synchronous reset
	var next_valid bool
	var next_data uint32

	if !resetn {
		next_valid = false
		next_data = 0
	} else {
		load := s_axis_valid && m_axis_ready
		consume := m_axis_ready && valid_reg

		if load {
			// Determine extension bit for upper 8 bits
			var ext_bit bool
			if dfmt_enable && dfmt_se {
				msb := (s_axis_data>>23)&1 == 1
				if dfmt_type {
					ext_bit = !msb
				} else {
					ext_bit = msb
				}
			}
			var upper uint32
			if ext_bit {
				upper = 0xFF << 24
			}
			next_data = upper | (s_axis_data & 0xFFFFFF)
			next_valid = true
		} else if consume {
			next_data = data_reg // hold old value while valid is cleared
			next_valid = false
		} else {
			next_data = data_reg
			next_valid = valid_reg
		}
	}

	// Update registered state for next cycle
	valid_reg = next_valid
	data_reg = next_data
}

func main() {}
