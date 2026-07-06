package main

var out_destination_reg [64]uint8

func unpack_one_hot(sign bool, size bool, one_hot_selector uint8, source_reg [32]uint8) {
	// initialize output to zero
	for i := range out_destination_reg {
		out_destination_reg[i] = 0
	}

	switch one_hot_selector {
	case 1: // 3'b001: each 1-bit -> 8-bit
		for i := 0; i < 64; i++ {
			byteIndex := i / 8
			bitIndex := i % 8
			bit := (source_reg[byteIndex] >> bitIndex) & 1
			var val uint8
			if sign && bit == 1 {
				val = 0xFF
			} else {
				val = bit
			}
			out_destination_reg[i] = val
		}
	case 2: // 3'b010: each 2-bit -> 8-bit
		for i := 0; i < 64; i++ {
			offset := i * 2
			byteIndex := offset / 8
			bitIndex := offset % 8
			val2 := (source_reg[byteIndex] >> bitIndex) & 3
			var val uint8
			if sign && (val2&2) != 0 {
				val = val2 | 0xFC
			} else {
				val = val2 & 3
			}
			out_destination_reg[i] = val
		}
	case 4: // 3'b100: size‑dependent
		if size {
			// size=1: each 8-bit -> 16-bit
			for i := 0; i < 32; i++ {
				val8 := uint16(source_reg[i])
				var val16 uint16
				if sign && (val8&0x80) != 0 {
					val16 = val8 | 0xFF00
				} else {
					val16 = val8
				}
				out_destination_reg[i*2] = uint8(val16 & 0xFF)
				out_destination_reg[i*2+1] = uint8(val16 >> 8)
			}
		} else {
			// size=0: each 4-bit -> 8-bit
			for i := 0; i < 64; i++ {
				offset := i * 4
				byteIndex := offset / 8
				bitIndex := offset % 8
				val4 := (source_reg[byteIndex] >> bitIndex) & 0xF
				var val uint8
				if sign && (val4&8) != 0 {
					val = val4 | 0xF0
				} else {
					val = val4 & 0xF
				}
				out_destination_reg[i] = val
			}
		}
	default: // direct assignment, upper 256 bits stay zero
		for i := 0; i < 32; i++ {
			out_destination_reg[i] = source_reg[i]
		}
	}
}

func main() {}
