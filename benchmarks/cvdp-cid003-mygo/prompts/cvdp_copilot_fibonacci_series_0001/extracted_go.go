package main

var (
	out_fib_out      uint32
	out_overflow_flag bool

	regA              uint32 = 0
	regB              uint32 = 1  // initial after reset: F(1) = 1
	overflowDetected  bool   = false
	prevClk           bool   = false
)

func fibonacci_series(clk bool, rst bool) {
	if rst {
		// Asynchronous reset
		regA = 0
		regB = 1
		overflowDetected = false
		out_fib_out = 0
		out_overflow_flag = false
		prevClk = clk
		return
	}

	// Positive edge detection
	if !prevClk && clk {
		if overflowDetected {
			// One cycle after overflow: set flag, restart sequence
			out_overflow_flag = true
			out_fib_out = 0
			regA = 0
			regB = 1
			overflowDetected = false
		} else {
			// Normal Fibonacci generation
			out_overflow_flag = false
			nextFib := uint64(regA) + uint64(regB)

			if nextFib > 0xFFFFFFFF {
				overflowDetected = true
				// Output the last valid Fibonacci number (current RegB)
				out_fib_out = regB
				// Update registers with the overflowed sum
				regA = regB
				regB = uint32(nextFib)
			} else {
				// Output the newly computed Fibonacci number
				out_fib_out = uint32(nextFib)
				// Shift registers
				regA = regB
				regB = uint32(nextFib)
			}
		}
	}

	// Update previous clock state
	prevClk = clk
}

func main() {}
