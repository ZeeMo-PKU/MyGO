package ir

import (
	"fmt"
	"testing"
)

func TestExportedPackageConstBuildsUsedModuleParameter(t *testing.T) {
	const source = `
package main

const LIMIT uint32 = 16
const privateLimit uint32 = 2

var out_result uint32

func TopModule(input uint32) {
	out_result = input + (LIMIT - 1) + privateLimit
}
`
	design := buildDesignFromSource(t, source)
	module := design.TopLevel
	if module == nil {
		t.Fatal("expected top-level module")
	}
	if len(module.Parameters) != 1 {
		t.Fatalf("parameters = %+v, want exactly LIMIT", module.Parameters)
	}
	parameter := module.Parameters[0]
	if parameter.Name != "LIMIT" || parameter.Type == nil || parameter.Type.Width != 32 || fmt.Sprint(parameter.Default) != "16" {
		t.Fatalf("unexpected LIMIT parameter: %+v", parameter)
	}

	parameterSignals := 0
	for _, signal := range module.Signals {
		reference, ok := signal.Value.(ParameterRef)
		if !ok {
			continue
		}
		parameterSignals++
		if reference.Name != "LIMIT" || signal.Kind != Const {
			t.Fatalf("unexpected parameter signal: %+v", signal)
		}
	}
	if parameterSignals != 1 {
		t.Fatalf("parameter signal count = %d, want 1", parameterSignals)
	}
}
