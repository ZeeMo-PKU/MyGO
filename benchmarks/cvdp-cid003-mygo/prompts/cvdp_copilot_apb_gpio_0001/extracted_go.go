package main

var (
	// Synchronization registers
	sync1 uint8
	sync2 uint8
	// Previous synchronized input for edge detection
	last_sync2 uint8
	// APB registers
	reg_out        uint32
	reg_enable     uint32
	reg_int_enable uint32
	reg_int_type   uint32
	reg_int_polarity uint32
	// Previous pclk for edge detection
	prev_pclk bool
)

// Outputs
var (
	out_prdata    uint32
	out_pready    bool
	out_pslverr   bool
	out_gpio_out  uint8
	out_gpio_enable uint8
	out_gpio_int  uint8
	out_comb_int  bool
)

func cvdp_copilot_apb_gpio(pclk bool, preset_n bool, psel bool, paddr uint8, penable bool, pwrite bool, pwdata uint32, gpio_in uint8) {
	if !preset_n {
		// Asynchronous reset: zero all registers
		sync1 = 0
		sync2 = 0
		last_sync2 = 0
		reg_out = 0
		reg_enable = 0
		reg_int_enable = 0
		reg_int_type = 0
		reg_int_polarity = 0
	} else {
		// Rising-edge clock sequential logic
		if pclk && !prev_pclk {
			// Update synchronizers
			last_sync2 = sync2
			sync2 = sync1
			sync1 = gpio_in

			// APB write
			if psel && penable && pwrite {
				addr := (paddr >> 2) & 0x3F
				switch addr {
				case 0x00: // GPIO Input Data (read-only, ignore)
				case 0x04:
					reg_out = pwdata
				case 0x08:
					reg_enable = pwdata
				case 0x0C:
					reg_int_enable = pwdata
				case 0x10:
					reg_int_type = pwdata
				case 0x14:
					reg_int_polarity = pwdata
				case 0x18: // Interrupt State (read-only, ignore)
				default: // Undefined, ignore
				}
			}
		}
	}

	// Combinational outputs
	out_pready = true
	out_pslverr = false

	// Interrupt generation
	var int_cond uint32 = 0
	for i := 0; i < 8; i++ {
		if ((reg_int_enable >> uint(i)) & 1) == 0 {
			continue
		}
		typ := (reg_int_type >> uint(i)) & 1
		pol := (reg_int_polarity >> uint(i)) & 1
		cur := (sync2 >> uint(i)) & 1
		last := (last_sync2 >> uint(i)) & 1
		cond := false
		if typ == 1 { // edge-sensitive
			if pol == 1 { // active-high: rising edge
				cond = (last == 0 && cur == 1)
			} else { // active-low: falling edge
				cond = (last == 1 && cur == 0)
			}
		} else { // level-sensitive
			if pol == 1 { // active-high
				cond = (cur == 1)
			} else { // active-low
				cond = (cur == 0)
			}
		}
		if cond {
			int_cond |= (1 << uint(i))
		}
	}
	out_gpio_int = uint8(int_cond & 0xFF)
	out_comb_int = (out_gpio_int != 0)

	// APB read
	var read_data uint32 = 0
	if psel && penable && !pwrite {
		addr := (paddr >> 2) & 0x3F
		switch addr {
		case 0x00:
			read_data = uint32(sync2)
		case 0x04:
			read_data = reg_out
		case 0x08:
			read_data = reg_enable
		case 0x0C:
			read_data = reg_int_enable
		case 0x10:
			read_data = reg_int_type
		case 0x14:
			read_data = reg_int_polarity
		case 0x18:
			read_data = uint32(out_gpio_int)
		default:
			read_data = 0
		}
	}
	out_prdata = read_data

	// GPIO output and enable
	out_gpio_out = uint8(reg_out & 0xFF)
	out_gpio_enable = uint8(reg_enable & 0xFF)

	prev_pclk = pclk
}

func main() {}
