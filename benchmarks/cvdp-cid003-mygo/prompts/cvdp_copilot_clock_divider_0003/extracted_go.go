package main

var out_clk_out bool
var counter uint8

func clock_divider(clk bool, rst_n bool, sel uint8) {
    if !rst_n {
        out_clk_out = false
        counter = 0
    } else if clk {
        if sel > 2 {
            out_clk_out = false
            counter = 0
        } else {
            var maxCount uint8
            switch sel {
            case 0:
                maxCount = 0
            case 1:
                maxCount = 1
            case 2:
                maxCount = 3
            }
            if counter >= maxCount {
                out_clk_out = !out_clk_out
                counter = 0
            } else {
                counter++
            }
        }
    }
}

func main() {}
