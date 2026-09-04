package ir

import "testing"

func TestOutputGlobalPrefixIsNotPartOfExternalPortName(t *testing.T) {
	const source = `
package main

var out_result uint8

func TopModule(input uint8) {
	result := input + 1
	out_result = result
}
`
	design := buildDesignFromSource(t, source)
	if design == nil || design.TopLevel == nil {
		t.Fatal("expected top-level module")
	}

	for _, port := range design.TopLevel.Ports {
		if port.Name == "out_result" {
			t.Fatalf("out_ DSL marker leaked into external port: %+v", port)
		}
		if port.Name == "result" {
			if port.Direction != Output {
				t.Fatalf("result direction = %v, want Output", port.Direction)
			}
			if port.Binding != "out_result" {
				t.Fatalf("result binding = %q, want out_result", port.Binding)
			}
			return
		}
	}
	t.Fatalf("expected result output port, got %+v", design.TopLevel.Ports)
}
