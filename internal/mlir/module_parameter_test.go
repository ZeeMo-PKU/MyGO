package mlir

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestExportedPackageConstEmitsHWModuleParameter(t *testing.T) {
	const source = `
package main

const LIMIT uint32 = 16

var out_result uint32

func TopModule(input uint32) {
	out_result = input + (LIMIT - 1)
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
	if !strings.Contains(text, "hw.module @TopModule<LIMIT: i32 = 16>(") {
		t.Fatalf("missing module parameter declaration:\n%s", text)
	}
	if !strings.Contains(text, "hw.param.value i32 = #hw.param.decl.ref<\"LIMIT\">") {
		t.Fatalf("missing module parameter value use:\n%s", text)
	}
	if strings.Contains(text, "__mygo_param_LIMIT = sv.reg") {
		t.Fatalf("parameter shadow was emitted as mutable storage:\n%s", text)
	}
}
