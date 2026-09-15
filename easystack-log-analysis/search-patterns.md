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

## Common Patterns

> **重要**: 默认搜索所有节点目录(`ecs.node-*`), 除非用户指定特定节点。
> 必须先运行 `bash scripts/decompress-eslog.sh`; 后续只搜索脚本生成的 `.log`。

```bash
# 列出所有可用节点
ls -d ecs.*/

# Find instance UUID across ALL nodes
find . -path "*/ecs.*/openstack/nova/*.log" -type f \
  -exec grep -l -F "<INSTANCE_UUID>" {} \; 2>/dev/null

# Simplified: search ALL readable logs for a UUID
for d in ecs.*/; do
  node=$(basename "$d")
  count=$(find "$d" -type f -name "*.log" \
    -exec grep -l -F "<UUID>" {} \; 2>/dev/null | wc -l)
  echo "$node: $count files"
done

# Find volume ID across all nodes
find . -type f \( -path "*/ecs.*/openstack/nova/*.log" \
  -o -path "*/ecs.*/openstack/cinder/*.log" \) \
  -exec grep -l "<VOLUME_ID>" {} \; 2>/dev/null

# Find error events in a time window across nodes
for d in ecs.*/; do
  echo "=== $(basename $d) ==="
  find "$d/openstack/nova" -type f -name "nova-compute*.log" \
    -exec grep "2026-06-18 10:2[5-9]" {} \; 2>/dev/null |
    grep -i "error\|fail\|traceback"
done

# Search a specific file type across all nodes
for d in ecs.*/; do
  echo "=== $(basename $d) ==="
  find "$d" -type f -name "nova-compute*.log" \
    -exec grep "<PATTERN>" {} \; 2>/dev/null
done
```

## Compute (nova-compute)

### Instance Lifecycle Events

```bash
# Reboot after nova-compute restart (init_host flow)
grep "Rebooting instance after nova-compute restart" openstack/nova/nova-compute.*.log

# Hard reboot (power_on) flow
grep -i "hard_reboot\|_hard_reboot\|power_on\|start_instance" openstack/nova/nova-compute.*.log

# Instance destroyed (during hard reboot)
grep "Instance destroyed successfully" openstack/nova/nova-compute.*.log

# Instance reboot success
grep "Instance rebooted successfully" openstack/nova/nova-compute.*.log

# Resume failure
grep "Failed to resume instance" openstack/nova/nova-compute.*.log

# Unexpected life cycle events
grep "Received unexpected event" openstack/nova/nova-compute.*.log

# Power state sync
grep "During.*sync_power_state\|During.*_sync_instance_power_state" openstack/nova/nova-compute.*.log

# Instance error state
grep "Setting instance vm_state to ERROR" openstack/nova/nova-compute.*.log
```

### Volume Operations

```bash
# Connect/disconnect volume
grep -i "connect.*volume\|disconnect.*volume\|Connect.*multipath\|Disconnect.*multipath" openstack/nova/nova-compute.*.log

# Volume device not found
grep "Volume device not found\|VolumeDeviceNotFound" openstack/nova/nova-compute.*.log

# iSCSI login/logout
grep -i "iscsiadm.*login\|iscsiadm.*logout\|iscsiadm.*login" openstack/nova/nova-compute.*.log

# iSCSI session listing
grep "iscsi session list\|iscsiadm.*session" openstack/nova/nova-compute.*.log

# Connection info (target portals)
grep "Connecting to multipath volume\|Disconnect multipath volume" openstack/nova/nova-compute.*.log | grep -oP "target_portals.*?\]" | head -5

# Find DM device lookup
grep -i "_find_dm_device\|get_volume_paths\|wwid.*fallback" openstack/nova/nova-compute.*.log
```

### Init Host / Resume State

```bash
# Nova-compute init flow
grep -i "init_host\|_init_host\|init_virt_events" openstack/nova/nova-compute.*.log

# Instance resume on host boot
grep "resume_state_on_host_boot\|_resume_guests_state\|_resume_instance" openstack/nova/nova-compute.*.log

# Instance BDM info
grep "_get_instance_block_device_info" openstack/nova/nova-compute.*.log
```

