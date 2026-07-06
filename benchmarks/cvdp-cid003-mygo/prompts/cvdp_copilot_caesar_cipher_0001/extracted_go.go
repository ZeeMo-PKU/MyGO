package main

var out_output_char uint8

func caesar_cipher(input_char uint8, key uint8) {
	if input_char >= 65 && input_char <= 90 { // 'A' to 'Z'
		offset := input_char - 65
		shifted := (offset + key) % 26
		out_output_char = shifted + 65
	} else if input_char >= 97 && input_char <= 122 { // 'a' to 'z'
		offset := input_char - 97
		shifted := (offset + key) % 26
		out_output_char = shifted + 97
	} else {
		out_output_char = input_char
	}
}

func main() {}
