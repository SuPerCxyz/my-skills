# Common Debugging Scenarios

## Execution Location 命令位置

**不要**在业务 pod(如 cinder-golem、cinder-api、nova-api 等)中执行 openstack 命令,这些 pod 没有 CLI 工具和认证环境。

| 操作类型 | 执行位置 | 说明 |
|---------|---------|------|
| 普通 openstack 操作 | **busybox** pod | `source /openrc` 后执行 |
| Nova 高级信息查看 | **nova-maintenance-xxx** pod | 仅查看 pod 和日志; 管理操作需授权 |
| Cinder 信息查看 | **cinder-volume** pod | 仅查看日志和配置; manage 操作需授权 |
| 业务日志查看 | 对应业务 pod | 用 `kubectl logs` 查看 |

## SSH 访问与节点跳转

环境后台访问、`172.18.*` 跳板、JumpServer、连接验证和节点间跳转统一参考
[access.md](access.md)。场景排查文件不重复维护 SSH 命令,避免与实际入口方式冲突。

## Common Resource Issues 常见资源问题

云主机异常和云硬盘异常属于常见问题。用户说 "看某个虚拟机异常原因"、
"查 server/instance 状态异常"、"云硬盘挂载失败"、"volume 创建失败" 或
"磁盘状态异常" 时, 先按 [access.md](access.md) 进入环境并完成只读验证,
再按本节选择日志优先的根因排查入口。

OpenStack 资源状态查询统一在 busybox 中执行, 认证方式见 [auth.md](auth.md)。
不要在 `nova-api`、`cinder-api`、`cinder-golem` 等业务 pod 中直接执行
`openstack` 命令。

如果用户问的是 "原因"、"为什么失败"、"创建失败"、"挂载失败", 或已经提供
traceback / error message / UUID, 先查相关服务日志。资源状态查询不是第一步,
除非用户明确要求状态, 或日志线索已经指向需要补充 server/volume 上下文。
允许先用 `kubectl get pods` 或 label 查询发现要读取日志的 pod。

### Virtual Machine Issues 云主机问题

先确认用户提供的是云主机名称还是 UUID。根因排查时, 优先用 server UUID 或
错误关键字查看 `nova-api`、`nova-conductor`、`nova-scheduler` 和相关
`nova-compute` 当前 pod 日志; 当前日志缺失或不完整时再查 fluentd 历史日志。

以下 OpenStack CLI 只用于补充上下文或用户明确要求查看资源状态, 不作为异常原因
排查的默认第一步:

```bash
kubectl exec -n openstack services/busybox -- bash -c 'source /openrc && openstack server show <server-id-or-name>'
kubectl exec -n openstack services/busybox -- bash -c 'source /openrc && openstack server list --long'
```

根据查询结果分流:

- `status` 为 `ERROR` 或存在 `fault` → 用 `fault` message 中的异常、server UUID
  或 request id 回到 Nova 日志定位具体服务。
