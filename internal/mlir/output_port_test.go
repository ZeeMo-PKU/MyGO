package mlir

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestOutputGlobalPrefixIsNotEmittedAsMLIRPortName(t *testing.T) {
	const source = `
package main

var out_result uint8

func TopModule(input uint8) {
	result := input + 1
	out_result = result
}
`
	design := buildMLIRDesignFromSource(t, source)
	out := filepath.Join(t.TempDir(), "design.mlir")
	if err := Emit(design, out); err != nil {
		t.Fatalf("Emit failed: %v", err)
	}
	data, err := os.ReadFile(out)
	if err != nil {
		t.Fatalf("read MLIR: %v", err)
	}
	text := string(data)
	if !strings.Contains(text, "out result: i8") {
		t.Fatalf("expected stripped result output port:\n%s", text)
	}
	if strings.Contains(text, "out out_result:") {
		t.Fatalf("out_ DSL marker leaked into MLIR port:\n%s", text)
	}
}
