# Az

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
| URL | `https://<IP>/eec/availability-zones` |
| 导航路径 | Computing → AZ & Host Aggregates |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

可用域(Availability Zone)用于将物理资源逻辑分组,支持跨可用域部署以提高容灾能力。主机聚合(Host Aggregate)允许将主机分组并应用特定的调度策略。

## Tabs 标签页

| 标签 | 定位方式 | 说明 |
|------|--------|------|
| Availability Zone | `tab "Availability Zone"` | 默认,可用域列表 |
| Host Aggregate | `tab "Host Aggregate"` | 主机聚合列表 |

## Availability Zone 标签页

### Availability Zone 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Availability Zone | `buttonByText("Create Availability Zone")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Delete | `buttonByText("Delete")` | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

### Availability Zone 表格列

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 可用域名称 |
| Description | ✅ | 描述 |
| Hosts | ✅ | 关联主机数 |
| Instances | ✅ | 实例数 |
| Projects | ✅ | 项目数 |
| Created Time | ✅ | 创建时间 |

### Create 创建 Availability Zone 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Description | ❌ | `input[placeholder="Enter a description"]` | 描述 |

弹窗按钮:Cancel、Create

## Host Aggregate 标签页

### Host Aggregate 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Host Aggregate | `buttonByText("Create Host Aggregate")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Edit | `buttonByText("Edit")` | 默认禁用,选中 1+ 行后可用 |
| Delete | `buttonByText("Delete")` | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

### Host Aggregate 表格列

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 聚合名称 |
| Description | ✅ | 描述 |
| Availability Zone | ✅ | 所属可用域 |
| Hosts | ✅ | 关联主机 |
| Metadata | ✅ | 元数据标签 |
| Projects | ✅ | 项目数 |
| Created Time | ✅ | 创建时间 |

### Create 创建 Host Aggregate 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Availability Zone | ✅ | `nz-select` 下拉 | 选择已有可用域 |
| Description | ❌ | `input[placeholder="Enter a description"]` | 描述 |
| Metadata | ❌ | 键值对输入 | 自定义元数据 |

弹窗按钮:Cancel、Create

### Edit Host Aggregate 弹窗

与创建弹窗类似,预填充已有数据。

## Filter Fields 过滤器字段

Name、Description、Availability Zone、Hosts、Metadata、Projects、Created Time

## Test Cases 测试用例

### TC-AZ001: 创建 Availability Zone

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 目标管理员项目, 唯一 AZ 名称及描述 |
| 操作 | 按页面已知 Create Availability Zone 表单填 Name/Description, 回读后提交一次 |
| 可观察断言与恢复 | 同一名称的 AZ 唯一出现, 描述一致; 失败时保留提交状态, 清理前确认没有关联主机/实例 |


### TC-AZ002: 创建 Host Aggregate

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例 AZ 已存在, 聚合名称唯一, 明确要关联的节点范围 |
| 操作 | 打开 Create Host Aggregate, 选择本用例 AZ 并填名称/metadata, 回读后提交 |
| 可观察断言与恢复 | 聚合唯一且 AZ/metadata 一致; 不默认加入已有生产节点, 清理先解除本次关联 |
