package main

var out_data_out uint64

func reverse8(b uint8) uint8 {
	// Reverse bits of an 8-bit value
	b = ((b & 0x55) << 1) | ((b >> 1) & 0x55)
	b = ((b & 0x33) << 2) | ((b >> 2) & 0x33)
	b = ((b & 0x0F) << 4) | ((b >> 4) & 0x0F)
	return b
}

func reverse16(b uint16) uint16 {
	// Reverse bits of a 16-bit value
	b = ((b & 0x5555) << 1) | ((b >> 1) & 0x5555)
	b = ((b & 0x3333) << 2) | ((b >> 2) & 0x3333)
	b = ((b & 0x0F0F) << 4) | ((b >> 4) & 0x0F0F)
	b = ((b & 0x00FF) << 8) | ((b >> 8) & 0x00FF)
	return b
}

func reverse32(b uint32) uint32 {
	// Reverse bits of a 32-bit value
	b = ((b & 0x55555555) << 1) | ((b >> 1) & 0x55555555)
	b = ((b & 0x33333333) << 2) | ((b >> 2) & 0x33333333)
	b = ((b & 0x0F0F0F0F) << 4) | ((b >> 4) & 0x0F0F0F0F)
	b = ((b & 0x00FF00FF) << 8) | ((b >> 8) & 0x00FF00FF)
	b = ((b & 0x0000FFFF) << 16) | ((b >> 16) & 0x0000FFFF)
	return b
}

func reverse64(b uint64) uint64 {
	// Reverse bits of a 64-bit value
	b = ((b & 0x5555555555555555) << 1) | ((b >> 1) & 0x5555555555555555)
	b = ((b & 0x3333333333333333) << 2) | ((b >> 2) & 0x3333333333333333)
	b = ((b & 0x0F0F0F0F0F0F0F0F) << 4) | ((b >> 4) & 0x0F0F0F0F0F0F0F0F)
	b = ((b & 0x00FF00FF00FF00FF) << 8) | ((b >> 8) & 0x00FF00FF00FF00FF)
	b = ((b & 0x0000FFFF0000FFFF) << 16) | ((b >> 16) & 0x0000FFFF0000FFFF)
	b = ((b & 0x00000000FFFFFFFF) << 32) | ((b >> 32) & 0x00000000FFFFFFFF)
	return b
}

// nbit_swizzling performs selective bit-reversal based on sel.
// This implementation assumes DATA_WIDTH = 64.
func nbit_swizzling(data_in uint64, sel uint8) {
	switch sel {
	case 0:
		out_data_out = reverse64(data_in)
	case 1:
		hi := reverse32(uint32(data_in >> 32))
		lo := reverse32(uint32(data_in & 0xFFFFFFFF))
		out_data_out = (uint64(hi) << 32) | uint64(lo)
	case 2:
		// Four 16-bit quarters: q3 (msb) .. q0 (lsb)
		q3 := reverse16(uint16(data_in >> 48))
		q2 := reverse16(uint16((data_in >> 32) & 0xFFFF))
		q1 := reverse16(uint16((data_in >> 16) & 0xFFFF))
		q0 := reverse16(uint16(data_in & 0xFFFF))
		out_data_out = (uint64(q3) << 48) | (uint64(q2) << 32) | (uint64(q1) << 16) | uint64(q0)
	case 3:
		// Eight 8-bit bytes
		b0 := reverse8(uint8(data_in))
		b1 := reverse8(uint8(data_in >> 8))
		b2 := reverse8(uint8(data_in >> 16))
		b3 := reverse8(uint8(data_in >> 24))
		b4 := reverse8(uint8(data_in >> 32))
		b5 := reverse8(uint8(data_in >> 40))
		b6 := reverse8(uint8(data_in >> 48))
		b7 := reverse8(uint8(data_in >> 56))
		out_data_out = (uint64(b7) << 56) | (uint64(b6) << 48) | (uint64(b5) << 40) | (uint64(b4) << 32) |
			(uint64(b3) << 24) | (uint64(b2) << 16) | (uint64(b1) << 8) | uint64(b0)
	default:
		// Default: pass through
		out_data_out = data_in
	}
}

func main() {}
