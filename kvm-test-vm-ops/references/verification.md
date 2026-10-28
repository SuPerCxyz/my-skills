# Verification

## Contents 目录

- [Variable Contract 变量契约](#variable-contract-变量契约)
- [Domain And QGA 域和 QGA](#domain-and-qga-域和-qga)
- [IPv4 Primary IPv4 首选](#ipv4-primary-ipv4-首选)
- [IPv6 Fallback IPv6 保底](#ipv6-fallback-ipv6-保底)
- [SSH Authentication SSH 认证](#ssh-authentication-ssh-认证)
- [Guest And Memory Evidence 客户机和内存证据](#guest-and-memory-evidence-客户机和内存证据)
- [Acceptance And Failure 验收和失败](#acceptance-and-failure-验收和失败)

## Variable Contract 变量契约

```bash
: "${KVM_MODE:?set KVM_MODE}"
case "$KVM_MODE" in inspect|reuse|provision|resize|verify) ;; *) exit 2 ;; esac
: "${KVM_NODE:?set KVM_NODE}"
: "${KVM_SSH_USER:?set KVM_SSH_USER}"
: "${LIBVIRT_URI:=qemu:///system}"
: "${KVM_DOMAIN:?set KVM_DOMAIN}"
: "${KVM_UUID:?set KVM_UUID from domain identity}"
: "${KVM_MAC:?set KVM_MAC}"
: "${GUEST_USER:=}"
: "${GUEST_AUTH_MODE:=}"
: "${KVM_IPV4_WAIT_SECONDS:=180}"
: "${KVM_ALLOW_IPV6_FALLBACK:=true}"
: "${KVM_SSH_READY_WAIT_SECONDS:=120}"

[[ "$KVM_DOMAIN" =~ ^[A-Za-z0-9._:-]+$ ]] || exit 2
[[ "$KVM_MAC" =~ ^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$ ]] || exit 2
[[ "$KVM_IPV4_WAIT_SECONDS" =~ ^[0-9]+$ ]] || exit 2
[[ "$KVM_SSH_READY_WAIT_SECONDS" =~ ^[0-9]+$ ]] || exit 2

KVM_SSH_TARGET="${KVM_SSH_USER}@${KVM_NODE}"
KVM_NODE_SSH=(ssh -o BatchMode=yes -o ConnectTimeout=5 "$KVM_SSH_TARGET")
```

`GUEST_USER` 和 `GUEST_AUTH_MODE` 仅在用户请求包含客户机内检查 (SSH、machine-id、内存证据、文件系统) 时必填; 纯 QGA/地址验证可留空并跳过 SSH 认证节.

## Domain And QGA 域和 QGA

`provision` 在克隆和配置完成后启动; `resize` 只有本次发生离线调整 (`KVM_OFFLINE_CHANGED=true`) 才按确认范围启动。无调整且原本关机时保留电源状态, 报告配置结果并跳过需开机的 QGA/SSH 检查. `inspect`, `reuse` 和 `verify` 不启动已关机的 VM:

```bash
KVM_DOMAIN_STATE="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domstate '$KVM_DOMAIN'" | xargs
)"
if test "$KVM_MODE" = provision; then
  test "$KVM_DOMAIN_STATE" = 'shut off' || {
    printf 'new provisioned domain state=%s, expected=shut off\n' "$KVM_DOMAIN_STATE" >&2
    exit 2
  }
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' start '$KVM_DOMAIN'"
elif test "$KVM_MODE" = resize; then
  case "$KVM_DOMAIN_STATE" in
    running) ;;
    'shut off')
      if test "${KVM_OFFLINE_CHANGED:-false}" = true; then
        "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' start '$KVM_DOMAIN'"
      else
        printf 'already_satisfied; domain remains shut off; skip guest checks\n'
        exit 0
      fi
      ;;
    *)
      printf 'mode=resize unexpected state=%s\n' "$KVM_DOMAIN_STATE" >&2
      exit 2
      ;;
  esac
elif test "$KVM_DOMAIN_STATE" != running; then
  printf 'mode=%s does not authorize start, state=%s\n' "$KVM_MODE" "$KVM_DOMAIN_STATE" >&2
  exit 2
fi
```

QGA JSON 的标准引用方式:

```bash
QGA_PING='{"execute":"guest-ping"}'
QGA_INFO='{"execute":"guest-info"}'
QGA_INTERFACES='{"execute":"guest-network-get-interfaces"}'

"${KVM_NODE_SSH[@]}" \
  "virsh --connect '$LIBVIRT_URI' qemu-agent-command '$KVM_DOMAIN' '$QGA_PING'"
"${KVM_NODE_SSH[@]}" \
  "virsh --connect '$LIBVIRT_URI' qemu-agent-command '$KVM_DOMAIN' '$QGA_INFO'"
```

## IPv4 Primary IPv4 首选

在截止时间内只等待和选择与 `KVM_MAC` 关联的非 loopback IPv4. 可以记录 IPv6, 但不能让它抢占 IPv4.

```bash
KVM_DEADLINE=$((SECONDS + KVM_IPV4_WAIT_SECONDS))
KVM_LAST_QGA_STATE=pending
KVM_LAST_ADDRESS_STATE=none
KVM_IPV4_CIDR=
KVM_IPV6_CIDR=
KVM_GUEST_INTERFACE=
KVM_IPV4_READY_AT=
KVM_IPV6_READY_AT=

while ((SECONDS < KVM_DEADLINE)); do
  if ! "${KVM_NODE_SSH[@]}" \
    "virsh --connect '$LIBVIRT_URI' qemu-agent-command '$KVM_DOMAIN' '$QGA_PING'" \
    >/dev/null 2>&1; then
    KVM_LAST_QGA_STATE=pending
    sleep 5
    continue
  fi
  KVM_LAST_QGA_STATE=ready

  if ! KVM_ADDRESS_OUTPUT="$(
    "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domifaddr '$KVM_DOMAIN' --source agent"
  )"; then
    KVM_LAST_ADDRESS_STATE=query-failed
    sleep 5
    continue
  fi

  read -r KVM_GUEST_INTERFACE KVM_IPV4_CIDR < <(
    awk -v mac="$KVM_MAC" '
      $1!="-" {current_if=$1; current_mac=$2}
      current_mac==mac && $3=="ipv4" && $4!~/^127\./ {print current_if, $4; exit}
    ' \
      <<<"$KVM_ADDRESS_OUTPUT"
  )
  if test -n "$KVM_IPV4_CIDR"; then
    KVM_LAST_ADDRESS_STATE=ipv4-ready
    KVM_IPV4_READY_AT="$(date --iso-8601=seconds)"
    break
  fi

  read -r KVM_GUEST_INTERFACE KVM_IPV6_CIDR < <(
    awk -v mac="$KVM_MAC" '
      $1!="-" {current_if=$1; current_mac=$2}
      current_mac==mac && $3=="ipv6" && tolower($4) !~ /^(::1\/|fe80)/ {print current_if, $4; exit}
    ' \
      <<<"$KVM_ADDRESS_OUTPUT"
  )
  if test -n "$KVM_IPV6_CIDR" && test -z "$KVM_IPV6_READY_AT"; then
    KVM_IPV6_READY_AT="$(date --iso-8601=seconds)"
  fi
  KVM_LAST_ADDRESS_STATE=pending-ipv4
  sleep 5
done
```

## IPv6 Fallback IPv6 保底

只有 IPv4 等待截止时间到期后才考虑 IPv6, 且只接受非链路本地地址; `fe80::/10` 不可路由, 一律不作为保底. 使用前确认执行机到该地址的路由可达, 不可达时按无可用地址处理:

```bash
KVM_ACCESS_FAMILY=
KVM_ACCESS_HOST=
KVM_FALLBACK_REASON=

if test -n "$KVM_IPV4_CIDR"; then
  KVM_ACCESS_FAMILY=ipv4
  KVM_ACCESS_HOST="${KVM_IPV4_CIDR%/*}"
elif test "$KVM_ALLOW_IPV6_FALLBACK" = true && test -n "$KVM_IPV6_CIDR"; then
  KVM_ACCESS_FAMILY=ipv6
  KVM_ACCESS_HOST="${KVM_IPV6_CIDR%/*}"
  KVM_FALLBACK_REASON=ipv4-unavailable-before-deadline
else
  printf 'no validated guest access address; qga=%s address=%s\n' \
    "$KVM_LAST_QGA_STATE" "$KVM_LAST_ADDRESS_STATE" >&2
  exit 4
fi
```

SSH 目标不使用方括号. VM 清单必须记录 `access_family`、`fallback_reason`、`ipv4_ready_at` 和 `ipv6_ready_at`.

## SSH Authentication SSH 认证

SSH key 和密码认证路径互斥. `HostKeyAlias` 使用 `域名-UUID首段`: 同名域重建产生新 UUID 后自动隔离 known_hosts 条目, 从源头避免主机密钥冲突; 若仍出现密钥冲突必须停止, 由用户决定是否清理条目. 首次连接使用 `accept-new`, 就绪检测在截止时间内重试:

```bash
test -n "$GUEST_USER" || { printf 'guest-level checks requested without GUEST_USER\n' >&2; exit 2; }

GUEST_SSH_TARGET="${GUEST_USER}@${KVM_ACCESS_HOST}"
GUEST_HOST_KEY_ALIAS="${KVM_DOMAIN}-${KVM_UUID%%-*}"
GUEST_SSH_COMMON=(
  -o ConnectTimeout=5
  -o StrictHostKeyChecking=accept-new
  -o HostKeyAlias="$GUEST_HOST_KEY_ALIAS"
)

case "$GUEST_AUTH_MODE" in
  ssh-key)
    GUEST_SSH=(ssh "${GUEST_SSH_COMMON[@]}" -o BatchMode=yes)
    if test -n "${GUEST_PRIVATE_KEY:-}" && test "$GUEST_PRIVATE_KEY" != null; then
      GUEST_SSH+=(-i "$GUEST_PRIVATE_KEY")
    fi
    ;;
  password)
    : "${GUEST_PASSWORD_ENV:=KVM_GUEST_PASSWORD}"
    command -v sshpass >/dev/null || { printf 'sshpass missing\n' >&2; exit 2; }
    test -n "${!GUEST_PASSWORD_ENV:-}" || { printf 'password environment is empty\n' >&2; exit 2; }
    export SSHPASS="${!GUEST_PASSWORD_ENV}"
    GUEST_SSH=(sshpass -e ssh "${GUEST_SSH_COMMON[@]}" -o PubkeyAuthentication=no -o PreferredAuthentications=password)
    ;;
  *) printf 'unsupported GUEST_AUTH_MODE=%s\n' "$GUEST_AUTH_MODE" >&2; exit 2 ;;
esac

KVM_SSH_READY_DEADLINE=$((SECONDS + KVM_SSH_READY_WAIT_SECONDS))
while :; do
  if "${GUEST_SSH[@]}" "$GUEST_SSH_TARGET" 'hostname; id -u'; then
    break
  fi
  ((SECONDS < KVM_SSH_READY_DEADLINE)) || { printf 'guest ssh not ready within deadline\n' >&2; exit 5; }
  sleep 5
done
```

密码值只存在于受控环境变量或 secret 来源中, 不写入 YAML、argv 或报告. 密码认证流程结束后执行 `unset SSHPASS`.

## Guest And Memory Evidence 客户机和内存证据

仅当进入客户机内检查时执行本节 (见 Variable Contract 中 `GUEST_USER` 的可选规则). 就绪状态和 guest 布局:

```bash
"${GUEST_SSH[@]}" "$GUEST_SSH_TARGET" \
  'hostname; id -u; cat /etc/machine-id; findmnt -n -o SOURCE,FSTYPE,TARGET /; lsblk -b -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS; df -B1 /'
```

记录客户机 machine-id 和 SSH 主机密钥指纹, 并验证它们与项目 VM 清单中的其它 VM 不重复.

内存证据只读命令:

```bash
"${GUEST_SSH[@]}" "$GUEST_SSH_TARGET" \
  'free -b; vmstat 1 5; dmesg --color=never | grep -iE "oom|out of memory|killed process" || true'
"${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' dommemstat '$KVM_DOMAIN'"
"${KVM_NODE_SSH[@]}" "awk '/MemAvailable:/ {print \$2}' /proc/meminfo"
```

DHCP、QGA、SSH 或存储延迟不能作为内存递增证据.

## Acceptance And Failure 验收和失败

按模式验收:

| 模式 | 完成条件 |
|------|----------|
| inspect/reuse | 用户请求的事实已刷新, 无变更 |
| provision | 源资源未改变, 目标身份独立, 实际状态满足 VM 计划 |
| resize | 用户请求的差异已验证, 或记录为 `already_satisfied` |
| verify | 用户请求的 QGA、地址、SSH 和客户机检查已报告, 无变更 |

退出码约定:

| 退出码 | 含义 |
|--------|------|
| 0 | 本次模式验收通过 |
| 2 | 门禁或校验失败, 安全停止并保留现场 |
| 3 | 变更流程被中断, 需要用户介入决策 (如受控关机超时) |
| 4 | 未获得可用的客户机访问地址 |
| 5 | 客户机 SSH 在截止时间内未就绪 |

失败报告至少包含 `mode`、`failed_gate`、`domain`、`disk`、`last_qga_state`、`last_address_state`、`access_family`、`actual_state` 和 `next_safe_action`. 失败 VM 默认保留; 清理需要单独授权.
