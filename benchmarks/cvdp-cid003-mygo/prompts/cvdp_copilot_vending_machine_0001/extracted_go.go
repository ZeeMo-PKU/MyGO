package main

var (
	out_dispense_item   bool
	out_return_change   bool
	out_item_price      uint8
	out_change_amount   uint8
	out_dispense_item_id uint8
	out_error           bool
	out_return_money    bool

	state             uint8
	coins_accumulated uint8
	prev_item_button  bool
	prev_cancel       bool
	prev_clk          bool

	item_price_reg      uint8
	dispense_item_id_reg uint8
	change_amount_reg   uint8
)

const (
	IDLE = iota
	ITEM_SELECTION
	PAYMENT_VALIDATION
	DISPENSING_ITEM
	RETURN_CHANGE
	RETURN_MONEY
	CANCEL_ERROR
	COIN_ERROR
)

func vending_machine(clk bool, rst bool, item_button bool, item_selected uint8, coin_input uint8, cancel bool) {
	if rst {
		out_dispense_item = false
		out_return_change = false
		out_item_price = 0
		out_change_amount = 0
		out_dispense_item_id = 0
		out_error = false
		out_return_money = false

		state = IDLE
		coins_accumulated = 0
		prev_item_button = false
		prev_cancel = false
		prev_clk = false

		item_price_reg = 0
		dispense_item_id_reg = 0
		change_amount_reg = 0
		return
	}

	if clk && !prev_clk {
		out_dispense_item = false
		out_return_change = false
		out_error = false
		out_return_money = false
		out_change_amount = 0

		rising_item := item_button && !prev_item_button
		rising_cancel := cancel && !prev_cancel

		switch state {
		case IDLE:
			out_item_price = 0
			out_dispense_item_id = 0
			if rising_item {
				state = ITEM_SELECTION
			} else if coin_input != 0 {
				out_error = true
				out_return_money = true
				state = COIN_ERROR
			}

		case ITEM_SELECTION:
			if rising_cancel {
				state = CANCEL_ERROR
			} else if item_selected >= 1 && item_selected <= 4 {
				switch item_selected {
				case 1:
					item_price_reg = 5
				case 2:
					item_price_reg = 7
				case 3:
					item_price_reg = 10
				case 4:
					item_price_reg = 15
				}
				dispense_item_id_reg = item_selected
				out_item_price = item_price_reg
				out_dispense_item_id = item_selected
				coins_accumulated = 0
				state = PAYMENT_VALIDATION
			} else if item_selected != 0 {
				out_error = true
				out_return_money = true
				state = COIN_ERROR
			}

		case PAYMENT_VALIDATION:
			if rising_cancel {
				state = CANCEL_ERROR
			} else if coin_input != 0 {
				if coin_input == 1 || coin_input == 2 || coin_input == 5 || coin_input == 10 {
					new_total := coins_accumulated + coin_input
					if new_total >= item_price_reg {
						coins_accumulated = new_total
						state = DISPENSING_ITEM
					} else {
						coins_accumulated = new_total
					}
				} else {
					out_error = true
					out_return_money = true
					state = COIN_ERROR
				}
			}

		case DISPENSING_ITEM:
			out_dispense_item = true
			out_dispense_item_id = dispense_item_id_reg
			if coins_accumulated > item_price_reg {
				change_amount_reg = coins_accumulated - item_price_reg
				out_change_amount = change_amount_reg
				state = RETURN_CHANGE
			} else {
				out_item_price = 0
				out_dispense_item_id = 0
				state = IDLE
			}

		case RETURN_CHANGE:
			out_return_change = true
			out_change_amount = change_amount_reg
			out_item_price = 0
			out_dispense_item_id = 0
			state = IDLE

		case CANCEL_ERROR:
			out_error = true
			state = RETURN_MONEY

		case RETURN_MONEY:
			if coins_accumulated > 0 {
				out_return_money = true
			}
			out_item_price = 0
			out_dispense_item_id = 0
			out_change_amount = 0
			state = IDLE

		case COIN_ERROR:
			out_error = true
			out_return_money = true
			out_item_price = 0
			out_dispense_item_id = 0
			state = IDLE
		}

		prev_item_button = item_button
		prev_cancel = cancel
	}

	prev_clk = clk
}

func main() {}
