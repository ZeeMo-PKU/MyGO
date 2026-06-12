# CVDP cid003 MyGo 前后对比报告

日期：2026-06-13  
对象：CVDP cid003 78 题子集  
模型：DeepSeek V4 Pro / OpenRouter 路由名 `deepseek/deepseek-v4-pro`  
对照代码基线：原始 `pku-lemonade/MyGO`

本报告只汇总 CVDP cid003 的结果，不把 RTLLM、Verilog-Eval 或 targeted/merged 结果混入总成绩。

## 1. 成绩总览

| 阶段 | 路径 | 成绩 | 状态统计 | 说明 |
|---|---:|---:|---|---|
| 修改前 | MyGo route | 56/78 PASS, 71.79% | PASS=56, FAIL=14, MODEL_OR_MYGO_ERROR=8 | 使用原始 `pku-lemonade/MyGO` 代码基线的服务器 run 作为修改前 MyGo 成绩。 |
| 修改前 | Direct Verilog | 68/78 PASS, 87.18% | PASS=68, FAIL=9, TIMEOUT=1 | LLM 直接生成 SystemVerilog，并用 CVDP cocotb harness 验证。 |
| 修改后 | MyGo route | 75/78 PASS, 96.15% | PASS=75, MYGO_COMPILE_ERROR=2, MODEL_STATIC_ERROR=1 | 使用当前优化后的 MyGo 编译器、全局 prompt、runner、repair flow fresh full run。 |
| 修改后 | Direct Verilog | 68/78 PASS, 87.18% | PASS=68, FAIL=9, TIMEOUT=1 | Direct Verilog 没有经过 MyGo 修改，保留同一 env-fixed baseline 作为对照。 |

核心结论：修改后 MyGo route 从 56/78 提升到 75/78，比 Direct Verilog baseline 的 68/78 高 7 题。这个结果不是把多次 targeted 结果合并出来的，而是一次 full 78 fresh run 的最终统计。

## 2. 结果来源与口径

### 2.1 修改前 MyGo

修改前定义为原始 `pku-lemonade/MyGO` 代码基线。服务器记录中对应的 CVDP MyGo run 成绩为：

```text
CVDP cid003 MyGO server run -- 56/78 PASS
```

这里使用 56/78 作为修改前 MyGo 的主口径。之前还有更早的 48/78、51/78 等中间结果，但那些结果受到环境、harness 或 runner 配置影响，本报告不把它们作为正式修改前成绩。

### 2.2 Direct Verilog baseline

Direct Verilog 使用同一批 CVDP cid003 题目，让 LLM 直接输出 SystemVerilog，然后进入 CVDP cocotb harness。env-fixed baseline 成绩为：

```text
PASS=68, FAIL=9, TIMEOUT=1
score = 68/78 = 87.18%
```

Direct Verilog 不经过 MyGo 编译器，所以 MyGo 修改前后它的成绩保持为同一对照基线。

### 2.3 修改后 MyGo

修改后 MyGo 使用当前服务器工作树、全局 restricted-Go prompt、Go 静态检查、编译器反馈修复、多次重试以及修复后的 MyGo 编译链。最新 full 78 fresh run 摘要：

```text
CVDP cid003 MyGo fresh full v31
score: 75/78 PASS (96.15%)
counts: PASS=75, MYGO_COMPILE_ERROR=2, MODEL_STATIC_ERROR=1
root: /home/rongxv/work/cvdp-runs/systematic-fixes-20260613/full78_fresh_v31_current_venv
```

## 3. 实验环境配置

| 项目 | 配置 |
|---|---|
| 服务器 | `Trifoliate` |
| 工作根目录 | `/home/rongxv/work` |
| MyGo 工作树 | `/home/rongxv/work/MyGo-PR21-repro-20260607-165808` |
| MyGo 可执行文件 | `/home/rongxv/work/MyGo-PR21-repro-20260607-165808/bin/mygo` |
| Go 工具链 | `/home/rongxv/.cache/gomod/golang.org/toolchain@v0.0.1-go1.25.4.linux-amd64/bin/go` |
| Go 版本 | `go version go1.25.4 linux/amd64` |
| Python runner | `/home/rongxv/venvs/cvdp-test/bin/python` |
| Python 版本 | `Python 3.13.12` |
| CIRCT | `/home/rongxv/work/tools/circt/firtool-1.146.0/bin/circt-opt` |
| CIRCT/LLVM 版本 | `LLVM version 23.0.0git` |
| Icarus Verilog | `Icarus Verilog version 13.0 (stable) (v13_0)` |
| CVDP 数据集 | `/home/rongxv/work/cvdp-assets/cvdp_v1.1.0_nonagentic_code_generation_no_commercial.jsonl` |
| CVDP 任务选择表 | `/home/rongxv/work/cvdp-assets/cvdp_code_generation_649_tasks.csv` |
| API key 文件 | `/home/rongxv/work/secrets/openrouter_key.txt` |
| 模型 | `deepseek/deepseek-v4-pro` |

