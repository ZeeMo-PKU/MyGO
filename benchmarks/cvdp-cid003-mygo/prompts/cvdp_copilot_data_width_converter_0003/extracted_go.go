package main

var out_o_data_out [4]uint32
var out_o_data_out_valid bool

var buffer [4]uint32
var count uint8

func data_width_converter(clk bool, reset bool, data_in uint32, data_valid bool) {
    if reset {
        out_o_data_out = [4]uint32{}
        out_o_data_out_valid = false
        buffer = [4]uint32{}
        count = 0
        return
    }

    // default output
    out_o_data_out_valid = false

    if data_valid {
        switch count {
        case 0:
            buffer[3] = data_in
            count = 1
        case 1:
            buffer[2] = data_in
            count = 2
        case 2:
            buffer[1] = data_in
            count = 3
        case 3:
            buffer[0] = data_in
            out_o_data_out = buffer
            out_o_data_out_valid = true
            count = 0
        }
    }
}

func main() {}
