# Operations

UI 引用中的 `\uFF0C` 表示原文全角逗号, 使用原文定位时须还原; 不将转义文本当作按钮或提示原值.

> 来源:`easystack-cloud-web-e2e/volume/volume.md`,按原文标题边界拆分。

## Other Page Actions 页面其他操作

### Button Actions 按钮操作

| 按钮 | 定位方式 | 说明 |
|------|--------|------|
| Create Volume | `byText("button.ant-btn-primary", "Create Volume")` | 创建新卷 |
| Attach | `buttonByText("Attach")` | 挂载卷到实例 |
| Detach | `buttonByText("Detach")` | 从实例卸载卷 |
| Update Status | `buttonByText("Update Status")` | 更新卷状态 |
| More | `buttonByText("More")` | 更多操作下拉菜单 |

### Table Columns 表格列信息

云硬盘列表表格通常包含以下列:
- Name(名称)
- Status(状态)
- Size(容量)
- Volume Type(类型)
- Attached To(挂载到)
- Created At(创建时间)

## More 菜单操作

### Menu Actions 菜单完整列表(9 项)

| 操作 | 定位方式 | 可用状态 | 弹窗类型 |
|------|--------|----------|----------|
| Reset Attach Status | `byText(".ant-dropdown-menu-item", "Reset Attach Status")` | In use 时可用 | 确认对话框 |
| Edit | `byText(".ant-dropdown-menu-item", "Edit")` | Available 时可用 | 表单 |
| Create Snapshot | `byText(".ant-dropdown-menu-item", "Create Snapshot")` | Available 时可用 | 表单 |
| Create Image | `byText(".ant-dropdown-menu-item", "Create Image")` | Available 时可用 | 表单 |
| Extend Size | `byText(".ant-dropdown-menu-item", "Extend Size")` | Available 时可用 | 表单 |
| Modify Property | `byText(".ant-dropdown-menu-item", "Modify Property")` | Available 时可用 | 确认对话框 |
| Migrate | `byText(".ant-dropdown-menu-item", "Migrate")` | In use 时可用 | 表单 |
| Delete | `byText(".ant-dropdown-menu-item", "Delete")` | 未挂载时可用 | 确认对话框 |
| Edit Tags | `byText(".ant-dropdown-menu-item", "Edit Tags")` | Always | 表单 |

### Edit 对话框

- **Volume Name** (文本输入, 可修改)
- **Description** (文本域, 可修改)

### Create Image 对话框

- 警告: "将私有镜像转为公有镜像可能导致其他用户隐私数据泄露"
- **Image Name** (必填, 1-128 字符)
- **Description** (可选)
- **Image Format**: Raw (默认)
- **Operating System Category** (必填, 下拉选择)
- **Minimum Root Disk Size (GiB)** (数字输入)
- **Minimum RAM (GiB)** (数字输入)
- **Forced to Create Image**: Yes / No

### Modify Property 对话框

- 说明: "将修改卷属性为可启动磁盘\uFF0C之后该卷可用作新实例的启动源"
- 确认按钮: Confirm

### Edit Tags 对话框

- **Edit Resource Tags**
- 提示: "最多可添加 20 个标签"
- 标签输入框: 输入 key=value 格式,按 Enter 添加

### Reset Attach Status 对话框

- 说明: "重置卷的挂载状态\uFF0C解决异常挂载问题"
- 确认按钮: Confirm

### Migrate 对话框(In use 时可用)

- 说明: "迁移卷到其他存储后端"
- **Volume** 信息表格
- **Target Backend** (下拉选择)
- 确认按钮: Migrate
