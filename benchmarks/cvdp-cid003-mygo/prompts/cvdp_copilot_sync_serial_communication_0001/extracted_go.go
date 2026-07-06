package main

// Internal state registers
var (
	// Transmitter (TX) registers
	tx_idle   bool
	tx_active bool
	tx_sel    uint8
	tx_count  uint8
	tx_shift  uint64

	// Receiver (RX) registers
	rx_idle     bool
	rx_count    uint8
	rx_shift    uint64
	rx_done_reg bool
	rx_sel      uint8
	rx_data_out uint64
)

// Top-level outputs (as required by MyGO)
var (
	out_data_out uint64
	out_done     bool
)

func sync_serial_communication_tx_rx(clk bool, reset_n bool, data_in uint64, sel uint8) {
	if !reset_n {
		// Asynchronous reset (active LOW)
		tx_idle = true
		tx_active = false
		tx_sel = 0
		tx_count = 0
		tx_shift = 0

		rx_idle = true
		rx_count = 0
		rx_shift = 0
		rx_done_reg = false
		rx_sel = 0
		rx_data_out = 0
	} else if clk {
		// ----- Combinational signals from current state -----
		serial_out_i := (tx_shift & 1) != 0 // LSB first

		// ----- Transmitter (TX) next-state logic -----
		next_tx_idle := tx_idle
		next_tx_active := tx_active
		next_tx_sel := tx_sel
		next_tx_count := tx_count
		next_tx_shift := tx_shift

		if tx_idle {
			// Start a new transmission only for valid non-zero width
			if sel >= 1 && sel <= 4 {
				next_tx_idle = false
				next_tx_active = true
				next_tx_sel = sel
				next_tx_count = 0
				next_tx_shift = data_in
			}
		} else {
			// Currently transmitting
			var bits_to_send uint8
			switch tx_sel {
			case 1:
				bits_to_send = 8
			case 2:
				bits_to_send = 16
			case 3:
				bits_to_send = 32
			case 4:
				bits_to_send = 64
			}

			if tx_count < bits_to_send {
				next_tx_shift = tx_shift >> 1
				next_tx_count = tx_count + 1
			} else {
				// Transmission complete
				next_tx_active = false
				next_tx_idle = true
			}
		}

		// ----- Receiver (RX) next-state logic -----
		next_rx_idle := rx_idle
		next_rx_count := rx_count
		next_rx_shift := rx_shift
		next_rx_done_reg := rx_done_reg
		next_rx_sel := rx_sel
		update_data_out := false
		var new_data_out uint64

		// RX is enabled when TX is active (gated serial_clk)
		if tx_active {
			if rx_idle {
				// Begin reception
				if sel >= 1 && sel <= 4 {
					next_rx_idle = false
					next_rx_count = 0
					next_rx_shift = 0
					next_rx_done_reg = false
					next_rx_sel = sel
				}
			} else {
				// Shift in one bit (LSB first)
				bit_in := serial_out_i
				var bitUint uint64
				if bit_in {
					bitUint = 1
				} else {
					bitUint = 0
				}

				switch rx_sel {
				case 1:
					next_rx_shift = (rx_shift >> 1) | (bitUint << 7)
				case 2:
					next_rx_shift = (rx_shift >> 1) | (bitUint << 15)
				case 3:
					next_rx_shift = (rx_shift >> 1) | (bitUint << 31)
				case 4:
					next_rx_shift = (rx_shift >> 1) | (bitUint << 63)
				}

				next_rx_count = rx_count + 1

				var bits_needed uint8
				switch rx_sel {
				case 1:
					bits_needed = 8
				case 2:
					bits_needed = 16
				case 3:
					bits_needed = 32
				case 4:
					bits_needed = 64
				}

				if next_rx_count == bits_needed {
					next_rx_done_reg = true
					next_rx_idle = true
					update_data_out = true
					switch rx_sel {
					case 1:
						new_data_out = next_rx_shift & 0xFF
					case 2:
						new_data_out = next_rx_shift & 0xFFFF
					case 3:
						new_data_out = next_rx_shift & 0xFFFFFFFF
					case 4:
						new_data_out = next_rx_shift
					default:
						new_data_out = 0
					}
				}
			}
		} else {
			// serial_clk inactive – clear done after it was asserted
			next_rx_done_reg = false
		}

		// ----- Update registers -----
		tx_idle = next_tx_idle
		tx_active = next_tx_active
		tx_sel = next_tx_sel
		tx_count = next_tx_count
		tx_shift = next_tx_shift

		rx_idle = next_rx_idle
		rx_count = next_rx_count
		rx_shift = next_rx_shift
		rx_done_reg = next_rx_done_reg
		rx_sel = next_rx_sel
		if update_data_out {
			rx_data_out = new_data_out
		}
	}

	// Drive top-level outputs
	out_data_out = rx_data_out
	out_done = rx_done_reg
}

func main() {}
