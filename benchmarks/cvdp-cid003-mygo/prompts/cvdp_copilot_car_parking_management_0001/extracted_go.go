package main

var out_available_spaces uint8
var out_count_car uint8
var out_led_status bool
var out_seven_seg_display_available_tens uint8
var out_seven_seg_display_available_units uint8
var out_seven_seg_display_count_tens uint8
var out_seven_seg_display_count_units uint8

var reg_available uint8
var reg_count uint8
var reg_state uint8
var prev_clk bool

const TOTAL_SPACES uint8 = 12

const (
	IDLE  uint8 = 0
	ENTRY uint8 = 1
	EXIT  uint8 = 2
	FULL  uint8 = 3
)

func sevenSeg(d uint8) uint8 {
	switch d {
	case 0:
		return 0b1111110
	case 1:
		return 0b0110000
	case 2:
		return 0b1101101
	case 3:
		return 0b1111001
	case 4:
		return 0b0110011
	case 5:
		return 0b1011011
	case 6:
		return 0b1011111
	case 7:
		return 0b1110000
	case 8:
		return 0b1111111
	case 9:
		return 0b1111011
	default:
		return 0b0000000
	}
}

func car_parking_system(clk bool, reset bool, vehicle_entry_sensor bool, vehicle_exit_sensor bool) {
	if reset {
		reg_available = TOTAL_SPACES
		reg_count = 0
		reg_state = IDLE
	} else if clk && !prev_clk {
		switch reg_state {
		case IDLE:
			if vehicle_entry_sensor && reg_available > 0 {
				reg_available--
				reg_count++
				reg_state = ENTRY
			} else if vehicle_exit_sensor && reg_count > 0 {
				reg_available++
				reg_count--
				reg_state = EXIT
			} else if reg_available == 0 {
				reg_state = FULL
			} else {
				reg_state = IDLE
			}
		case ENTRY:
			reg_state = IDLE
		case EXIT:
			reg_state = IDLE
		case FULL:
			if vehicle_exit_sensor && reg_count > 0 {
				reg_available++
				reg_count--
				reg_state = IDLE
			} else if reg_available == 0 {
				reg_state = FULL
			} else {
				reg_state = IDLE
			}
		}
	}
	prev_clk = clk

	out_available_spaces = reg_available
	out_count_car = reg_count
	out_led_status = reg_available > 0

	avail_tens := uint8(reg_available / 10)
	avail_units := uint8(reg_available % 10)
	count_tens := uint8(reg_count / 10)
	count_units := uint8(reg_count % 10)

	out_seven_seg_display_available_tens = sevenSeg(avail_tens)
	out_seven_seg_display_available_units = sevenSeg(avail_units)
	out_seven_seg_display_count_tens = sevenSeg(count_tens)
	out_seven_seg_display_count_units = sevenSeg(count_units)
}

func main() {}
