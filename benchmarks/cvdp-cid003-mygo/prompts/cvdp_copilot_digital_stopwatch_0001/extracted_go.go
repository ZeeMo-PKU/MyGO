package main

var (
	clk_prev    bool
	cycle_count uint64
	seconds     uint8
	minutes     uint8
	hour        bool
	out_seconds uint8
	out_minutes uint8
	out_hour    bool
)

const CLK_FREQ uint64 = 50000000

func dig_stopwatch(clk bool, reset bool, start_stop bool) {
	if reset {
		clk_prev = false
		cycle_count = 0
		seconds = 0
		minutes = 0
		hour = false
		out_seconds = 0
		out_minutes = 0
		out_hour = false
		return
	}

	rising := clk && !clk_prev
	clk_prev = clk

	if rising && start_stop && !hour {
		if cycle_count == CLK_FREQ-1 {
			cycle_count = 0
			if seconds == 59 {
				seconds = 0
				if minutes == 59 {
					minutes = 0
					hour = true
				} else {
					minutes++
				}
			} else {
				seconds++
			}
		} else {
			cycle_count++
		}
	}

	out_seconds = seconds
	out_minutes = minutes
	out_hour = hour
}

func main() {}
