package main

var out_morse_out   uint16
var out_morse_length uint8

func morse_encoder(ascii_in uint8) {
	switch ascii_in {
	case 0x41: // 'A'
		out_morse_out = 0x1  // 10'b01
		out_morse_length = 2
	case 0x42: // 'B'
		out_morse_out = 0x8  // 10'b1000
		out_morse_length = 4
	case 0x43: // 'C'
		out_morse_out = 0xA  // 10'b1010
		out_morse_length = 4
	case 0x44: // 'D'
		out_morse_out = 0x4  // 10'b100
		out_morse_length = 3
	case 0x45: // 'E'
		out_morse_out = 0x0  // 10'b0
		out_morse_length = 1
	case 0x46: // 'F'
		out_morse_out = 0x2  // 10'b0010
		out_morse_length = 4
	case 0x47: // 'G'
		out_morse_out = 0x6  // 10'b110
		out_morse_length = 3
	case 0x48: // 'H'
		out_morse_out = 0x0  // 10'b0000
		out_morse_length = 4
	case 0x49: // 'I'
		out_morse_out = 0x0  // 10'b00
		out_morse_length = 2
	case 0x4A: // 'J'
		out_morse_out = 0x7  // 10'b0111
		out_morse_length = 4
	case 0x4B: // 'K'
		out_morse_out = 0x5  // 10'b101
		out_morse_length = 3
	case 0x4C: // 'L'
		out_morse_out = 0x4  // 10'b0100
		out_morse_length = 4
	case 0x4D: // 'M'
		out_morse_out = 0x3  // 10'b11
		out_morse_length = 2
	case 0x4E: // 'N'
		out_morse_out = 0x2  // 10'b10
		out_morse_length = 2
	case 0x4F: // 'O'
		out_morse_out = 0x7  // 10'b111
		out_morse_length = 3
	case 0x50: // 'P'
		out_morse_out = 0x6  // 10'b0110
		out_morse_length = 4
	case 0x51: // 'Q'
		out_morse_out = 0xD  // 10'b1101
		out_morse_length = 4
	case 0x52: // 'R'
		out_morse_out = 0x2  // 10'b010
		out_morse_length = 3
	case 0x53: // 'S'
		out_morse_out = 0x0  // 10'b000
		out_morse_length = 3
	case 0x54: // 'T'
		out_morse_out = 0x1  // 10'b1
		out_morse_length = 1
	case 0x55: // 'U'
		out_morse_out = 0x1  // 10'b001
		out_morse_length = 3
	case 0x56: // 'V'
		out_morse_out = 0x1  // 10'b0001
		out_morse_length = 4
	case 0x57: // 'W'
		out_morse_out = 0x3  // 10'b011
		out_morse_length = 3
	case 0x58: // 'X'
		out_morse_out = 0x9  // 10'b1001
		out_morse_length = 4
	case 0x59: // 'Y'
		out_morse_out = 0xB  // 10'b1011
		out_morse_length = 4
	case 0x5A: // 'Z'
		out_morse_out = 0xC  // 10'b1100
		out_morse_length = 4
	case 0x30: // '0'
		out_morse_out = 0x1F // 10'b11111
		out_morse_length = 5
	case 0x31: // '1'
		out_morse_out = 0x0F // 10'b01111
		out_morse_length = 5
	case 0x32: // '2'
		out_morse_out = 0x07 // 10'b00111
		out_morse_length = 5
	case 0x33: // '3'
		out_morse_out = 0x03 // 10'b00011
		out_morse_length = 5
	case 0x34: // '4'
		out_morse_out = 0x01 // 10'b00001
		out_morse_length = 5
	case 0x35: // '5'
		out_morse_out = 0x00 // 10'b00000
		out_morse_length = 5
	case 0x36: // '6'
		out_morse_out = 0x10 // 10'b10000
		out_morse_length = 5
	case 0x37: // '7'
		out_morse_out = 0x18 // 10'b11000
		out_morse_length = 5
	case 0x38: // '8'
		out_morse_out = 0x1C // 10'b11100
		out_morse_length = 5
	case 0x39: // '9'
		out_morse_out = 0x1E // 10'b11110
		out_morse_length = 5
	default:
		out_morse_out = 0
		out_morse_length = 0
	}
}

func main() {}
