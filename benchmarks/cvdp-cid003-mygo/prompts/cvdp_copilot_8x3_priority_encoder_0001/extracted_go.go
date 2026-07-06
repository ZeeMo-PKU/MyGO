package main

var out_out uint8

func priority_encoder_8x3(in uint8) {
	if in&0x80 != 0 {
		out_out = 7
	} else if in&0x40 != 0 {
		out_out = 6
	} else if in&0x20 != 0 {
		out_out = 5
	} else if in&0x10 != 0 {
		out_out = 4
	} else if in&0x08 != 0 {
		out_out = 3
	} else if in&0x04 != 0 {
		out_out = 2
	} else if in&0x02 != 0 {
		out_out = 1
	} else if in&0x01 != 0 {
		out_out = 0
	} else {
		out_out = 0
	}
}

func main() {}
