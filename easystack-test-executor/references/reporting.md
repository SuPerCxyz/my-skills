# Reporting

## Result Model 结果模型

面向用户的 `执行结果` 只允许 `成功` 或 `失败`:

```text
all required functional checks PASS -> functional_status=PASS -> 成功
otherwise                           -> functional_status=FAIL -> 失败
```

模型不得手填 Functional status。`python3 scripts/finalize-case.py` 使用 contract evaluator 和
Action evidence 自动派生:

```text
functional_status
timing_status
evidence_status
cleanup_status
diagnostic_status
execution_quality
```

命令 return code 为 0 不能单独证明功能通过。Manual evaluator 只作为无法声明
declarative evaluator 的 fallback; 缺少 Actual 或 Evidence 时为 UNKNOWN。

Timing、Evidence 和 Cleanup 是独立质量维度, 不覆盖已经由 Functional checks 得出的
结果。当 `timing_status=INVALID` 或 required evidence 为 PARTIAL/MISSING/INVALID 时,
在成功/失败下一行输出一条简短 `说明:`。

optional 日志未采集使用 `OPTIONAL_NOT_COLLECTED`, 不输出关键日志缺失说明, 不把用例
标为 PARTIAL。`log_requirement=none` 使用 `NOT_APPLICABLE`。

## Functional Verification 功能验证

每个用例至少有一个 `required=true`、`check_type=functional` 的检查。按需覆盖:

- 资源终态, 不只验证资源存在或 API return code。
- deterministic data 或 SHA-256。
- Server ACTIVE、guest readiness、登录和 dataplane。
- Snapshot、clone、cache、migration、retype、upload、rebuild 或 evacuation。
- encryption key ID relation 和 ownership, 但不记录 key material。
- negative path 的拒绝层级、状态一致性和无残留。

内部路径使用 `check_type=diagnostic`。需要证明 clone、cache、copy、connector、
scheduler 或 driver 分支时, Evidence 必须指向 worker/backend 原文。无直接证据写
UNKNOWN, 不从资源终态或 UI 反推。

## Step Evidence 步骤证据

每个 contract action 都必须有 terminal step event。真实执行的步骤还必须有:

```text
command_id
start_local
end_local
timezone
duration_ms
timeout_seconds
timed_out
return_code
stdout_path
stderr_path
request_ids
```

每次尝试写唯一 output path, 不覆盖证据。缺少任何 action 时间时派生
`timing_status=INVALID`, 在 `执行结果` 简单说明, 但不伪造时间。

## Resource Ledger 资源台账

资源由 Action output 自动 capture 到 event。Case/global ledger 是 event projection,
记录 type、name、ID、created local time、owning action、dependency、cleanup policy、
final state 和 cleanup result。

资源名使用 `test-<case_id>-<role>-<short_suffix>`, 不包含 Run ID 时间戳。Floating IP
以 address 作为 name。Server 同时记录 Boot Volume、Port、Floating IP 关联和实际
force delete strategy。

## Log Evidence 日志证据

报告只引用最小充分且已脱敏的 worker 日志。每条证据记录 service、Pod、Container、
本地时间、原始 timestamp、source timezone、Request/Resource ID、source path 和
excerpt。完整 raw log 留在用例目录。

required 日志只有覆盖全部 contract targets 且存在 correlation evidence 时才是
COMPLETE。API 日志不能替代 `cinder-volume`、`nova-compute` 或实际 network/backend
worker 对内部执行分支的证明。

## Cleanup Policies 清理策略

支持 `preserve_all`、`preserve_on_failure`、`cleanup_on_success`、`cleanup_all` 和
`explicit_per_case`。证据收集后按资源依赖图逆序清理, 不删除运行外资源。

每个资源的 cleanup result 必须终态化为 DELETED、PRESERVED、NOT_APPLICABLE 或
FAILED。任一 PENDING/FAILED 使 `cleanup_status=PARTIAL`; 全部保留则为 PRESERVED。

## Output Layout 输出目录

```text
<RESULT_ROOT>/
├── execution-contract.json
├── events.jsonl
├── run-state.json
├── resume.md
├── environment-profile.json
├── impact-analysis.json
├── authorization.json
├── artifact-manifest.jsonl
├── normalized-cases.json
├── resources-all.json
├── summary.md
├── results.csv
├── run.json
└── cases/<CASE_ID>/
    ├── case.json
    ├── commands.jsonl
    ├── resources.json
    ├── case-verdict.json
    ├── result.json
    ├── result.md
    ├── attempt-<NN>/openstack/
    └── logs/
        ├── instances-before.json
        ├── instances-after.json
        ├── collection-status.json
        └── raw/
```

`RunID` 格式为 `R<YYYYMMDDHHmmss>`, 只用于结果目录和内部关联。目录权限为 `0700`,
证据文件为 `0600`。环境 profile 独立保存在
`/tmp/easystack-test-executor-profiles`, 不打包到 skill。

## Deterministic Output 确定性输出

严格格式、标题、索引、字段顺序和示例由
[report-format.md](report-format.md) 定义。只能运行:

```bash
python3 scripts/render-report.py --result-root <RESULT_ROOT>
python3 scripts/validate-run.py --result-root <RESULT_ROOT>
```

不得手工编辑 `result.json`、`result.md`、`summary.md`、`results.csv` 或 `run.json`。
用例顺序来自 immutable contract, 不按字符串重新排序。validator 返回 0 前不得声明
测试运行完成。