修改后 full 78 run 的关键 runner 参数：

```text
--retries 5
--go-attempts 4
--model-timeout 900
--mygo-timeout 240
--mygo-sim-timeout 180
--shards 6
--tasks-per-shard 13
```

工具路径中显式加入：

```text
/home/rongxv/work/tools/bin
/home/rongxv/work/tools/apt-root/usr/bin
/home/rongxv/work/tools/circt/firtool-1.146.0/bin
```

这样做是为了避免之前出现的环境性失败，例如 `iverilog executable not found`、CIRCT 找不到、Python venv 不一致等问题。v31 结果里没有再把环境缺失类问题计入 MyGo 失败。

## 4. 修改后 MyGo 仍失败的题目逐题分析

修改后 MyGo route 只有 3 个非 PASS：

```text
PASS=75
MYGO_COMPILE_ERROR=2
MODEL_STATIC_ERROR=1
```

下面逐题列出原始状态、artifact、准确报错摘录和原因分析。

### 4.1 `cvdp_copilot_16qam_mapper_0006`

| 字段 | 内容 |
|---|---|
| 状态 | `MYGO_COMPILE_ERROR` |
| artifact | `/home/rongxv/work/cvdp-runs/systematic-fixes-20260613/full78_fresh_v31_current_venv/shard00/02_cvdp_copilot_16qam_mapper_0006` |
| 最终错误 | `MyGo compile failed after DeepSeek revision attempts: MyGo mlir TIMEOUT after 240.1s` |
| 静态检查提示 | `Do not use for loops. Rewrite using scalar state or a compact arithmetic/bitwise formula; for memory/register-bank behavior, keep only the scalar visible state needed by the transaction.` |

原始报错摘录：

```text
cvdp_copilot_16qam_mapper_0006: MYGO_COMPILE_ERROR
MyGo compile failed after DeepSeek revision attempts: MyGo mlir TIMEOUT after 240.1s

evidence restricted_go_check_attempt3.txt:
Do not use for loops. Rewrite using scalar state or a compact arithmetic/bitwise formula; for memory/register-bank behavior, keep only the scalar visible state needed by the transaction.
```

分析：这题最终不是仿真答案错误，而是 MyGo route 在生成 Go 到 MLIR 的阶段没能在 240 秒内完成。静态检查记录显示，模型在修复轮次中仍生成了 `for` loop。当前 MyGo 子集和 CVDP 全局 prompt 都要求 LLM 把这种逻辑改成标量状态、位运算公式或手动展开，因为循环会让下游 IR/MLIR 生成变复杂，尤其在 mapper 这类位映射任务中容易触发过大的控制/数据路径。

这类失败的责任可以分两层看：第一层是 LLM 生成的 Go 仍不完全符合 MyGo restricted subset；第二层是 MyGo 对循环或复杂展开的编译鲁棒性仍不足。如果以后要继续提升，这题适合从两个方向做：继续强化全局 prompt/revision prompt，要求 16QAM mapper 用查表式 `if/else` 或组合逻辑表达式；同时在 MyGo 前端增加更早的循环拒绝与更短错误反馈，避免进入长时间 MLIR timeout。

### 4.2 `cvdp_copilot_car_parking_management_0001`

| 字段 | 内容 |
|---|---|
| 状态 | `MYGO_COMPILE_ERROR` |
| artifact | `/home/rongxv/work/cvdp-runs/systematic-fixes-20260613/full78_fresh_v31_current_venv/shard01/19_cvdp_copilot_car_parking_management_0001` |
| 最终错误 | `MyGo compile failed after DeepSeek revision attempts: MyGo mlir TIMEOUT after 240.1s` |
| 静态检查提示 | `Do not define helper functions; extra functions found: seg7. Delete every extra func and inline its body with local temporary variables at each call site.` |

原始报错摘录：

```text
cvdp_copilot_car_parking_management_0001: MYGO_COMPILE_ERROR
MyGo compile failed after DeepSeek revision attempts: MyGo mlir TIMEOUT after 240.1s

evidence restricted_go_check_attempt3.txt:
Do not define helper functions; extra functions found: seg7. Delete every extra func and inline its body with local temporary variables at each call site.
```

