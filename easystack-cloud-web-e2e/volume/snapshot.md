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
| URL | `https://<IP>/ebs/volume-snapshots` |
| 导航路径 | Service Catalog → Block Storage → Volume Snapshot |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

云硬盘快照是逻辑保护服务,提供数据保护能力。当卷上的数据遭受病毒入侵或误删时,可以快速恢复到最后一个快照检查点,保护数据安全并提高系统安全性。

## Page Buttons 页面按钮

| 按钮 | 定位方式 | 状态 | 说明 |
|------|--------|------|------|
| Create Volume | `buttonByText("Create Volume")` | 需选择快照 | 从快照创建新卷 |
| Update Status | `buttonByText("Update Status")` | 需选择快照 | 更新快照状态 |
| Roll Back Volume | `buttonByText("Roll Back Volume")` | 需选择快照 | 回滚卷到快照状态 |
| Delete | `buttonByText("Delete")` | 需选择快照 | 删除快照 |
| More | `buttonByText("More")` | 需选择快照 | 更多操作 |

> 注意:所有操作按钮在未选择快照时处于禁用状态

## Table Columns 表格列信息

| 列名 | 说明 |
|------|------|
| Name | 快照名称 |
| Tags | 标签 |
| Description | 描述 |
| Status | 状态 |
| Size | 大小 |
| Volume Name | 来源卷名称 |
| Domain | 域 |
| Project | 项目 |
| Creation Time | 创建时间 |

## Test Cases 测试用例

### TC-S001: 从卷创建快照

**前置条件:** 已登录且存在可用卷

**步骤:**
1. 导航到云硬盘页面 (`/ebs/volumes`)
2. 选择一个可用的卷(状态为 Available)
3. 点击 "More" 按钮
4. 选择 "Create Snapshot" 选项
5. 填写快照名称和描述
6. 点击确认创建

**代码:**

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例卷 UUID与数据基线明确, 在线强制快照语义已授权 |
| 操作 | 调用 create_volume_snapshot, 按卷状态选择 Forced 并提交唯一名称 |
| 可观察断言与恢复 | 快照 Available 且源卷 UUID 一致; 在线快照需记录一致性级别, 不用名称出现判成功 |


### TC-S002: 查看快照详情

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例快照 UUID 已记录且 Available |
| 操作 | 打开精确快照详情并回读 Name/Volume/Size/Status/Project |
| 可观察断言与恢复 | 字段与创建输入和源卷一致; 详情无匹配或权限不足停止, 不使用同名替代 |


### TC-S003: 删除快照

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例快照 UUID 确定, 本次删除已授权 |
| 操作 | 调用 delete_volume_snapshot, 核对两层确认目标 |
| 可观察断言与恢复 | 完整加载后精确 UUID 消失, 其他快照保留; 超时回读, 不以半加载空白成功 |


### TC-S004: 从快照恢复卷

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例快照与源卷 UUID 确定, 数据基线/停机范围明确 |
| 操作 | 调用 rollback_volume_snapshot, 核对快照链与两层确认, 等任务完成 |
| 可观察断言与恢复 | 源卷稳定且快照点数据/校验和一致; 不自动删除未授权的后续快照, 无证据保持未确认 |


## Snapshot States 常见快照状态

| 状态 | 说明 |
|------|------|
| Available | 可用,可以进行操作 |
| Creating | 创建中 |
| Restoring | 恢复中 |
| Error | 错误状态 |
| Deleting | 删除中 |
