# Group

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
| URL | `https://<IP>/eec/instance-groups` |
| 导航路径 | Computing → Instance Group |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

云主机分组允许将多个实例组织在一起,支持反亲和性策略(Anti-Affinity),确保组内实例分布在不同计算节点上以提高可用性。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Instance Group | `buttonByText("Create Instance Group")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Edit Tags | `buttonByText("Edit Tags")` | 默认禁用,选中 1+ 行后可用 |
| More | `buttonByText("More")` | 默认禁用,选中 1+ 行后可用 |
| Delete | `buttonByText("Delete")` | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## Filter Fields 过滤器字段

Name、Tags、Description、Policy、Instances、Domain、Project、Created Time

## Table Columns 表格列(9 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 分组名称 |
| Tags | ❌ | 标签 |
| Description | ✅ | 描述 |
| Policy | ✅ | 策略(如 anti-affinity) |
| Instances | ✅ | 关联实例数量 |
| Domain | ✅ | 域名 |
| Project | ✅ | 项目 |
| Created Time | ✅ | 创建时间 |

## Create 创建 Instance Group 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Description | ❌ | `input[placeholder="Enter a description"]` | 描述 |
| Policy | ✅ | `nz-select` 下拉 | 策略选择 |

Policy 下拉选项:

| 策略 | 说明 |
|------|------|
| anti-affinity | 反亲和性:组内实例分布在不同计算节点 |

弹窗按钮:Cancel、Create

## More 菜单(选中分组后)

| 操作 | 说明 |
|------|------|
| Edit Tags | 编辑标签 |
| Associate Instances | 关联实例到分组 |
| Disassociate Instances | 从分组中移除实例 |

## Test Cases 测试用例

### TC-G001: 创建 Instance Group

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 唯一组名与明确 anti-affinity 策略 |
| 操作 | Create Instance Group 填名称/策略并提交, 回读详情 |
| 可观察断言与恢复 | 组名/策略一致且初始成员为空; 提交未确认先回读, 不重建同名组 |


### TC-G002: 关联实例到分组

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例组与实例已创建且 UUID 明确 |
| 操作 | 精确选中组, More -> Associate Instances, 选择本用例实例并确认 |
| 可观察断言与恢复 | 组成员列/详情包含相同实例 UUID; 关联不代表既有实例立即迁移, 不用节点变化证明此动作; 清理先解除本次成员关联 |
