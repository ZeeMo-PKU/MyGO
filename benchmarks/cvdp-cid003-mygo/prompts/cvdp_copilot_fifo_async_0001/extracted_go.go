package main

const (
	DATA_WIDTH = 8  // data width in bits
	DEPTH      = 8  // FIFO depth (must be power of 2)
	PTR_WIDTH  = 4  // log2(DEPTH)+1, must be adjusted when DEPTH changes
)

var out_r_data uint64
var out_w_full bool
var out_r_empty bool

func binToGray(bin uint) uint {
	return bin ^ (bin >> 1)
}

func grayToBin(gray uint, width int) uint {
	bin := gray
	for i := 0; i < width; i++ {
		bin ^= (bin >> 1)
	}
	// mask to width bits (optional, but safe)
	return bin & ((1 << width) - 1)
}

func fifo_async(w_clk bool, w_rst bool, w_inc bool, w_data uint64, r_clk bool, r_rst bool, r_inc bool) {
	var wptr_bin uint
	var rptr_bin uint
	var wptr_gray uint
	var rptr_gray uint
	var w_rptr_sync1, w_rptr_sync2 uint
	var r_wptr_sync1, r_wptr_sync2 uint
	var mem [DEPTH]uint64
	var rdata_reg uint64

	// Write clock domain
	if w_clk {
		// 2‑stage synchronizer for read pointer
		w_rptr_sync1 = rptr_gray
		w_rptr_sync2 = w_rptr_sync1

		if w_rst {
			wptr_bin = 0
		} else if w_inc && !out_w_full {
			mem[wptr_bin&(DEPTH-1)] = w_data
			wptr_bin = (wptr_bin + 1) & ((1 << PTR_WIDTH) - 1)
		}
		wptr_gray = binToGray(wptr_bin)
	}

	// Read clock domain
	if r_clk {
		// 2‑stage synchronizer for write pointer
		r_wptr_sync1 = wptr_gray
		r_wptr_sync2 = r_wptr_sync1

		if r_rst {
			rptr_bin = 0
			rdata_reg = 0
		} else if r_inc && !out_r_empty {
			rdata_reg = mem[rptr_bin&(DEPTH-1)]
			rptr_bin = (rptr_bin + 1) & ((1 << PTR_WIDTH) - 1)
		}
		rptr_gray = binToGray(rptr_bin)
	}

	// Combinational flags
	w_rptr_sync_bin := grayToBin(w_rptr_sync2, PTR_WIDTH)
	// Full: write pointer one full cycle ahead of synchronized read pointer
	out_w_full = (wptr_bin == (w_rptr_sync_bin ^ (1 << (PTR_WIDTH - 1))))

	r_wptr_sync_bin := grayToBin(r_wptr_sync2, PTR_WIDTH)
	// Empty: synchronized write pointer equals read pointer
	out_r_empty = (rptr_bin == r_wptr_sync_bin)

	out_r_data = rdata_reg
}

func main() {}