### DB / Conductor Errors

```bash
# DB connection errors (Galera/WSREP)
grep "WSREP\|DBConnectionError\|pymysql.err.OperationalError" openstack/nova/nova-compute.*.log

# RPC errors
grep "oslo_messaging.rpc.client.RemoteError" openstack/nova/nova-compute.*.log

# Conductor errors
grep "nova.conductor\|object_action\|object_class_action" openstack/nova/nova-compute.*.log
```

## Cinder Volume

```bash
# Volume attach/detach
grep -i "attach_volume\|detach_volume\|initialize_connection\|terminate_connection" openstack/cinder/cinder-volume.*.log

# Volume status changes
grep "volume.*status\|volume.*state" openstack/cinder/cinder-volume.*.log

# Driver initialization
grep "Driver initialization" openstack/cinder/cinder-volume.*.log

# DB errors
grep "DBError\|WSREP\|pymysql.err" openstack/cinder/cinder-volume.*.log

# AMQP/RabbitMQ issues
grep "AMQP server\|rabbitmq\|unreachable\|connection closed" openstack/cinder/cinder-volume.*.log
```

## Alcubierre (iSCSI)

```bash
# iSCSI connection management
grep -i "connect_volume\|disconnect_volume\|connect.*iscsi\|disconnect.*iscsi" alcubierre/alcubierre-node.*.log

# Multi-path device discovery
grep -i "_find_dm_device\|get_volume_paths\|multipath\|dm device" alcubierre/alcubierre-node.*.log

# Target/node connectivity
grep -i "target_iqn\|target_portal\|login\|logout" alcubierre/alcubierre-node.*.log

# Alcubierre API calls
grep -i "Requesting GET\|Requesting POST\|alcubierre-manul" alcubierre/alcubierre-node.*.log

# Error conditions
grep -i "error\|fail\|exception\|traceback" alcubierre/alcubierre-node.*.log
```

## Libvirt

```bash
# Domain lifecycle
grep -i "destroy\|reboot\|shutdown\|start\|define\|undefine" libvirt/libvirt.*.log

# QEMU/KVM errors
grep -i "qemu\|kvm\|accel\|capability" libvirt/libvirt.*.log

# Storage errors
grep -i "storage\|volume\|disk\|ceph\|rbd" libvirt/libvirt.*.log

# Agent issues
grep -i "guest agent\|agent.*not configured\|agent.*timeout" libvirt/libvirt.*.log

# Network errors
grep -i "network\|bridge\|vnet\|tap" libvirt/libvirt.*.log

# Keepalive/client issues
grep -i "max requests limit\|keep-alive timeout" libvirt/libvirt.*.log
```

## OS Messages

```bash
# Hardware/disk errors
grep -i "error\|fail\|critical\|i/o error\|kernel.*panic" os/messages.*.log | tail -100

# SCSI/iSCSI
grep -i "iscsi\|scsi\|multipath\|dm-" os/messages.*.log

# iSCSI target reachability — Connection refused is the most direct signal
# that the iSCSI target backend is not serving the portal
grep -iE "iscsid.*connect to.*failed \(Connection refused\)" os/messages.*.log

# Network
grep -i "link.*down\|link.*up\|carrier\|nic\|eth" os/messages.*.log

# OOM/memory
grep -i "oom\|out of memory\|kill" os/messages.*.log

# Filesystem
grep -i "filesystem.*error\|fsck\|journal\|corrupt" os/messages.*.log
```

## Boot Log (os/boot.*.log)

The boot log captures systemd's view of the boot sequence — when each OS-level
service (iscsid, kubelet, containerd, OVS, chronyd, sshd) actually started.
Useful for:

- Determining the **exact reboot time** of a physical node
- **Service startup order** — whether kubelet/iscsid started before or after
  nova-compute tried to reconnect volumes
- Identifying **failed systemd units** during boot