分析：这题是停车管理逻辑，通常会包含计数、车位状态、入口/出口控制、七段数码管显示等逻辑。静态检查显示模型生成了额外 helper function `seg7`。当前 MyGo route 的全局规则要求只保留一个硬件函数和空 `main`，不要额外定义 helper function。原因是额外函数在 Go AST、IR 构造、call inline、宽度推断和 MLIR emission 之间会扩大编译状态空间，容易让编译链进入复杂路径。

这里已经不是环境问题，也不是 cocotb 对端口名不匹配的问题，而是生成 Go 和 MyGo 子集之间仍有不一致。虽然我们后续加入了 helper/call inline 相关支持，但这题仍然在 MLIR 阶段超时，说明 helper 展开或其后续组合逻辑仍然过大。进一步优化可以考虑：把 `seg7` 这种常见显示译码作为全局 prompt 的固定写法，要求直接在主函数内用 `if/else` 产生七段输出；或者在 MyGo 编译器里对纯组合 helper 做更轻量的 inline 与 memoization，避免重复展开导致 timeout。

### 4.3 `cvdp_copilot_unpacker_one_hot_0001`

| 字段 | 内容 |
|---|---|
| 状态 | `MODEL_STATIC_ERROR` |
| artifact | `/home/rongxv/work/cvdp-runs/systematic-fixes-20260613/full78_fresh_v31_current_venv/shard05/75_cvdp_copilot_unpacker_one_hot_0001` |
| 最终错误 | `MyGo compile failed after DeepSeek revision attempts: MyGo compile failed` |
| 静态检查提示 | `Do not use for loops. Rewrite using scalar state or a compact arithmetic/bitwise formula; for memory/register-bank behavior, keep only the scalar visible state needed by the transaction.` |

原始报错摘录：

```text
cvdp_copilot_unpacker_one_hot_0001: MODEL_STATIC_ERROR
MyGo compile failed after DeepSeek revision attempts: MyGo compile failed

evidence restricted_go_check_attempt4.txt:
Do not use for loops. Rewrite using scalar state or a compact arithmetic/bitwise formula; for memory/register-bank behavior, keep only the scalar visible state needed by the transaction.
```

分析：这题是 one-hot unpacker 类型，合理实现一般应该是根据输入索引或 bit mask 生成 one-hot 输出。失败类别是 `MODEL_STATIC_ERROR`，说明问题更靠近 LLM 产物本身：经过多轮修复后，模型仍没有给出满足 restricted-Go 静态规则且能被 MyGo 编译的版本。静态检查明确指出仍存在 `for` loop。

这类题本来适合用简单公式或手动展开实现，例如按输入位宽写成若干条件赋值，或者用位移表达式生成 one-hot。但模型倾向写通用循环，这在普通 Go 里自然，在 MyGo restricted subset 里不合格。因此本题主要体现的是 LLM Go 生成质量问题，而不是后端仿真答案错误。后续改进方向是继续把全局 prompt 写得更“硬”：遇到 one-hot、priority encoder、unpacker、mapper 这类任务时，禁止使用通用循环模板，优先使用固定宽度表达式、case-like if/else 或手动展开。

## 5. 修改后 MyGo 相比原始 `pku-lemonade/MyGO` 改了哪些地方

当前服务器工作树相对于原始基线有编译器、runner、prompt 和评测脚本四类修改。粗略 diff 规模为：

```text
15 files changed, 1935 insertions(+), 179 deletions(-)
```

涉及文件包括：

```text
internal/frontend/preprocess.go
internal/frontend/preprocess_test.go
internal/ir/builder.go
internal/ir/builder_sensitivity.go
internal/ir/call_inline.go
internal/ir/ir.go
internal/mlir/emitter.go
internal/mlir/emitter_test.go
internal/passes/widthinfer.go
internal/passes/widthinfer_test.go
scripts/run_cvdp_deepseek_mygo.py
tests/verilog-eval/eval_ab_harness.py
tests/verilog-eval/go_dsl.md
tests/verilog-eval/prompt_template.md
tests/verilog-eval/repair_go_prompt_template.md
```

### 5.1 CVDP runner 与 API 调用

1. 增加 OpenRouter / DeepSeek V4 Pro 调用支持，并在 OpenAI SDK 不可用时使用 HTTP fallback。
2. 增加 API timeout、空响应、MODEL_ERROR 的重试逻辑，减少“模型没返回”导致的无效失败。
3. 增加多次 Go 生成/修复尝试，本次 full run 使用 `--go-attempts 4`。
4. 保存每轮 prompt、模型原始输出、Go 文件、静态检查结果、MyGo 日志、SystemVerilog 输出、cocotb 日志和 JSON 结果，方便失败复盘。
5. 修复工具路径，显式加入 Go、CIRCT、iverilog、vvp，避免把环境缺失当成 MyGo 失败。

