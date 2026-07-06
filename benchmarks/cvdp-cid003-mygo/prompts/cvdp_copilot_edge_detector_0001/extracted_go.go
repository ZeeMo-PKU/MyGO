package main

var (
	out_o_positive_edge_detected bool
	out_o_negative_edge_detected bool
	det_reg                      bool
)

func sync_pos_neg_edge_detector(i_clk bool, i_rstb bool, i_detection_signal bool) {
	if !i_rstb {
		out_o_positive_edge_detected = false
		out_o_negative_edge_detected = false
		det_reg = false
		return
	}

	out_o_positive_edge_detected = i_detection_signal && !det_reg
	out_o_negative_edge_detected = !i_detection_signal && det_reg
	det_reg = i_detection_signal
}

func main() {}