- `OS-EXT-SRV-ATTR:host` 有值 → 同时查该计算节点上的 `nova-compute` pod。
- 创建、调度、迁移、evacuation、host maintenance 相关问题 → 参考
  [openstack/nova.md](openstack/nova.md) 和
  [special-operations.md](special-operations.md#nova-maintenance-pod)。
- 网络连通、端口、安全组、浮动 IP 相关问题 → 参考
  [openstack/networking.md](openstack/networking.md) 和 [network.md](network.md)。
- 根盘或数据盘相关报错 → 同时按下方 Cloud Volume Issues 查询云硬盘。

### Cloud Volume Issues 云硬盘问题

先确认用户提供的是云硬盘名称还是 UUID。根因排查时, 优先用 volume UUID 或
错误关键字查看 `cinder-api`、`cinder-scheduler`、`cinder-volume` 当前 pod
日志; 当前日志缺失或不完整时再查 fluentd 历史日志。

如果上游服务日志只显示等待云硬盘操作超时或状态异常, 不要停在上游错误栈。
继续用 volume UUID、request id、backend、host 或异常关键字搜索 Cinder 日志,
再按实际失败服务的日志定位根因。

以下 OpenStack CLI 只用于补充上下文或用户明确要求查看资源状态, 不作为创建失败
根因排查的默认第一步:

```bash
kubectl exec -n openstack services/busybox -- bash -c 'source /openrc && openstack volume show <volume-id-or-name>'
kubectl exec -n openstack services/busybox -- bash -c 'source /openrc && openstack volume list --all --long'
```

根据查询结果分流:

- `status` 为 `error`、`error_extending`、`error_attaching` 或长期卡在中间态
  → 回到 `cinder-api`、`cinder-scheduler`、相关 `cinder-volume` 当前 pod 日志定位异常。
- 创建失败后资源可能很快被删除; `volume show` 返回 404 时, 用 volume UUID 搜
  cinder 当前 pod 日志; 当前日志缺失或不完整时再查 fluentd 历史日志。
- `Filtering removed all hosts` 且某个 filter 最终 `end: 0` → 按该 filter
  定位原因; `CapabilitiesFilter` 归零时优先检查 volume type/extra specs
  和后端 capabilities。
- `cinder-volume ... not sending heartbeat` 或 `Update driver status failed:
  (config name <backend>) is uninitialized` → 后端服务不健康或 driver 未初始化,
  会影响 scheduler 获取可用 capabilities。
- `attachments` 指向某个 server → 同时按 Virtual Machine Issues 查询该云主机。
- 云硬盘后端、Ceph/RBD、容量或 pool 相关线索 → 同时参考 [ceph/index.md](ceph/index.md)
  和 [openstack/cinder.md](openstack/cinder.md)。
- 挂载、卸载、extend、snapshot、backup 相关管理动作会改变环境状态; 未经用户明确授权,
  只能查询状态和日志。

## Service Failing to Start 服务启动失败

```bash
# 1. Check pod status and events
kubectl describe pod -n openstack <pod-name>

# 2. Check logs
kubectl logs -n openstack <pod-name> --tail=50
kubectl logs -n openstack <pod-name> --previous   # Previous instance if crashed

# 3. If current pod logs are missing or incomplete, check fluentd logs
kubectl exec -n openstack fluentd-0 -c httpd -- ls /var/www/html/td-agent/openstack/<service>/

# 4. If config issue, inspect config only
kubectl get cm -n openstack <service>-etc -o yaml
kubectl describe pod -n openstack <pod-name>
```

## Database Issues 数据库问题

```bash
kubectl exec -n openstack mariadb-0 -- mysql --defaults-file=/etc/mysql/admin_user.cnf -e "show databases;"
kubectl exec -n openstack mariadb-0 -- mysql --defaults-file=/etc/mysql/admin_user.cnf -e "show processlist;"
```

需要进一步检查数据库时, SQL 保持只读:

```sql
show databases;
use <service_name>;
show tables;
show processlist;
```

常见服务数据库包括 `keystone`, `nova`/`nova_api`/`nova_cell0`, `cinder`,
`glance`, `neutron`。

## Configuration Debugging 配置排查

```bash
# View a configmap (don't edit yet)
kubectl get cm -n openstack <service>-etc -o yaml

# Find the specific config file
kubectl get cm -n openstack <service>-etc -o yaml | grep "cinder.conf\|nova.conf"

# Check current mounted config in a running pod
kubectl exec -n openstack <pod-name> -- cat /etc/<service>/<config-file>
```

## Inspecting a Bad Change 查看异常变更

```bash
# View Helm history only
helm history -n openstack <release-name>

# View current config only
kubectl get cm -n openstack <service>-etc -o yaml
```

Rollback, manual restore, ConfigMap edits, and pod restarts affect the environment.
Do not run them unless the user explicitly authorizes that exact change.
