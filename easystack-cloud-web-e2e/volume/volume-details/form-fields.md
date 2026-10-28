# Form Fields

> 来源:`easystack-cloud-web-e2e/volume/volume.md`,按原文标题边界拆分。

## Page Information 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/ebs/volumes` |
| 导航路径 | Service Catalog → Block Storage → Volume |
| 页面标题 | EasyStack Cloud |

## Volume Form Fields 创建云硬盘表单字段

### Volume Name(卷名称)⭐ 必填

| 属性 | 值 |
|------|-----|
| 类型 | 文本输入 |
| 必填 | 是 |
| 长度限制 | 1-128 字符 |
| placeholder | "Enter 1 to 128 characters in length" |
| 定位方式 | `fieldInput("Volume Name", "input")` |

### Description(描述)

| 属性 | 值 |
|------|-----|
| 类型 | 多行文本域 |
| 必填 | 否 |
| placeholder | "Enter description of the volume" |
| 定位方式 | `fieldInput("Description", "textarea")` |

### Volume Source(卷来源)⭐ 必填

| 属性 | 值 |
|------|-----|
| 类型 | 下拉选择 |
| 必填 | 是 |
| 默认值 | "Empty Volume" |
| 定位方式 | `formItemByLabel("Volume Source")?.querySelector(".ant-select, nz-select")` |

**可选项:**

| 选项 | 说明 | 额外字段 |
|------|------|----------|
| Empty Volume | 创建空白卷 | 无 |
| Image | 从镜像创建 | 出现 "Image" 定位方式 |
| Instance Snapshot | 从实例快照创建 | 出现 "Instance Snapshot" 定位方式 |
| Volume Snapshot | 从卷快照创建 | 出现 "Volume Snapshot" 定位方式 |

### Type(类型)

| 属性 | 值 |
|------|-----|
| 类型 | 下拉选择 |
| 必填 | 是 |
| 默认值 | "hdd" |
| 定位方式 | `formItemByLabel("Type")?.querySelector(".ant-select, nz-select")` |

**可选项:**

| 选项 | 说明 |
|------|------|
| hdd | 机械硬盘类型 |

> 注意:其他环境可能有 ssd 等更多类型

### Size(容量)⭐ 必填

| 属性 | 值 |
|------|-----|
| 类型 | 数字输入 + 滑块 |
| 必填 | 是 |
| 单位 | GiB |
| 范围 | 1 GiB ~ 65536 GiB |
| 默认值 | 1 |
| 步长 | 1 |
| 定位方式 | `fieldInput("Size", ".ant-input-number input")` |
