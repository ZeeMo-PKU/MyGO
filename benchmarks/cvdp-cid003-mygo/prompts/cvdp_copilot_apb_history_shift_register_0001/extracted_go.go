package main

// Output globals
var out_pready bool
var out_prdata uint8
var out_pslverr bool
var out_history_full bool
var out_history_empty bool
var out_error_flag bool
var out_interrupt_full bool
var out_interrupt_error bool

// Internal state registers
var ctrl_reg uint8
var train_hist uint8
var pred_hist uint8
var error_flg bool
var pready bool
var pslverr bool
var prdata uint8
var state uint8 // 0=IDLE, 1=READ, 2=WRITE
var prev_hs_valid bool

// APBGlobalHistoryRegister is the hardware entry function.
func APBGlobalHistoryRegister(
	pclk bool,
	presetn bool,
	paddr uint16,
	pwdata uint8,
	pwrite bool,
	penable bool,
	pselx bool,
	history_shift_valid bool,
	clk_gate_en bool,
) {
	// Reset behavior (asynchronous active-low)
	if !presetn {
		ctrl_reg = 0
		train_hist = 0
		pred_hist = 0
		error_flg = false
		pready = false
		pslverr = false
		prdata = 0
		state = 0
		prev_hs_valid = false
	} else {
		// Detect rising edge of history_shift_valid
		if !prev_hs_valid && history_shift_valid {
			// Misprediction has highest priority
			if (ctrl_reg & 0x04) != 0 { // train_mispredicted set
				// Restore history: {train_hist[6:0], train_taken}
				pred_hist = ((train_hist & 0x7F) << 1) | ((ctrl_reg >> 3) & 1)
			} else if (ctrl_reg & 0x01) != 0 { // predict_valid set
				// Shift in predict_taken
				pred_hist = (pred_hist << 1) | ((ctrl_reg >> 1) & 1)
			}
		}
		// Update previous history_shift_valid value
		prev_hs_valid = history_shift_valid

		// APB state machine transitions
		valid_addr := (paddr == 0 || paddr == 1 || paddr == 2)

		if state == 0 { // IDLE
			if pselx && !penable {
				if pwrite {
					state = 2 // WRITE
				} else {
					state = 1 // READ
				}
			}
		} else { // READ or WRITE state
			if pselx && penable {
				// Execute read/write on access phase
				if state == 1 { // READ
					if valid_addr {
						switch paddr {
						case 0:
							prdata = ctrl_reg & 0x0F
						case 1:
							prdata = train_hist & 0x7F
						case 2:
							prdata = pred_hist
						}
					} else {
						prdata = 0
					}
				} else { // WRITE
					if valid_addr {
						switch paddr {
						case 0:
							ctrl_reg = pwdata
						case 1:
							train_hist = pwdata
						// case 2 is read-only, ignored
						}
					}
				}
				state = 0 // transaction complete, back to IDLE
			}
		}

		// After reset, pready is always driven high (1)
		pready = true

		// Drive pslverr based on address validity during access phase
		if pselx && penable && !valid_addr {
			pslverr = true
			error_flg = true // sticky error flag
		} else {
			pslverr = false
		}
		// Note: error_flg remains set if already set; only cleared by reset
	}

	// Drive outputs
	out_pready = pready
	out_prdata = prdata
	out_pslverr = pslverr

	out_history_full = (pred_hist == 0xFF)
	out_history_empty = (pred_hist == 0)

	out_error_flag = error_flg

	out_interrupt_full = out_history_full
	out_interrupt_error = out_error_flag
}

func main() {}
