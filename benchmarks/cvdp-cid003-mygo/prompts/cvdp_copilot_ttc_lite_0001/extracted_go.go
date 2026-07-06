package main

var count uint16
var match_value uint16
var reload_value uint16
var enable bool
var interval_mode bool
var interrupt_enable bool
var match_flag bool

var out_axi_rdata uint32
var out_interrupt bool

func ttc_counter_lite(clk bool, reset bool, axi_addr uint8, axi_wdata uint32, axi_write_en bool, axi_read_en bool) {
	if reset {
		count = 0
		match_value = 0
		reload_value = 0
		enable = false
		interval_mode = false
		interrupt_enable = false
		match_flag = false
		out_axi_rdata = 0
		out_interrupt = false
		return
	}

	// AXI write operations
	if axi_write_en {
		if axi_addr == 0x1 {
			match_value = uint16(axi_wdata)
		} else if axi_addr == 0x2 {
			reload_value = uint16(axi_wdata)
		} else if axi_addr == 0x3 {
			enable = (axi_wdata & 1) != 0
			interval_mode = (axi_wdata & 2) != 0
			interrupt_enable = (axi_wdata & 4) != 0
		} else if axi_addr == 0x4 {
			match_flag = false
		}
	}

	// Timer counter logic
	if enable {
		if count == match_value {
			match_flag = true
			if interval_mode {
				count = reload_value
			}
			// in non‑interval mode counter holds at match_value
		} else {
			count++
		}
	}

	// Interrupt output
	out_interrupt = match_flag && interrupt_enable

	// AXI read output
	if axi_read_en {
		if axi_addr == 0x0 {
			out_axi_rdata = uint32(count)
		} else if axi_addr == 0x1 {
			out_axi_rdata = uint32(match_value)
		} else if axi_addr == 0x2 {
			out_axi_rdata = uint32(reload_value)
		} else if axi_addr == 0x3 {
			var ctrl uint32
			if enable {
				ctrl |= 1
			}
			if interval_mode {
				ctrl |= 2
			}
			if interrupt_enable {
				ctrl |= 4
			}
			out_axi_rdata = ctrl
		} else if axi_addr == 0x4 {
			var status uint32
			if match_flag {
				status |= 1
			}
			out_axi_rdata = status
		} else {
			out_axi_rdata = 0
		}
	} else {
		out_axi_rdata = 0
	}
}

func main() {
}
