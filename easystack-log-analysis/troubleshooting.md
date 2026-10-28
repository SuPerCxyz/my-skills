# Troubleshooting Scenarios

Use this file for known failure signatures and example evidence chains. Treat it as a scenario reference after the standard workflow in [analysis-playbook.md](analysis-playbook.md), not as a replacement for fresh log evidence.

## Table of Contents 目录

[Scenario 1](#scenario-1-vm-hard-reboot-fails--volume-device-not-found) |
[Scenario 2](#scenario-2-node-reboot--crash) |
[Scenario 3](#scenario-3-iscsi-connection-failure) |
[Scenario 4](#scenario-4-database-connectivity-issues) |
[Scenario 5](#scenario-5-volume-attachmentdetachment-failure) |
[Scenario 6](#scenario-6-vm-reboot-after-host-reboot) |
[Scenario 7](#scenario-7-实战-case---云主机启动失败排查的高确定性路径)

<a id="scenario-1-vm-hard-reboot-fails--volume-device-not-found"></a>

## Scenario 1: Volume Device Missing 云硬盘设备未找到

### Scenario 1 Symptom 问题现象
After a compute node restart, VM hard reboot fails with:
```
Volume device not found at .
os_brick.exception.VolumeDeviceNotFound: Volume device not found at .
```

### Scenario 1 Diagnosis Flow 排查流程

**Step 1 - Check nova-compute for the error:**
```bash
grep "Failed to resume instance\|VolumeDeviceNotFound" ecs.*/openstack/nova/nova-compute.*.log
```

**Step 2 - Identify the timeline:**
```bash
# Find the reconnect attempt
grep "Rebooting instance after nova-compute restart\|Connecting to multipath volume" ecs.*/openstack/nova/nova-compute.*.log
```

**Step 3 - Check what target portals the BDM has stored:**
```bash
grep "Connecting to multipath volume\|Disconnect multipath volume" ecs.*/openstack/nova/nova-compute.*.log | grep -oP "target_iqns.*?\]"
```

先核对实际 IQN/portal 命名和后端拓扑。全部路径位于同一节点只能作为线索, 结合当前 Cinder 返回、实际会话和目标版本的连接逻辑核实, 不直接认定 BDM 陈旧。

**Step 4 - Check actual iSCSI session state:**
```bash
grep "iscsi session list\|iscsiadm.*session" ecs.*/openstack/nova/nova-compute.*.log
```

将会话与目标云硬盘的 WWID、LUN、portal 对齐, 排除其他资源共用会话; 再与 BDM 和当前后端信息比较。单独存在其他会话不能确认 connection_info 陈旧。

**Step 5 - Check WWID fallback behavior:**
```bash
grep "_find_dm_device\|wwid.*fallback\|get_volume_paths" ecs.*/openstack/nova/nova-compute.*.log
```

该日志只证明当前发现流程没有找到目标设备。是否曾被重启移除, 仍需设备事件和重启前后证据, 不能仅由 fallback 失败推定。

### Root Cause Pattern 根因候选

确认目标版本 Nova 如何保存和刷新 BDM connection_info, 对照其调用 Cinder initialize_connection/attachment API 的真实路径。后端拓扑改变后是否需要刷新必须由该版本代码和实际资源证据确认, 不套固定行号或默认行为。

To verify:
1. In the DB: compare `cinder.volume_attachment.connection_info` vs `nova.block_device_mapping.connection_info` for the same volume
2. Look for differences in `target_iqns` and `target_portals`

### Resolution 处理建议

1. 先确认根因及用户对目标资源、动作、影响和恢复方式的授权, 再选择目标版本支持的连接信息刷新入口; 不直接写数据库
2. 对照该版本的 refresh_connection_info、attachment_get 或 initialize_connection 实现确认刷新及失败恢复语义, 不将历史行号视为永久契约
3. 仅在授权范围内重试原操作并核对实际终态及关联资源, 保留失败证据

### Diagnostic Techniques 诊断技巧

以下信号用于提出待验证分支, 只有 portal、会话、后端映射及目标版本证据一致时才能确认 connection_info 陈旧, 不以数量或日志缺失直接下结论:

1. **`target_iqns` 重复**: 先核对 backend 的 IQN/portal 约定。同一 IQN 可以对应多个 portal, 不能仅凭重复 IQN 认定单节点路径; 结合 target_portals、实际会话及当前拓扑核对。

   ```bash
   # 抽取每个云硬盘的 target_iqns,看是否塌缩
   grep "Connecting to multipath volume" ecs.*/openstack/nova/nova-compute.*.log \
     | grep -oE "'target_iqns': \[[^]]+\]" | sort | uniq -c | sort -rn
   ```

2. **`_find_dm_device: wwid fallback also failed`**:multipath 扫了所有 dm-X 都找不到这个 wwid,是 `VolumeDeviceNotFound` 的最直接前置告警。

3. **后端 target 日志未命中 mapping**: 只说明所选来源和时间窗没有对应记录。先核对节点、采集范围、轮转及 WWID/LUN 标识, 必要时补查实际 mapping; 日志未命中不能证明后端没有承载该云硬盘。

   ```bash
   # 用 wwid 反查后端 target 是否真的服务这云硬盘
   for d in ecs.*/; do
     n=$(basename "$d" | cut -d. -f2)
     hit=$(grep -l "<WWID_NO_PREFIX_3>" "$d/alcubierre/alcubierre-target.node-"*.log  | wc -l)
     [ "$hit" -gt 0 ] && echo "$n serves this wwid"
   done
   ```

4. **同节点对照组**:在 nova-compute 重启后,**同时**看节点上其它云主机是否成功 resume。

   - 全部失败 → 节点级问题(基础设施 / Galera / RabbitMQ / OS)
   - 只这一台失败、其它成功 → **云主机个体 + 云硬盘个体的 BDM/拓扑问题**(本场景)
   - 失败云主机都有 iSCSI 云硬盘、成功的都是本地盘/RBD → 进一步聚焦在 iSCSI 后端

   ```bash
   # 一行抓出节点上所有 resume 结果
   grep -E "Instance rebooted successfully|Failed to resume instance" \
     ecs.*/openstack/nova/nova-compute.*.log \
     | awk -F' ¦ ' '{print $1, "|", $5}' | grep -oE "instance: [^]]+|rebooted|Failed to resume"
   ```

5. **重试间隔**: 从同一请求和资源的真实时间戳计算总窗口, 对照目标版本的超时和重试设置。1024 秒约为 17 分钟, 不写成 4 分钟; 固定经验节奏不能排除网络抖动。

6. **服务启动时序对齐**: 对齐 nova 重连与后端实际可用时间。Starting/Started 不单独证明业务 ready; 结合健康状态、连接结果及实际重试窗口判断, 不使用固定时长排除时序问题。

   ```bash
   # 服务时序快速对照
   for d in ecs.*/; do
     n=$(basename "$d" | cut -d. -f2)
     echo "--- $n ---"
     grep "Starting alcubierre" "$d/alcubierre/alcubierre-target.node-"*.log  | head -1 | awk -F' ¦ ' '{print "target start:", $1}'
     grep "Rebooting instance after nova-compute restart" "$d/openstack/nova/nova-compute.node-"*.log  | head -1 | awk -F' ¦ ' '{print "nova reboot:", $1}'
   done
   ```

---

<a id="scenario-2-node-reboot--crash"></a>

## Scenario 2: Node Reboot 节点重启

### Scenario 2 Symptom 问题现象
Compute node becomes unavailable, instances are in error state or need evacuation.

### Scenario 2 Diagnosis Flow 排查流程

**Step 1 - Check OS messages for cause of restart:**
```bash
grep -i "reboot\|shutdown\|panic\|watchdog\|hung_task\|softlockup" ecs.*/os/messages.*.log
```

**Step 2 - Check nova-compute init sequence:**
```bash
grep -i "init_host\|resume_state_on_host_boot\|_resume_guests_state\|Rebooting instance after" ecs.*/openstack/nova/nova-compute.*.log
```

This shows: which instances nova tried to recover, and which failed.

**Step 3 - Check Kubernetes node status:**
```bash
grep -i "node.*not ready\|node.*ready\|NotReady" ecs.*/kubernetes/kube-controller-manager.*.log
```

**Step 4 - Check libvirt state:**
```bash
grep -i "domain\|destroy\|start\|state" ecs.*/libvirt/libvirt.*.log
```

---

<a id="scenario-3-iscsi-connection-failure"></a>

## Scenario 3: iSCSI Connection Failure 连接失败

### Scenario 3 Symptom 问题现象
Volume attachment fails, `VolumeDeviceNotFound` or iSCSI login failures.

### Scenario 3 Diagnosis Flow 排查流程

**Step 1 - Check the target portals in nova-compute:**
```bash
grep "Connecting to multipath volume\|Trying to connect to iSCSI portal" ecs.*/openstack/nova/nova-compute.*.log
```

**Step 2 - Check Alcubierre node agent:**
```bash
grep -i "connect_volume\|disconnect_volume\|login\|logout\|error\|fail" ecs.*/alcubierre/alcubierre-node.*.log
```

**Step 3 - Check active iSCSI sessions:**
```bash
grep "iscsi session list" ecs.*/openstack/nova/nova-compute.*.log
```

Count which target nodes have active sessions.

**Step 4 - Check cinder volume backend:**
```bash
grep "initialize_connection\|terminate_connection" ecs.*/openstack/cinder/cinder-volume.*.log
```

Check which backend driver (RBDDriver, AlcubierreDriver, etc.) is handling the volume.

---

<a id="scenario-4-database-connectivity-issues"></a>

## Scenario 4: Database Connectivity 数据库连接

### Scenario 4 Symptom 问题现象
Services report `WSREP has not yet prepared node for application use` or `DBConnectionError`.

### Scenario 4 Diagnosis Flow 排查流程

**Step 1 - Check nova and cinder logs for DB errors:**
```bash
grep "WSREP\|DBConnectionError\|pymysql.err.OperationalError" ecs.*/openstack/nova/nova-compute.*.log ecs.*/openstack/cinder/cinder-volume.*.log
```

**Step 2 - Check mariadb logs:**
```bash
grep -i "WSREP\|galera\|cluster\|sync\|donor\|joiner" ecs.*/openstack/mariadb/mariadb.*.log
```

---

<a id="scenario-5-volume-attachmentdetachment-failure"></a>

## Scenario 5: Volume Attachment 云硬盘挂卸载失败

### Scenario 5 Symptom 问题现象
Volume attach fails or volume disappears from VM.

### Scenario 5 Diagnosis Flow 排查流程

**Step 1 - Check nova-compute volume operations:**
```bash
grep -i "attach_volume\|detach_volume\|_connect_volume\|_disconnect_volume" ecs.*/openstack/nova/nova-compute.*.log
```

**Step 2 - Check connect/disconnect detailed info:**
```bash
grep "Connecting to multipath volume\|Disconnect multipath volume" ecs.*/openstack/nova/nova-compute.*.log
```

Look at `target_iqns`, `target_portals`, `target_luns`, `wwid`, `device_path`.

**Step 3 - Check cinder volume operations:**
```bash
grep "initialize_connection\|terminate_connection\|attachment" ecs.*/openstack/cinder/cinder-volume.*.log
```

**Step 4 - Check Alcubierre if iSCSI type:**
```bash
grep -i "volume_id.*<VOLUME_ID>\|connect_volume\|disconnect_volume" ecs.*/alcubierre/alcubierre-node.*.log
```

---

<a id="scenario-6-vm-reboot-after-host-reboot"></a>

## Scenario 6: Host Recovery 宿主重启后恢复

This is a special case of Scenario 1. When a compute node restarts, nova-compute's `init_host` triggers `_resume_guests_state` which calls `_hard_reboot` on each instance that was running.

### Key Log Sequence 关键日志顺序

```bash
# 1. Nova-compute starts
grep "init_host\|Starting compute node" ecs.*/openstack/nova/nova-compute.*.log

# 2. Instance detected as running before restart
grep "expect_running\|_resume_guests_state\|Rebooting instance after" ecs.*/openstack/nova/nova-compute.*.log

# 3. Hard reboot: destroy phase
grep "Instance destroyed successfully\|destroy" ecs.*/openstack/nova/nova-compute.*.log

# 4. Hard reboot: reconnect volumes  
grep "Connecting to multipath volume\|Disconnect multipath volume" ecs.*/openstack/nova/nova-compute.*.log

# 5. Hard reboot: start instance
grep "Instance rebooted successfully\|Failed to resume instance" ecs.*/openstack/nova/nova-compute.*.log
```

### Failure Differences 故障差异

If some instances resume successfully while others fail, compare:
- **Volume type**: iSCSI vs Ceph RBD volumes have different reconnection behavior
- **Target node**: volumes with targets on the rebooted node vs other nodes
- **Connection_info freshness**: BDM may have stale data for some volumes

---

## Scenario 7: 实战 case - 云主机启动失败排查的高确定性路径

**用户问题**:"分析云主机 `<UUID>` 在某天的启动异常"。

以下流程用于缩小检索范围, 不承诺固定耗时或置信度。每个判断仍须对应本次证据。

### Step 1:定位节点 + req-ID

```bash
VM=<UUID>
# 节点定位
for d in ecs.*/; do
  c=$(grep -l "$VM" "$d/openstack/nova/nova-compute."*.log  | wc -l)
  [ "$c" -gt 0 ] && echo "$(basename $d): $c"
done
# 抽出主 req(多数情况下整个生命周期事件共用一个 req)
grep "$VM" ecs.<node>/openstack/nova/nova-compute.*.log | grep -oE "req-[0-9a-f-]+" | sort | uniq -c | sort -rn | head -3
```

> 找到的 req 是后续跨服务关联的钥匙。

### Step 2:抽云主机的事件主线(结论性事件)

只看"结论性"事件,不要被几千行 INFO 淹没:

```bash
grep "$VM" ecs.<node>/openstack/nova/nova-compute.*.log \
  | grep -E "Rebooting instance|Instance destroyed|Instance rebooted successfully|Failed to resume|VolumeDeviceNotFound|Setting instance vm_state to ERROR|During.*sync.*power_state|VM (Started|Resumed|Stopped) \(Lifecycle Event\)" \
  | awk -F' ¦ ' '{raw=$5; sub(/^[^F]*F /, "", raw); print $1, "|", substr(raw,1,250)}'
```

读得出"开始 → 销毁 → 重连云硬盘 → 成功/失败 → ERROR"的就是主线。

### Step 3:如果是"云硬盘连接"失败,**必看 4 个东西**

```bash
# (a) BDM 给的 target 列表 + wwid
grep -F "$VM" ecs.<node>/openstack/nova/nova-compute.*.log \
  | grep "Connecting to multipath volume" | head -3 \
  | awk -F' ¦ ' '{print substr($5,1,500)}'

# (b) 当时 iscsi 实际 session 落在哪
grep "iscsi session list" ecs.<node>/openstack/nova/nova-compute.*.log | tail -3 \
  | awk -F' ¦ ' '{print $1, "|", substr($5,1,300)}'

# (c) 从真实日志计算重试次数和时间间隔, 对照目标版本配置
grep -c "Connecting to multipath volume.*<VOLUME_ID>" ecs.<node>/openstack/nova/nova-compute.*.log

# (d) 远端 target 是否真在服务这云硬盘(最上游证据)
WWID=<wwid_no_prefix3>
for d in ecs.*/; do
  n=$(basename "$d" | cut -d. -f2)
  hit=$(grep -l "$WWID" "$d/alcubierre/alcubierre-target.node-"*.log  | wc -l)
  echo "$n: $hit alcubierre-target files mention this wwid"
done
```

### Step 4:同节点对照组(强诊断手段)

同时间窗内同节点上的**其它云主机**是否成功:

```bash
grep -E "Instance rebooted successfully|Failed to resume instance" \
  ecs.<node>/openstack/nova/nova-compute.*.log \
  | awk -F' ¦ ' '{raw=$5; sub(/^[^F]*F /, "", raw); print $1, "|", substr(raw,1,200)}' \
  | head -20
```

- 全部失败 -> 出现节点级或基础设施信号, 去 Step 5 定向检查对应分支。
- 只这一台失败 -> 聚焦该云主机的云硬盘、BDM、镜像或 qemu 因果链, 继续验证底层触发机制,
  不因故障范围较小就直接输出根因结论。

### Step 5:按信号检查上游基础设施

只有对照组显示多个云主机同时失败、主服务日志指向基础设施, 或当前证据无法解释直接失败
时, 才选择与信号匹配的检查。不要把以下所有命令作为每个云主机工单的固定步骤。

```bash
# (a) OS 层:内核错误、OOM、磁盘 I/O、网络链路
grep -iE "panic|softlockup|Out of memory|i/o error|link is (up|down)|iscsi.*recovery|iscsid.*connect to.*failed \(Connection refused\)|multipath" \
  ecs.<node>/os/messages.*.log | head -20

# (b) 控制面基础设施:Galera 集群、RabbitMQ 分区、chrony 时钟漂移
grep -iE "WSREP|non-primary|partition|HEALTH_(WARN|ERR)" \
  ecs.<node>/openstack/mariadb/*.log ecs.<node>/openstack/rabbitmq/*.log \
  ecs.<node>/os/chrony.*.log  | head -20

# (c) Ceph 集群健康
grep -E "HEALTH_(WARN|ERR)" ecs.<node>/ceph/host.ceph.*.log  | tail -5

# (d) Ceph CSI driver 是否注册(影响 RBD PVC 挂载)
grep -iE "rbd.csi.ceph.com not found in the list of registered CSI drivers" \
  ecs.<node>/os/messages.*.log | head -5

# (e) 仅在存在人工变更线索时检查事件时间窗内的操作历史, 引用内容必须脱敏
grep -E "systemctl|reboot|shutdown|drain|reset|kubectl delete" \
  ecs.<node>/openstack/dozer/bash-history.*.log | tail -20
```

命中结果先作为关联线索。只有能够与目标云主机、请求和时间窗建立因果关系, 并解释它如何
触发直接失败时, 才能写入根因; 否则记录为待验证线索或证据缺口。

**快速判断分支:**
- 基础设施无异常,仅个别云主机失败 → 聚焦云主机个体(云硬盘 / BDM / 镜像)
- 基础设施有异常 + 多个服务同时报错 → 先解基础设施问题,再回看云主机
- 仅 iSCSI target `Connection refused` → 检查 Alcubierre 节点状态和启动时序

### Step 6:节点重启时间 + 服务可用时间对齐

> `os/boot.*.log` 比 `os/messages.*.log` 更准确。boot.log 记录 systemd 启动序列,
> 可以精确看到 iscsid/containerd/kubelet 各在什么时间点 ready。

```bash
# 节点真实启动时间(kernel 起来)
grep -h "Linux version\|Command line: BOOT_IMAGE" ecs.<node>/os/messages.*.log | head -3 \
  | awk -F' ¦ ' '{print $1, "|", substr($5,1,150)}'

# systemd boot complete(更准确)
grep -E "Reached target.*(Multi-User|Graphical)" \
  ecs.<node>/os/boot.*.log | tail -1 | awk -F' ¦ ' '{print $1}'

# 各 OpenStack/存储/网络服务可用时间
for svc in nova-compute cinder-volume alcubierre-target alcubierre-node libvirt kubelet containerd iscsid; do
  f=$(find ecs.<node> -type f -name "$svc.node-*.log" -print -quit)
  [ -z "$f" ] && continue
  ts=$(grep -iE "Starting|started" "$f" | head -1 | awk -F' ¦ ' '{print $1}')
  [ -n "$ts" ] && echo "$svc ready: $ts"
done
```

对照实际后端可用时间和该版本重试窗口判断连接是否成功, 不从启动日志或固定秒数推定。

### Step 7:写报告(用 [analysis-playbook.md](analysis-playbook.md) 模板)

务必包含:
- **结论 1 句话** + 关键失败行 file:line
- **时间线与直接证据**: 使用共享 [report-format.md](report-format.md) 的事件结构, 不输出表格; 区分节点 boot、进程启动、业务可用、云主机事件与失败时间
- **同节点对照组**结果(成功 vs 失败的云主机各几台、差异点是什么)
- **未验证项**:哪些证据是间接的(例如"日志窗口内没有 cinder 操作"≠"cinder 从来没操作过这云硬盘")

### 这类问题的高频根因 TOP 5

| # | 根因 | 关键证据 |
|---|------|---------|
| 1 | **BDM connection_info 陈旧候选** | 比较已确认的 portal、会话及后端映射; 重复 IQN 和日志未命中不能单独确认 |
| 2 | **节点重启后 alcubierre/cinder 后端未就绪** | nova reconnect 时 target 日志显示服务尚未 Starting |
| 3 | **iSCSI 网络瞬断** | os/messages 中 `iscsi: session.*recovery`、`link is down`;只此一次重试就成功 |
| 4 | **RBD 云硬盘在 Ceph 健康异常** | ceph HEALTH_ERR/PG down,nova-compute 卡在 `librbd` 调用 |
| 5 | **libvirt/qemu 启动失败**(非云硬盘问题) | qemu.instance-<HEX>.log 末尾出现 `qemu-kvm:` 错误;nova 看到 domain define 成功但 start 失败 |
