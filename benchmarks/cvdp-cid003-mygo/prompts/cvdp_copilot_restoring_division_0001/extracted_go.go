package main

const WIDTH = 6
const mask = uint16(1<<WIDTH - 1)
const mask2 = uint16(1<<(2*WIDTH) - 1)

var (
    out_quotient  uint8
    out_remainder uint8
    out_valid     bool
)

var (
    prev_clk     bool
    state        uint8 // 0=IDLE, 1=COMPUTE, 2=DONE
    combined_reg uint16
    counter      uint8
    divisor_reg  uint8
)

func restoring_division(clk bool, rst bool, start bool, dividend uint8, divisor uint8) {
    if !rst { // active-low asynchronous reset
        out_quotient = 0
        out_remainder = 0
        out_valid = false
        combined_reg = 0
        counter = 0
        state = 0
        divisor_reg = 0
        prev_clk = false
        return
    }

    // synchronous logic on rising edge
    if !prev_clk && clk {
        if state == 0 { // IDLE
            if start {
                combined_reg = uint16(dividend) & mask
                counter = 0
                divisor_reg = divisor & uint8(mask)
                state = 1 // COMPUTE
                out_valid = false
            }
        } else if state == 1 { // COMPUTE
            shifted := (combined_reg << 1) & mask2
            A := uint8(shifted >> WIDTH) & uint8(mask)
            if A >= divisor_reg {
                newA := A - divisor_reg
                shifted = (shifted & mask) | (uint16(newA) << WIDTH)
                shifted |= 1
            }
            combined_reg = shifted
            counter++
            if counter == WIDTH {
                state = 2 // DONE
                out_valid = true
                out_quotient = uint8(combined_reg & mask)
                out_remainder = uint8(combined_reg >> WIDTH) & uint8(mask)
            }
        } else { // DONE
            state = 0 // IDLE
            out_valid = false
        }
    }
    prev_clk = clk
}

func main() {}
