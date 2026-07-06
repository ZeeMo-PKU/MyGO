package main

var (
    // state register
    state uint8
    // output register
    out_reg_valid bool
    out_reg_data  uint8
    out_reg_last  bool
    out_reg_user  uint8
)

const (
    STATE_IDLE = 0
    STATE_1    = 1
    STATE_2    = 2
    STATE_3    = 3
    TAG_1      = 1
    TAG_2      = 2
    TAG_3      = 3
)

// Output globals
var (
    out_s_axis_tready_1 bool
    out_s_axis_tready_2 bool
    out_s_axis_tready_3 bool
    out_m_axis_tdata    uint8
    out_m_axis_tvalid   bool
    out_m_axis_tlast    bool
    out_m_axis_tuser    uint8
    out_busy            bool
)

func axis_joiner(
    clk bool,
    rst bool,
    s_axis_tdata_1 uint8,
    s_axis_tvalid_1 bool,
    s_axis_tlast_1 bool,
    s_axis_tdata_2 uint8,
    s_axis_tvalid_2 bool,
    s_axis_tlast_2 bool,
    s_axis_tdata_3 uint8,
    s_axis_tvalid_3 bool,
    s_axis_tlast_3 bool,
    m_axis_tready bool,
) {
    if rst {
        state = STATE_IDLE
        out_reg_valid = false
        out_reg_data = 0
        out_reg_last = false
        out_reg_user = 0
        out_s_axis_tready_1 = false
        out_s_axis_tready_2 = false
        out_s_axis_tready_3 = false
        out_m_axis_tdata = 0
        out_m_axis_tvalid = false
        out_m_axis_tlast = false
        out_m_axis_tuser = 0
        out_busy = false
        return
    }

    // Grants for transition from IDLE (priority: 1 > 2 > 3)
    grant_1 := state == STATE_IDLE && s_axis_tvalid_1 && !out_reg_valid
    grant_2 := state == STATE_IDLE && s_axis_tvalid_2 && !out_reg_valid && !grant_1
    grant_3 := state == STATE_IDLE && s_axis_tvalid_3 && !out_reg_valid && !grant_1 && !grant_2

    // tready outputs
    out_s_axis_tready_1 = (state == STATE_1 && !out_reg_valid) || grant_1
    out_s_axis_tready_2 = (state == STATE_2 && !out_reg_valid) || grant_2
    out_s_axis_tready_3 = (state == STATE_3 && !out_reg_valid) || grant_3

    // m_axis outputs driven by output register
    out_m_axis_tvalid = out_reg_valid
    out_m_axis_tdata = out_reg_data
    out_m_axis_tlast = out_reg_last
    out_m_axis_tuser = out_reg_user
    out_busy = (state != STATE_IDLE) || out_reg_valid

    // FSM next state and load logic
    next_state := state
    load := false
    var load_data uint8
    var load_last bool
    var load_user uint8

    if state == STATE_IDLE {
        if s_axis_tvalid_1 && !out_reg_valid {
            next_state = STATE_1
            load = true
            load_data = s_axis_tdata_1
            load_last = s_axis_tlast_1
            load_user = TAG_1
        } else if s_axis_tvalid_2 && !out_reg_valid {
            next_state = STATE_2
            load = true
            load_data = s_axis_tdata_2
            load_last = s_axis_tlast_2
            load_user = TAG_2
        } else if s_axis_tvalid_3 && !out_reg_valid {
            next_state = STATE_3
            load = true
            load_data = s_axis_tdata_3
            load_last = s_axis_tlast_3
            load_user = TAG_3
        } else {
            next_state = STATE_IDLE
        }
    } else {
        // processing state (1, 2, or 3)
        if out_reg_valid && m_axis_tready {
            // word transferred downstream
            if out_reg_last {
                next_state = STATE_IDLE
            } else {
                next_state = state
            }
        } else if !out_reg_valid {
            // output register empty, try to load next word from selected stream
            if state == STATE_1 && s_axis_tvalid_1 {
                load = true
                load_data = s_axis_tdata_1
                load_last = s_axis_tlast_1
                load_user = TAG_1
            } else if state == STATE_2 && s_axis_tvalid_2 {
                load = true
                load_data = s_axis_tdata_2
                load_last = s_axis_tlast_2
                load_user = TAG_2
            } else if state == STATE_3 && s_axis_tvalid_3 {
                load = true
                load_data = s_axis_tdata_3
                load_last = s_axis_tlast_3
                load_user = TAG_3
            }
            next_state = state
        } else {
            // out_reg_valid true but downstream not ready -> stall
            next_state = state
        }
    }

    // Update registers
    state = next_state
    if load {
        out_reg_valid = true
        out_reg_data = load_data
        out_reg_last = load_last
        out_reg_user = load_user
    } else if out_reg_valid && m_axis_tready {
        out_reg_valid = false
    }
    // else out_reg_valid holds
}

func main() {}
