# Recycle Bin

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
| URL | `https://<IP>/eec/instance-recycle-bin` |
| 导航路径 | Computing → Instance Recycle Bin |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

云主机回收站用于防止误操作导致的数据丢失。删除云主机时,默认将其移入回收站而非直接删除。用户可在回收站中恢复或永久删除实例。

> **生命周期**:实例移入回收站后,浮动 IP 和数据磁盘会自动解绑。实例保留 **24 小时**,超时后自动强制删除。

## Deletion Policy 从云主机页面删除时的策略选择

从云主机列表删除实例时,弹窗提供两种删除策略(单选):

| 策略 | 说明 |
|------|------|
| Remove to Recycle Bin(默认) | 移入回收站,可恢复 |
| Force Delete | 立即强制删除,不可恢复 |

> ⚠️ Force Delete 会同时删除实例创建的 vNIC。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Restore Instance | 工具栏 icon 按钮 | 默认禁用,选中 1+ 行后可用 |
| Force Delete Instance | 工具栏 icon 按钮 | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 无数据时禁用,有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## Status Filter 状态过滤下拉

定位方式:`nz-select`(含 "All Status" 文本)

| 状态值 | 说明 |
|--------|------|
| All Status | 默认,显示所有状态 |
| Wait for Delete | 等待删除 |
| Restoring | 正在恢复 |
| Deleting | 正在删除 |

## Advanced Filters 高级过滤器字段

定位方式:`input[placeholder="Click here for filters."]`

| 过滤字段 |
|----------|
| Name |
| Availability Zone |
| Node |
| Tags |
| Flavor:vCPU |
| Flavor:RAM |
| Flavor:DISK |
| Flavor:GPU |
| Boot Source |
| Private IP |
| Floating IP |
| Domain |
| Project |
| Estimated Delete Time |

## Table Columns 表格列(8 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 实例名称 |
| Availability Zone / Node | ❌ | 可用域和计算节点(两行显示) |
| Status | ✅ | 实例状态 |
| Flavor / Boot Source | ❌ | 规格和启动源(两行显示) |
| IP Address | ❌ | 私网 IP / 浮动 IP |
| Domain / Project | ❌ | 域名和项目(两行显示) |
| Estimated Delete Time | ✅ | 预计自动删除时间 |

### Example Row 示例数据行

```
Name: <INSTANCE_NAME>
Availability Zone / Node: <AZ> / <COMPUTE_NODE>
Status: Wait for Delete
Flavor / Boot Source: 1C / 1.0GiB / 1GiB / TestVM
IP Address: (Private IP) <PRIVATE_IP>
Domain / Project: <DOMAIN> / <PROJECT>
Estimated Delete Time: <LOCAL_TIME>
```

## Setup 列配置

可配置列:Name、Availability Zone / Node、Status、Flavor / Boot Source、IP Address、Domain / Project、Estimated Delete Time

按钮:Restore Defaults、Select All、Cancel、Confirm

## Restore Instance 确认弹窗

| 元素 | 说明 |
|------|------|
| 标题 | Restore Instance |
| 描述 | "The amount of instance these will be restored is: N" |
| 补充说明 | "After the instances restored, you can view and manage them in the Instance page." |
| 表格列 | Name(可排序)、Estimated Delete Time(可排序) |
| 按钮 | Cancel、Restore Instance |

## Force Delete Instance 确认弹窗

| 元素 | 说明 |
|------|------|
| 标题 | Force Delete Instance |
| 警告 | "After the instance is forcibly deleted, it cannot be recovered. Please proceed with caution." |
| 补充 | "The vNICs created with the instance will also be deleted automatically." |
| 表格列 | Name(可排序)、Root Disk(可排序) |
| Root Disk 信息 | "Quantity: N, Set to delete with instance: N" |
| 说明 | Root Disk 删除行为说明、Data Disk 不会被删除 |
| 按钮 | Cancel、Force Delete |

## Pagination 分页

| 项目 | 值 |
|------|-----|
| 默认每页 | 10 条 |
| 每页定位方式 | 下拉,"10 / page" |
| 总数显示 | "Total N items, last updated [timestamp]" |
| 翻页 | 上一页/下一页、页码按钮 |

## Test Cases 测试用例

### TC-RCY001: 验证回收站页面加载

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 已登录目标项目 |
| 操作 | 打开 /eec/instance-recycle-bin, 等待加载完成 |
| 可观察断言与恢复 | URL 未回登录且表格/空态和项目范围明确; 无资源时不伪造测试实例 |


### TC-RCY002: 状态过滤验证

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例已确认移入回收站的实例或明确授权的观察对象 |
| 操作 | 依次使用当前可见状态筛选并等待列表更新 |
| 可观察断言与恢复 | 各结果的状态符合筛选值, 清空筛选可恢复原视图; 不将空列表解释为资源已删除 |


### TC-RCY003: 恢复实例确认弹窗验证

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例回收站实例 UUID 已知, 操作仅验证弹窗 |
| 操作 | 选中目标后打开 Restore Instance, 核对数量/名称并 Cancel |
| 可观察断言与恢复 | 只含目标实例且关闭后仍在回收站, 不提交恢复; 出现额外对象立即取消 |


### TC-RCY004: 永久删除确认弹窗验证

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例回收站实例 UUID 已知, 未授权永久删除 |
| 操作 | 打开 Force Delete Instance, 核实不可恢复提示及磁盘策略, Cancel |
| 可观察断言与恢复 | 数量/身份/根盘策略准确, 实例仍可回读; 未获得准确目标删除授权不得点 Force Delete |


### TC-RCY005: 高级过滤验证

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 目标项目与已知名称/UUID, 列筛选入口可见 |
| 操作 | 选择真实筛选字段并提交条件, 等表格加载, 再清除条件 |
| 可观察断言与恢复 | 结果字段满足条件且清除后筛选被撤销; 控件只打开面板时继续观察, 不盲等即时搜索 |
