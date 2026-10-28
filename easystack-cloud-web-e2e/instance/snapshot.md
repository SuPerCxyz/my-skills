# Snapshot

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
| URL | `https://<IP>/eec/instance-snapshots` |
| 导航路径 | Computing → Instance Snapshot |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

实例快照是特定时间点上根磁盘和卷磁盘数据的完整副本。可用于将实例恢复到快照创建时的状态。

> **注意**:快照没有独立的"创建"按钮,需从云主机页面 More → Create Snapshot 创建。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Refresh | 工具栏第一个 icon 按钮 | 始终可用 |
| Edit Tags | `buttonByText("Edit Tags")` | 默认禁用,选中 1+ 行后可用 |
| More | `buttonByText("More")` | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 无数据时禁用,有数据时可用 |
| Setup | 工具栏最后一个 icon 按钮 | 始终可用 |

## Status Filter 状态过滤下拉

定位方式:`nz-select`(含 "All Status" 文本)

| 选项 |
|------|
| All Status(默认) |
| Available |
| Pending Delete |
| Deleted |
| Saving |
| Queued |
| Creating |

## Filter Fields 过滤器字段

Name、Tags、Description、Snapshot Source、Size、Format、Domain、Project、Created Time

## Table Columns 表格列(11 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 快照名称,点击进入详情 |
| Tags | ❌ | 标签 |
| Description | ✅ | 描述 |
| Status | ✅ | 状态徽章 |
| Snapshot Source | ✅ | 来源实例名称 |
| Size | ✅ | 磁盘大小 |
| Format | ✅ | 镜像格式 |
| Domain | ✅ | 域名 |
| Project | ✅ | 项目 |
| Created Time | ✅ | YYYY-MM-DD HH:mm:ss |

## Setup 列配置

可配置列:Name、Tags、Description、Status、Snapshot Source、Size、Format、Domain、Project、Created Time

按钮:Restore Defaults、Select All、Cancel、Confirm

## More 菜单(选中快照后)

| 操作 | 说明 |
|------|------|
| Edit Tags | 编辑标签 |
| Delete | 删除快照 |

## Create Snapshot 创建快照(从云主机页面)

入口:Instance 页面 → 选择实例 → More → Create Snapshot

### Create Snapshot 创建快照弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Snapshot Name | ✅ | `textbox "Enter 1 to 128 characters in length"` | 1-128 字符 |
| Description | ❌ | `textbox "Enter a description"` | 描述 |

弹窗按钮:Cancel、Create

> ⚠️ 警告信息:"It is strongly recommended to create snapshot during the shutdown state of the instance or during non busy periods of instance I/O, otherwise it may cause data consistency issues."

## Test Cases 测试用例

### TC-S001: 从云主机创建快照

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例实例 UUID 明确, 数据已静止或明确接受 crash-consistent 语义 |
| 操作 | 调用 create_instance_snapshot, 用唯一快照名提交一次 |
| 可观察断言与恢复 | 同项目快照指向该实例且达到 Available; Saving/Queued/Creating 不成功; 超时保留身份并回读 |


### TC-S002: 恢复快照(Snapshot Rollback)

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例实例/快照与基线数据明确, 关机和回滚范围已授权 |
| 操作 | 在当前 UI 核实 Snapshot Rollback 入口/支持条件, 选择确切快照并处理确认 |
| 可观察断言与恢复 | 本次回滚任务完成且快照点数据/校验和一致; 无入口/规则不明时不提交, 不能用 Active 代替数据验证 |


### TC-S003: 删除快照

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例快照 UUID 已知且后续步骤不依赖 |
| 操作 | 精确选中快照, More -> Delete, 核对确认目标并提交 |
| 可观察断言与恢复 | 完整刷新后快照 UUID 消失, 其他快照不变; 超时回读而非扩展删除目标 |
