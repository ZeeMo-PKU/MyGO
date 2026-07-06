package main

var (
	state           uint8 = 0 // IDLE
	out_o_ready     bool  = false
	out_o_error     bool  = false
	out_o_fsm_status uint8 = 0
	out_o_vector_1  uint8 = 0
	out_o_vector_2  uint8 = 0
	out_o_vector_3  uint8 = 0
	out_o_vector_4  uint8 = 0
)

const (
	IDLE    uint8 = 0
	PROCESS uint8 = 1
	READY   uint8 = 2
	FAULT   uint8 = 3
)

func enhanced_fsm_signal_processor(i_clk, i_rst_n, i_enable, i_clear, i_ack, i_fault bool, i_vector_1, i_vector_2, i_vector_3, i_vector_4, i_vector_5, i_vector_6 uint8) {
	if !i_rst_n {
		// Asynchronous active-low reset
		state = IDLE
		out_o_ready = false
		out_o_error = false
		out_o_fsm_status = IDLE
		out_o_vector_1 = 0
		out_o_vector_2 = 0
		out_o_vector_3 = 0
		out_o_vector_4 = 0
	} else {
		// Sequential logic synchronous to i_clk (assumed to be called on posedge)
		var next_state uint8 = state

		switch state {
		case IDLE:
			out_o_ready = false
			out_o_error = false
			out_o_fsm_status = IDLE
			out_o_vector_1 = 0
			out_o_vector_2 = 0
			out_o_vector_3 = 0
			out_o_vector_4 = 0
			if i_fault {
				next_state = FAULT
			} else if i_enable {
				next_state = PROCESS
			}
		case PROCESS:
			// Concatenate six 5-bit vectors, append 2'b11 at LSB, split into four 8-bit outputs
			v1 := uint32(i_vector_1 & 0x1F)
			v2 := uint32(i_vector_2 & 0x1F)
			v3 := uint32(i_vector_3 & 0x1F)
			v4 := uint32(i_vector_4 & 0x1F)
			v5 := uint32(i_vector_5 & 0x1F)
			v6 := uint32(i_vector_6 & 0x1F)
			concat30 := (v1 << 25) | (v2 << 20) | (v3 << 15) | (v4 << 10) | (v5 << 5) | v6
			result32 := (concat30 << 2) | 0x3
			out_o_vector_1 = uint8((result32 >> 24) & 0xFF)
			out_o_vector_2 = uint8((result32 >> 16) & 0xFF)
			out_o_vector_3 = uint8((result32 >> 8) & 0xFF)
			out_o_vector_4 = uint8(result32 & 0xFF)

			out_o_ready = false
			out_o_error = false
			out_o_fsm_status = PROCESS
			if i_fault {
				next_state = FAULT
			} else {
				next_state = READY
			}
		case READY:
			out_o_ready = true
			out_o_error = false
			out_o_fsm_status = READY
			// out_o_vector_* keep their previously registered values
			if i_fault {
				next_state = FAULT
			} else if i_ack {
				next_state = IDLE
			}
		case FAULT:
			out_o_ready = false
			out_o_error = true
			out_o_fsm_status = FAULT
			out_o_vector_1 = 0
			out_o_vector_2 = 0
			out_o_vector_3 = 0
			out_o_vector_4 = 0
			if i_clear && !i_fault {
				next_state = IDLE
			}
		default:
			next_state = IDLE
			out_o_ready = false
			out_o_error = false
			out_o_fsm_status = IDLE
			out_o_vector_1 = 0
			out_o_vector_2 = 0
			out_o_vector_3 = 0
			out_o_vector_4 = 0
		}
		state = next_state
	}
}

func main() {
	// Required by MyGO, no runtime logic needed
}
