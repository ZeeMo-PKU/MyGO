package main

// Parameter AFINITY: controls which master wins when both are valid simultaneously.
// 0: m0 wins, 1: m1 wins.
const AFINITY = 0

// Outputs
var out_m0_read bool
var out_m1_read bool
var out_s_valid bool
var out_s_data uint32

// Internal registers for one-cycle pipeline
var s_valid_reg bool
var s_data_reg uint32

func data_bus_controller(clk bool, rst_n bool, m0_valid bool, m0_data uint32, m1_valid bool, m1_data uint32, s_ready bool) {
    // Asynchronous reset: active low
    if !rst_n {
        out_m0_read = false
        out_m1_read = false
        out_s_valid = false
        out_s_data = 0
        s_valid_reg = false
        s_data_reg = 0
        return
    }

    // Arbitration: choose master based on AFINITY when both are valid
    var m0_selected bool
    var m1_selected bool
    if m0_valid && m1_valid {
        if AFINITY == 0 {
            m0_selected = true
            m1_selected = false
        } else {
            m0_selected = false
            m1_selected = true
        }
    } else {
        m0_selected = m0_valid
        m1_selected = m1_valid
    }

    // Drive master ready signals depending on selection and slave ready
    m0_ready := m0_selected && s_ready
    m1_ready := m1_selected && s_ready

    out_m0_read = m0_ready
    out_m1_read = m1_ready

    // Output current pipeline registers to slave
    out_s_valid = s_valid_reg
    out_s_data = s_data_reg

    // A transaction occurs in this cycle if a master was selected and slave is ready
    transaction := (m0_selected && m0_valid) || (m1_selected && m1_valid) // either selected and valid (since selected already implies valid)
    // Actually, for the selected master, valid is guaranteed true.
    transaction = (m0_selected && s_ready) || (m1_selected && s_ready) // handshake condition

    // Update pipeline registers for the next cycle
    if transaction {
        s_valid_reg = true
        if m0_selected {
            s_data_reg = m0_data
        } else {
            s_data_reg = m1_data
        }
    } else {
        s_valid_reg = false
        s_data_reg = 0
    }
}

func main() {}
