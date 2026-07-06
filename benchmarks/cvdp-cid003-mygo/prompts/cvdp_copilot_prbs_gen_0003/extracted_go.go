package main

// Constants for module parameters (default values)
const CHECK_MODE = 0 // 0 = generator, 1 = checker
const POLY_LENGTH = 31
const POLY_TAP = 3
const WIDTH = 16

// Internal state
var lfsr uint32   // LFSR shift register, 31 bits used
var out_data_out uint16

// Hardware entry function
func cvdp_prbs_gen(clk bool, rst bool, data_in uint16) {
    if clk {
        if rst {
            // Synchronous reset: PRBS registers all ones, data_out all ones
            lfsr = (1 << POLY_LENGTH) - 1
            out_data_out = (1 << WIDTH) - 1
        } else {
            if CHECK_MODE == 0 {
                // Generator mode
                var out uint16
                for i := 0; i < WIDTH; i++ {
                    // Output bit is current LSB
                    bit := lfsr & 1
                    out |= uint16(bit) << uint(i)

                    // Feedback tap XOR (positions POLY_LENGTH and POLY_TAP, 1-indexed)
                    tap1 := (lfsr >> (POLY_LENGTH - 1)) & 1
                    tap2 := (lfsr >> (POLY_TAP - 1)) & 1
                    feedback := tap1 ^ tap2

                    // Shift right, insert feedback at MSB
                    lfsr = (lfsr >> 1) | (feedback << (POLY_LENGTH - 1))
                }
                out_data_out = out
            } else {
                // Checker mode
                var err uint16
                for i := 0; i < WIDTH; i++ {
                    expected := lfsr & 1
                    inBit := (data_in >> uint(i)) & 1
                    errBit := inBit ^ expected
                    err |= uint16(errBit) << uint(i)

                    // Update LFSR identically to generator
                    tap1 := (lfsr >> (POLY_LENGTH - 1)) & 1
                    tap2 := (lfsr >> (POLY_TAP - 1)) & 1
                    feedback := tap1 ^ tap2
                    lfsr = (lfsr >> 1) | (feedback << (POLY_LENGTH - 1))
                }
                out_data_out = err
            }
        }
    }
}

func main() {}
