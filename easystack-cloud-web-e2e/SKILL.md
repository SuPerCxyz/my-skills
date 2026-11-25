---
name: easystack-cloud-web-e2e
description: "Use when executing or optimizing EasyStack Cloud Web UI operations with agent-browser: login, page probes, resource actions, selectors, batching, state verification and evidence capture."
---

# EasyStack Cloud Web E2E

## Scope Boundary 适用边界

负责 EasyStack Cloud Web 的页面探索、原子操作、状态回读、取证和操作库优化。
单次登录、查询和资源操作可直接使用本 skill, 按目标核对会话、项目及必要资源。

用户要求执行用例或测试计划时, 通过当前客户端加载 `easystack-release-test` 做用例编排、
预检和汇总。发布测试回调本 skill 时, 只执行传入的已授权 UI 操作并返回观察与证据。
需要准备发布测试的项目、账号或配额时, 转接发布测试的环境预检。遇到能力缺口时说明限制,
按现有授权继续可完成的任务。

## Hard Rules 执行硬规则

- 执行前读取当前 `agent-browser` 操作说明, 只用 `agent-browser` 操作 UI。安装、连接和
  selector 规则见 [连接](connection.md) 和 [交互](interactions.md)。
- 在同一稳定页面批量执行关联动作, 在页面变化或异步边界回读。确认项目和资源身份,
  使用 Observe -> Act -> Wait -> Verify 验证到实际业务终态。
- 使用 [原子操作约定](patterns.md#operation-contract-原子操作调用约定)。`ok: true` 表示稳定
  终态成功。中间状态报告 `terminal: false`, 提交不明时先回读并按有限重试规则处理。
- 按 [执行说明](execution.md) 返回最后观察、实际终态、资源 ID 和证据。删除、关机、解绑
  等有副作用操作按真实对象和已确认授权执行。
- 优先用 `ready-validated`, `ready-template` 现场确认后执行, `planned` 仅作能力线索。
  可复用操作先记入 `skill_improvements`, 获得维护授权后再更新操作库和索引。

## Entry Selection 入口选择

| 用户目标 | 先读 |
|----------|------|
| 用途、示例和快速开始 | [README.md](README.md) |
| 登录、环境、会话复用 | [connection.md](connection.md) |
| 页面路径、菜单入口 | [navigation.md](navigation.md) |
| 操作、终态验证和技术取证 | [execution.md](execution.md) |
| 组件交互 helper | [interactions.md](interactions.md) |
| 当前控制台探索结果 | [patterns/current-console-discovery.md](patterns/current-console-discovery.md) |
| 原子操作约定及等待 | [patterns.md](patterns.md) |
| 资源关系和联动 | [relationships.md](relationships.md) |

## Atomic Operations 原子操作库

| 资源域 | 文档 |
|--------|------|
| 登录前置 | [patterns/login.md](patterns/login.md) |
| 实例 | [patterns/instance-ops.md](patterns/instance-ops.md) |
| 云硬盘 | [patterns/volume-ops.md](patterns/volume-ops.md) |
| VM 镜像与容器镜像的不同契约 | [patterns/image-ops.md](patterns/image-ops.md) |
| 网络 | [patterns/network-ops.md](patterns/network-ops.md) |
| 页面只读探测 | [patterns/page-probes.md](patterns/page-probes.md) |
| 清理资源编排 | [patterns/cleanup-resources.md](patterns/cleanup-resources.md) |
| 常用操作索引 | [patterns/quick-reference.md](patterns/quick-reference.md) |
| 操作模板 | [patterns/operation-template.md](patterns/operation-template.md) |
| 平台信息和主路径 | [patterns/platform-info.md](patterns/platform-info.md) |
| 校验 operation 终态语义 | [scripts/validate-patterns.py](scripts/validate-patterns.py) |
| 离线回归与覆盖边界 | [tests/README.md](tests/README.md) |

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
| 容器镜像页面及 VM 镜像路由边界 | [image/image.md](image/image.md) |
| 网络 | [network/network.md](network/network.md) |
| 虚拟网卡 | [network/vnic.md](network/vnic.md) |
| 路由器 | [network/router.md](network/router.md) |
| 浮动 IP | [network/floating-ip.md](network/floating-ip.md) |

## Decision Path 决策路径

1. 登录、创建、挂载、绑定或查询时, 读取实际操作和目标资源对应的入口。
2. 用户目标为明确用例、测试计划或发布验证时, 加载 `easystack-release-test`。
3. 页面字段、按钮和表格检查从 [页面探测](patterns/page-probes.md) 与页面知识库开始。
4. 稳定的可复用操作按 [操作模板](patterns/operation-template.md) 编写, 同步
   [常用操作索引](patterns/quick-reference.md)。

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
