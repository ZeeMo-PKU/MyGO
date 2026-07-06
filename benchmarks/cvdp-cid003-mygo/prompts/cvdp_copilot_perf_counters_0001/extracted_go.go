package main

// Parameter: Counter width in bits (default 32)
const CNT_W = 32

// Internal state
var count_q uint32

// Output signal
var out_p_count_o uint32

// cvdp_copilot_perf_counters is the hardware entry function for the performance counter.
// It takes clk, reset, sw_req_i, cpu_trig_i as inputs and updates output p_count_o.
func cvdp_copilot_perf_counters(clk bool, reset bool, sw_req_i bool, cpu_trig_i bool) {
	// Output value: zero unless a software read is requested.
	out_p_count_o = 0
	if sw_req_i {
		out_p_count_o = count_q
	}

	// Asynchronous active-high reset.
	if reset {
		count_q = 0
	} else {
		// On software read, reset counter in the next cycle.
		if sw_req_i {
			count_q = 0
		} else if cpu_trig_i {
			// Increment on CPU trigger event.
			count_q = count_q + 1
		}
		// Note: overflow is handled by wrapping around the uint32 type,
		// matching the parameterized width behavior.
	}
}

func main() {
}
