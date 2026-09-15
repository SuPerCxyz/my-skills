# Log Evidence

## Collection Decision 采集判断

标准化用例先设置 `log_requirement`:

- `required`: 测试目标包含内部路径、日志、错误处理或 observability 断言, 或功能失败
  需要 worker 日志诊断。
- `optional`: 日志有助于补充证据, 但不是当前功能验证所需。
- `none`: 资源状态、数据面或 guest 验证已足够, 且没有失败需要诊断。

`optional` 或 `none` 用例允许不采集日志, 分别记录 `OPTIONAL_NOT_COLLECTED` 或
`NOT_APPLICABLE`。
日志采集状态不覆盖 `functional_status`; 只有日志或 observability 本身作为 functional
check 时, 该检查的实际结果才能影响功能结果。

## Window Rules 窗口规则

维护:

```text
RUN_START_LOCAL
PREVIOUS_CASE_END_LOCAL
CASE_START_LOCAL
CASE_END_LOCAL
LOG_WINDOW_START_LOCAL
LOG_WINDOW_END_LOCAL
LOG_QUERY_START_UTC
LOG_QUERY_END_UTC
```

首个用例:

```text
LOG_WINDOW_START_LOCAL = RUN_START_LOCAL
```

后续用例:

```text
LOG_WINDOW_START_LOCAL = PREVIOUS_CASE_END_LOCAL
```

所有用例:

```text
LOG_WINDOW_END_LOCAL = CASE_END_LOCAL
```

本地时间使用带 UTC offset 的 RFC3339。查询日志前将窗口边界转换为
`LOG_QUERY_START_UTC` 和 `LOG_QUERY_END_UTC`; 日志和证据完成前不得推进游标。

## Timezone Normalization 时区归一化

报告默认展示目标环境本地时间。优先使用 profile 中的 IANA timezone, offset 只作为
采集时快照; 这样存在 DST 的环境也能按具体日期正确换算。

日志时间按以下规则处理:

1. 原始 timestamp 带 `Z` 或 UTC offset 时直接按其声明解析。
2. 原始 timestamp 不带 offset 时, 从该 Pod、Container 或服务配置确认 source
   timezone; 不得默认把它当作 UTC 或本地时间。
3. 保留 `raw_timestamp` 和 `source_timezone`, 同时生成带 offset 的
   `timestamp_local` 用于排序、窗口过滤和报告展示。
4. 无法确认 source timezone 时标记 `TIMEZONE_UNCONFIRMED`; 时间顺序影响结论的
   证据不得判为 `COMPLETE`。

例如本地时区为 `Asia/Shanghai`, UTC 日志 `2026-07-23T06:08:08Z` 在报告中展示为
`2026-07-23T14:08:08+08:00`, 同时保留原始 UTC timestamp。

## Instance Discovery 实例发现

每个目标服务在用例操作前后各保存一次实例清单, 并对两个清单取并集。优先使用稳定
label, 缺少 label 时才使用已记录的名称模式。

Kubernetes 实例按 Pod UID 识别, 不只按 pod name。记录 pod、UID、node、phase、
原始 creation timestamp、归一化本地时间、container name、container ID、restart
count 和 readiness。
涉及 compute 或 storage 节点时不得只收 controller Pod 日志。

使用 `python3 scripts/collect-logs.py snapshot` 在操作前后固化实例。target 参数格式为
`SERVICE|LABEL_SELECTOR|CONTAINER`; collection 必须以两个快照的 Pod UID 并集为准。

## Target Priority 目标优先级

日志按实际执行路径选择, 不默认收集全部 control-plane 服务:

1. Primary executor: `cinder-volume`、相关 `nova-compute`、实际 `glance-api`、
   `neutron-server` 或 `proton-server`、Neutron/OVN worker、storage driver 或
   node-side DaemonSet Pod。
2. Orchestrator: scheduler、conductor 或 taskflow, 仅在 scheduling、RPC 或状态机
   需要时补充。
3. API: 仅在 Request ID、policy、input validation、HTTP status 或 API error
   需要时补充。

报告以 Primary worker 原文作为内部路径证据。API 日志不能替代 worker 执行证据。

## Kubernetes Logs Kubernetes 日志

对实例并集中的每个容器收集当前日志:

```bash
kubectl logs -n <NAMESPACE> <POD> -c <CONTAINER> \
  --since-time=<LOG_QUERY_START_UTC> --timestamps=true
```

restart count 非 0 或发生增长时, 同时尝试 `--previous`。保存 current 和 previous
原始日志。若命令不支持结束边界, 在记录 `CASE_END_LOCAL` 后立即抓取, 再使用归一化
时间按 `LOG_QUERY_END_UTC` 过滤 merged output。

pod 可能在用例中被替换或删除时, 启动运行级连续采集并按 Pod UID 保存流。连续采集
只补充直接采集, 不能替代用例前后清单。

## Correlation 关联

优先使用 Request ID, 并同时记录:

```text
server_ids
volume_ids
snapshot_ids
attachment_ids
migration_ids
image_ids
security_group_ids
security_group_rule_ids
port_ids
floating_ip_ids
floating_ip_addresses
secret_ids
resource_names
source_hosts
destination_hosts
backends
```

使用这些关联键从 raw log 生成 `collection-status.json` 中的最小 evidence entries。
同时检查 `ERROR`、`WARNING`、`Traceback` 和用例特定失败词。不得把空日志解释为
没有错误。

对于 API/UI 不可见的执行分支, 先按 Request ID 和资源 ID 定位, 再匹配操作词,
例如 `create_cloned_volume`、`create_volume_from_snapshot`、`copy_image_to_volume`
或目标 driver 的等价日志。将证明分支的最小充分原文写入 `result.md`, 并标明
service、pod、container、timestamp_local、raw_timestamp、source timezone 和
raw source path。

只贴相关原文, 不把完整服务日志复制进报告。原文必须脱敏, 但保留 Request ID、
resource ID、函数或操作名等关联信息。

## Evidence Status 证据状态

每个目标服务记录:

- `COMPLETE`: 全部预期实例和必需日志流已收集。
- `PARTIAL`: 至少一个预期实例或 previous stream 缺失。
- `MISSING`: 没有可用日志。
- `OPTIONAL_NOT_COLLECTED`: optional 日志未采集, 不属于缺陷。
- `NOT_APPLICABLE`: 用例不需要该目标。

证据为 `PARTIAL` 或 `MISSING` 时记录告警和缺失范围, 不自动改变 `执行结果`。
`NOT_APPLICABLE` 不是异常。

## Output 输出

每个用例保存窗口、前后实例清单、`collection-status.json` 和按 Pod UID 分隔的 raw
current/previous log。collection status 汇总每个服务的预期实例、实际 stream、
correlation IDs 和最小 evidence entries。
