package main

var state uint8 = 0 // 0=IDLE, 1=BUSY, 2=DONE
var n_reg uint8
var cnt uint8
var product_reg uint64

var out_busy bool
var out_fact uint64
var out_done bool

func factorial(clk bool, arst_n bool, num_in uint8, start bool) {
	if !arst_n {
		state = 0
		n_reg = 0
		cnt = 0
		product_reg = 1
		out_busy = false
		out_fact = 0
		out_done = false
		return
	}

	if clk {
		switch state {
		case 0: // IDLE
			out_busy = false
			out_done = false
			if start {
				n_reg = num_in
				if num_in == 0 {
					state = 2 // DONE
					product_reg = 1
				} else {
					cnt = num_in
					product_reg = 1
					state = 1 // BUSY
				}
			}
		case 1: // BUSY
			out_busy = true
			out_done = false
			if cnt > 0 {
				product_reg = product_reg * uint64(cnt)
				cnt = cnt - 1
				if cnt == 0 {
					state = 2 // DONE
				}
			} else {
				state = 2 // DONE
			}
		case 2: // DONE
			out_busy = false
			out_done = true
			out_fact = product_reg
			state = 0 // IDLE
		default:
			state = 0
			out_busy = false
			out_done = false
		}
	}
}

func main() {}
