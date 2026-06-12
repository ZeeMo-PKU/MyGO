# Go DSL Summary

This workflow expects Go files in the MyGO style below.

## Required Shape

1. The file starts with `package main`.
2. The hardware entry function is `func TopModule(...)`.
3. Inputs are ordinary `TopModule` parameters.
4. Outputs are package-level globals whose names start with `out_`.
5. `TopModule` assigns to those `out_*` globals directly.
6. Add `func main() {}` as an empty stub at the end.

## Forbidden Or Discouraged

- no return-value outputs
- no pointer outputs such as `*bool` or `*uint8`
- no structs, interfaces, maps, `select`, recursion, or dynamic goroutines
- avoid complex abstractions outside straightforward hardware logic
- no imports, `fmt`, `unsafe`, dynamic slices, or software-style helpers
- no arrays as memories, register banks, queues, or lookup tables
- fixed `[N]bool` arrays are allowed only for very wide vector ports and the documented Bits* helper stubs
- avoid `for`/`range` loops in generated logic; use direct expressions, short if/else chains, or Bits* helpers
- for adders, subtractors, and comparators up to 64 bits, use integer arithmetic with a wider temporary instead of bit-by-bit bool carry expansion
- for sequential logic, keep persistent state in package-level registers and update related registers in one reset/clock block
- for numeric clocks use `clk != 0`; for bool clocks use `clk`
- assign persistent `out_*` values from package-level output registers after the clocked block so outputs remain stable between edges
- cast operands to a wider unsigned type before applying large masks

## Preferred Types

- `bool` for 1-bit values
- `uint8`, `uint16`, `uint32` for packed vectors up to 32 bits
- fixed-size arrays only when wide vectors are necessary

## Vector Rules

- prefer scalar integer bit operations for packed vectors up to 32 bits
- use shifts, masks, bitwise ops, and integer comparisons
- use `[N]bool` mainly for very wide vectors such as 100-bit or 256-bit cases
- when using `[N]bool`, index `0` represents the least-significant bit unless the case clearly requires otherwise

## Minimal Example

```go
package main

var out_zero bool

func TopModule() {
    out_zero = false
}

func main() {}
```
