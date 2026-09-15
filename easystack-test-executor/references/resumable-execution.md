# Resumable Execution

## Purpose 目标

V3 harness 将 profile、impact、authorization、Action 和 checks 编译为 immutable
contract。状态、commands、resources 和 artifacts 从 hash-chained events 投影。

## Step 1: Compile Plan 编译计划

先按 [case-normalization.md](case-normalization.md) 生成完整 YAML/JSON, 再运行:

```bash
python3 scripts/compile-plan.py \
  --plan <NORMALIZED_PLAN> \
  --profile /tmp/easystack-test-executor-profiles/<ENVIRONMENT_KEY>.yaml \
  --result-root <RESULT_ROOT> \
  --run-id <RUN_ID> \
  --timezone <IANA_TIMEZONE> \
  --cleanup-policy preserve_on_failure
```

编译器冻结 profile digest、impact、authorization、用例顺序、argv、expected
outcome、capture、checks、logs 和 cleanup。非空目录会被拒绝。

## Step 2: Follow One Allowed Action 执行唯一动作

每次操作前运行:

```bash
python3 scripts/checkpoint.py next --result-root <RESULT_ROOT>
```

只执行输出的 `launcher_argv`。常见 `allowed_action` 为 `run_action`、
`advance_phase`、`derive_verdict`、`skip_action`、`finalize_result` 和
`run_complete`。`blocked_contract` 必须先修复 contract 输入, 不得自行替代命令。

## Step 3: Run Bound Action 执行绑定动作

`launcher_argv` 使用显式 Python 解释器调用 `run-action.py`, runner 只执行 contract 中的 argv。它自动记录
local time、duration、return code、timeout、Request ID、stdout/stderr hash 和 status。
V3 禁止 `python3 scripts/record-command.py`、`python3 scripts/checkpoint.py step` 和手填 PASS/FAIL。

Expected non-zero 通过 `expected.return_codes` 表达。实际返回码属于允许集合且未超时才
为 PASS。Command exit 0 不能替代 declarative check。

## Step 4: Capture Resources 捕获资源

Create Action 必须使用 `-f json` 或 `-f value`, 并在 `capture.resources` 声明 key、
type、ID 和 name selector。Command、resource capture 和 status 写入同一 Action event,
随后重建 case/global ledger。模型不得另行补记 UUID。

## Step 5: Collect Logs 收集日志

required/optional 日志先后执行 `python3 scripts/collect-logs.py snapshot --stage before/after`, 再执行
`python3 scripts/collect-logs.py collect`。工具按 Pod UID 合并滚动期间的实例, 保存 raw log、
correlation ID、UTC 原始时间和本地时间。required 目标未覆盖时不能标记 COMPLETE。

optional 日志未采集派生为 `OPTIONAL_NOT_COLLECTED`, 不产生功能失败或虚假的 PARTIAL。
required 日志缺失派生为 MISSING; 内部分支检查缺少证据时 observation 必须为 UNKNOWN。

## Step 6: Derive Verdict And Result 派生结果

在 `DERIVE_VERDICT` 执行返回的 launcher, 由 `action_status`、`json_path`、`regex`
或显式 manual evaluator 生成 immutable `case-verdict.json`。所有 required
Functional checks 为 PASS 时 Functional status 才为 PASS。

Cleanup 完成后在 `FINALIZE_RESULT` 生成 `result.json`, 添加 cleanup、remaining
resources 和 run fingerprint。模型不得创建或编辑这两个文件。

## Step 7: Render And Validate 生成和校验

所有用例 COMPLETE 后运行:

```bash
python3 scripts/render-report.py --result-root <RESULT_ROOT>
python3 scripts/validate-run.py --result-root <RESULT_ROOT>
```

Validator 校验 contract/profile digest、event chain、Action projection、artifact hash、
checks、严格日志关联、resources、verdict、cleanup 和 Markdown。exit code 0 才能完成。

## Recovery Rules 恢复规则

1. Context compaction 后只读 `resume.md`, 再运行 `python3 scripts/checkpoint.py next`。
2. 不重做有 terminal event 的 Action。
3. 不修改 event、contract、projection、verdict 或 report。
4. 超时后先核对后台 task 和资源, 只有 contract 允许才重试。
5. 需要中止时使用 `python3 scripts/checkpoint.py abort`, 再生成 partial report。
6. V2 结果只读校验和渲染, 不继续执行任意命令。
