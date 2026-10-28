# Flavor

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
| URL | `https://<IP>/eec/flavors` |
| 导航路径 | Computing → Instance Flavor |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

实例规格定义了云主机的计算资源配额(vCPU、内存、根磁盘、临时磁盘)。创建云主机时需选择合适的规格。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Flavor | `buttonByText("Create Flavor")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Edit Tags | `buttonByText("Edit Tags")` | 默认禁用,选中 1+ 行后可用 |
| Edit | `buttonByText("Edit")` | 默认禁用,选中 1+ 行后可用 |
| Delete | `buttonByText("Delete")` | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## Filter Fields 过滤器字段

Name、Tags、Description、Category、vCPUs、Memory Size、Root Disk Size、Ephemeral Disk Size、Swap Disk Size、RX/TX Factor、Domain、Project、Created Time

## Table Columns 表格列(15 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 规格名称 |
| Tags | ❌ | 标签 |
| Description | ✅ | 描述 |
| Category | ✅ | 分类 |
| vCPUs | ✅ | 虚拟 CPU 数量 |
| Memory Size | ✅ | 内存大小 |
| Root Disk Size | ✅ | 根磁盘大小 |
| Ephemeral Disk Size | ✅ | 临时磁盘大小 |
| Swap Disk Size | ✅ | 交换磁盘大小 |
| RX/TX Factor | ✅ | 网络收发因子 |
| Domain | ✅ | 域名 |
| Project | ✅ | 项目 |
| Created Time | ✅ | 创建时间 |

### Flavor Categories 规格分类(Category)

| 分类 | 说明 |
|------|------|
| general | 通用计算 |
| computing-optimized | 计算优化 |
| network-optimized | 网络优化 |
| computing-network-optimized | 计算网络优化 |
| gpu-accelerated | GPU 加速 |

## Create 创建 Flavor 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Description | ❌ | `input[placeholder="Enter a description"]` | 描述 |
| Category | ✅ | `nz-select` 下拉 | 分类选择 |
| vCPUs | ✅ | `input[type="number"]` | 正整数 |
| Memory Size | ✅ | 数字输入 + 单位选择 | MB 或 GB |
| Root Disk Size | ✅ | 数字输入 + 单位选择 | GB |
| Ephemeral Disk Size | ❌ | 数字输入 + 单位选择 | GB,默认 0 |
| Swap Disk Size | ❌ | 数字输入 + 单位选择 | MB,默认 0 |
| RX/TX Factor | ❌ | 数字输入 | 网络因子,默认 1.0 |

弹窗按钮:Cancel、Create

## More 菜单(选中规格后)

| 操作 | 说明 |
|------|------|
| Edit Tags | 编辑标签 |

## Test Cases 测试用例

### TC-F001: 创建 Instance Flavor

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 明确本用例规格名、vCPU、内存、根盘及访问范围 |
| 操作 | 打开 Create Flavor, 输入资源值并核对单位和分类, 提交一次 |
| 可观察断言与恢复 | 详情资源值与单位一致, 名称唯一; 同名或单位不符停止, 无实例引用后按授权删除 |
