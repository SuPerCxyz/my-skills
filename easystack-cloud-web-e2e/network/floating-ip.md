# Floating Ip

Use this file when the UI task specifically involves floating IP list fields, allocation, association, release, or related assertions. For reusable action sequences, prefer [patterns/network-ops.md](../patterns/network-ops.md).

## Scenario Status 场景状态

以下是基于现有页面知识的场景规范, 不是已运行的自动化结果. 使用 agent-browser,
先核实项目与精确资源身份, 复用对应 patterns 操作及 interactions helper.
`planned` 表示缺少已确认的可调用操作或字段, 先现场只读发现, 不编造入口/参数.
场景执行不要求先修改 skill; 缺少必要控件或权限时报告未验证及恢复点.
清理只针对本用例记录的实际资源, 按已有准确授权执行; 未授权时只列清单和依赖顺序.
任何提交未确认都先回读, 不因超时重复提交或自动删除.

## Page Information 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/ens/floatingIPs` |
| 导航路径 | Network → Floating IP |
| 页面标题 | Floating IP |

## Page Description 页面说明

浮动 IP(Floating IP)用于管理云平台中的公网 IP 地址。用户可在此页面分配、释放、绑定和解绑浮动 IP,为云主机提供公网访问能力。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Apply For IP To Project | `agent-browser find text "Apply For IP To Project" click` | 始终可用 |
| Release Floating IPs | 顶部批量按钮 | 默认禁用,选中 1+ 行后可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## Status Filter 状态过滤下拉

定位方式:`nz-select`(含 "All Status" 文本)

| 状态值 | 说明 |
|--------|------|
| All Status | 默认,显示所有状态 |
| Bound | 已绑定(绑定到某个端口/实例) |
| Unbound | 未绑定(空闲状态) |

## Filter Fields 过滤器字段

定位方式:`input[placeholder="Click here for filters."]`

| 过滤字段 |
|----------|
| Floating IP / Name |
| Description |
| Status |
| Port |
| Domain |
| Project |
| Created At |

## Table Columns 表格列

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| IP Address | ✅ | 浮动 IP 地址 |
| Tags | ❌ | 标签 |
| Related router | ❌ | 关联路由 |
| Attach Resource | ✅ | 已绑定资源,如 `Instance: <name>` |
| Bandwidth(Mbps) | ✅ | 带宽 |
| Floating IP Pool | ✅ | 资源池 |
| Domain/Project | ❌ | 租户/项目 |
| Creation Time | ✅ | 创建时间 |
| Action | ❌ | 行内动作列 |

### Observed Row Actions 行内动作实测

- 已绑定资源行:
  `Release Floating IPs`、`Disassociate`、`Update Bandwidth`、`More`
- 未绑定资源行:
  `Release Floating IPs`、`Bind to resource`、`Update Bandwidth`、`More`

## Selection And Batch Actions 勾选与批量操作

- 未勾选时,顶部 `Release Floating IPs` disabled
- 勾选单条后,顶部 `Release Floating IPs` enabled
- 本页同时存在“顶部批量动作”和“行内动作”,不要混淆两类入口

## Permissions 权限限制

- 以当前云管理员账号在某些浮动 IP 上点击 `Bind to resource` 时,页面可能不会弹出
  绑定表单,而是直接提示:
  `Please do this by re-logging into the console as the project administrator/user to which the resource belongs`
- 这属于产品权限反馈,不应误判为自动化 click 失败。

## Setup 列配置

可配置列:Floating IP / Name、Description、Port、Status、Created At

按钮:Restore Defaults、Select All、Cancel、Confirm

## Allocate Floating IP 弹窗

标题:**Apply For IP To Project**

> ⚠️ 注意:由于物理节点上承载公网流量的物理网卡的带宽限制,浮动 IP 的最大带宽设置不能大于 1000 Mbps。

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Project | ✅ | `nz-select` 下拉 | 选择目标 Project, 默认值以当前会话为准 |
| Resource Pool | ✅ | `nz-select` 下拉 | 选择浮动 IP 资源池,默认 public_net_1 0/253 |
| Floating IP | ❌ | `input` 文本输入 | 占位符:"Please enter IP address.",可选填写特定 IP |
| Bandwidth | ✅ | 数字输入框 | 单位 Mbps,默认 1,范围 1-1000 |

弹窗按钮:Cancel、Allocate

> 可通过 "Add IP address." 按钮添加多个 IP 地址。不填写 Floating IP 时系统自动分配。

## Pagination 分页

| 项目 | 值 |
|------|-----|
| 默认每页 | 10 条 |
| 每页定位方式 | 下拉,"10 / page" |
| 总数显示 | "Total N items, last updated [timestamp]" |
| 翻页 | 上一页/下一页、页码按钮 |

## Test Cases 测试用例

### TC-FIP001: 验证浮动 IP 页面加载

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 目标项目明确 |
| 操作 | 打开 /ens/floatingIPs, 等待列表与项目范围可回读 |
| 可观察断言与恢复 | IP/Attach Resource/Action列完整, 不将权限反馈当click失败 |


### TC-FIP002: Allocate Floating IP 弹窗验证

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 只探测分配弹窗, 不提交 |
| 操作 | 点击Apply For IP To Project, 核对Project/Resource Pool/Bandwidth与可选IP字段, Cancel |
| 可观察断言与恢复 | 入口和弹窗主按钮Allocate区分, 必填状态正确且未分配新IP |


### TC-FIP003: 状态过滤验证

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例IP/项目已记录 |
| 操作 | 切换Bound/Unbound筛选并核对Attach Resource, 结束清除 |
| 可观察断言与恢复 | 实际附件状态与筛选一致, 不用空列表证明释放成功 |


### TC-FIP004: 按名称过滤浮动 IP

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例精确IP及项目明确 |
| 操作 | 用真实IP/Name筛选提交条件, 核实IP单元格完全相等后清除 |
| 可观察断言与恢复 | IP如192.0.2.1不能命中192.0.2.10, 项目正确且清除条件后恢复列表 |
