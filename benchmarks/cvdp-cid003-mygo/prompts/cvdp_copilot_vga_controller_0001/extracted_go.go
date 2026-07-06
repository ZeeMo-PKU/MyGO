package main

const (
	H_ACTIVE uint8 = 0
	H_FRONT  uint8 = 1
	H_PULSE  uint8 = 2
	H_BACK   uint8 = 3
	V_ACTIVE uint8 = 0
	V_FRONT  uint8 = 1
	V_PULSE  uint8 = 2
	V_BACK   uint8 = 3
)

var (
	out_hsync  bool
	out_vsync  bool
	out_red    uint8
	out_green  uint8
	out_blue   uint8
	out_next_x uint16
	out_next_y uint16
	out_sync   bool
	out_clk    bool
	out_blank  bool
)

var (
	h_state   uint8  = H_ACTIVE
	v_state   uint8  = V_ACTIVE
	h_count   uint16 = 0
	v_count   uint16 = 0
	line_done bool   = false
)

func hLimit(s uint8) uint16 {
	switch s {
	case H_ACTIVE:
		return 640
	case H_FRONT:
		return 16
	case H_PULSE:
		return 96
	case H_BACK:
		return 48
	default:
		return 1
	}
}

func vLimit(s uint8) uint16 {
	switch s {
	case V_ACTIVE:
		return 480
	case V_FRONT:
		return 10
	case V_PULSE:
		return 2
	case V_BACK:
		return 33
	default:
		return 1
	}
}

func vga_controller(clock bool, reset bool, color_in uint8) {
	if reset {
		h_state = H_ACTIVE
		v_state = V_ACTIVE
		h_count = 0
		v_count = 0
		line_done = false

		out_clk = clock
		out_hsync = false
		out_vsync = false
		out_sync = false
		out_blank = false
		out_next_x = 0
		out_next_y = 0
		out_red = 0
		out_green = 0
		out_blue = 0
		return
	}

	// horizontal FSM
	h_lim := hLimit(h_state)
	var next_h_count uint16
	var next_h_state uint8 = h_state
	var next_line_done bool = false

	if h_count < h_lim-1 {
		next_h_count = h_count + 1
	} else {
		next_h_count = 0
		switch h_state {
		case H_ACTIVE:
			next_h_state = H_FRONT
		case H_FRONT:
			next_h_state = H_PULSE
		case H_PULSE:
			next_h_state = H_BACK
		case H_BACK:
			next_h_state = H_ACTIVE
			next_line_done = true
		}
	}

	// vertical FSM (triggered by line_done)
	v_lim := vLimit(v_state)
	var next_v_count uint16 = v_count
	var next_v_state uint8 = v_state

	if next_line_done {
		if v_count < v_lim-1 {
			next_v_count = v_count + 1
		} else {
			next_v_count = 0
			switch v_state {
			case V_ACTIVE:
				next_v_state = V_FRONT
			case V_FRONT:
				next_v_state = V_PULSE
			case V_PULSE:
				next_v_state = V_BACK
			case V_BACK:
				next_v_state = V_ACTIVE
			}
		}
	}

	// update state registers
	h_state = next_h_state
	h_count = next_h_count
	v_state = next_v_state
	v_count = next_v_count
	line_done = next_line_done

	// output assignments
	out_clk = clock
	out_hsync = (h_state == H_PULSE)
	out_vsync = (v_state == V_PULSE)
	out_sync = false
	out_blank = (h_state != H_ACTIVE) || (v_state != V_ACTIVE)

	if h_state == H_ACTIVE {
		out_next_x = h_count
	} else {
		out_next_x = 0
	}
	if v_state == V_ACTIVE {
		out_next_y = v_count
	} else {
		out_next_y = 0
	}

	if h_state == H_ACTIVE && v_state == V_ACTIVE {
		out_red = color_in & 0xE0
		out_green = ((color_in >> 2) & 0x07) << 5
		out_blue = (color_in & 0x03) << 6
	} else {
		out_red = 0
		out_green = 0
		out_blue = 0
	}
}

func main() {}
