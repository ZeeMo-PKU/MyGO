package main

var (
	state uint8
	beat_cnt uint8
	temp_extracted_field uint16
)

var (
	out_ack bool
	out_field uint16
	out_field_vld bool
)

const (
	IDLE = 0
	EXTRACTING = 1
	DONE = 2
	FAIL_FINAL = 3
)

// field_extract implements the Ethernet packet parser at the second beat.
func field_extract(clk bool, rst bool, vld bool, sof bool, eof bool, data uint32) {
	// Fixed acknowledge – always ready.
	out_ack = true

	// Synchronous reset (active high).
	if rst {
		state = IDLE
		beat_cnt = 0
		temp_extracted_field = 0
		out_field = 0
		out_field_vld = false
		return
	}

	// Output logic – driven combinationaly by current state.
	switch state {
	case IDLE:
		out_field = 0
		out_field_vld = false
	case EXTRACTING:
		out_field = 0
		out_field_vld = false
	case DONE:
		out_field = temp_extracted_field
		out_field_vld = true
	case FAIL_FINAL:
		out_field = 0
		out_field_vld = false
	default:
		out_field = 0
		out_field_vld = false
	}

	// Next‑state logic.
	switch state {
	case IDLE:
		if vld && sof {
			state = EXTRACTING
			beat_cnt = 1 // first beat counted
		}
	case EXTRACTING:
		if vld {
			if beat_cnt == 1 { // second beat reached
				temp_extracted_field = uint16(data >> 16) // most significant two bytes
				state = DONE
			} else {
				beat_cnt = beat_cnt + 1
			}
		}
	case DONE:
		if eof {
			state = FAIL_FINAL
		}
	case FAIL_FINAL:
		state = IDLE
	}
}

func main() {}
