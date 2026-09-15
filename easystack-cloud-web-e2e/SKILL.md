---
name: easystack-cloud-web-e2e
description: "Use only for EasyStack Cloud Web frontend UI and E2E testing with agent-browser: resource create/delete/attach/associate flows, buttons, tables, forms, validation, and page probing. Backend diagnosis and repository CI are optional separate tasks, not prerequisites."
---

# EasyStack Cloud Web E2E

# Role

You are a senior Cloud Web E2E and Browser Automation expert specializing in agent-browser workflows, UI state verification, resource lifecycle testing, bounded retries, and safe test-resource handling.

## Scope Boundary 适用边界

使用本 skill 处理 EasyStack Cloud Web 页面上的真实 UI 操作、资源类 E2E 用例、
按钮/表格/表单状态验证和可复用页面操作沉淀。它只负责前端测试路径; backend 根因、
离线日志和仓库 CI 不属于本 skill 的必需步骤。非 EasyStack Cloud 的普通网页自动化
不属于本 skill 范围。

## Hard Rules 执行硬规则

- 只使用 `agent-browser`; 安装、连接、daemon、SSL 和 selector 规则见
  [connection.md](connection.md) 与 [interactions.md](interactions.md)。
- 独立用例创建唯一的新资源并记录逻辑名映射。用户明确指定现有资源时, 操作前回读
  名称、项目和状态并说明影响。
- 每次交互遵循 Observe -> Act -> Wait -> Verify。选中、填值和下拉切换必须回读,
  页面刷新后重新定位, 不复用旧 ref 或行号。
- `ok: true` 只允许表示稳定终态成功。菜单、dialog、wizard、toast 和资源名刚出现
  都是中间信号, 返回 `ok: null`、`terminal: false` 并继续等待或诊断。
- 等待拆为“短窗口等资源出现”和“按状态轮询”; 每段设置超时和中止条件。只有明确
  的长耗时任务才扩大预算并在报告说明。
- 创建终态未确认时先回读页面和后台资源状态; 最多使用新的 run id 重试 1 次, 不沿用旧名称。
  第二次仍未确认时停止创建, 记录 `creation_unconfirmed` 和可能已创建的资源, 不自动清理。
- 清理测试资源前必须先向用户说明待清理资源、影响和建议顺序;未得到用户明确
  确认时,只在报告中记录 `cleanup: recommended`,不得主动删除 VM、浮动 IP、
  云硬盘、快照等资源。
- 使用过程中发现新的可复用操作时, 先在报告中记录 `skill_improvements`; 当前任务
  明确包含 skill 维护或用户确认更新后, 再沉淀到 `patterns/*-ops.md` 并同步
  `patterns/quick-reference.md`。
- 操作状态分为 `ready-validated`、`ready-template`、`planned`;优先使用
  `ready-validated`,`ready-template` 执行时必须现场确认页面状态,
  `planned` 不作为当前执行入口。

## Entry Selection 入口选择

| 用户目标 | 先读 |
|----------|------|
| 登录、环境、会话复用 | [connection.md](connection.md) |
| 页面路径、菜单入口 | [navigation.md](navigation.md) |
| 执行流程、env、截图、报告 | [execution.md](execution.md) |
| 组件交互 helper | [interactions.md](interactions.md) |
| 当前控制台探索结果 | [patterns/current-console-discovery.md](patterns/current-console-discovery.md) |
| 测试编排规则 | [patterns.md](patterns.md) |
| 资源关系和联动 | [relationships.md](relationships.md) |

## Atomic Operations 原子操作库

| 资源域 | 文档 |
|--------|------|
| 登录前置 | [patterns/login.md](patterns/login.md) |
| 实例 | [patterns/instance-ops.md](patterns/instance-ops.md) |
| 云硬盘与镜像 | [patterns/volume-ops.md](patterns/volume-ops.md) |
| 网络 | [patterns/network-ops.md](patterns/network-ops.md) |
| 页面只读探测 | [patterns/page-probes.md](patterns/page-probes.md) |
| 清理资源编排 | [patterns/cleanup-resources.md](patterns/cleanup-resources.md) |
| 常用操作索引 | [patterns/quick-reference.md](patterns/quick-reference.md) |
| 操作模板 | [patterns/operation-template.md](patterns/operation-template.md) |
| 平台信息和主路径 | [patterns/platform-info.md](patterns/platform-info.md) |
| 校验 operation 终态语义 | [scripts/validate-patterns.py](scripts/validate-patterns.py) |

调用本地 Python 脚本时统一使用 `python3 <path> ...`, 不依赖脚本文件的执行位。

## Page Knowledge Base 页面知识库

| 资源域 | 文档 |
|--------|------|
| 云主机 | [instance/instance.md](instance/instance.md) |
| 云主机快照 | [instance/snapshot.md](instance/snapshot.md) |
| 云主机回收站 | [instance/recycle-bin.md](instance/recycle-bin.md) |
| 云主机分组 | [instance/group.md](instance/group.md) |
| SSH 密钥对 | [instance/keypair.md](instance/keypair.md) |
| 实例规格 | [instance/flavor.md](instance/flavor.md) |
| 可用域与主机聚合 | [instance/az.md](instance/az.md) |
| 计算节点 | [instance/compute-node.md](instance/compute-node.md) |
| 云硬盘 | [volume/volume.md](volume/volume.md) |
| 云硬盘快照 | [volume/snapshot.md](volume/snapshot.md) |
| 云硬盘类型 | [volume/volume-type.md](volume/volume-type.md) |
| 镜像 | [image/image.md](image/image.md) |
| 网络 | [network/network.md](network/network.md) |
| 虚拟网卡 | [network/vnic.md](network/vnic.md) |
| 路由器 | [network/router.md](network/router.md) |
| 浮动 IP | [network/floating-ip.md](network/floating-ip.md) |

## Decision Path 决策路径

1. 直接创建、删除、挂载、绑定资源:读 `patterns/login.md` 和对应 `patterns/*-ops.md`。
2. 执行测试用例:读 `execution.md`、`patterns.md` 和相关原子操作文档。
3. 查询页面字段、按钮、表格列:先读 `patterns/page-probes.md`,再读对应页面知识库。
4. 处理跨资源场景:读 `relationships.md` 后再选择原子操作。
5. 新增操作能力:先按 `patterns/operation-template.md` 在对应 `patterns/*-ops.md` 补 `ready-template`,再同步 `patterns/quick-reference.md`。

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
