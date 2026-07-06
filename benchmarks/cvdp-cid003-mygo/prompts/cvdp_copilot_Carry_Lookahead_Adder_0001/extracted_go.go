package main

var out_o_generate bool
var out_o_propagate bool
var out_o_Cout bool

// GP implements a Generate/Propagate cell for a carry-lookahead adder.
func GP(i_A bool, i_B bool, i_Cin bool) {
    out_o_generate = i_A && i_B
    out_o_propagate = i_A || i_B
    out_o_Cout = out_o_generate || (i_Cin && out_o_propagate)
}

func main() {}