```bash
# Extract the full boot timeline (systemd journal-style)
cat os/boot.*.log

# Focus on specific service start times
grep -iE "Starting|Started|FAILED" os/boot.*.log

# Check iscsid / iSCSI readiness
grep -iE "iscsi|open-iscsi" os/boot.*.log

# Check container runtime readiness
grep -iE "containerd|kubelet|docker" os/boot.*.log

# Check storage services
grep -iE "ceph|rbd|multipath" os/boot.*.log

# Check network services
grep -iE "open.?vswitch|ovs|network|ethernet" os/boot.*.log
```

## Ceph

```bash
# OSD status
ceph/host.ceph-osd.*.log

# Health
grep -i "health.*err\|health.*warn\|PG.*down\|pg.*inconsistent" ceph/host.ceph.*.log

# Network
grep -i "slow\|slow request\|network\|peer\|timeout" ceph/host.ceph-osd.*.log
```

## Kubernetes

```bash
# Node status
grep -i "node.*not ready\|node.*ready\|cord\|drain" kubernetes/kube-controller-manager.*.log

# Pod failures
grep -i "back-off\|crash\|fail\|error" kubernetes/kube-apiserver.*.log
```

## Galera / MariaDB (Control-plane DB)

```bash
# WSREP cluster state
grep -i "WSREP\|cluster status\|primary component\|donor\|joiner\|sst" openstack/mariadb/mariadb.*.log

# Galera split-brain / desync
grep -i "non-primary\|desync\|inconsistent\|leaving cluster\|cluster suspended" openstack/mariadb/mariadb.*.log

# Pod-side readiness probe
grep -i "fail\|not ready\|error" openstack/mariadb/mariadb-*-readiness.*.log

# Cross-service DB failure symptom
grep -E "WSREP has not yet prepared node|DBConnectionError|MySQL server has gone away" \
  openstack/{nova,cinder,neutron,glance,keystone}/*.log
```

## RabbitMQ / AMQP

```bash
# Cluster events
grep -i "node.*down\|node.*up\|partition\|netsplit\|cluster_status" \
  openstack/rabbitmq/rabbitmq.*.log

# Connection / channel errors
grep -i "connection_closed\|channel_closed\|missed heartbeats\|closing AMQP connection" \
  openstack/rabbitmq/rabbitmq.*.log

# Queue mirroring / HA
grep -i "ha-policy\|mirror\|slave\|sync" openstack/rabbitmq/rabbitmq.*.log

# Client-side symptom (any oslo.messaging consumer)
grep -i "AMQP server.*unreachable\|reconnecting in\|kombu.*connection\|Recovering from a failed" \
  openstack/{nova,cinder,neutron,glance,keystone}/*.log
```

## Time Sync (chrony)

> Galera, Ceph, and OVN are all sensitive to clock drift. Always check chrony
> first when seeing "weird" cluster-wide failures.

```bash
# Sync state
grep -i "selected\|fall back\|step\|jump\|drift\|cannot find\|no suitable source" \
  os/chrony.*.log

# Compare clock offsets across nodes
for d in ecs.*/; do
  echo "=== $(basename $d) ==="
  grep -i "system clock" "$d/os/chrony.*.log" 2>/dev/null | tail -5
done
```

## Operator Audit Trail (bash-history)

Captures every interactive root shell command on each node — invaluable for
correlating cluster anomalies with human actions.
仅当事件时间、错误、状态变化或其它证据表明可能存在人工操作时使用本节。搜索范围必须
限制在关联时间窗内, 保留或输出命中结果前对凭据和敏感命令参数脱敏。

```bash
# All commands across all nodes, sorted by wrapper timestamp
for d in ecs.*/; do
  grep . "$d/openstack/dozer/bash-history.*.log" 2>/dev/null
done | sort -k1,2

# Find risky commands
grep -E "systemctl (stop|restart)|kubectl delete|reboot|shutdown|rm -rf|reset --hard|drain" \
  openstack/dozer/bash-history.*.log

# Around a specific event time
grep "2026-06-18 10:2[0-9]" openstack/dozer/bash-history.*.log
```

## K8s CSI / RBD volume mount

When pods fail to mount RBD-backed PVs (common for control-plane services):

