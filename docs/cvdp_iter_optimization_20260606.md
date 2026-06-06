# CVDP MyGo Iteration Report - 2026-06-06

## Scope

- Task file: `C:\Users\贾镕旭\Desktop\迭代优化.txt`
- Server: `Trifoliate`
- Local MyGo source: `C:\Users\贾镕旭\Documents\MyGo\MyGo-ZeeMo`
- Server MyGo source: `/home/rongxv/work/MyGo-ZeeMo`
- Baselines checked:
  - MyGo server run: `/home/rongxv/work/cvdp-runs/mygo-deepseek-v4-server-20260606`
  - Direct Verilog fresh run: `/home/rongxv/work/cvdp-runs/direct-deepseek-v4-server-fresh-20260606`

## Baseline

- Original MyGo result: 56 / 78 PASS.
- Direct Verilog fresh result: 67 / 78 PASS.

## Fixes

- Fixed root/output MLIR handling for const-like and non-reg signals so named return defaults do not lower to undeclared `sv.read_inout %const_*`.
- Stopped synthetic `clk`/`rst` aliases from being created as readable ports when the module only has package-level globals with those names.
- Added plain-value reads for module-level reg references before emitting `sv.if`, avoiding inout values being used where `i1` is required.
- Added per-block read/value scope for combinational reg control lowering, avoiding SSA values from sibling regions leaking into later `sv.if` conditions.
- Strengthened the CVDP MyGo prompt/static checks for duplicate input/output names, Go reserved identifiers, missing final bare returns, literal `\n` model output, and `1 << 64` overflow.

## Validated Recovered Tasks

These tasks were non-PASS in the original MyGo server run and passed after this iteration:

- `03_cvdp_copilot_64b66b_encoder_0001`
- `08_cvdp_copilot_apb_gpio_0001`
- `25_cvdp_copilot_configurable_digital_low_pass_filter_0001`
- `30_cvdp_copilot_data_width_converter_0003`
- `35_cvdp_copilot_edge_detector_0001`
- `36_cvdp_copilot_ethernet_packet_parser_0001`
- `43_cvdp_copilot_gcd_0001`
- `60_cvdp_copilot_piso_0001`
- `62_cvdp_copilot_restoring_division_0001`
- `64_cvdp_copilot_secure_read_write_bus_0001`
- `68_cvdp_copilot_set_bit_calculator_0001`
- `75_cvdp_copilot_unpacker_one_hot_0001`
- `77_cvdp_copilot_vga_controller_0001`

Lower-bound result after targeted validation: 56 original PASS + 13 recovered = 69 / 78 PASS.
This exceeds the direct Verilog fresh baseline of 67 / 78 PASS.

## Server Evidence

- Reused-output MyGo/compiler check: `/home/rongxv/work/cvdp-runs/iter-mygo-fixes-20260606/reuse-priority`
- Prompt/static-feedback rerun: `/home/rongxv/work/cvdp-runs/iter-mygo-fixes-20260606/model-priority`
- Remaining direct-PASS rerun: `/home/rongxv/work/cvdp-runs/iter-mygo-fixes-20260606/model-remaining-direct-pass`
- 64-bit mask focused rerun: `/home/rongxv/work/cvdp-runs/iter-mygo-fixes-20260606/model-03-mask-rerun`

## Verification

- Server build: `go build -o bin/mygo ./cmd/mygo`
- Server tests:
  - `go test ./internal/mlir ./cmd/mygo -count=1`
  - `go test ./internal/mlir -run 'TestNamedReturnDefaultConstantsDoNotReadUndeclaredInouts|TestPackageLevelResetGlobalIsNotAssumedReadablePort|TestEmitTopLevelNamedReturnPorts' -count=1`
  - `go test ./cmd/mygo -run TestDetectVerilatorTopInfo -count=1`
