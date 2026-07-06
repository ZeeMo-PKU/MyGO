package main

var out_dice_value uint8
var state_idle bool
var counter uint8
var prev_clk bool

// digital_dice_roller implements a dice roller FSM with two states: IDLE and ROLLING.
// - Asynchronous reset (active low) forces output to 0, sets state to IDLE, and initialises counter.
// - On posedge clk when button is high, it transitions to ROLLING and cycles counter 1..6.
// - When button goes low, the current counter value is captured as out_dice_value and state returns to IDLE.
func digital_dice_roller(clk bool, reset_n bool, button bool) {
	if !reset_n {
		out_dice_value = 0
		state_idle = true
		counter = 1
		prev_clk = clk
		return
	}

	// rising edge of clk
	if clk && !prev_clk {
		if button {
			if state_idle {
				state_idle = false
				counter = 1
			} else {
				if counter == 6 {
					counter = 1
				} else {
					counter = counter + 1
				}
			}
		} else { // button released
			if !state_idle {
				out_dice_value = counter
				state_idle = true
			}
		}
	}
	prev_clk = clk
}

func main() {}
