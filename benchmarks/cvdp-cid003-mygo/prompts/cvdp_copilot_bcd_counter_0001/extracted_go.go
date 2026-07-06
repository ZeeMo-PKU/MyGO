package main

var (
	ms_hr, ls_hr, ms_min, ls_min, ms_sec, ls_sec uint8
	prev_clk                                    bool
)

var out_ms_hr uint8
var out_ls_hr uint8
var out_ms_min uint8
var out_ls_min uint8
var out_ms_sec uint8
var out_ls_sec uint8

func bcd_counter(clk bool, rst bool) {
	if clk && !prev_clk {
		if rst {
			ms_hr, ls_hr, ms_min, ls_min, ms_sec, ls_sec = 0, 0, 0, 0, 0, 0
		} else {
			var carry_sec bool
			if ls_sec == 9 {
				ls_sec = 0
				if ms_sec == 5 {
					ms_sec = 0
					carry_sec = true
				} else {
					ms_sec++
				}
			} else {
				ls_sec++
			}

			if carry_sec {
				var carry_min bool
				if ls_min == 9 {
					ls_min = 0
					if ms_min == 5 {
						ms_min = 0
						carry_min = true
					} else {
						ms_min++
					}
				} else {
					ls_min++
				}

				if carry_min {
					if ms_hr == 2 && ls_hr == 3 {
						ms_hr = 0
						ls_hr = 0
					} else if ls_hr == 9 {
						ls_hr = 0
						ms_hr++
					} else {
						ls_hr++
					}
				}
			}
		}
	}
	prev_clk = clk

	out_ms_hr = ms_hr
	out_ls_hr = ls_hr
	out_ms_min = ms_min
	out_ls_min = ls_min
	out_ms_sec = ms_sec
	out_ls_sec = ls_sec
}

func main() {}
