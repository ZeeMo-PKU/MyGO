# Prompt Template

Use this template to generate one MyGO Go file for one benchmark case.

## System Prompt

```text
Generate only valid Go source code for MyGO.
Follow the provided DSL exactly.
Outputs must use out_* package globals.
Do not use pointer outputs or return-value outputs.
Do not use imports, slices, maps, structs, arrays-as-memories, or helper functions except documented MyGO builtin stubs.
Use package-level registers for sequential state and keep clock/reset logic in one block.
```

## User Prompt Template

```text
Generate one complete Go source file for the MyGO compiler.
Return Go code only.

Follow this Go DSL summary exactly:
{{GO_DSL_SUMMARY}}

Global constraints:
- Return one complete Go file only.
- Do not use arrays as memories/register banks; fixed [N]bool arrays are only for wide vector ports and Bits* helper stubs.
- Avoid for/range loops; use direct expressions, short if/else chains, or Bits* helpers.
- Cast to wider unsigned types before large masks.

Original task prompt:
{{TASK_PROMPT}}

Reference Verilog:
{{REFERENCE_VERILOG}}
```

## Placeholder Meanings

- `{{GO_DSL_SUMMARY}}`: the rules in `go_dsl.md`
- `{{TASK_PROMPT}}`: the benchmark problem statement for the case
- `{{REFERENCE_VERILOG}}`: the matching reference Verilog file for the case

## Output Rule

The model should return exactly one complete Go file.
