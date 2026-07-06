package main

var (
	state        uint8 = 0 // 0: IDLE, 1: SETUP, 2: ACCESS
	timeout_cnt  uint8 = 0 // 4-bit timeout counter
	capture_addr uint32
	capture_data uint32

	out_apb_psel_o    bool
	out_apb_penable_o bool
	out_apb_pwrite_o  bool
	out_apb_paddr_o   uint32
	out_apb_pwdata_o  uint32
)

func apb_controller(clk bool, reset_n bool, select_a_i bool, select_b_i bool, select_c_i bool, addr_a_i uint32, data_a_i uint32, addr_b_i uint32, data_b_i uint32, addr_c_i uint32, data_c_i uint32, apb_pready_i bool) {
	if !reset_n {
		state = 0
		timeout_cnt = 0
		capture_addr = 0
		capture_data = 0
		out_apb_psel_o = false
		out_apb_penable_o = false
		out_apb_pwrite_o = false
		out_apb_paddr_o = 0
		out_apb_pwdata_o = 0
		return
	}

	// Sequential logic on posedge clk
	switch state {
	case 0: // IDLE
		out_apb_psel_o = false
		out_apb_penable_o = false
		out_apb_pwrite_o = false
		out_apb_paddr_o = 0
		out_apb_pwdata_o = 0
		if select_a_i {
			capture_addr = addr_a_i
			capture_data = data_a_i
			state = 1 // SETUP
		} else if select_b_i {
			capture_addr = addr_b_i
			capture_data = data_b_i
			state = 1
		} else if select_c_i {
			capture_addr = addr_c_i
			capture_data = data_c_i
			state = 1
		}
		timeout_cnt = 0

	case 1: // SETUP
		out_apb_psel_o = true
		out_apb_pwrite_o = true
		out_apb_paddr_o = capture_addr
		out_apb_pwdata_o = capture_data
		out_apb_penable_o = false
		state = 2 // ACCESS

	case 2: // ACCESS
		out_apb_psel_o = true
		out_apb_pwrite_o = true
		out_apb_paddr_o = capture_addr
		out_apb_pwdata_o = capture_data
		out_apb_penable_o = true
		if apb_pready_i {
			state = 0 // return to IDLE
			timeout_cnt = 0
		} else {
			if timeout_cnt == 15 {
				state = 0 // abort, return to IDLE
				timeout_cnt = 0
			} else {
				timeout_cnt++
			}
		}

	default: // safety fallback
		state = 0
		timeout_cnt = 0
		out_apb_psel_o = false
		out_apb_penable_o = false
		out_apb_pwrite_o = false
		out_apb_paddr_o = 0
		out_apb_pwdata_o = 0
	}
}

func main() {}
