package main

var out_serial_out bool
var tmp uint8
var sreg uint8
var bit_cnt uint8

func piso_8bit(clk bool, rst bool) {
	if !rst {
		out_serial_out = false
		tmp = 0x01
		sreg = 0x01
		bit_cnt = 0
		return
	}
	// posedge clk
	out_serial_out = (sreg & 0x80) != 0
	if bit_cnt == 7 {
		tmp = (tmp + 1) & 0xFF
		sreg = tmp
		bit_cnt = 0
	} else {
		sreg = (sreg << 1) & 0xFF
		bit_cnt = bit_cnt + 1
	}
}

func main() {}
