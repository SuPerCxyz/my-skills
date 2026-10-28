# Search Patterns by Issue Type

Use this file after the issue domain and time window are known. For cross-service evidence selection, read [cross-domain-analysis.md](cross-domain-analysis.md) first.

## Table of Contents 目录

[Common](#common-patterns) | [Nova](#compute-nova-compute) |
[Cinder](#cinder-volume) | [iSCSI](#alcubierre-iscsi) | [Libvirt](#libvirt) |
[OS](#os-messages) | [Boot](#boot-log-osbootlog) | [Ceph](#ceph) |
[Kubernetes](#kubernetes) | [MariaDB](#galera--mariadb-control-plane-db) |
[RabbitMQ](#rabbitmq--amqp) | [Time](#time-sync-chrony) |
[Audit](#operator-audit-trail-bash-history) | [CSI](#k8s-csi--rbd-volume-mount) |
[OVN](#ovn--open-vswitch) | [Time Window](#time-windowed-analysis) |
[Correlation](#cross-service-correlation) | [实战模式](#高价值模式实战沉淀)

<a id="common-patterns"></a>

## Common Patterns 通用模式

> 从确认的解压根执行, 该目录直接包含所选 `ecs.*`。复用完整对应输出; 仅缺失、
> 不完整或明确刷新时解压。已有明确节点/服务/时间窗时仅检索该范围。
> grep 片段要求先确认文件集合非空, 启用 `set -o pipefail` 并保留错误输出;
> 不能确认输入时使用入口中的 `search-logs.py`, 不把输入错误当无命中。

```bash
# 列出所有可用节点
ls -d ecs.*/

# Find instance UUID across ALL nodes
find . -path "*/ecs.*/openstack/nova/*.log" -type f \
  -exec grep -l -F "<INSTANCE_UUID>" {} \;

# Simplified: search ALL readable logs for a UUID
for d in ecs.*/; do
  node=$(basename "$d")
  count=$(find "$d" -type f -name "*.log" \
    -exec grep -l -F "<UUID>" {} \;  | wc -l)
  echo "$node: $count files"
done

# Find volume ID across all nodes
find . -type f \( -path "*/ecs.*/openstack/nova/*.log" \
  -o -path "*/ecs.*/openstack/cinder/*.log" \) \
  -exec grep -l "<VOLUME_ID>" {} \;

# Find error events in a time window across nodes
for d in ecs.*/; do
  echo "=== $(basename $d) ==="
  find "$d/openstack/nova" -type f -name "nova-compute*.log" \
    -exec grep "2026-06-18 10:2[5-9]" {} \;  |
    grep -i "error\|fail\|traceback"
done

# Search a specific file type across all nodes
for d in ecs.*/; do
  echo "=== $(basename $d) ==="
  find "$d" -type f -name "nova-compute*.log" \
    -exec grep "<PATTERN>" {} \;
done
```

<a id="compute-nova-compute"></a>

## Compute (nova-compute) 计算日志

### Instance Lifecycle Events 云主机事件

```bash
# Reboot after nova-compute restart (init_host flow)
grep "Rebooting instance after nova-compute restart" ecs.*/openstack/nova/nova-compute.*.log

# Hard reboot (power_on) flow
grep -i "hard_reboot\|_hard_reboot\|power_on\|start_instance" ecs.*/openstack/nova/nova-compute.*.log

# Instance destroyed (during hard reboot)
grep "Instance destroyed successfully" ecs.*/openstack/nova/nova-compute.*.log

# Instance reboot success
grep "Instance rebooted successfully" ecs.*/openstack/nova/nova-compute.*.log

# Resume failure
grep "Failed to resume instance" ecs.*/openstack/nova/nova-compute.*.log

# Unexpected life cycle events
grep "Received unexpected event" ecs.*/openstack/nova/nova-compute.*.log

# Power state sync
grep "During.*sync_power_state\|During.*_sync_instance_power_state" ecs.*/openstack/nova/nova-compute.*.log

# Instance error state
grep "Setting instance vm_state to ERROR" ecs.*/openstack/nova/nova-compute.*.log
```

### Volume Operations 云硬盘操作

```bash
# Connect/disconnect volume
grep -i "connect.*volume\|disconnect.*volume\|Connect.*multipath\|Disconnect.*multipath" ecs.*/openstack/nova/nova-compute.*.log

# Volume device not found
grep "Volume device not found\|VolumeDeviceNotFound" ecs.*/openstack/nova/nova-compute.*.log

# iSCSI login/logout
grep -i "iscsiadm.*login\|iscsiadm.*logout\|iscsiadm.*login" ecs.*/openstack/nova/nova-compute.*.log

# iSCSI session listing
grep "iscsi session list\|iscsiadm.*session" ecs.*/openstack/nova/nova-compute.*.log

# Connection info (target portals)
grep "Connecting to multipath volume\|Disconnect multipath volume" ecs.*/openstack/nova/nova-compute.*.log | grep -oP "target_portals.*?\]" | head -5

# Find DM device lookup
grep -i "_find_dm_device\|get_volume_paths\|wwid.*fallback" ecs.*/openstack/nova/nova-compute.*.log
```

### Init Host / Resume State 初始化与恢复

```bash
# Nova-compute init flow
grep -i "init_host\|_init_host\|init_virt_events" ecs.*/openstack/nova/nova-compute.*.log

# Instance resume on host boot
grep "resume_state_on_host_boot\|_resume_guests_state\|_resume_instance" ecs.*/openstack/nova/nova-compute.*.log

# Instance BDM info
grep "_get_instance_block_device_info" ecs.*/openstack/nova/nova-compute.*.log
```

### DB / Conductor Errors 数据库与编排错误

```bash
# DB connection errors (Galera/WSREP)
grep "WSREP\|DBConnectionError\|pymysql.err.OperationalError" ecs.*/openstack/nova/nova-compute.*.log

# RPC errors
grep "oslo_messaging.rpc.client.RemoteError" ecs.*/openstack/nova/nova-compute.*.log

# Conductor errors
grep "nova.conductor\|object_action\|object_class_action" ecs.*/openstack/nova/nova-compute.*.log
```

<a id="cinder-volume"></a>

## Cinder Volume 存储日志

```bash
# Volume attach/detach
grep -i "attach_volume\|detach_volume\|initialize_connection\|terminate_connection" ecs.*/openstack/cinder/cinder-volume.*.log

# Volume status changes
grep "volume.*status\|volume.*state" ecs.*/openstack/cinder/cinder-volume.*.log

# Driver initialization
grep "Driver initialization" ecs.*/openstack/cinder/cinder-volume.*.log

# DB errors
grep "DBError\|WSREP\|pymysql.err" ecs.*/openstack/cinder/cinder-volume.*.log

# AMQP/RabbitMQ issues
grep "AMQP server\|rabbitmq\|unreachable\|connection closed" ecs.*/openstack/cinder/cinder-volume.*.log
```

<a id="alcubierre-iscsi"></a>

## Alcubierre (iSCSI) 高性能存储

```bash
# iSCSI connection management
grep -i "connect_volume\|disconnect_volume\|connect.*iscsi\|disconnect.*iscsi" ecs.*/alcubierre/alcubierre-node.*.log

# Multi-path device discovery
grep -i "_find_dm_device\|get_volume_paths\|multipath\|dm device" ecs.*/alcubierre/alcubierre-node.*.log

# Target/node connectivity
grep -i "target_iqn\|target_portal\|login\|logout" ecs.*/alcubierre/alcubierre-node.*.log

# Alcubierre API calls
grep -i "Requesting GET\|Requesting POST\|alcubierre-manul" ecs.*/alcubierre/alcubierre-node.*.log

# Error conditions
grep -i "error\|fail\|exception\|traceback" ecs.*/alcubierre/alcubierre-node.*.log
```

<a id="libvirt"></a>

## Libvirt 虚拟化日志

```bash
# Domain lifecycle
grep -i "destroy\|reboot\|shutdown\|start\|define\|undefine" ecs.*/libvirt/libvirt.*.log

# QEMU/KVM errors
grep -i "qemu\|kvm\|accel\|capability" ecs.*/libvirt/libvirt.*.log

# Storage errors
grep -i "storage\|volume\|disk\|ceph\|rbd" ecs.*/libvirt/libvirt.*.log

# Agent issues
grep -i "guest agent\|agent.*not configured\|agent.*timeout" ecs.*/libvirt/libvirt.*.log

# Network errors
grep -i "network\|bridge\|vnet\|tap" ecs.*/libvirt/libvirt.*.log

# Keepalive/client issues
grep -i "max requests limit\|keep-alive timeout" ecs.*/libvirt/libvirt.*.log
```

<a id="os-messages"></a>

## OS Messages 系统消息

```bash
# Hardware/disk errors
grep -i "error\|fail\|critical\|i/o error\|kernel.*panic" ecs.*/os/messages.*.log | tail -100

# SCSI/iSCSI
grep -i "iscsi\|scsi\|multipath\|dm-" ecs.*/os/messages.*.log

# iSCSI target reachability — Connection refused is the most direct signal
# that the iSCSI target backend is not serving the portal
grep -iE "iscsid.*connect to.*failed \(Connection refused\)" ecs.*/os/messages.*.log

# Network
grep -i "link.*down\|link.*up\|carrier\|nic\|eth" ecs.*/os/messages.*.log

# OOM/memory
grep -i "oom\|out of memory\|kill" ecs.*/os/messages.*.log

# Filesystem
grep -i "filesystem.*error\|fsck\|journal\|corrupt" ecs.*/os/messages.*.log
```

<a id="boot-log-osbootlog"></a>

## Boot Log (os/boot.*.log) 启动日志

The boot log captures systemd's view of the boot sequence - when each OS-level
service (iscsid, kubelet, containerd, OVS, chronyd, sshd) actually started.
Useful for:

- Determining the **exact reboot time** of a physical node
- **Service startup order** - whether kubelet/iscsid started before or after
  nova-compute tried to reconnect volumes
- Identifying **failed systemd units** during boot

```bash
# Extract the full boot timeline (systemd journal-style)
cat ecs.*/os/boot.*.log

# Focus on specific service start times
grep -iE "Starting|Started|FAILED" ecs.*/os/boot.*.log

# Check iscsid / iSCSI readiness
grep -iE "iscsi|open-iscsi" ecs.*/os/boot.*.log

# Check container runtime readiness
grep -iE "containerd|kubelet|docker" ecs.*/os/boot.*.log

# Check storage services
grep -iE "ceph|rbd|multipath" ecs.*/os/boot.*.log

# Check network services
grep -iE "open.?vswitch|ovs|network|ethernet" ecs.*/os/boot.*.log
```

<a id="ceph"></a>

## Ceph 存储日志

```bash
# OSD status
ecs.*/ceph/host.ceph-osd.*.log

# Health
grep -i "health.*err\|health.*warn\|PG.*down\|pg.*inconsistent" ecs.*/ceph/host.ceph.*.log

# Network
grep -i "slow\|slow request\|network\|peer\|timeout" ecs.*/ceph/host.ceph-osd.*.log
```

<a id="kubernetes"></a>

## Kubernetes 集群日志

```bash
# Node status
grep -i "node.*not ready\|node.*ready\|cord\|drain" ecs.*/kubernetes/kube-controller-manager.*.log

# Pod failures
grep -i "back-off\|crash\|fail\|error" ecs.*/kubernetes/kube-apiserver.*.log
```

<a id="galera--mariadb-control-plane-db"></a>

## Galera / MariaDB 控制面数据库

```bash
# WSREP cluster state
grep -i "WSREP\|cluster status\|primary component\|donor\|joiner\|sst" ecs.*/openstack/mariadb/mariadb.*.log

# Galera split-brain / desync
grep -i "non-primary\|desync\|inconsistent\|leaving cluster\|cluster suspended" ecs.*/openstack/mariadb/mariadb.*.log

# Pod-side readiness probe
grep -i "fail\|not ready\|error" ecs.*/openstack/mariadb/mariadb-*-readiness.*.log

# Cross-service DB failure symptom
grep -E "WSREP has not yet prepared node|DBConnectionError|MySQL server has gone away" \
  ecs.*/openstack/{nova,cinder,neutron,glance,keystone}/*.log
```

<a id="rabbitmq--amqp"></a>

## RabbitMQ / AMQP 消息队列

```bash
# Cluster events
grep -i "node.*down\|node.*up\|partition\|netsplit\|cluster_status" \
  ecs.*/openstack/rabbitmq/rabbitmq.*.log

# Connection / channel errors
grep -i "connection_closed\|channel_closed\|missed heartbeats\|closing AMQP connection" \
  ecs.*/openstack/rabbitmq/rabbitmq.*.log

# Queue mirroring / HA
grep -i "ha-policy\|mirror\|slave\|sync" ecs.*/openstack/rabbitmq/rabbitmq.*.log

# Client-side symptom (any oslo.messaging consumer)
grep -i "AMQP server.*unreachable\|reconnecting in\|kombu.*connection\|Recovering from a failed" \
  ecs.*/openstack/{nova,cinder,neutron,glance,keystone}/*.log
```

<a id="time-sync-chrony"></a>

## Time Sync (chrony) 时间同步

> Galera, Ceph, and OVN are all sensitive to clock drift. Always check chrony
> first when seeing "weird" cluster-wide failures.

```bash
# Sync state
grep -i "selected\|fall back\|step\|jump\|drift\|cannot find\|no suitable source" \
  ecs.*/os/chrony.*.log

# Compare clock offsets across nodes
for d in ecs.*/; do
  echo "=== $(basename $d) ==="
  grep -i "system clock" "$d"/os/chrony.*.log  | tail -5
done
```

<a id="operator-audit-trail-bash-history"></a>

## Operator Audit Trail (bash-history) 操作历史

Captures every interactive root shell command on each node - invaluable for
correlating cluster anomalies with human actions.
仅当事件时间、错误、状态变化或其它证据表明可能存在人工操作时使用本节。搜索范围必须
限制在关联时间窗内, 保留或输出命中结果前对凭据和敏感命令参数脱敏。

```bash
# All commands across all nodes, sorted by wrapper timestamp
for d in ecs.*/; do
  grep . "$d"/openstack/dozer/bash-history.*.log
done | sort -k1,2

# Find risky commands
grep -E "systemctl (stop|restart)|kubectl delete|reboot|shutdown|rm -rf|reset --hard|drain" \
  ecs.*/openstack/dozer/bash-history.*.log

# Around a specific event time
grep "2026-06-18 10:2[0-9]" ecs.*/openstack/dozer/bash-history.*.log
```

<a id="k8s-csi--rbd-volume-mount"></a>

## K8s CSI / RBD Volume Mount 挂载日志

When pods fail to mount RBD-backed PVs (common for control-plane services):

```bash
# CSI plugin errors
grep -iE "fail|error|timeout|not found|unmounter\.teardown" ecs.*/kubernetes/csi-rbdplugin.*.log

# Kubelet view of mount failures
grep -E "UnmountVolume|MountVolume|csi.*not.found|nestedpendingoperations" ecs.*/os/messages.*.log

# Driver registration
grep -iE "registrar|register|csi driver" ecs.*/kubernetes/driver-registrar.*.log
```

## OS Messages Expanded 系统扩展检查

```bash
# Kernel panics, soft/hard lockups, watchdog
grep -iE "kernel panic|softlockup|hung_task|watchdog|BUG:|call trace|RIP:" ecs.*/os/messages.*.log

# OOM killer (extract victim + score)
grep -B 2 -A 5 "Out of memory" ecs.*/os/messages.*.log
grep -E "killed process [0-9]+.*total-vm" ecs.*/os/messages.*.log

# Block I/O / device errors
grep -iE "i/o error|end_request|sd [a-z]:.*error|nvme.*error|blk_update_request|medium error" \
  ecs.*/os/messages.*.log

# iSCSI session / SCSI
grep -iE "iscsi: connection.*closed|iscsi: session.*recovery|sd.*alua|scsi target" ecs.*/os/messages.*.log

# Multipath
grep -iE "multipath|dm-[0-9]|wwid|path.*(up|down|fail)" ecs.*/os/messages.*.log

# Network NIC / bonding
grep -iE "link is (up|down)|carrier|bond.*member|bond.*active|enp[0-9]" ecs.*/os/messages.*.log

# Power / thermal
grep -iE "thermal|mce:|machine check|power loss|psu" ecs.*/os/messages.*.log
```

## Ceph Expanded 存储扩展检查

```bash
# Cluster health snapshot points
grep -E "HEALTH_(WARN|ERR)" ecs.*/ceph/host.ceph.*.log | tail -20

# OSD flapping (down → up → down)
grep -E "osd\.[0-9]+ .*(down|up|booted)" ecs.*/ceph/host.ceph-mon.*.log | tail -50

# Slow ops / stuck PGs
grep -iE "slow ops|slow request|stuck (inactive|unclean|stale)|peering" ecs.*/ceph/host.ceph-osd.*.log

# Recovery / backfill
grep -iE "recovery|backfill|degraded|misplaced" ecs.*/ceph/host.ceph-mgr.*.log | tail -30

# Auth / quorum
grep -iE "election|quorum|leader|monmap|mon\..*(up|down)" ecs.*/ceph/host.ceph-mon.*.log
```

<a id="ovn--open-vswitch"></a>

## OVN / Open vSwitch 网络数据面

```bash
# Tunnel / chassis state
grep -iE "chassis|tunnel|encap|bfd|sb_db" ecs.*/os/openvswitch/ovn-controller.*.log

# OVN DB events
grep -iE "leader|election|raft|cluster" ecs.*/os/openvswitch/ovn-ovsdb-{nb,sb}*.log

# Datapath flow errors
grep -iE "fail|error|drop|reject" ecs.*/os/openvswitch/ovs-vswitchd.*.log | head -30
```

## Libvirt QEMU 云主机进程日志

```bash
# Pick the right per-instance log
ls ecs.*/libvirt/qemu.instance-*.log

# Domain start failures (often the actual reason hard_reboot fails)
grep -iE "error|fail|kvm.*not allowed|qemu-kvm:|aborting" \
  ecs.*/libvirt/qemu.instance-<DOMAIN_HEX>.*.log

# Block device events inside qemu
grep -iE "block.*open|block.*close|drive|virtio-blk" \
  ecs.*/libvirt/qemu.instance-<DOMAIN_HEX>.*.log
```

<a id="time-windowed-analysis"></a>

## Time-Windowed Analysis 时间窗分析

```bash
# Extract logs within a 5-minute window
grep "2026-06-18 10:2[5-9]\|2026-06-18 10:3[0-4]" ecs.*/openstack/nova/nova-compute.*.log

# Extract logs around a specific minute
grep "2026-06-18 10:25:1[5-9]" ecs.*/openstack/nova/nova-compute.*.log

# Parallel search across all logs for same time window
for f in ecs.*/openstack/nova/nova-compute.*.log ecs.*/openstack/cinder/cinder-volume.*.log ecs.*/alcubierre/alcubierre-node.*.log; do
  echo "=== $f ==="
  grep "2026-06-18 10:25" "$f"
done
```

<a id="cross-service-correlation"></a>

## Cross-Service Correlation 跨服务关联

For issues spanning multiple services, correlate the same `req-<UUID>` (request ID) across logs:

```bash
# Track a request ID across all logs
grep -r "req-30eb5314-8245-4193-91b4-3b0b67be19bf" ecs.*/openstack/nova/nova-compute.*.log

# Or search across all directories
python3 <SKILL_DIR>/scripts/search-logs.py --root <EXTRACTED_ROOT> \
  --pattern 'ecs.*/openstack/nova/*.log' --pattern 'ecs.*/openstack/cinder/*.log' \
  --text 'req-<REQUEST_ID>'
```

<a id="高价值模式实战沉淀"></a>

## Diagnostic Patterns 诊断模式

### 检测 `target_iqns` 列表塌缩(BDM 陈旧的强信号)

```bash
# 抽出每个云硬盘的 target_iqns 唯一组合及命中次数
grep "Connecting to multipath volume" ecs.*/openstack/nova/nova-compute.*.log \
  | grep -oE "'target_iqns': \[[^]]+\]" | sort | uniq -c | sort -rn

# 重复 IQN 只是线索; 必须核对 portal、会话、后端拓扑和版本, 不能直接判定 BDM 陈旧
```

### 抽出云主机完整生命周期主线(屏蔽噪声 INFO)

```bash
VM=<UUID>
grep "$VM" ecs.*/openstack/nova/nova-compute.*.log | grep -E \
  "Rebooting instance after nova-compute restart|Instance destroyed successfully|Instance rebooted successfully|Failed to resume instance|VolumeDeviceNotFound|Setting instance vm_state to ERROR|During.*sync.*power_state|VM (Started|Resumed|Paused|Stopped) \(Lifecycle Event\)|Received unexpected event" \
  | awk -F' ¦ ' '{raw=$5; sub(/^[^F]*F /, "", raw); print $1, "|", substr(raw,1,250)}'
```

### 同节点对照组(同时窗内成功 vs 失败的云主机)

```bash
grep -E "Instance rebooted successfully|Failed to resume instance" \
  ecs.*/openstack/nova/nova-compute.*.log \
  | awk -F' ¦ ' '{raw=$5; sub(/^[^F]*F /, "", raw); print $1, "|", substr(raw,1,200)}'
```

### 用 wwid 反查后端 target 是否服务这云硬盘

```bash
WWID=<wwid>      # 例:36001405acbc174502609ea455fb42783
for d in ecs.*/; do
  n=$(basename "$d" | cut -d. -f2)
  hit=$(grep -l "$WWID" "$d/alcubierre/alcubierre-target.node-"*.log  | wc -l)
  echo "$n alcubierre-target hits: $hit"
done
# 全为 0 只表示所选日志未命中; 先核对轮转、时间窗、标识及采集覆盖
```

### Service Timeline 服务可用时间线

> `os/boot.*.log` 比 `os/messages.*.log` 更准确地给出系统级服务的启动时序。
> 优先从 boot.log 提取 iscsid/containerd/kubelet/OVS 的 ready 时间。

```bash
# 一个节点上各关键服务的 "Starting" 时间
NODE_DIR=ecs.node-X.YYYYMMDD.N

# kernel boot 时间(messages 第一条)
echo "== kernel boot =="
head -1 "$NODE_DIR/os/messages."*.log | awk -F' ¦ ' '{print $1}'

# systemd multi-user target 时间(boot.log 结尾)
echo "== systemd boot complete =="
grep -E "Reached target.*(Multi-User|Graphical)" \
  "$NODE_DIR/os/boot."*.log | tail -1 | awk -F' ¦ ' '{print $1}'

# 各服务启动时间
for svc in nova-compute cinder-volume alcubierre-target alcubierre-node \
           alcubierre-manager libvirtd kubelet containerd iscsid; do
  f=$(find "$NODE_DIR" -type f -name "$svc.node-*.log" -print -quit)
  [ -z "$f" ] && continue
  ts=$(grep -iE "Starting|started" "$f" | head -1 | awk -F' ¦ ' '{print $1}')
  [ -n "$ts" ] && printf "%-22s %s\n" "$svc" "$ts"
done
```

跨节点对比:

```bash
for d in ecs.*/; do
  node=$(basename "$d" | cut -d. -f2)
  for svc in nova-compute cinder-volume alcubierre-target; do
    f=$(find "$d" -type f -name "$svc.node-*.log" -print -quit)
    ts=$(grep -iE "Starting|started" "$f"  | head -1 | awk -F' ¦ ' '{print $1}')
    [ -n "$ts" ] && printf "%-10s %-22s %s\n" "$node" "$svc" "$ts"
  done
done
```

### Retry Window 实际重试窗口

```bash
# 数同一云硬盘的 Connecting to multipath volume 重试次数和间隔
VOL=<VOLUME_ID>
grep "Connecting to multipath volume.*$VOL" ecs.*/openstack/nova/nova-compute.*.log \
  | awk -F' ¦ ' '{print $1}'
# 从同一请求/资源的实际时间戳计算间隔和总时长, 对照目标版本 retry/timeout 配置
# 相同退避节奏不能单独排除网络抖动或确定根因
```

### Domain UUID ↔ instance-XXXX 一次性映射

```bash
# 用 -uuid 启动参数行从 qemu 日志反查 hex domain
for f in ecs.*/libvirt/qemu.instance-*.log; do
  uid=$(grep -m1 "^.*¦ libvirt ¦  ¦ -uuid " "$f" | awk '{print $NF}')
  dom=$(basename "$f" | sed -E 's/qemu\.(instance-[0-9a-f]+).*/\1/')
  echo "$dom -> $uid"
done
```
