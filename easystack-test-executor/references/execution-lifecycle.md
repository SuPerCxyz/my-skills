# Execution Lifecycle

## Concurrency 并发

默认全局串行执行。以下任一条件成立时禁止并行:

- 日志窗口从上一个用例结束延续到当前用例结束。
- 用例共享 Cache、Volume、Snapshot、Image、Server、Host 或 Backend。
- 包含故障注入、服务重启或主机操作。
- 资源名称、依赖或清理动作可能冲突。
- Request ID 不足以可靠分离日志。

只有计划明确允许, 且资源、日志、依赖和清理完全隔离时才可并行。并行前记录隔离
依据和最大并发数。

## State Machine 状态机

```text
DISCOVER_CASE_CONTEXT -> OPEN_LOG_WINDOW -> SNAPSHOT_SERVICE_INSTANCES
-> PREPARE -> EXECUTE -> WAIT -> VERIFY -> CLOSE_LOG_WINDOW
-> COLLECT_LOGS -> COLLECT_RESOURCES -> DERIVE_VERDICT
-> APPLY_CLEANUP_POLICY -> FINALIZE_RESULT -> CASE_GATE
-> ADVANCE_LOG_CURSOR -> COMPLETE
```

Action phases 可包含 0 到多个 contract action。其余 phase 由 harness gate 控制。
`case-verdict.json` 在 cleanup 前生成且不可修改; `result.json` 只在 cleanup 后生成。

## Invariants 必守不变量

1. 只执行 `python3 scripts/checkpoint.py next` 的 `launcher_argv`; phase 只推进一个相邻状态。
2. Action argv、allowed return codes、capture 和 evaluator 编译后不可变。
3. Action terminal status 由 runner 自动派生; expected non-zero 可判定为 PASS。
4. 每个 Action 保存 local time、offset、monotonic duration、Command ID 和 output hash。
5. Resource capture 与 Action event 一起提交, 台账从 event 重建。
6. Required Functional checks 自动派生 verdict; 模型不能填写 Functional status。
7. Worker log 只能用已知 Request/Resource ID 关联, 并保存 Pod UID 和 Container。
8. 先收集证据再 cleanup; 只删除 contract 授权且由本运行创建的资源。
9. `执行结果` 只映射 Functional status。timing、evidence、cleanup 只产生说明。
10. 恢复只信任 contract、hash-chained events 和 `python3 scripts/checkpoint.py next`。

## Command Records 命令记录

每条 Action event 包含 Case/Action/Attempt/Command ID、脱敏命令、执行位置、本地
时间、duration、timeout、实际/允许返回码、Request ID 和 artifact metadata。

```text
cases/<CASE_ID>/commands.jsonl
cases/<CASE_ID>/attempt-<NN>/<KIND>/<ACTION>.<COMMAND_ID>.stdout.log
artifact-manifest.jsonl
```

`commands.jsonl` 和 resource ledger 是 event projection, 不可手工修改。

## Timeouts And Polling 超时和轮询

异步 Action 声明 timeout、success/failure states 和 polling。超时必须产生 terminal
event。只在 contract 声明幂等或明确允许时重试。

## Failure Handling 失败处理

Action 失败仍关闭窗口、收集日志和资源、派生 verdict、执行 cleanup policy、生成结果。
失败依赖的后续用例自动 skip; 独立用例继续。全局中止使用 `python3 scripts/checkpoint.py abort`,
随后以 `--allow-partial` 生成报告。

## Retry Handling 重试处理

重试使用独立 Attempt 和 Command ID, 不覆盖证据。重试前确认后台任务和资源状态;
不能确认幂等性时标记 BLOCKED。

## Destructive Cases 破坏性用例

删除、重启、故障注入或主机操作必须同时出现在 authorization 和 Case
`destructive_operations`, 并记录前置状态、精确目标、恢复路径和操作后证据。