```bash
# CSI plugin errors
grep -iE "fail|error|timeout|not found|unmounter\.teardown" kubernetes/csi-rbdplugin.*.log

# Kubelet view of mount failures
grep -E "UnmountVolume|MountVolume|csi.*not.found|nestedpendingoperations" os/messages.*.log

# Driver registration
grep -iE "registrar|register|csi driver" kubernetes/driver-registrar.*.log
```

## OS Messages — Expanded checks

```bash
# Kernel panics, soft/hard lockups, watchdog
grep -iE "kernel panic|softlockup|hung_task|watchdog|BUG:|call trace|RIP:" os/messages.*.log

# OOM killer (extract victim + score)
grep -B 2 -A 5 "Out of memory" os/messages.*.log
grep -E "killed process [0-9]+.*total-vm" os/messages.*.log

# Block I/O / device errors
grep -iE "i/o error|end_request|sd [a-z]:.*error|nvme.*error|blk_update_request|medium error" \
  os/messages.*.log

# iSCSI session / SCSI
grep -iE "iscsi: connection.*closed|iscsi: session.*recovery|sd.*alua|scsi target" os/messages.*.log

# Multipath
grep -iE "multipath|dm-[0-9]|wwid|path.*(up|down|fail)" os/messages.*.log

# Network NIC / bonding
grep -iE "link is (up|down)|carrier|bond.*member|bond.*active|enp[0-9]" os/messages.*.log

# Power / thermal
grep -iE "thermal|mce:|machine check|power loss|psu" os/messages.*.log
```

## Ceph (Expanded)

```bash
# Cluster health snapshot points
grep -E "HEALTH_(WARN|ERR)" ceph/host.ceph.*.log | tail -20

# OSD flapping (down → up → down)
grep -E "osd\.[0-9]+ .*(down|up|booted)" ceph/host.ceph-mon.*.log | tail -50

# Slow ops / stuck PGs
grep -iE "slow ops|slow request|stuck (inactive|unclean|stale)|peering" ceph/host.ceph-osd.*.log

# Recovery / backfill
grep -iE "recovery|backfill|degraded|misplaced" ceph/host.ceph-mgr.*.log | tail -30

# Auth / quorum
grep -iE "election|quorum|leader|monmap|mon\..*(up|down)" ceph/host.ceph-mon.*.log
```

## OVN / Open vSwitch

```bash
# Tunnel / chassis state
grep -iE "chassis|tunnel|encap|bfd|sb_db" os/openvswitch/ovn-controller.*.log

# OVN DB events
grep -iE "leader|election|raft|cluster" os/openvswitch/ovn-ovsdb-{nb,sb}*.log

# Datapath flow errors
grep -iE "fail|error|drop|reject" os/openvswitch/ovs-vswitchd.*.log | head -30
```

## Libvirt qemu (per-instance)

```bash
# Pick the right per-instance log
ls libvirt/qemu.instance-*.log

# Domain start failures (often the actual reason hard_reboot fails)
grep -iE "error|fail|kvm.*not allowed|qemu-kvm:|aborting" \
  libvirt/qemu.instance-<DOMAIN_HEX>.*.log

# Block device events inside qemu
grep -iE "block.*open|block.*close|drive|virtio-blk" \
  libvirt/qemu.instance-<DOMAIN_HEX>.*.log
```

## Time-Windowed Analysis

```bash
# Extract logs within a 5-minute window
grep "2026-06-18 10:2[5-9]\|2026-06-18 10:3[0-4]" openstack/nova/nova-compute.*.log

# Extract logs around a specific minute
grep "2026-06-18 10:25:1[5-9]" openstack/nova/nova-compute.*.log

# Parallel search across all logs for same time window
for f in openstack/nova/nova-compute.*.log openstack/cinder/cinder-volume.*.log alcubierre/alcubierre-node.*.log; do
  echo "=== $f ==="
  grep "2026-06-18 10:25" "$f" 2>/dev/null
done
```

## Cross-Service Correlation

For issues spanning multiple services, correlate the same `req-<UUID>` (request ID) across logs:

