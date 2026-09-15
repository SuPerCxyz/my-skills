# Logs

当问题涉及可访问环境中的运行时日志时阅读本文件。仅分析离线 `.eslog` 或已解压
`ecs.*` 目录时使用 `easystack-log-analysis`。若问题发生时间较久且本地同时存在
这两类离线日志, 按 [SKILL.md](SKILL.md#offline-historical-log-coordination-离线历史日志协同)
联合使用两个 skill。

## Log Lookup Order 日志查询顺序

调查刚发生或仍在发生的问题时, 先从相关业务 pod 读取当前日志。不要一开始就进入
fluentd pod 查历史日志, 因为当前 pod 的 stdout/stderr 往往还保留最近错误,
定位更快且能直接对应当前副本。

用户说 “看异常原因”、“为什么失败”、“创建失败”、“挂载失败”, 或提供 traceback、
error message、server UUID、volume UUID 时, 即使没有明确说 “直接看日志”,
也按日志优先处理。不要先进入 busybox 执行 `openstack server show`、
`openstack volume show` 或 list 类资源状态查询。`kubectl get pods` / label
查询只用于发现要读取日志的 pod, 不属于资源状态优先。

使用 fluentd 的条件:

- 当前业务 pod 日志没有目标时间段或关键 UUID
- pod 已重启, 当前日志缺失, `--previous` 也没有足够信息
- 同一服务多个 pod 中只有部分 pod 还能看到日志, 需要补齐其他副本或节点的历史日志
- 需要跨节点、跨副本或按日期搜索完整历史

搜索停止条件:

- 已覆盖故障时间窗、目标资源所在节点和当前已发现的关联服务时, 停止扩展搜索。
- 只有发现新的 request ID、资源标识、节点或底层异常信号时, 才扩展到新的节点或服务。
- 同一节点、服务、时间窗和关键词已经取得证据时, 不重复执行相同查询; 只在需要更大上下文
  或验证矛盾证据时重查。

## Evidence Preservation 关键证据保全

问题调查开始前先读取 [report-format.md](report-format.md), 再按报告中的时间线字段收集
证据。发现能证明关键操作、状态变化、直接失败或底层触发机制的日志时, 立即记录以下
最小信息, 不要在报告阶段依赖重新搜索:

- 原始日志: 保留原文, 不改写错误信息、堆栈、时间或字段. 报告输出时按模板需要添加
  `原文: ` 前缀, 但不得把前缀混入保存的原始内容。
- 来源: 在线日志记录 namespace、pod、container、服务和节点; fluentd 记录 pod、文件
  路径和日期; 离线日志记录 `file:line`。
- 时间和关联: 记录日志时间、资源显示名称和 UUID、request ID、云主机名、volume ID 或
  其它已出现的关联标识。
- 必要上下文: 保留能说明触发动作、结果和因果关系的相邻行, 不保留无关大段日志。
- 证据作用: 标明该日志证明用户现象、直接失败还是底层根因, 以及它需要由哪个关联
  组件继续验证。

凭据、token、密码和私钥必须在保留或输出前脱敏。证据缺口不能由推测填补, 应记录为
后续最小查询或第 3 节的未确认项。

## Real-time Logs (kubectl) 实时日志

服务日志输出到 stdout/stderr, 不写入 pod 内的 `/var/log/`。
以下 `--tail` 示例只适用于查看最新日志。按 UUID、request id、错误关键字或
traceback 搜日志时, 不要在 `grep` 之前加 `--tail`; 先过滤, 再限制最终输出。

```bash
# Single-container pod
kubectl logs -n openstack <pod-name> --tail=200

# Multi-container pod - specify container name
kubectl logs -n openstack <pod-name> -c <container-name> --tail=200

# List containers first
kubectl get pod -n openstack <pod-name> -o jsonpath='{.spec.containers[*].name}'

# Follow only when waiting for new log output
kubectl logs -f -n openstack <pod-name> --tail=50

# Previous instance (if crashed/restarted)
kubectl logs -n openstack <pod-name> --previous
```

## Filter Before Tail 先过滤再截断

按资源 UUID 或错误关键字查日志时, 前置 `--tail=100` 只会搜索最近 100 行,
容易漏掉真正的失败日志。正确顺序是先用时间范围、pod、service 或文件范围缩小
输入, 再 `grep` / `zgrep`, 最后用 `tail` / `head` 限制输出给 agent 的结果。

```bash
# Current pod logs: filter first, then limit final output
kubectl logs -n openstack <pod-name> --since=2h 2>/dev/null | grep -F "<resource-uuid>" -B 5 -A 20 | tail -200

# If the time window is unknown, do not add --tail before grep
kubectl logs -n openstack <pod-name> 2>/dev/null | grep -F "<resource-uuid>" -B 5 -A 20 | tail -200
```

## Historical Logs (Fluentd) 历史日志

fluentd pod 数量随环境而变。要获取某个服务的完整历史日志, 先列出实际 fluentd pod,
再逐个检查。

**日志位置:** `/var/www/html/td-agent/openstack/<service>/<component>.<node>.<YYYYMMDD>.log.gz`

**目录结构:**
```
/var/www/html/td-agent/
├── openstack/          ← OpenStack service logs (nova, cinder, glance, keystone, ...)
├── ceph/               ← Ceph service logs
├── kubernetes/         ← K8s component logs
├── archives/           ← Older rotated logs (may be empty if cleaned)
```

**访问 fluentd pod**(默认容器为 `httpd`):
```bash
# View logs for a specific service on one fluentd pod
kubectl exec -n openstack <fluentd-pod> -c httpd -- ls /var/www/html/td-agent/openstack/<service>/

# Read a specific log file
kubectl exec -n openstack <fluentd-pod> -c httpd -- zcat /var/www/html/td-agent/openstack/<service>/<component>.node-<N>.<date>.log.gz | tail -100
```

**Search across all fluentd pods** (requires shell on target node entered by env-access):
```bash
# First enter the target node via `bash <path>/env-access.sh`, then run:
fluentd_pods=$(kubectl get pods -n openstack -o name | sed 's#^pod/##' | grep '^fluentd-[0-9]\+$')
for pod in $fluentd_pods; do
  echo "=== $pod ==="
  kubectl exec -n openstack "$pod" -c httpd -- ls /var/www/html/td-agent/openstack/<service>/ 2>/dev/null
done

# Search log content across all pods:
for pod in $fluentd_pods; do
  echo "=== $pod ==="
  kubectl exec -n openstack "$pod" -c httpd -- sh -c 'zcat /var/www/html/td-agent/openstack/<service>/*.gz 2>/dev/null' | grep "<search-keyword>" | tail -20
done
```

按资源 UUID 搜日志时, 先搜对应服务目录, 例如 volume 查 `openstack/cinder`,
server 查 `openstack/nova`。根因排查默认可以跳过数据库和 OpenStack CLI 状态查询;
只有日志缺少关联信息或用户明确要求资源状态时再补查。

```bash
fluentd_pods=$(kubectl get pods -n openstack -o name | sed 's#^pod/##' | grep '^fluentd-[0-9]\+$')
for pod in $fluentd_pods; do
  echo "=== $pod ==="
  kubectl exec -n openstack "$pod" -c httpd -- sh -c 'zgrep -h -F "<resource-uuid>" /var/www/html/td-agent/openstack/<service>/*.gz 2>/dev/null' | tail -50
done
```

**日志行格式**(以竖线分隔):
```
<fluentd-timestamp> | <node-name> | <pod-name> | <service-name> | <actual log line>
```

**何时使用 fluentd 或 kubectl logs:**
- `kubectl logs` - 默认优先, 适合刚发生的问题、当前 pod、当前副本和短时间窗口
- Fluentd - 回退或补齐, 适合当前 pod 日志缺失、不完整、重启后丢失或需要跨副本搜索
