package main

var out_ciphertext uint16
var out_done bool

var state uint8
var pt0, pt1, pt2 uint8
var k00, k01, k02, k10, k11, k12, k20, k21, k22 uint8
var c0, c1, c2 uint8

func hill_cipher(clk bool, reset bool, start bool, plaintext uint16, key uint64) {
    if reset {
        out_ciphertext = 0
        out_done = false
        state = 0
        pt0 = 0
        pt1 = 0
        pt2 = 0
        k00 = 0
        k01 = 0
        k02 = 0
        k10 = 0
        k11 = 0
        k12 = 0
        k20 = 0
        k21 = 0
        k22 = 0
        c0 = 0
        c1 = 0
        c2 = 0
    } else {
        // FSM: IDLE(0) -> CAPTURE(1) -> COMPUTE(2) -> DONE(3) -> IDLE
        switch state {
        case 0: // IDLE
            if start {
                pt0 = uint8((plaintext >> 10) & 0x1F)
                pt1 = uint8((plaintext >> 5) & 0x1F)
                pt2 = uint8(plaintext & 0x1F)

                k00 = uint8((key >> 40) & 0x1F)
                k01 = uint8((key >> 35) & 0x1F)
                k02 = uint8((key >> 30) & 0x1F)
                k10 = uint8((key >> 25) & 0x1F)
                k11 = uint8((key >> 20) & 0x1F)
                k12 = uint8((key >> 15) & 0x1F)
                k20 = uint8((key >> 10) & 0x1F)
                k21 = uint8((key >> 5) & 0x1F)
                k22 = uint8(key & 0x1F)

                state = 1
            }
        case 1: // CAPTURE
            state = 2
        case 2: // COMPUTE
            c0 = uint8((uint16(k00)*uint16(pt0) + uint16(k01)*uint16(pt1) + uint16(k02)*uint16(pt2)) % 26)
            c1 = uint8((uint16(k10)*uint16(pt0) + uint16(k11)*uint16(pt1) + uint16(k12)*uint16(pt2)) % 26)
            c2 = uint8((uint16(k20)*uint16(pt0) + uint16(k21)*uint16(pt1) + uint16(k22)*uint16(pt2)) % 26)
            state = 3
        case 3: // DONE
            out_ciphertext = (uint16(c0) << 10) | (uint16(c1) << 5) | uint16(c2)
            out_done = true
            state = 0
        }
    }
}

func main() {}