### 5.2 全局 prompt 与静态检查

1. 把任务从“随意写 Go”收紧为“restricted Go hardware DSL”。
2. 要求只生成一个目标硬件函数和一个空 `main`。
3. 禁止 `for` loop、额外 helper function、array/slice/map/struct、switch、动态内存、重复命名等不稳定写法。
4. 要求使用标量状态、位运算、短 `if/else`、手动展开来表达硬件逻辑。
5. repair prompt 会把静态检查和 MyGo 编译错误反馈给模型，让模型按全局规则重写，而不是对每个题目写定制 prompt。

这部分直接解决了大量“LLM 生成的 Go 不在 MyGo 子集里”的问题。

### 5.3 CVDP harness 与 wrapper 兼容性

1. 修正 cocotb 结果判定：即使进程 return code 为 0，只要日志中出现 `AssertionError`、`failed`、readback mismatch 等，也要判为 FAIL。
2. 对 missing child object、端口名不匹配、参数名不匹配等问题做更准确分类，避免把“答题格式不匹配”误报成环境问题。
3. 增加 wrapper/端口兼容处理，使 MyGo 生成设计更容易接入 CVDP harness。
4. 保留原始 cocotb 报错，便于区分“答案逻辑错”和“端口/测试契约错”。

这部分提升了成绩可信度，也让失败 taxonomy 更适合向老师汇报。

### 5.4 MyGo 编译器前端与 IR

1. 增加/改进 frontend preprocessing，用于清理 LLM 常见生成模式。
2. 改进 IR builder，对赋值路径、敏感信号、组合/时序逻辑构造更稳。
3. 增加 call inline 相关逻辑，处理部分 helper function 或调用式代码。
4. 改进 sensitivity 分析，并做缓存/去重，减少复杂生成代码导致的展开爆炸。
5. 改进宽度推断，尤其是 unsigned mask、packed value、布尔/多 bit 混用等场景。

这些修改主要解决“Go 能写出来，但 MyGo 前端或 IR 接不稳”的问题。

### 5.5 MLIR emission 修复

1. 修复 clock/reset/condition 类信号在 MLIR 中的类型不一致问题。
2. 当多 bit 端口被用作 `sv.if` 或 `sv.always` 的控制条件时，自动提取 bit0，避免 `i1` 与 `i8` 等类型冲突。
3. 改进信号派生条件、packed value、fallback read 等 emission 路径。
4. 增加相关测试，避免修复某一类 reset/condition 后破坏其他 emission 场景。

这部分解决的是典型 MyGo 编译器后端问题，例如多 bit reset、控制条件类型和 MLIR verifier 不接受的问题。

### 5.6 和 GitHub 同步状态

已经同步到 `ZeeMo-PKU/MyGO` 的公开 PR：

```text
PR #2: https://github.com/ZeeMo-PKU/MyGO/pull/2
branch: systematic-mygo-fixes-20260612
commit: a2eab6d36045f06e192e3f87b603a92366c345fd
```

注意：服务器 v31 full run 使用的是当前服务器工作树，里面包含 PR #2 已同步内容，也包含后续本地继续迭代的编译器/frontend/IR 相关修改。因此，如果老师要完全复现 75/78，需要以服务器当前工作树或后续整理后的完整 commit 为准，而不应只看原始 `pku-lemonade/MyGO`。

## 6. 结果解释

CVDP 上当前最重要的结论是：修改后 MyGo route 已经在 fresh full 78 run 上达到 75/78，超过 Direct Verilog 的 68/78。也就是说，MyGo 这条路线不是只靠“多跑几次合并 pass 数”变好，而是在一次完整重跑里已经体现出优势。

剩余 3 个失败并不是环境缺失，也不是 iverilog、CIRCT、Python venv 没配好。它们集中在两类问题：

1. LLM 仍生成了不符合 MyGo restricted subset 的 Go，比如 `for` loop、helper function。
2. MyGo 对少数复杂生成代码仍可能在 MLIR 阶段 timeout，说明 compiler-guided repair 和编译器鲁棒性还有继续提升空间。

因此，当前可以向老师汇报的口径是：CVDP 上 MyGo 经过全局 prompt、静态检查、compiler-guided repair 和编译器修复后，fresh full run 已经显著超过 Direct Verilog baseline；剩余失败主要集中在 restricted-Go 约束违反和少数 MLIR timeout，后续优化方向明确。