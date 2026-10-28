# Environment Discovery Record

## Purpose 用途

本文件定义通用环境记录结构和刷新规则. 真实主机名、IP、模板、路径、VM 和凭据来源只写入当前项目根目录的 `environment.local.yaml` 和 `vm-inventory.local.yaml`.

## Project Identity 项目标识

每个项目记录以下字段:

| 字段 | 规则 |
|------|------|
| `project.id` | 稳定且可读的项目标识 |
| `project.root` | 用户确认的项目根目录; monorepo 存在歧义时不得猜测 |
| `project.git_revision` | 当前 Git revision; 非 Git 项目标记为 `not-applicable` |
| `project.architecture_fingerprint` | 对本次实际读取的架构证据生成 hash |
| `project.verified_at` | 带时区的 ISO 8601 时间戳 |

## Stable Fields 稳定字段

验证项目标识兼容后可以复用:

- 已授权的 SSH alias、用户和 libvirt URI
- 已知宿主机身份和工具能力
- storage pool 和路径命名
- 模板身份和预期客户机 OS 元数据
- 默认资源和访问策略

## Volatile Fields 动态字段

以下字段在每次变更前强制刷新, 不依赖旧 timestamp:

- 模板和域的电源状态以及 UUID
- 目标是否存在、磁盘 source/target 和容量
- 宿主机可用内存和存储空间
- MAC、网卡接口、IPv4、IPv6 和 SSH 就绪状态
- QGA 状态和客户机文件系统布局

## Freshness Result 刷新结果

每次使用 local state 时记录:

```text
field | previous value | current value | checked_at | source | status
```

状态只使用 `current`、`changed`、`missing`、`incompatible` 或 `not-applicable`. 项目标识或架构指纹不兼容时, 不得隐式复用旧 VM 计划.

## Variable Mapping 变量映射

执行前把兼容的记录字段加载为环境变量; 缺少必需变量时按 discovery 契约停止, 不猜测节点或凭据。`defaults.*` 只提供 `provision` 的创建默认值; `resize` 的 `PLAN_*` 仅注入本次明确确认的字段, 未指定项留空并保留当前持久配置, 不自动导入创建默认值:

| 记录字段 | 环境变量 |
|----------|----------|
| `node.ssh_alias` 或节点地址 | `KVM_NODE` |
| `node.ssh_user` | `KVM_SSH_USER` |
| `node.libvirt_uri` | `LIBVIRT_URI` |
| `guest_access.username` | `GUEST_USER` |
| `guest_access.auth_mode` | `GUEST_AUTH_MODE` |
| `guest_access.private_key` | `GUEST_PRIVATE_KEY` |
| `guest_access.password_env` | `GUEST_PASSWORD_ENV` (存放密码值的变量名) |
| `policy.ipv4_wait_seconds` | `KVM_IPV4_WAIT_SECONDS` |
| `policy.allow_ipv6_fallback` | `KVM_ALLOW_IPV6_FALLBACK` |
| `policy.shutdown_wait_seconds` | `KVM_SHUTDOWN_WAIT_SECONDS` |
| `defaults.default_vcpus` | `PLAN_VCPUS` |
| `defaults.default_memory` | `PLAN_MEMORY_KIB` (G 转 KiB) |
| `defaults.memory_max` | `PLAN_MEMORY_MAX_KIB` (G 转 KiB) |
| `defaults.memory_step` | `PLAN_MEMORY_STEP_KIB` (G 转 KiB) |
| `defaults.target_virtual_size` | `PLAN_DISK_BYTES` (G 转字节) |

## Security 安全

- 项目本地状态文件权限必须为 `0600`.
- Git 项目必须通过 `git check-ignore` 验证两个本地状态文件已忽略.
- Git 跟踪的 skill、报告和普通日志不得包含 password、private key 或 secret 值.
- 共享 skill 不保存任何真实测试节点或 VM 清单.
