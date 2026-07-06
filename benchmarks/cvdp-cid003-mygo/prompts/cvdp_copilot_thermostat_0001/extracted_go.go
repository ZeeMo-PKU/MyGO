package main

var (
	out_heater_full   bool
	out_heater_medium bool
	out_heater_low    bool
	out_aircon_full   bool
	out_aircon_medium bool
	out_aircon_low    bool
	out_fan           bool
	out_state         uint8
)

var (
	curr_state    uint8 = 3   // AMBIENT
	prev_clk      bool  = false
	fault_latched bool  = false
)

const (
	HEAT_LOW   uint8 = 0
	HEAT_MED   uint8 = 1
	HEAT_FULL  uint8 = 2
	AMBIENT    uint8 = 3
	COOL_LOW   uint8 = 4
	COOL_MED   uint8 = 5
	COOL_FULL  uint8 = 6
)

// thermostat implements a thermostat controller FSM.
func thermostat(i_temp_feedback uint8, i_fan_on bool, i_enable bool, i_fault bool, i_clr bool, i_clk bool, i_rst bool) {
	// Asynchronous reset: forces AMBIENT and clears fault latch.
	if !i_rst {
		curr_state = AMBIENT
		fault_latched = false
	} else if i_clk && !prev_clk {
		// Rising edge of clock.
		if i_clr {
			// Clear fault latch and move to AMBIENT.
			fault_latched = false
			curr_state = AMBIENT
		} else {
			// Set fault latch if fault signal is asserted.
			if i_fault {
				fault_latched = true
			}
			if fault_latched {
				// Keep current state – outputs are forced to 0 externally.
				// No state change.
			} else if !i_enable {
				curr_state = AMBIENT
			} else {
				curr_state = nextStateFromTemp(i_temp_feedback)
			}
		}
	}
	prev_clk = i_clk

	// Fully combinational output logic with override priorities:
	// 1) reset (already handled above; curr_state==AMBIENT, fault_latched==false)
	// 2) fault_latched
	// 3) disabled (i_enable==0)
	// 4) normal operation

	// Compute base heater, cooler, fan from current state.
	var heatFull, heatMed, heatLow, coolFull, coolMed, coolLow bool
	switch curr_state {
	case HEAT_FULL:
		heatFull = true
	case HEAT_MED:
		heatMed = true
	case HEAT_LOW:
		heatLow = true
	case COOL_FULL:
		coolFull = true
	case COOL_MED:
		coolMed = true
	case COOL_LOW:
		coolLow = true
	case AMBIENT:
		// all false
	}
	base_fan := heatFull || heatMed || heatLow || coolFull || coolMed || coolLow || i_fan_on

	// Apply overrides.
	if !i_rst {
		out_heater_full = false
		out_heater_medium = false
		out_heater_low = false
		out_aircon_full = false
		out_aircon_medium = false
		out_aircon_low = false
		out_fan = false
		out_state = AMBIENT
		return
	}

	if fault_latched {
		out_heater_full = false
		out_heater_medium = false
		out_heater_low = false
		out_aircon_full = false
		out_aircon_medium = false
		out_aircon_low = false
		out_fan = false
		out_state = curr_state
	} else if !i_enable {
		out_heater_full = false
		out_heater_medium = false
		out_heater_low = false
		out_aircon_full = false
		out_aircon_medium = false
		out_aircon_low = false
		out_fan = false
		out_state = curr_state
	} else {
		out_heater_full = heatFull
		out_heater_medium = heatMed
		out_heater_low = heatLow
		out_aircon_full = coolFull
		out_aircon_medium = coolMed
		out_aircon_low = coolLow
		out_fan = base_fan
		out_state = curr_state
	}
}

// nextStateFromTemp determines the next FSM state solely from temperature feedback bits.
// Priority: cold bits first (full > med > low), then hot bits (full > med > low), else AMBIENT.
func nextStateFromTemp(feedback uint8) uint8 {
	// i_full_cold = feedback[5], i_medium_cold = feedback[4], i_low_cold = feedback[3]
	// i_low_hot = feedback[2], i_medium_hot = feedback[1], i_full_hot = feedback[0]
	if feedback&0x20 != 0 {
		return HEAT_FULL
	}
	if feedback&0x10 != 0 {
		return HEAT_MED
	}
	if feedback&0x08 != 0 {
		return HEAT_LOW
	}
	if feedback&0x01 != 0 {
		return COOL_FULL
	}
	if feedback&0x02 != 0 {
		return COOL_MED
	}
	if feedback&0x04 != 0 {
		return COOL_LOW
	}
	return AMBIENT
}

func main() {
}
