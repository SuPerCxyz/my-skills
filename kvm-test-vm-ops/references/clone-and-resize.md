# Clone and Resize

## Contents 目录

- [Variable Contract 变量契约](#variable-contract-变量契约)
- [Controlled Shutdown 受控关机](#controlled-shutdown-受控关机)
- [Provision Preflight 创建预检](#provision-preflight-创建预检)
- [Clone And Identity 克隆和身份](#clone-and-identity-克隆和身份)
- [Compute Resources 计算资源](#compute-resources-计算资源)
- [Host Disk 宿主机磁盘](#host-disk-宿主机磁盘)
- [Guest Filesystem 客户机文件系统](#guest-filesystem-客户机文件系统)
- [Memory Escalation 内存递增](#memory-escalation-内存递增)

## Variable Contract 变量契约

本参考文档只适用于 `provision` 或 `resize`. 变量来自已确认的 VM 计划和 [discovery.md](discovery.md), 不接受尖括号占位符。
以下契约在本次目标开始时初始化一次, 后续章节复用; 切换目标重新初始化, 不沿用其他 VM 的变更标记。

```bash
: "${KVM_MODE:?set KVM_MODE}"
case "$KVM_MODE" in provision|resize) ;; *) printf 'invalid mutation mode\n' >&2; exit 2 ;; esac

: "${KVM_NODE:?set KVM_NODE}"
: "${KVM_SSH_USER:?set KVM_SSH_USER}"
: "${LIBVIRT_URI:=qemu:///system}"
: "${KVM_DOMAIN:?set KVM_DOMAIN}"
: "${KVM_DISK_TARGET:?set KVM_DISK_TARGET}"
: "${KVM_DEST_DISK:?set KVM_DEST_DISK from domblklist}"
if test "$KVM_MODE" = provision; then
  : "${PLAN_DISK_BYTES:=21474836480}"
  : "${PLAN_VCPUS:=2}"
  : "${PLAN_MEMORY_KIB:=1048576}"
  : "${PLAN_MEMORY_MAX_KIB:=4194304}"
else
  : "${PLAN_DISK_BYTES:=}"
  : "${PLAN_VCPUS:=}"
  : "${PLAN_MEMORY_KIB:=}"
  : "${PLAN_MEMORY_MAX_KIB:=}"
fi
: "${PLAN_MEMORY_STEP_KIB:=524288}"
: "${KVM_SHUTDOWN_WAIT_SECONDS:=120}"
KVM_OFFLINE_CHANGED=false

[[ "$KVM_DOMAIN" =~ ^[A-Za-z0-9._:-]+$ ]] || { printf 'unsafe domain name\n' >&2; exit 2; }
[[ "$KVM_DISK_TARGET" =~ ^[A-Za-z0-9._-]+$ ]] || { printf 'unsafe disk target\n' >&2; exit 2; }
for requested_value in "$PLAN_DISK_BYTES" "$PLAN_VCPUS" "$PLAN_MEMORY_KIB" "$PLAN_MEMORY_MAX_KIB"; do
  [[ -z "$requested_value" || "$requested_value" =~ ^[0-9]+$ ]] || exit 2
done
[[ "$PLAN_MEMORY_STEP_KIB" =~ ^[0-9]+$ ]] || exit 2
[[ "$KVM_SHUTDOWN_WAIT_SECONDS" =~ ^[0-9]+$ ]] || exit 2
case "$KVM_DEST_DISK" in *"'"*|*$'\n'*) printf 'unsafe disk path\n' >&2; exit 2 ;; esac

KVM_SSH_TARGET="${KVM_SSH_USER}@${KVM_NODE}"
KVM_NODE_SSH=(ssh -o BatchMode=yes -o ConnectTimeout=5 "$KVM_SSH_TARGET")
```

## Controlled Shutdown 受控关机

需要 `shut off` 状态的变更 (计算资源、宿主机磁盘、内存步长) 遇到运行中域时直接调用本函数. 测试 VM 的受控关机和开机属于本次已确认调整范围的一部分, 无需再次请求用户确认. 只使用优雅 `shutdown`, 不使用 `destroy`; 超时返回 3 交由用户决策:

```bash
controlled_shutdown() {
  local state deadline
  state="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domstate '$KVM_DOMAIN'")" || return 2
  state="$(xargs <<<"$state")"
  case "$state" in
    'shut off') return 0 ;;
    running) ;;
    *) printf 'unsupported domain state=%s\n' "$state" >&2; return 2 ;;
  esac
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' shutdown '$KVM_DOMAIN'" || return 2
  deadline=$((SECONDS + KVM_SHUTDOWN_WAIT_SECONDS))
  while :; do
    state="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domstate '$KVM_DOMAIN'")" || return 2
    state="$(xargs <<<"$state")"
    test "$state" = 'shut off' && return 0
    ((SECONDS < deadline)) || { printf 'graceful shutdown timeout\n' >&2; return 3; }
    sleep 5
  done
}
```

## Provision Preflight 创建预检

`provision` 模式额外要求:

```bash
: "${KVM_TEMPLATE:?set KVM_TEMPLATE}"
: "${KVM_SOURCE_DISK:?set KVM_SOURCE_DISK}"
: "${KVM_TEMPLATE_GENERALIZED:?set KVM_TEMPLATE_GENERALIZED}"

test "$KVM_TEMPLATE_GENERALIZED" = true || {
  printf 'template generalization is not verified\n' >&2
  exit 2
}
case "$KVM_SOURCE_DISK" in *"'"*|*$'\n'*) printf 'unsafe source disk path\n' >&2; exit 2 ;; esac

KVM_TEMPLATE_STATE="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domstate '$KVM_TEMPLATE'" | xargs
)"
test "$KVM_TEMPLATE_STATE" = 'shut off' || {
  printf 'template state=%s, expected=shut off\n' "$KVM_TEMPLATE_STATE" >&2
  exit 2
}

KVM_PROBE_RC=0
"${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' dominfo '$KVM_DOMAIN'" >/dev/null 2>&1 || KVM_PROBE_RC=$?
case "$KVM_PROBE_RC" in
  0) printf 'destination domain already exists\n' >&2; exit 2 ;;
  1) ;;
  *) printf 'domain probe failed rc=%s\n' "$KVM_PROBE_RC" >&2; exit 2 ;;
esac

KVM_DEST_PROBE_RC=0
"${KVM_NODE_SSH[@]}" "test ! -e '$KVM_DEST_DISK'" || KVM_DEST_PROBE_RC=$?
case "$KVM_DEST_PROBE_RC" in
  0) ;;
  1) printf 'destination disk already exists\n' >&2; exit 2 ;;
  *) printf 'disk probe failed rc=%s\n' "$KVM_DEST_PROBE_RC" >&2; exit 2 ;;
esac

KVM_DISK_DIR="$(dirname -- "$KVM_DEST_DISK")"
KVM_STORAGE_FREE_BYTES="$(
  "${KVM_NODE_SSH[@]}" "df -PB1 '$KVM_DISK_DIR'" | awk 'NR==2 {print $4}'
)"
KVM_SOURCE_ALLOCATED_BYTES="$(
  "${KVM_NODE_SSH[@]}" "du -B1 '$KVM_SOURCE_DISK'" | awk '{print $1}'
)"
KVM_BASELINE_BYTES="$((KVM_SOURCE_ALLOCATED_BYTES > PLAN_DISK_BYTES ? KVM_SOURCE_ALLOCATED_BYTES : PLAN_DISK_BYTES))"
KVM_REQUIRED_HEADROOM_BYTES=$((1024 * 1024 * 1024))
((KVM_STORAGE_FREE_BYTES > KVM_BASELINE_BYTES + KVM_REQUIRED_HEADROOM_BYTES)) || {
  printf 'insufficient storage free=%s required>%s baseline=%s\n' \
    "$KVM_STORAGE_FREE_BYTES" \
    "$((KVM_BASELINE_BYTES + KVM_REQUIRED_HEADROOM_BYTES))" \
    "$KVM_BASELINE_BYTES" >&2
  exit 2
}
```

遇到多磁盘、块设备后端磁盘或 NVRAM 模板时, 必须在发现阶段停止. 不把本流程扩展成猜测式 `--file` 列表.

## Clone And Identity 克隆和身份

所有预检通过后执行一次克隆:

```bash
"${KVM_NODE_SSH[@]}" \
  "virt-clone --connect '$LIBVIRT_URI' --original '$KVM_TEMPLATE' --name '$KVM_DOMAIN' --file '$KVM_DEST_DISK'"
```

立即验证独立身份和存储:

```bash
KVM_DEST_INFO="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' dominfo '$KVM_DOMAIN'")"
KVM_DEST_BLOCKS="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domblklist '$KVM_DOMAIN' --details")"
KVM_DEST_INTERFACES="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domiflist '$KVM_DOMAIN'")"

grep -Fq "$KVM_DEST_DISK" <<<"$KVM_DEST_BLOCKS" || { printf 'destination disk mismatch\n' >&2; exit 2; }
KVM_DEST_UUID="$(awk '/^UUID:/ {print $2}' <<<"$KVM_DEST_INFO")"
KVM_DEST_MAC="$(awk 'NR>2 && $5!="" {print $5; exit}' <<<"$KVM_DEST_INTERFACES")"
test -n "$KVM_DEST_UUID" && test -n "$KVM_DEST_MAC" || { printf 'missing clone identity\n' >&2; exit 2; }
# 统一导出, 供 verification.md 的变量契约使用
KVM_UUID="$KVM_DEST_UUID"
KVM_MAC="$KVM_DEST_MAC"
```

模板元数据必须证明 machine-id、主机名和 SSH 主机密钥会在克隆首次启动时唯一化. 不能证明时, 保持克隆 VM 处于 `shut off` 并停止. `virt-sysprep` 只允许对目标 VM 经单独授权执行, 不允许处理源模板.

## Compute Resources 计算资源

先分别读取运行态和持久配置。`dominfo` 不代表下次启动配置; 使用 `dumpxml --inactive` 核实后者, 不假设 `dominfo` 有 `--config`。只有明确请求的字段参与比较和写入, `resize` 未指定项保留持久值, 不从运行态或创建默认值推导目标。

```bash
command -v python3 >/dev/null || { printf 'local python3 missing\n' >&2; exit 2; }
KVM_REQUEST_VCPUS=false
KVM_REQUEST_MEMORY=false
KVM_REQUEST_MAX_MEMORY=false
test -z "${PLAN_VCPUS:-}" || KVM_REQUEST_VCPUS=true
test -z "${PLAN_MEMORY_KIB:-}" || KVM_REQUEST_MEMORY=true
test -z "${PLAN_MEMORY_MAX_KIB:-}" || KVM_REQUEST_MAX_MEMORY=true

read_compute_config() {
  local xml
  xml="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' dumpxml '$KVM_DOMAIN' --inactive")" || return 2
  python3 -c '
import sys
import xml.etree.ElementTree as ET
root = ET.fromstring(sys.stdin.read())
cpu = root.find("vcpu")
if cpu is None or not cpu.text:
    raise ValueError("persistent vcpu count missing")
maximum = int(cpu.text)
current = int(cpu.get("current", str(maximum)))
def kib(node):
    if node is None or node.get("unit", "KiB") != "KiB":
        raise ValueError("expected normalized KiB memory in inactive XML")
    return int(node.text)
memory_max = kib(root.find("memory"))
memory_node = root.find("currentMemory")
memory = kib(memory_node) if memory_node is not None else memory_max
if min(current, maximum, memory, memory_max) < 1 or current > maximum or memory > memory_max:
    raise ValueError("invalid persistent compute configuration")
print(current, maximum, memory, memory_max)
' <<<"$xml"
}
KVM_DOMAIN_STATE="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domstate '$KVM_DOMAIN'")" || exit 2
KVM_DOMAIN_STATE="$(xargs <<<"$KVM_DOMAIN_STATE")"
case "$KVM_DOMAIN_STATE" in running|'shut off') ;; *) exit 2 ;; esac
KVM_DOMAIN_INFO="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' dominfo '$KVM_DOMAIN'")" || exit 2
KVM_CURRENT_VCPUS="$(awk '/^CPU\(s\):/ {print $2}' <<<"$KVM_DOMAIN_INFO")"
KVM_CURRENT_MEMORY_KIB="$(awk '/^Used memory:/ {print $3}' <<<"$KVM_DOMAIN_INFO")"
KVM_CURRENT_MAX_MEMORY_KIB="$(awk '/^Max memory:/ {print $3}' <<<"$KVM_DOMAIN_INFO")"
KVM_CONFIG_VALUES="$(read_compute_config)" || exit 2
read -r KVM_CONFIG_VCPUS KVM_CONFIG_MAX_VCPUS KVM_CONFIG_MEMORY_KIB KVM_CONFIG_MAX_MEMORY_KIB <<<"$KVM_CONFIG_VALUES"
: "${PLAN_VCPUS:=$KVM_CONFIG_VCPUS}"
: "${PLAN_MEMORY_KIB:=$KVM_CONFIG_MEMORY_KIB}"
: "${PLAN_MEMORY_MAX_KIB:=$KVM_CONFIG_MAX_MEMORY_KIB}"
for numeric_value in "$KVM_CURRENT_VCPUS" "$KVM_CURRENT_MEMORY_KIB" "$KVM_CURRENT_MAX_MEMORY_KIB" "$PLAN_VCPUS" "$PLAN_MEMORY_KIB" "$PLAN_MEMORY_MAX_KIB"; do
  [[ "$numeric_value" =~ ^[0-9]+$ ]] && ((numeric_value > 0)) || exit 2
done
((PLAN_MEMORY_KIB <= PLAN_MEMORY_MAX_KIB)) || { printf 'memory exceeds maximum\n' >&2; exit 2; }

KVM_NEEDS_RESTART=false
if test "$KVM_DOMAIN_STATE" = running; then
  if { test "$KVM_REQUEST_VCPUS" = true && test "$KVM_CURRENT_VCPUS" != "$PLAN_VCPUS"; } ||
     { test "$KVM_REQUEST_MEMORY" = true && test "$KVM_CURRENT_MEMORY_KIB" != "$PLAN_MEMORY_KIB"; } ||
     { test "$KVM_REQUEST_MAX_MEMORY" = true && test "$KVM_CURRENT_MAX_MEMORY_KIB" != "$PLAN_MEMORY_MAX_KIB"; }; then
    KVM_NEEDS_RESTART=true
    if test "$KVM_REQUEST_VCPUS" = false && test "$KVM_CURRENT_VCPUS" != "$KVM_CONFIG_VCPUS"; then
      printf 'pending_unrequested_vcpus: live=%s persistent=%s; restart applies existing config\n' "$KVM_CURRENT_VCPUS" "$KVM_CONFIG_VCPUS"
    fi
    if { test "$KVM_REQUEST_MEMORY" = false && test "$KVM_CURRENT_MEMORY_KIB" != "$KVM_CONFIG_MEMORY_KIB"; } ||
       { test "$KVM_REQUEST_MAX_MEMORY" = false && test "$KVM_CURRENT_MAX_MEMORY_KIB" != "$KVM_CONFIG_MAX_MEMORY_KIB"; }; then
      printf 'pending_unrequested_memory: restart applies existing persistent memory=%s max=%s KiB\n' "$KVM_CONFIG_MEMORY_KIB" "$KVM_CONFIG_MAX_MEMORY_KIB"
    fi
    controlled_shutdown || exit $?
    KVM_OFFLINE_CHANGED=true
  fi
fi

KVM_CONFIG_CHANGED=false
if test "$KVM_REQUEST_VCPUS" = true && test "$KVM_CONFIG_VCPUS" != "$PLAN_VCPUS"; then
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' setvcpus '$KVM_DOMAIN' '$PLAN_VCPUS' --maximum --config" || exit 2
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' setvcpus '$KVM_DOMAIN' '$PLAN_VCPUS' --config" || exit 2
  KVM_CONFIG_CHANGED=true
fi
if test "$KVM_REQUEST_MAX_MEMORY" = true && test "$KVM_CONFIG_MAX_MEMORY_KIB" != "$PLAN_MEMORY_MAX_KIB"; then
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' setmaxmem '$KVM_DOMAIN' '${PLAN_MEMORY_MAX_KIB}KiB' --config" || exit 2
  KVM_CONFIG_CHANGED=true
fi
if test "$KVM_REQUEST_MEMORY" = true && test "$KVM_CONFIG_MEMORY_KIB" != "$PLAN_MEMORY_KIB"; then
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' setmem '$KVM_DOMAIN' '${PLAN_MEMORY_KIB}KiB' --config" || exit 2
  KVM_CONFIG_CHANGED=true
fi
KVM_CONFIG_VALUES="$(read_compute_config)" || exit 2
read -r KVM_FINAL_VCPUS KVM_FINAL_MAX_VCPUS KVM_FINAL_MEMORY_KIB KVM_FINAL_MAX_MEMORY_KIB <<<"$KVM_CONFIG_VALUES"
if { test "$KVM_REQUEST_VCPUS" = true && test "$KVM_FINAL_VCPUS" != "$PLAN_VCPUS"; } ||
   { test "$KVM_REQUEST_MEMORY" = true && test "$KVM_FINAL_MEMORY_KIB" != "$PLAN_MEMORY_KIB"; } ||
   { test "$KVM_REQUEST_MAX_MEMORY" = true && test "$KVM_FINAL_MAX_MEMORY_KIB" != "$PLAN_MEMORY_MAX_KIB"; }; then
  printf 'persistent compute configuration does not match confirmed target\n' >&2
  exit 2
fi
if test "$KVM_CONFIG_CHANGED" = true && test "$KVM_DOMAIN_STATE" = 'shut off'; then
  KVM_OFFLINE_CHANGED=true
fi
if test "$KVM_CONFIG_CHANGED" = false && test "$KVM_NEEDS_RESTART" = false; then
  printf 'requested compute already_satisfied in live and persistent state\n'
fi
```

只更正持久配置而运行态已满足时不关机; 原本关机且本次未调整时保留关机状态。需要重启时如实说明将随重启生效的既有未请求差异, 不覆盖这些字段。最终按 `verification.md` 核对实际启动结果, 不用持久配置成功冒充运行态已生效。

QEMU 的 `setvcpus --maximum --config` 会调整持久 vCPU 上限, 缩小时同时裁剪其 vCPU 定义; 保留先 maximum 后 current 的现有顺序。NUMA/topology 不支持目标时停止并报告, 不自动修改拓扑。依据 [libvirt v8.0.0 QEMU 实现](https://gitlab.com/libvirt/libvirt/-/blob/v8.0.0/src/qemu/qemu_driver.c#L3971-4012) 和 [vCPU 定义调整](https://gitlab.com/libvirt/libvirt/-/blob/v8.0.0/src/conf/domain_conf.c#L1866-1889), 实际环境仍须核实版本与命令结果。

## Host Disk 宿主机磁盘

先通过 libvirt 读取实际磁盘 target 的容量, 避免对运行中镜像直接使用 `qemu-img` 引发锁冲突。仅容量不足时关机并复核, 不缩盘。`resize` 必须有明确的磁盘目标容量。

```bash
: "${PLAN_DISK_BYTES:?set confirmed disk target}"
[[ "$PLAN_DISK_BYTES" =~ ^[0-9]+$ ]] && ((PLAN_DISK_BYTES > 0)) || exit 2
KVM_BLOCK_INFO="$("${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domblkinfo '$KVM_DOMAIN' '$KVM_DISK_TARGET'")" || exit 2
KVM_CURRENT_DISK_BYTES="$(awk '/^Capacity:/ {print $2}' <<<"$KVM_BLOCK_INFO")"
[[ "$KVM_CURRENT_DISK_BYTES" =~ ^[0-9]+$ ]] && ((KVM_CURRENT_DISK_BYTES > 0)) || exit 2

if ((KVM_CURRENT_DISK_BYTES >= PLAN_DISK_BYTES)); then
  printf 'disk already_satisfied; no shutdown or shrink\n'
else
  command -v python3 >/dev/null || { printf 'local python3 missing\n' >&2; exit 2; }
  "${KVM_NODE_SSH[@]}" 'command -v qemu-img' >/dev/null || exit 2
  controlled_shutdown || exit $?
  KVM_DISK_JSON="$("${KVM_NODE_SSH[@]}" "qemu-img info --output=json '$KVM_DEST_DISK'")" || exit 2
  KVM_CURRENT_DISK_BYTES="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["virtual-size"])' <<<"$KVM_DISK_JSON")" || exit 2
  [[ "$KVM_CURRENT_DISK_BYTES" =~ ^[0-9]+$ ]] || exit 2
  if ((KVM_CURRENT_DISK_BYTES < PLAN_DISK_BYTES)); then
    "${KVM_NODE_SSH[@]}" "qemu-img resize '$KVM_DEST_DISK' '$PLAN_DISK_BYTES'" || exit 2
  fi
  KVM_DISK_JSON="$("${KVM_NODE_SSH[@]}" "qemu-img info --output=json '$KVM_DEST_DISK'")" || exit 2
  KVM_FINAL_DISK_BYTES="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["virtual-size"])' <<<"$KVM_DISK_JSON")" || exit 2
  [[ "$KVM_FINAL_DISK_BYTES" =~ ^[0-9]+$ ]] && ((KVM_FINAL_DISK_BYTES >= PLAN_DISK_BYTES)) || exit 2
  KVM_OFFLINE_CHANGED=true
fi
```

运行态只使用实际磁盘 target:

```bash
"${KVM_NODE_SSH[@]}" \
  "virsh --connect '$LIBVIRT_URI' domblkinfo '$KVM_DOMAIN' '$KVM_DISK_TARGET' --human"
```

## Guest Filesystem 客户机文件系统

只在宿主机磁盘已增长, 且客户机尚未使用新增空间时执行. 先使用 [verification.md](verification.md) 建立 `GUEST_SSH` 数组和 `GUEST_SSH_TARGET`.

只读布局:

```bash
"${GUEST_SSH[@]}" "$GUEST_SSH_TARGET" \
  'findmnt -n -o SOURCE,FSTYPE,TARGET /; lsblk -b -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS; pvs 2>/dev/null || true; vgs 2>/dev/null || true; lvs 2>/dev/null || true'
```

常见直接分区分支:

```bash
"${GUEST_SSH[@]}" "$GUEST_SSH_TARGET" 'bash -se' <<'GUEST'
set -eu
ROOT_SOURCE="$(readlink -f "$(findmnt -n -o SOURCE /)")"
ROOT_FSTYPE="$(findmnt -n -o FSTYPE /)"
ROOT_PARENT="$(lsblk -n -o PKNAME "$ROOT_SOURCE" | xargs)"
ROOT_PARTNUM="$(lsblk -n -o PARTNUM "$ROOT_SOURCE" | xargs)"
test -n "$ROOT_PARENT" && test -n "$ROOT_PARTNUM" || { printf 'not a direct partition\n' >&2; exit 2; }
command -v growpart >/dev/null || { printf 'growpart missing\n' >&2; exit 2; }
command -v udevadm >/dev/null || { printf 'udevadm missing\n' >&2; exit 2; }
case "$ROOT_FSTYPE" in
  xfs) ROOT_GROW_TOOL=xfs_growfs ;;
  ext2|ext3|ext4) ROOT_GROW_TOOL=resize2fs ;;
  *) printf 'unsupported direct filesystem=%s\n' "$ROOT_FSTYPE" >&2; exit 2 ;;
esac
command -v "$ROOT_GROW_TOOL" >/dev/null || { printf '%s missing\n' "$ROOT_GROW_TOOL" >&2; exit 2; }

if GROWPART_DRY_RUN="$(growpart -N "/dev/$ROOT_PARENT" "$ROOT_PARTNUM" 2>&1)"; then
  growpart "/dev/$ROOT_PARENT" "$ROOT_PARTNUM"
  udevadm settle
elif grep -q '^NOCHANGE:' <<<"$GROWPART_DRY_RUN"; then
  printf 'already_satisfied\n'
else
  printf '%s\n' "$GROWPART_DRY_RUN" >&2
  exit 2
fi

case "$ROOT_FSTYPE" in
  xfs)
    xfs_growfs /
    ;;
  ext2|ext3|ext4)
    resize2fs "$ROOT_SOURCE"
    ;;
  *) printf 'unsupported direct filesystem=%s\n' "$ROOT_FSTYPE" >&2; exit 2 ;;
esac
lsblk -b -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
df -B1 /
GUEST
```

LVM 只支持单 PV、单 root LV 的无歧义布局. 其它 LVM、加密设备、Btrfs、多设备或 root 非末分区布局必须停止. 常见模板自带独立 swap LV 时会命中该约束, 需要处理此类布局时由用户单独给出方案:

```bash
"${GUEST_SSH[@]}" "$GUEST_SSH_TARGET" 'bash -se' <<'GUEST'
set -eu
ROOT_LV="$(readlink -f "$(findmnt -n -o SOURCE /)")"
ROOT_FSTYPE="$(findmnt -n -o FSTYPE /)"
command -v pvs >/dev/null && command -v vgs >/dev/null && command -v lvs >/dev/null && command -v pvresize >/dev/null || {
  printf 'LVM tools missing\n' >&2
  exit 2
}
ROOT_VG="$(lvs --noheadings -o vg_name "$ROOT_LV" | xargs)"
mapfile -t ROOT_PVS < <(pvs --noheadings -o pv_name,vg_name | awk -v vg="$ROOT_VG" '$2==vg {print $1}')
mapfile -t ROOT_LVS < <(lvs --noheadings -o lv_path "$ROOT_VG" | xargs -n1)
((${#ROOT_PVS[@]} == 1 && ${#ROOT_LVS[@]} == 1)) || {
  printf 'ambiguous LVM layout\n' >&2
  exit 2
}
case "$ROOT_FSTYPE" in
  xfs) ROOT_GROW_TOOL=xfs_growfs ;;
  ext2|ext3|ext4) ROOT_GROW_TOOL=resize2fs ;;
  *) printf 'unsupported LVM filesystem=%s\n' "$ROOT_FSTYPE" >&2; exit 2 ;;
esac
command -v "$ROOT_GROW_TOOL" >/dev/null && command -v lvextend >/dev/null || {
  printf 'filesystem or lvextend tool missing\n' >&2
  exit 2
}
ROOT_PV="${ROOT_PVS[0]}"
ROOT_PARENT="$(lsblk -n -o PKNAME "$ROOT_PV" | xargs)"
ROOT_PARTNUM="$(lsblk -n -o PARTNUM "$ROOT_PV" | xargs)"
test -n "$ROOT_PARENT" && test -n "$ROOT_PARTNUM" || { printf 'unsupported PV mapping\n' >&2; exit 2; }
command -v growpart >/dev/null || { printf 'growpart missing\n' >&2; exit 2; }
command -v udevadm >/dev/null || { printf 'udevadm missing\n' >&2; exit 2; }

if GROWPART_DRY_RUN="$(growpart -N "/dev/$ROOT_PARENT" "$ROOT_PARTNUM" 2>&1)"; then
  growpart "/dev/$ROOT_PARENT" "$ROOT_PARTNUM"
  udevadm settle
elif ! grep -q '^NOCHANGE:' <<<"$GROWPART_DRY_RUN"; then
  printf '%s\n' "$GROWPART_DRY_RUN" >&2
  exit 2
fi
pvresize "$ROOT_PV"
lvextend -r -l +100%FREE "$ROOT_LV"
pvs; vgs; lvs; df -B1 /
GUEST
```

## Memory Escalation 内存递增

先从 [verification.md](verification.md) 收集 OOM 或持续内存压力证据. 无证据不调整. ballooning 无法超过开机时的物理内存, 因此递增一律采用受控关机 -> 配置 -> 开机路径, 不做 `--live` 调整:

```bash
: "${PLAN_MEMORY_MAX_KIB:?set confirmed memory ceiling}"
[[ "$PLAN_MEMORY_MAX_KIB" =~ ^[0-9]+$ ]] && ((PLAN_MEMORY_MAX_KIB > 0)) || exit 2
KVM_HOST_AVAILABLE_KIB="$(
  "${KVM_NODE_SSH[@]}" "awk '/MemAvailable:/ {print \$2}' /proc/meminfo"
)"
KVM_CURRENT_MEMORY_KIB="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' dominfo '$KVM_DOMAIN'" \
    | awk '/^Used memory:/ {print $3}'
)"
KVM_NEXT_MEMORY_KIB=$((KVM_CURRENT_MEMORY_KIB + PLAN_MEMORY_STEP_KIB))

((KVM_NEXT_MEMORY_KIB <= PLAN_MEMORY_MAX_KIB)) || { printf 'memory ceiling reached\n' >&2; exit 2; }
((KVM_HOST_AVAILABLE_KIB > PLAN_MEMORY_STEP_KIB + 524288)) || { printf 'insufficient host memory\n' >&2; exit 2; }

controlled_shutdown || exit $?

"${KVM_NODE_SSH[@]}" \
  "virsh --connect '$LIBVIRT_URI' setmem '$KVM_DOMAIN' '${KVM_NEXT_MEMORY_KIB}KiB' --config"
"${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' start '$KVM_DOMAIN'"
```

每次只执行一个步长. 开机后回到 [verification.md](verification.md) 重新收集工作负载和内存证据, 再决定下一步. 关机超时返回 3 交由用户决策; 不自动重复递增, 不清理资源.
