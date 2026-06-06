# CVDP MyGo Generation Prompt

Use this prompt when asking an LLM to translate a CVDP RTL task into MyGo source.

```text
You are generating Go/MyGo source code for the MyGo hardware compiler.

Return exactly one Go source file and nothing else. Do not wrap the answer in Markdown.

Task:
{{TASK_PROMPT}}

Requirements:
- Use package main.
- Implement the hardware as the requested top function name when it is a valid Go identifier.
- Match the task's SystemVerilog top-level interface exactly:
  - keep every input/output name from the prompt;
  - keep clk/clock ports as bool inputs;
  - keep reset, rst, areset, arst as active-high bool inputs;
  - keep resetn, rst_n, reset_n, aresetn, areset_n, arst_n as active-low bool inputs;
  - use named return values for output ports when the task expects output ports.
- If an input and output have the same port name, keep the input parameter exact and give the Go named return a safe suffix such as `out_<name>`; Go cannot compile duplicate parameter/result names.
- Never use Go reserved keywords such as `go`, `type`, `range`, or `var` as identifiers. Rename such ports safely, for example `go_in`; the wrapper reconnects ports by position.
- Include only an empty `func main() {}` besides the requested top function.
- Do not print, log, call fmt, use goroutines, channels, maps, slices, reflection, unsafe, or dynamic allocation.
- Use only synthesizable fixed-size data:
  - bool for 1-bit signals;
  - uint8/uint16/uint32/uint64 or int8/int16/int32/int64 for vectors;
  - fixed arrays like [N]bool or [N]uint8 when an interface is naturally an unpacked array.
- Use package-level variables for sequential state. Update state only inside TopModule.
- For sequential designs, model one clock tick per TopModule call. When reset is asserted, assign all state registers to their reset values before computing normal next-state behavior.
- For active-low reset ports such as resetn, reset when the value is false.
- Preserve bit widths explicitly with masks after arithmetic or shifts, for example x &= 0xff for an 8-bit register.
- For a full-width 64-bit mask, use `^uint64(0)` instead of `1 << 64`.
- Use simple for loops with compile-time constant bounds only.
- Avoid early returns except for reset handling. Ensure every named output is assigned on every path.
- End the top function's final fallthrough path with an explicit bare `return` when it has named return values.
- For APB/AXI-style tasks, assign deterministic defaults to ready/error/data outputs before protocol-specific branches.
- Do not read a named return value before assigning it; use local temporaries and assign outputs at the end.
- Avoid declaring local variables with the same names as ports or named return values.
- If the prompt names a finite-state machine, encode states with typed integer constants and provide complete default transitions.
- If the prompt requires memory, use fixed-size package-level arrays and constant-bound loops.
- For one-hot, encoder, decoder, set-bit, packer, and unpacker tasks, initialize outputs to zero and build them with explicit shifts and masks.
- Emit actual newlines in the source. Do not return literal `\n` or `\t` text in place of line breaks.

Output:
- Only the Go source code.
- No comments unless they clarify a non-obvious state encoding.
```

For direct comparison runs, keep the model, dataset, retry policy, and server environment fixed before comparing MyGo against direct SystemVerilog.
