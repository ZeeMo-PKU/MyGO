package main

var out_one_hot_out uint32

func binary_to_one_hot_decoder(binary_in uint8) {
	const OUTPUT_WIDTH = 32
	if binary_in >= OUTPUT_WIDTH {
		out_one_hot_out = 0
	} else {
		out_one_hot_out = 1 << binary_in
	}
}

func main() {}
