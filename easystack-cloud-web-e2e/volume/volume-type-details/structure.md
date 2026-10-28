# Structure

> 来源:`easystack-cloud-web-e2e/volume/volume-type.md`,按原文标题边界拆分。

## Page Information 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/ebs/volume-types` |
| 导航路径 | Service Catalog → Block Storage → Volume Type |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

云硬盘类型在创建卷时映射到不同的存储后端。可以根据业务场景创建多种类型来满足需求。

## Page Structure 页面结构

### Tabs 标签页

| 标签 | 定位方式 | 说明 |
|------|--------|------|
| Volume Type | `byText(".ant-tabs-tab-btn", "Volume Type")` | 卷类型管理 |
| QoS Specs | `byText(".ant-tabs-tab-btn", "QoS Specs")` | QoS 规格管理 |

### Volume Type 标签页按钮

| 按钮 | 定位方式 | 状态 | 说明 |
|------|--------|------|------|
| Create Volume Type | `buttonByText("Create Volume Type")` | 始终可用 | 创建新类型 |
| Manage QoS Spec Association | `buttonByText("Manage QoS Spec Association")` | 需选择类型 | 管理 QoS 关联 |
| Edit | `buttonByText("Edit")` | 需选择类型 | 编辑类型 |
| Delete | `buttonByText("Delete")` | 需选择类型 | 删除类型 |

### QoS Specs 标签页按钮

| 按钮 | 定位方式 | 状态 | 说明 |
|------|--------|------|------|
| Create QoS Spec | `buttonByText("Create QoS Spec")` | 始终可用 | 创建 QoS 规格 |
| Delete QoS Spec | `buttonByText("Delete QoS Spec")` | 需选择规格 | 删除 QoS 规格 |

## Volume Type 表格列

| 列名 | 说明 |
|------|------|
| Name | 类型名称 |
| Description | 描述 |
| Associated QoS Spec | 关联的 QoS 规格 |
| Support shared volume | 是否支持共享卷 |

### Extra Specs(扩展规格)

每个 Volume Type 可以有多个 Extra Specs,以 Key-Value 形式存储:

| 常用 Key | 说明 | 示例值 |
|----------|------|--------|
| volume_backend_name | 存储后端名称 | hdd, ssd |
| multiattach | 是否支持多附加 | \<is\> True |
| replication_enabled | 是否启用复制 | \<is\> True |
| compression | 是否启用压缩 | \<is\> True |
| encryption | 是否启用加密 | \<is\> True |

## QoS Specs 表格列

| 列名 | 说明 |
|------|------|
| Name | QoS 规格名称 |
| Consume | 消费类型(如 front-end) |

## Create 创建 Volume Type 表单

### Form Fields 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Name | 文本输入 | ✅ | 类型名称 |
| Extra Specs | 标签页 | ❌ | 扩展规格配置 |
| - Pre Define | 标签页 | ❌ | 预定义规格 |
| - Self Define | 标签页 | ❌ | 自定义规格 |
| Key | 下拉选择 | ❌ | 规格键(选择 Pre Define 时) |
| Value | 文本输入 | ❌ | 规格值 |
| Description | 文本输入 | ❌ | 描述 |
| Support shared volume | 复选框 | ❌ | 是否支持共享卷 |

### Create 创建 QoS Spec 表单

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Name | 文本输入 | ✅ | QoS 规格名称 |

> 注意:QoS 规格需要与 Volume Type 关联后才能生效。关联或编辑 QoS 规则不会对已挂载的卷生效,需要重新挂载才能使 QoS 规则生效。
