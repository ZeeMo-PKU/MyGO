package main

var state uint8 = S_IDLE

const (
	S_IDLE           = 0
	S_GOT_8_BYTES    = 1
	S_RECV_CHECKSUM  = 2
	S_BUILD_RESPONSE = 3
	S_SEND_FIRST_BYTE = 4
	S_RESPONSE_READY = 5
)

var byte_cnt uint8 = 0
var buf [8]uint8
var stored_sum uint8
var num1 uint16
var num2 uint16
var opcode uint8
var tx_buf [5]uint8
var tx_index uint8 = 0

var out_tx_start_o bool
var out_tx_data_8_o uint8

func packet_controller(clk bool, rst bool, rx_valid_i bool, rx_data_8_i uint8, tx_done_tick_i bool) {
	if rst {
		state = S_IDLE
		byte_cnt = 0
		stored_sum = 0
		num1 = 0
		num2 = 0
		opcode = 0
		tx_index = 0
		out_tx_start_o = false
		out_tx_data_8_o = 0
		return
	}

	// default outputs
	out_tx_start_o = false
	out_tx_data_8_o = 0

	switch state {
	case S_IDLE:
		if rx_valid_i {
			buf[byte_cnt] = rx_data_8_i
			byte_cnt++
			if byte_cnt == 8 {
				state = S_GOT_8_BYTES
				byte_cnt = 0
			}
		}
	case S_GOT_8_BYTES:
		header16 := (uint16(buf[0]) << 8) | uint16(buf[1])
		if header16 == 0xBACD {
			var sum uint8 = 0
			for i := 0; i < 8; i++ {
				sum += buf[i]
			}
			stored_sum = sum
			state = S_RECV_CHECKSUM
		} else {
			state = S_IDLE
		}
	case S_RECV_CHECKSUM:
		if stored_sum == 0 {
			num1 = (uint16(buf[2]) << 8) | uint16(buf[3])
			num2 = (uint16(buf[4]) << 8) | uint16(buf[5])
			opcode = buf[6]
			state = S_BUILD_RESPONSE
		} else {
			state = S_IDLE
		}
	case S_BUILD_RESPONSE:
		var result uint16
		if opcode == 0 {
			result = num1 + num2
		} else if opcode == 1 {
			result = num1 - num2
		} else {
			result = 0
		}
		tx_buf[0] = 0xAB
		tx_buf[1] = 0xCD
		tx_buf[2] = uint8(result >> 8)
		tx_buf[3] = uint8(result & 0xFF)
		sum_hdr := uint8(0xAB + 0xCD + uint8(result>>8) + uint8(result&0xFF))
		tx_buf[4] = uint8(0 - sum_hdr)
		tx_index = 0
		state = S_SEND_FIRST_BYTE
	case S_SEND_FIRST_BYTE:
		out_tx_start_o = true
		out_tx_data_8_o = tx_buf[0]
		if tx_done_tick_i {
			tx_index = 1
			state = S_RESPONSE_READY
		}
	case S_RESPONSE_READY:
		out_tx_start_o = true
		out_tx_data_8_o = tx_buf[tx_index]
		if tx_done_tick_i {
			if tx_index == 4 {
				state = S_IDLE
			} else {
				tx_index++
			}
		}
	}
}

func main() {}
