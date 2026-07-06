package main

// state register
var state uint8

// previous hclk for edge detection
var prev_hclk bool

// latched Wishbone transaction attributes
var latched_addr uint32
var latched_sel  uint8
var latched_we   bool
var latched_wdata uint32

// captured read data after conversion
var read_data_reg uint32

// outputs
var out_data_o  uint32
var out_ack_o   bool
var out_htrans  uint8
var out_hsize   uint8
var out_hburst  uint8
var out_hwrite  bool
var out_haddr   uint32
var out_hwdata  uint32

// count trailing 1-bits in a 4-bit sel value
func trailing_ones(sel uint8) uint8 {
	if sel&1 == 0 {
		return 0
	}
	if sel&2 == 0 {
		return 1
	}
	if sel&4 == 0 {
		return 2
	}
	if sel&8 == 0 {
		return 3
	}
	return 4
}

// compute AHB hsize from Wishbone sel_i
func compute_hsize(sel uint8) uint8 {
	cnt := trailing_ones(sel)
	switch cnt {
	case 4:
		return 2 // 32-bit
	case 2:
		return 1 // 16-bit
	default:
		return 0 // 8-bit
	}
}

// endian conversion for write data: Wishbone little-endian -> AHB big-endian
func convert_wr_endian(data uint32, sel uint8) uint32 {
	cnt := trailing_ones(sel)
	switch cnt {
	case 4:
		return (data&0xFF)<<24 | ((data>>8)&0xFF)<<16 | ((data>>16)&0xFF)<<8 | ((data>>24)&0xFF)
	case 2:
		if sel == 0x03 {
			// low halfword: swap byte0 and byte1
			return (data & 0xFFFF0000) | ((data&0xFF)<<8) | ((data>>8)&0xFF)
		} else if sel == 0x0C {
			// high halfword: swap byte2 and byte3
			return (data & 0x0000FFFF) | ((data>>8)&0xFF000000) | ((data&0xFF0000)<<8)
		}
		return data // unexpected pattern, no conversion
	default:
		return data // byte, no conversion
	}
}

// endian conversion for read data: AHB big-endian -> Wishbone little-endian
// same operation as write conversion
func convert_rd_endian(data uint32, sel uint8) uint32 {
	return convert_wr_endian(data, sel)
}

// Hardware entry function
func wishbone_to_ahb_bridge(
	clk_i   bool,
	rst_i   bool,
	cyc_i   bool,
	stb_i   bool,
	sel_i   uint8,
	we_i    bool,
	addr_i  uint32,
	data_i  uint32,
	hclk    bool,
	hreset_n bool,
	hrdata  uint32,
	hresp   uint8,
	hready  bool,
) {
	// rising edge on hclk (ignore clk_i)
	posedge_hclk := hclk && !prev_hclk
	prev_hclk = hclk

	// asynchronous reset (either reset active low)
	if !rst_i || !hreset_n {
		state = 0
		latched_addr  = 0
		latched_sel   = 0
		latched_we    = false
		latched_wdata = 0
		read_data_reg = 0
	} else if posedge_hclk {
		switch state {
		case 0: // IDLE
			if cyc_i && stb_i {
				latched_addr  = addr_i
				latched_sel   = sel_i
				latched_we    = we_i
				latched_wdata = data_i
				state = 1 // ADDR
			}
		case 1: // ADDR phase
			state = 2 // DATA
		case 2: // DATA phase
			if hready {
				if !latched_we {
					read_data_reg = convert_rd_endian(hrdata, latched_sel)
				}
				state = 0 // back to IDLE
			}
		}
	}

	// combinational outputs

	// AHB outputs
	if state == 1 { // address phase drives NONSEQ
		out_htrans = 2 // 2'b10
	} else {
		out_htrans = 0 // IDLE
	}
	out_hburst = 0 // single transfer always

	if state == 1 || state == 2 {
		out_hsize  = compute_hsize(latched_sel)
		out_hwrite = latched_we
		out_haddr  = latched_addr
		out_hwdata = convert_wr_endian(latched_wdata, latched_sel)
	} else {
		out_hsize  = 0
		out_hwrite = false
		out_haddr  = 0
		out_hwdata = 0
	}

	// Wishbone outputs
	out_data_o = read_data_reg
	out_ack_o  = (state == 2 && hready)
}

func main() {}
