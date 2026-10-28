# Discovery

## Contents 目录

- [Mode And Project 模式和项目](#mode-and-project-模式和项目)
- [Architecture Evidence 架构证据](#architecture-evidence-架构证据)
- [Local State 本地状态](#local-state-本地状态)
- [Node And Libvirt 节点和 Libvirt](#node-and-libvirt-节点和-libvirt)
- [Existing VM Discovery 已有 VM 发现](#existing-vm-discovery-已有-vm-发现)
- [Template Discovery 模板发现](#template-discovery-模板发现)
- [Freshness Gate 刷新门禁](#freshness-gate-刷新门禁)

## Mode And Project 模式和项目

先确定 `KVM_MODE` 和 `PROJECT_ROOT`. 合法模式为 `inspect`、`reuse`、`provision`、`resize` 或 `verify`. `cleanup` 必须重新 Review, 不进入本参考文档.

```bash
: "${KVM_MODE:?set KVM_MODE}"
case "$KVM_MODE" in
  inspect|reuse|provision|resize|verify) ;;
  *) printf 'unsupported KVM_MODE=%s\n' "$KVM_MODE" >&2; exit 2 ;;
esac

PROJECT_ROOT="${PROJECT_ROOT:-$(pwd -P)}"
test -d "$PROJECT_ROOT" || { printf 'invalid PROJECT_ROOT=%s\n' "$PROJECT_ROOT" >&2; exit 2; }
```

当前目录属于 monorepo 或存在多个项目候选时, 不使用 Git 根目录猜测目标; 先请求用户指定 `PROJECT_ROOT`.

## Architecture Evidence 架构证据

先列出项目中实际存在的候选入口. 不预设任何技术、部署方式或 VM role.

```bash
rg --files "$PROJECT_ROOT" \
  -g '!*/*' \
  -g '!environment.local.yaml' -g '!vm-inventory.local.yaml' \
  | sort
```

先读取实际存在的顶层入口, 再只跟随其中明确引用的架构或部署配置、测试入口或脚本. 不扫描未引用目录, 不运行宽泛关键词搜索. 将选中的文件放入 `ARCH_FILES`:

```bash
ARCH_FILES=()
# Example only after the file is observed:
# ARCH_FILES+=("$PROJECT_ROOT/README.md")
((${#ARCH_FILES[@]} > 0)) || { printf 'no architecture evidence selected\n' >&2; exit 2; }

for architecture_file in "${ARCH_FILES[@]}"; do
  test -f "$architecture_file" || { printf 'missing evidence=%s\n' "$architecture_file" >&2; exit 2; }
done

# 指纹仅由文件内容哈希组成, 与绝对路径和读取顺序无关
ARCHITECTURE_FINGERPRINT="$(
  printf '%s\0' "${ARCH_FILES[@]}" \
    | xargs -0 sha256sum \
    | awk '{print $1}' \
    | sort \
    | sha256sum \
    | awk '{print $1}'
)"

if git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PROJECT_REVISION="$(git -C "$PROJECT_ROOT" rev-parse HEAD)"
else
  PROJECT_REVISION=not-applicable
fi
```

VM 计划至少包含 `purpose`、`os_requirement`、`template_requirement`、`vcpus`、`memory`、`memory_max`、`disk_target`、`network`、`access` 和 `responsibility`. 多个关键解释并存时, 先请求一次合并确认.

## Local State 本地状态

项目状态文件固定在 `PROJECT_ROOT`:

```bash
ENVIRONMENT_FILE="$PROJECT_ROOT/environment.local.yaml"
INVENTORY_FILE="$PROJECT_ROOT/vm-inventory.local.yaml"

if git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$PROJECT_ROOT" check-ignore -q "${ENVIRONMENT_FILE#$PROJECT_ROOT/}" || {
    printf 'environment.local.yaml is not ignored by Git\n' >&2
    exit 2
  }
  git -C "$PROJECT_ROOT" check-ignore -q "${INVENTORY_FILE#$PROJECT_ROOT/}" || {
    printf 'vm-inventory.local.yaml is not ignored by Git\n' >&2
    exit 2
  }
fi

for state_file in "$ENVIRONMENT_FILE" "$INVENTORY_FILE"; do
  if test -e "$state_file"; then
    test "$(stat -c '%a' "$state_file")" = 600 || {
      printf 'unsafe mode: %s\n' "$state_file" >&2
      exit 2
    }
  fi
done
```

只有 `project.root`、`project.git_revision` 和 `project.architecture_fingerprint` 与当前项目兼容时, 才复用 VM 计划. `inspect` 和 `verify` 可以读取不兼容记录作为线索, 但不得将其视为当前事实.

## Node And Libvirt 节点和 Libvirt

从用户授权信息和 `environment.local.yaml` 加载以下变量. 变量值为空时立即停止:

```bash
: "${KVM_NODE:?load authorized KVM_NODE}"
: "${KVM_SSH_USER:?load authorized KVM_SSH_USER}"
: "${LIBVIRT_URI:=qemu:///system}"

KVM_SSH_TARGET="${KVM_SSH_USER}@${KVM_NODE}"
KVM_NODE_SSH=(ssh -o BatchMode=yes -o ConnectTimeout=5 "$KVM_SSH_TARGET")
```

只读验证:

```bash
"${KVM_NODE_SSH[@]}" 'hostname -f; command -v virsh virt-clone qemu-img'
"${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' uri"
"${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' version"
"${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' list --all"
```

任一命令失败时停止. 不猜测替代节点、用户、端口或 URI.

## Existing VM Discovery 已有 VM 发现

`inspect`、`reuse`、`resize` 和 `verify` 模式必须从项目 VM 清单或用户请求中获得明确的域:

```bash
: "${KVM_DOMAIN:?set requested KVM_DOMAIN}"
[[ "$KVM_DOMAIN" =~ ^[A-Za-z0-9._:-]+$ ]] || { printf 'unsafe domain name\n' >&2; exit 2; }

KVM_DOMAIN_INFO="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' dominfo '$KVM_DOMAIN'"
)"
KVM_DOMAIN_BLOCKS="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domblklist '$KVM_DOMAIN' --details"
)"
KVM_DOMAIN_INTERFACES="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domiflist '$KVM_DOMAIN'"
)"
KVM_UUID="$(awk '/^UUID:/ {print $2}' <<<"$KVM_DOMAIN_INFO")"
KVM_MAC="$(awk 'NR>2 && $5!="" {print $5; exit}' <<<"$KVM_DOMAIN_INTERFACES")"
test -n "$KVM_UUID" && test -n "$KVM_MAC" || { printf 'domain identity incomplete\n' >&2; exit 2; }
```

`resize` 必须明确 `KVM_DISK_TARGET`; 从 `domblklist` 验证唯一来源:

```bash
if test "$KVM_MODE" = resize; then
  : "${KVM_DISK_TARGET:?set requested KVM_DISK_TARGET}"
  mapfile -t KVM_MATCHED_DISKS < <(
    awk -v target="$KVM_DISK_TARGET" '$2=="disk" && $3==target && $4!="-" {print $4}' \
      <<<"$KVM_DOMAIN_BLOCKS"
  )
  ((${#KVM_MATCHED_DISKS[@]} == 1)) || { printf 'disk target is ambiguous\n' >&2; exit 2; }
  KVM_DEST_DISK="${KVM_MATCHED_DISKS[0]}"
fi
```

## Template Discovery 模板发现

只有 `provision` 模式需要模板. 从实际域列表和 VM 计划中选择后设置变量:

```bash
: "${KVM_TEMPLATE:?set selected KVM_TEMPLATE}"
[[ "$KVM_TEMPLATE" =~ ^[A-Za-z0-9._:-]+$ ]] || {
  printf 'unsafe template name\n' >&2
  exit 2
}

KVM_TEMPLATE_STATE="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domstate '$KVM_TEMPLATE'" | xargs
)"
test "$KVM_TEMPLATE_STATE" = 'shut off' || {
  printf 'template must be shut off, actual=%s\n' "$KVM_TEMPLATE_STATE" >&2
  exit 2
}

KVM_BLOCKS="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' domblklist '$KVM_TEMPLATE' --details"
)"
mapfile -t KVM_DISK_ROWS < <(
  printf '%s\n' "$KVM_BLOCKS" | awk '$2=="disk" && $4!="-" {print $1 " " $3 " " $4}'
)
((${#KVM_DISK_ROWS[@]} == 1)) || {
  printf 'single-disk workflow only, disk_count=%s\n' "${#KVM_DISK_ROWS[@]}" >&2
  exit 2
}
read -r KVM_DISK_TYPE KVM_DISK_TARGET KVM_SOURCE_DISK <<<"${KVM_DISK_ROWS[0]}"
test "$KVM_DISK_TYPE" = file || {
  printf 'file-backed template disk required, actual=%s\n' "$KVM_DISK_TYPE" >&2
  exit 2
}

KVM_TEMPLATE_XML="$(
  "${KVM_NODE_SSH[@]}" "virsh --connect '$LIBVIRT_URI' dumpxml '$KVM_TEMPLATE'"
)"
grep -q 'org.qemu.guest_agent.0' <<<"$KVM_TEMPLATE_XML" || {
  printf 'template lacks QGA channel\n' >&2
  exit 2
}
if grep -q '<nvram' <<<"$KVM_TEMPLATE_XML"; then
  printf 'NVRAM clone requires a separate reviewed path\n' >&2
  exit 2
fi
```

使用项目本地的模板元数据, 或节点上的 `virt-inspector` 验证客户机 OS. 选择 `virt-inspector` 时先确认工具存在, 再核对检测结果与 `os_requirement`:

```bash
"${KVM_NODE_SSH[@]}" 'command -v virt-inspector'
"${KVM_NODE_SSH[@]}" "virt-inspector --no-applications --no-x11 '$KVM_SOURCE_DISK'"
```

无法验证 OS 要求或模板泛化状态时停止, 不按名称猜测. `virt-sysprep` 只能在克隆磁盘上经单独授权执行.

## Freshness Gate 刷新门禁

稳定字段可以在项目标识兼容时复用. 以下动态事实在变更前总是重新读取:

```text
template/domain state, destination existence, disk source/target/capacity,
host free memory, storage free bytes, MAC/interface, QGA, IPv4/IPv6, SSH,
guest root layout and required tools
```

每次检查报告带时区的 ISO 8601 时间戳。仅在本地记录写入已获授权时更新状态文件, 严格只读模式不落盘. 详细结构见 [environment-discovery.md](../environment-discovery.md).
