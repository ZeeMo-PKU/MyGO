package main

const (
	ADDR_WIDTH = 32
	DATA_WIDTH = 32
	STRB_WIDTH = DATA_WIDTH / 8 // 4
)

// Output globals
var (
	out_awready   bool
	out_wready    bool
	out_bvalid    bool
	out_bresp     uint8
	out_arready   bool
	out_rvalid    bool
	out_rresp     uint8
	out_rdata     uint32
	out_beat      uint32
	out_start     bool
	out_writeback bool
)

// Internal state
var (
	wrState      uint8 // 0: IDLE, 1: WAIT_DATA, 2: RESP
	rdState      uint8 // 0: IDLE, 1: RESP
	wrAddr       uint32
	wrData       uint32
	wrStrb       uint8
	rdAddr       uint32

	beatCounter   uint32
	startFlag     bool
	writebackFlag bool
	doneFlag      bool
)

func axi_register(clk_i bool, rst_n_i bool,
	awaddr_i uint32, awvalid_i bool,
	wdata_i uint32, wvalid_i bool, wstrb_i uint8,
	bready_i bool,
	araddr_i uint32, arvalid_i bool,
	rready_i bool,
	done_i bool) {

	// Asynchronous reset (active low)
	if !rst_n_i {
		wrState = 0
		rdState = 0
		beatCounter = 0
		startFlag = false
		writebackFlag = false
		doneFlag = false

		out_awready = true
		out_wready = false
		out_bvalid = false
		out_bresp = 0
		out_arready = true
		out_rvalid = false
		out_rresp = 0
		out_rdata = 0
		out_beat = 0
		out_start = false
		out_writeback = false
		return
	}

	// Capture done_i (level sensitive, sets done flag)
	if done_i {
		doneFlag = true
	}

	// Write channel state machine
	switch wrState {
	case 0: // IDLE
		out_awready = true
		out_wready = false
		out_bvalid = false
		if awvalid_i && out_awready {
			wrAddr = awaddr_i
			wrState = 1
		}
	case 1: // WAIT_DATA
		out_awready = false
		out_wready = true
		out_bvalid = false
		if wvalid_i && out_wready {
			wrData = wdata_i
			wrStrb = wstrb_i

			// Process write
			switch wrAddr {
			case 0x100: // Beat counter
				if wrStrb == 0xF { // Full write only
					beatCounter = wrData & 0xFFFFF
				}
			case 0x200: // Start
				if (wrStrb & 1) != 0 {
					startFlag = (wrData & 1) != 0
				}
			case 0x300: // Done (clear on write of 1)
				if (wrStrb & 1) != 0 {
					if (wrData & 1) != 0 {
						doneFlag = false
					}
				}
			case 0x400: // Writeback
				if (wrStrb & 1) != 0 {
					writebackFlag = (wrData & 1) != 0
				}
				// ID and default: no change
			}

			// Compute write response
			resp := uint8(0) // OKAY
			if wrAddr == 0x500 {
				resp = 2 // SLVERR (read-only)
			} else if wrAddr != 0x100 && wrAddr != 0x200 &&
				wrAddr != 0x300 && wrAddr != 0x400 {
				resp = 2 // SLVERR (invalid)
			}
			out_bresp = resp
			wrState = 2
		}
	case 2: // RESP
		out_awready = false
		out_wready = false
		out_bvalid = true
		if bready_i && out_bvalid {
			wrState = 0
			out_bvalid = false
		}
	}

	// Read channel state machine
	switch rdState {
	case 0: // IDLE
		out_arready = true
		out_rvalid = false
		if arvalid_i && out_arready {
			rdAddr = araddr_i
			rdState = 1
		}
	case 1: // RESP
		out_arready = false
		out_rvalid = true

		var rdata uint32
		var rresp uint8 = 0
		switch rdAddr {
		case 0x100:
			rdata = beatCounter & 0xFFFFF
		case 0x200:
			if startFlag {
				rdata = 1
			}
		case 0x300:
			if doneFlag {
				rdata = 1
			}
		case 0x400:
			if writebackFlag {
				rdata = 1
			}
		case 0x500:
			rdata = 0x00010001
		default:
			rdata = 0
			rresp = 2 // SLVERR
		}
		if rdAddr == 0x100 || rdAddr == 0x200 || rdAddr == 0x300 ||
			rdAddr == 0x400 || rdAddr == 0x500 {
			rresp = 0 // OKAY
		}
		out_rdata = rdata
		out_rresp = rresp

		if rready_i && out_rvalid {
			rdState = 0
			out_rvalid = false
		}
	}

	// Continuous assignments for beat, start, writeback outputs
	out_beat = beatCounter & 0xFFFFF
	out_start = startFlag
	out_writeback = writebackFlag
}

func main() {}
