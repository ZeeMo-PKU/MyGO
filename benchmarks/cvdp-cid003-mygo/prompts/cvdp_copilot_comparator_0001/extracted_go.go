package main

var out_o_greater bool
var out_o_less bool
var out_o_equal bool

func signed_unsigned_comparator(i_A uint8, i_B uint8, i_enable bool, i_mode bool) {
	if !i_enable {
		out_o_greater = false
		out_o_less = false
		out_o_equal = false
		return
	}

	if i_mode {
		// signed mode (2's complement, 5‑bit)
		sa := int8(i_A & 0x0F)
		if i_A&0x10 != 0 {
			sa -= 16
		}
		sb := int8(i_B & 0x0F)
		if i_B&0x10 != 0 {
			sb -= 16
		}
		out_o_greater = sa > sb
		out_o_less = sa < sb
		out_o_equal = sa == sb
	} else {
		// magnitude (unsigned) mode – ignore the sign bit, compare as unsigned
		ua := i_A & 0x1F
		ub := i_B & 0x1F
		out_o_greater = ua > ub
		out_o_less = ua < ub
		out_o_equal = ua == ub
	}
}

func main() {}
