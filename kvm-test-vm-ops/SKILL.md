---
name: kvm-test-vm-ops
description: "Use when provisioning or validating project-scoped test VMs on an authorized KVM/libvirt host using prepared QGA/DHCP templates. Use for cloning, resource or disk changes, guest expansion, address discovery, SSH readiness, and project VM inventory. Not for production VM administration, generic libvirt diagnosis, or OpenStack-managed instances."
---

# KVM Test VM Operations

## Role 角色

根据当前项目和用户请求, 安全地复用、创建、调整或验证 KVM 测试 VM. 只执行所选模式需要的操作, 并对账项目 VM 计划、宿主机、客户机、访问路径和本地 VM 清单.

## Mode Routing 模式路由

| 用户目标 | 模式 (KVM_MODE 取值) | 必读 | 允许的 mutation |
|----------|----------------------|------|-----------------|
| 查看或复用已有 VM | inspect / reuse | [discovery.md](references/discovery.md), [verification.md](references/verification.md) | 无 |
| 创建项目测试 VM | provision | 全部参考文档 | 克隆和已确认 VM 计划内的配置 |
| 调整已有 VM 资源或磁盘 | resize (即 reconfigure) | [discovery.md](references/discovery.md), [clone-and-resize.md](references/clone-and-resize.md), [verification.md](references/verification.md) | 仅用户要求的调整; 离线变更完成后允许一次受控关机/开机 |
| 只验证 QGA、IP、SSH 或客户机状态 | verify (即 verify-only) | [discovery.md](references/discovery.md), [verification.md](references/verification.md) | 无 |
| 删除或清理 | cleanup (不进入参考文档) | 先重新 Review | 仅单独明确授权的资源 |

合法 `KVM_MODE` 取值仅为 `inspect`, `reuse`, `provision`, `resize`, `verify`.

## Safety Gate 安全门禁

- 先确定目标项目和模式, 再读取对应参考文档. 存在多个项目根目录候选时, 先请求用户选择.
- 只使用用户授权的 SSH 节点、模板、VM 和凭据来源. 不操作生产 VM 或 OpenStack 管理的实例.
- `provision` 前确认 VM 计划; 变更前刷新模板和域状态、磁盘身份和容量、宿主机内存和存储空间以及权限.
- 不修改源模板或源磁盘. 遇到多磁盘、NVRAM、未泛化模板或不支持的客户机布局时必须停止并报告.
- 需要关机的变更只使用优雅 `virsh shutdown` 并限时等待, 不使用 `destroy`; 超时时停止并交由用户决策.
- 20 GiB 磁盘、2 vCPU / 1 GiB RAM、512 MiB 内存步长和 4 GiB 上限仅为可覆盖的默认值.
- IPv4 是首选. 只有 IPv4 在策略内不可用, 且目标 VM 存在与目标 MAC 关联、从执行机可路由的非链路本地 IPv6 时, 才使用 IPv6 保底访问.
- 密码不得进入 Git 跟踪文件、argv、报告或普通日志. 失败后保留资源; 清理需要单独授权.

## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| 项目标识、架构指纹、状态刷新、节点和模板发现 | [references/discovery.md](references/discovery.md) |
| 克隆、计算资源、磁盘和客户机文件系统变更 | [references/clone-and-resize.md](references/clone-and-resize.md) |
| QGA、IPv4/IPv6、SSH、内存证据和验收 | [references/verification.md](references/verification.md) |
| 通用环境记录结构和刷新规则 | [environment-discovery.md](environment-discovery.md) |
| 项目根目录 `environment.local.yaml` 模板 | [environment.example.yaml](environment.example.yaml) |
| 本地 mock 验证命令门禁和顺序 | [tests/test_command_gates.py](tests/test_command_gates.py) |

## Workflow 工作流

1. 解析项目根目录和模式, 读取实际存在的项目入口文件, 生成或验证 VM 计划.
2. 读取项目根目录的本地状态, 仅在项目标识和架构指纹兼容时复用稳定字段.
3. 按模式读取参考文档. 变更前重新确认授权并执行全部预检门禁.
4. 执行后读取实际状态并对账。纯 `inspect/reuse/verify` 默认只报告, 不写项目文件; 创建或调整任务在已确认范围内更新项目 VM 清单。另有记录授权时可写回只读检查结果, 不将远端只读等同于本地可写.

## Completion Gate 完成门禁

- inspect/reuse: 用户请求的事实已刷新, 未发生变更.
- provision: 源资源未修改, 目标身份独立, 实际状态满足已确认的 VM 计划.
- resize/reconfigure: 只完成用户请求的差异; 已满足时记录 `already_satisfied`.
- verify-only: 只报告用户请求的就绪状态; 不要求克隆、扩容或文件系统变更.
- 所有模式: IPv4/IPv6 状态、失败证据和项目本地记录已对账, 无凭据泄露.

## Execution Feedback 执行反馈

执行本 skill 时, 若出现说明不清、重复尝试、权限或工具阻塞、路径失效、QGA/SSH 绕行或额外探测, 任务结束时必须报告触发位置、问题现象、实际影响、临时处理和可复用的优化建议. 没有实际问题时不要输出空反馈. 所有凭据、IP 以外的用户敏感数据和客户机内容必须脱敏.
