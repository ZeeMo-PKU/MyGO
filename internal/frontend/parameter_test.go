package frontend

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestPreprocessExportedConstAsModuleParameterShadow(t *testing.T) {
	dir := t.TempDir()
	file := filepath.Join(dir, "main.go")
	source := `package main

const LIMIT uint32 = 16
const privateLimit uint32 = 2

func TopModule(input uint32) uint32 {
	return input + (LIMIT - 1) + privateLimit
}
`
	if err := os.WriteFile(file, []byte(source), 0o644); err != nil {
		t.Fatal(err)
	}
	overlay, err := preprocessSourcesForOverlay([]string{file})
	if err != nil {
		t.Fatalf("preprocess: %v", err)
	}
	text := string(overlay[file])
	if !strings.Contains(text, "var __mygo_param_LIMIT = LIMIT") {
		t.Fatalf("missing generated parameter shadow:\n%s", text)
	}
	if !strings.Contains(text, "__mygo_param_LIMIT - 1") {
		t.Fatalf("exported constant use was not preserved as a runtime parameter expression:\n%s", text)
	}
	if strings.Contains(text, "__mygo_param_privateLimit") {
		t.Fatalf("unexported constant became a module parameter:\n%s", text)
	}
}

func TestPreprocessDoesNotRewriteShadowedExportedConst(t *testing.T) {
	dir := t.TempDir()
	file := filepath.Join(dir, "main.go")
	source := `package main

const LIMIT uint32 = 16

func usePackageConst() uint32 { return LIMIT }

func useLocalConst() uint32 {
	const LIMIT uint32 = 3
	return LIMIT
}
`
	if err := os.WriteFile(file, []byte(source), 0o644); err != nil {
		t.Fatal(err)
	}
	overlay, err := preprocessSourcesForOverlay([]string{file})
	if err != nil {
		t.Fatalf("preprocess: %v", err)
	}
	text := string(overlay[file])
	if strings.Count(text, "return __mygo_param_LIMIT") != 1 {
		t.Fatalf("expected only the package constant use to be rewritten:\n%s", text)
	}
	if !strings.Contains(text, "return LIMIT\n}") {
		t.Fatalf("local constant use was unexpectedly rewritten:\n%s", text)
	}
}

func TestPreprocessKeepsParameterizedArrayWidthAsCompileTimeConstant(t *testing.T) {
	dir := t.TempDir()
	file := filepath.Join(dir, "main.go")
	source := `package main

const WIDTH = 8

func TopModule(input [WIDTH]bool) bool { return input[0] }
`
	if err := os.WriteFile(file, []byte(source), 0o644); err != nil {
		t.Fatal(err)
	}
	overlay, err := preprocessSourcesForOverlay([]string{file})
	if err != nil {
		t.Fatalf("preprocess: %v", err)
	}
	if text := string(overlay[file]); strings.Contains(text, "__mygo_param_WIDTH") {
		t.Fatalf("compile-time array width was incorrectly rewritten as a scalar module parameter:\n%s", text)
	}
}

func TestPreprocessKeepsSwitchCaseConstantsInternal(t *testing.T) {
	dir := t.TempDir()
	file := filepath.Join(dir, "main.go")
	source := `package main

const IDLE uint8 = 0

func TopModule(state uint8) uint8 {
	switch state {
	case IDLE:
		return IDLE
	default:
		return 1
	}
}
`
	if err := os.WriteFile(file, []byte(source), 0o644); err != nil {
		t.Fatal(err)
	}
	overlay, err := preprocessSourcesForOverlay([]string{file})
	if err != nil {
		t.Fatalf("preprocess: %v", err)
	}
	if text := string(overlay[file]); strings.Contains(text, "__mygo_param_IDLE") {
		t.Fatalf("switch case constant was only partially parameterized:\n%s", text)
	}
}
