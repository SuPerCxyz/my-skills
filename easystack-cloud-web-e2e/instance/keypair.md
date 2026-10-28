# Keypair

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
| URL | `https://<IP>/eec/keypairs` |
| 导航路径 | Computing → SSH Key Pair |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

SSH 密钥对基于非对称加密,用于安全访问云主机。创建云主机时可选择公钥,平台不保存私钥。用户需通过本地私钥访问实例。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Key Pair | `buttonByText("Create Key Pair")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Import Key Pair | `buttonByText("Import Key Pair")` | 始终可用 |
| Edit Tag | `buttonByText("Edit Tag")` | 默认禁用,选中 1+ 行后可用 |
| Delete Key Pair | `buttonByText("Delete Key Pair")` | 默认禁用,选中 1+ 行后可用 |
| Export | `buttonByText("Export")` | 始终可用 |
| Setup | `buttonByText("Setup")` | 始终可用 |

## Filter Fields 过滤器字段

Name、Tags、User、Fingerprint

## Table Columns 表格列(5 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (展开/折叠) | ❌ | 展开显示公钥 |
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 密钥对名称 |
| Tags | ❌ | 标签 |
| User | ✅ | 创建用户 |
| Fingerprint | ✅ | MD5 指纹 |

### Expanded Rows 展开行(子表格)

点击展开按钮显示公钥内容:

| 列名 | 说明 |
|------|------|
| Public Key | 完整公钥文本(如 ssh-ed25519 AAAA...) |

## Setup 列配置

可配置列:Name、Tags、User、Fingerprint

按钮:Restore Defaults、Select All、Cancel、Confirm

## Export 行为

点击 Export 立即下载 CSV 文件

文件名格式:`SSH Key Pair_YYYYMMDDHHmmss.csv`

CSV 列:Name、Tags、User、Fingerprint、Public Key

## Create 创建 Key Pair 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Key Pair Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |

弹窗按钮:Cancel、Create

> 创建后会显示私钥下载对话框,需立即保存私钥。

## Import Key Pair 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Key Pair Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Public Key | ✅ | `input[placeholder="Please public Key is required."]` | 完整公钥文本 |

弹窗按钮:Cancel、Import

## Test Cases 测试用例

### TC-K001: 创建 Key Pair

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 唯一密钥名, 安全下载目录与后续验证需求明确 |
| 操作 | Create Key Pair 输入名称, 保存一次性私钥到本次临时文件并设 0600 |
| 可观察断言与恢复 | 列表名称/指纹可回读, 私钥文件存在且权限正确, 不输出私钥; 下载失败不声称 SSH 可用, 报告后按授权删测试密钥与临时文件 |


### TC-K002: 导入 Key Pair

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 已生成可信本次公钥, 指纹及唯一名称已知 |
| 操作 | Import Key Pair 填名称和公钥, 提交后回读 |
| 可观察断言与恢复 | 列表/详情公钥指纹与输入一致; 私钥不上传不记录, 无用例实例引用后按授权清理 |


### TC-K003: 删除 Key Pair

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例密钥名/指纹明确, 不被后续步骤依赖 |
| 操作 | 精确选中密钥, Delete Key Pair 并处理当前确认框 |
| 可观察断言与恢复 | 完整刷新后目标指纹消失且其他密钥仍在; 超时先回读, 不扩大删除范围 |
