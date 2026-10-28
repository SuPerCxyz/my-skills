# Log Line Format

Use this file when parsing log lines, grouping by node/pod/container, or writing awk/grep pipelines against decompressed `.log` files.

## Wrapper Format 日志包装格式

All decompressed `.log` files use a uniform 5-field prefix added by the log
collector, separated by a single Unicode middle-bar character `¦` (U+00A6,
NOT the ASCII pipe `|`):

```
<wrapper_ts> +0800 ¦ <node> ¦ <pod_or_source> ¦ <container> ¦ <raw_log_line>
```

Example (from `openstack/nova/nova-compute.node-1.20260618.log`):

```
2026-06-18 10:24:24.517 +0800 ¦ node-1 ¦ nova-compute-67lgd ¦ nova-compute ¦ 2026-06-18T10:24:24.517915479+08:00 stderr F ++ hostname -s
```

Fields:

| # | Field | Notes |
|---|-------|-------|
| 1 | `wrapper_ts` | Collector timestamp (wall clock when the line was harvested) |
| 2 | `node` | Hostname (e.g. `node-1`) |
| 3 | `pod_or_source` | Kubernetes pod name, or `messages` / `bash-history` etc. for OS-level sources |
| 4 | `container` | Container name inside the pod (may be empty for OS sources) |
| 5 | `raw_log_line` | The actual log line emitted by the service |

The application's own timestamp lives **inside** field 5 (e.g.
`2026-06-18T10:24:24.517915479+08:00 stderr F ...`), so a regex on
"date" matches twice per line - the wrapper TS and the inner TS.

## Practical Implications 使用要点

### Plain grep 直接检索

Plain `grep "VolumeDeviceNotFound" nova-compute.*.log` works because the
text inside field 5 is unchanged. **You do not need to parse the wrapper to
do content search.**

### Awk Axes 按实例维度分析

```bash
# Count events per pod
awk -F' ¦ ' '/ERROR/ {print $3}' ecs.*/openstack/nova/nova-compute.*.log | sort | uniq -c

# Extract only the raw log line (drop wrapper)
awk -F' ¦ ' '{print $5}' ecs.*/openstack/nova/nova-compute.*.log

# Filter by container name (multi-container pods)
awk -F' ¦ ' '$4 == "nova-compute" {print}' ecs.*/openstack/nova/nova-compute.*.log

# Wrapper TS + raw line only (for clean correlation)
awk -F' ¦ ' '{print $1, $5}' ecs.*/openstack/nova/nova-compute.*.log
```

### Pod Lifecycle Pod 生命周期

容器在同一 Pod 内重启时可保留名称和 UID。Pod 替换时 UID 改变, 名称是否改变
取决于 controller; StatefulSet 可复用名称。下面只能列出采集到的名称:

```bash
awk -F' ¦ ' '{print $3}' ecs.*/openstack/nova/nova-compute.*.log | sort -u
```

出现多个名称表示多个 Pod 身份线索; 结合 UID、restart count、节点和事件区分
副本并存、滚动替换与容器重启, 不仅凭名称下结论。

### Time-Window Filtering 时间窗过滤

先核对本次日志的 wrapper 格式、原始时间、时区及节点时钟偏移。wrapper 可用于定位
采集范围, 但不能直接替代事件发生时间或假设跨节点天然有序; 应结合源服务时间
构建时间线。下面只演示对已确认 wrapper 格式的候选范围过滤:

```bash
grep "^2026-06-18 10:2[5-9]:" ecs.*/openstack/nova/nova-compute.*.log
```

### OS Sources 系统原始格式

For `os/messages.*.log`, `os/chrony.*.log`, `openstack/dozer/bash-history.*.log`,
field 4 (container) is empty and field 5 contains the classic syslog line:

```
2026-06-18 10:23:27.000 +0800 ¦ node-1 ¦ messages ¦  ¦ Jun 18 10:23:27 node-1 kubelet[9241]: E0618 10:23:27.448026 ...
```

## Filename Convention 文件命名

```
<service>.<node>.<date>.log
```

The hostname appears both in the directory name (`ecs.node-1.20260618.0/`)
and the filename. The decompression script keeps the original `.log.gz` and generated
`.log`. It also copies readable logs into a cross-platform `components/` view; the original
`ecs.*` paths remain the authoritative evidence sources. `.0` suffix on the directory is the
rollover index when multiple collections are made the same day.

## Bundle Time Window 采集时间窗

```
ecs.<start_ts>-<end_ts>.eslog
ecs.20260618-20260623183823.eslog
       │                  │
       │                  └── 2026-06-23 18:38:23 collection end
       └── 2026-06-18 collection start (no time = 00:00:00)
```

Read this **first** to know what time range the bundle covers and to
narrow your search.
