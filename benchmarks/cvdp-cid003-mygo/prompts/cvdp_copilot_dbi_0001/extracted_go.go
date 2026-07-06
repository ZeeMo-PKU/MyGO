package main

var out_data_out uint64
var out_dbi_cntrl uint8

var prev_data uint64
var prev_clk bool

func dbi_enc(data_in uint64, clk bool, rst_n bool) {
    if !rst_n {
        out_data_out = 0
        out_dbi_cntrl = 0
        prev_data = 0
        prev_clk = false
        return
    }

    // Rising-edge triggered sequential logic
    if !prev_clk && clk {
        // Mask input to 40 bits
        din := data_in & 0xFFFFFFFFFF

        // Split into two 20-bit groups
        group1_in := (din >> 20) & 0xFFFFF
        group0_in := din & 0xFFFFF

        prev_group1 := (prev_data >> 20) & 0xFFFFF
        prev_group0 := prev_data & 0xFFFFF

        diff1 := group1_in ^ prev_group1
        diff0 := group0_in ^ prev_group0

        // Count bits that differ
        count1 := 0
        count0 := 0
        for i := 0; i < 20; i++ {
            if (diff1>>uint(i))&1 != 0 {
                count1++
            }
            if (diff0>>uint(i))&1 != 0 {
                count0++
            }
        }

        ctrl1 := count1 > 10
        ctrl0 := count0 > 10

        var out_group1, out_group0 uint64
        if ctrl1 {
            out_group1 = ^group1_in & 0xFFFFF
        } else {
            out_group1 = group1_in
        }
        if ctrl0 {
            out_group0 = ^group0_in & 0xFFFFF
        } else {
            out_group0 = group0_in
        }

        data_out := (out_group1 << 20) | out_group0
        dbi_cntrl_val := uint8(0)
        if ctrl1 {
            dbi_cntrl_val |= 2
        }
        if ctrl0 {
            dbi_cntrl_val |= 1
        }

        prev_data = data_out
        out_data_out = data_out
        out_dbi_cntrl = dbi_cntrl_val
    }

    prev_clk = clk
}

func main() {}