```bash
# Track a request ID across all logs
grep -r "req-30eb5314-8245-4193-91b4-3b0b67be19bf" openstack/nova/nova-compute.*.log

# Or search across all directories
grep -r "req-<REQUEST_ID>" . --include="*.log"
```

## 高价值模式(实战沉淀)

### 检测 `target_iqns` 列表塌缩(BDM 陈旧的强信号)

```bash
# 抽出每个云硬盘的 target_iqns 唯一组合及命中次数
grep "Connecting to multipath volume" openstack/nova/nova-compute.*.log \
  | grep -oE "'target_iqns': \[[^]]+\]" | sort | uniq -c | sort -rn

# 4 项全相同 → portal 塌缩 = BDM 已经退化为单节点路径
```

### 抽出云主机完整生命周期主线(屏蔽噪声 INFO)

```bash
VM=<UUID>
grep "$VM" openstack/nova/nova-compute.*.log | grep -E \
  "Rebooting instance after nova-compute restart|Instance destroyed successfully|Instance rebooted successfully|Failed to resume instance|VolumeDeviceNotFound|Setting instance vm_state to ERROR|During.*sync.*power_state|VM (Started|Resumed|Paused|Stopped) \(Lifecycle Event\)|Received unexpected event" \
  | awk -F' ¦ ' '{raw=$5; sub(/^[^F]*F /, "", raw); print $1, "|", substr(raw,1,250)}'
```

### 同节点对照组(同时窗内成功 vs 失败的云主机)

```bash
grep -E "Instance rebooted successfully|Failed to resume instance" \
  openstack/nova/nova-compute.*.log \
  | awk -F' ¦ ' '{raw=$5; sub(/^[^F]*F /, "", raw); print $1, "|", substr(raw,1,200)}'
```

### 用 wwid 反查后端 target 是否服务这云硬盘

```bash
WWID=<wwid>      # 例:36001405acbc174502609ea455fb42783
for d in ecs.*/; do
  n=$(basename "$d" | cut -d. -f2)
  hit=$(grep -l "$WWID" "$d/alcubierre/alcubierre-target.node-"*.log 2>/dev/null | wc -l)
  echo "$n alcubierre-target hits: $hit"
done
# 全为 0 → 远端没人在承载这云硬盘 = nova 永远拿不到设备
```

### 服务可用时间线(节点重启后)

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
grep -E "Reached target.*Multi-User\|Reached target.*Graphical" \
  "$NODE_DIR/os/boot."*.log | tail -1 | awk -F' ¦ ' '{print $1}'

# 各服务启动时间
for svc in nova-compute cinder-volume alcubierre-target alcubierre-node \
           alcubierre-manager libvirtd kubelet containerd iscsid; do
  f=$(ls "$NODE_DIR"/**/$svc.node-*.log 2>/dev/null | head -1)
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
    f=$(ls "$d"/**/$svc.node-*.log 2>/dev/null | head -1)
    ts=$(grep -iE "Starting|started" "$f" 2>/dev/null | head -1 | awk -F' ¦ ' '{print $1}')
    [ -n "$ts" ] && printf "%-10s %-22s %s\n" "$node" "$svc" "$ts"
  done
done
```

### 重试节奏判定(标准 4 分钟超时 vs 短瞬抖动)

```bash
# 数同一云硬盘的 Connecting to multipath volume 重试次数和间隔
VOL=<VOLUME_ID>
grep "Connecting to multipath volume.*$VOL" openstack/nova/nova-compute.*.log \
  | awk -F' ¦ ' '{print $1}'
# 典型超时模式:10→10→10→30→65→130→255→512s 退避，总累计 ~1024s ≈ 17 min(实际看版本)
```

### Domain UUID ↔ instance-XXXX 一次性映射

```bash
# 用 -uuid 启动参数行从 qemu 日志反查 hex domain
for f in libvirt/qemu.instance-*.log; do
  uid=$(grep -m1 "^.*¦ libvirt ¦  ¦ -uuid " "$f" | awk '{print $NF}')
  dom=$(basename "$f" | sed -E 's/qemu\.(instance-[0-9a-f]+).*/\1/')
  echo "$dom -> $uid"
done
```
