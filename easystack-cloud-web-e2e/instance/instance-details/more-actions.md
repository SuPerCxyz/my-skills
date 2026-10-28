# More Actions

UI 引用中的 `\uFF0C` 表示原文全角逗号, 使用原文定位时须还原; 不将转义文本当作按钮或提示原值.

> 来源:`easystack-cloud-web-e2e/instance/instance.md`,按原文标题边界拆分。

## More 菜单操作(Active 状态下 31 项)

### Toolbar States 顶部按钮状态

| 按钮 | 定位方式 | Active 状态 | 弹窗类型 |
|------|--------|-------------|----------|
| Start | `buttonByText("Start")` | disabled | - |
| Shutoff | `buttonByText("Shutoff")` | enabled | 确认对话框 |
| Reboot | `buttonByText("Reboot")` | enabled | 确认对话框 + Hard Reboot 复选框 |
| More | `buttonByText("More")` | enabled | 下拉菜单(31 项) |

### Status(状态管理)

| 操作 | 定位方式 | Active 状态 | 弹窗 |
|------|--------|-------------|------|
| Pause | `byText(".ant-dropdown-menu-item", "Pause")` | enabled | 确认对话框 |
| Unpause | `byText(".ant-dropdown-menu-item", "Unpause")` | disabled | - |
| Suspend | `byText(".ant-dropdown-menu-item", "Suspend")` | enabled | 确认对话框 |
| Unsuspend | `byText(".ant-dropdown-menu-item", "Unsuspend")` | disabled | - |

### Configuration(配置管理)

| 操作 | 定位方式 | Active 状态 | 弹窗/字段 |
|------|--------|-------------|-----------|
| Edit Name | `byText(".ant-dropdown-menu-item", "Edit Name")` | enabled | Instance Name (必填, 1-128字符) |
| Resize | `byText(".ant-dropdown-menu-item", "Resize")` | enabled | 完整表单(见下方) |
| Modify Boot Order | `byText(".ant-dropdown-menu-item", "Modify Boot Order")` | disabled | - |
| Reset Password | `byText(".ant-dropdown-menu-item", "Reset Password")` | disabled | - |
| Enable Agent | `byText(".ant-dropdown-menu-item", "Enable Agent")` | enabled | 确认对话框 |

#### Resize Instance 对话框

- 提示: "Living resize 不影响数据卷和系统卷"
- 当前 Flavor: General Computing / 1C / 1.0GiB / 1GiB
- **Resize Flavor Mode**: Offline Resize (默认) / Live Resize
- **Flavor 分类**: General Computing / Computing Optimized / Network Optimized / Computing Network Optimized / GPU-accelerated
- **Flavor 列表表格**: checkbox, Flavor Name, vCPU, RAM, vCPU Model
- 按钮: Cancel, Confirm (选择 flavor 后启用)

### Operation(操作)

| 操作 | 定位方式 | Active 状态 | 弹窗/字段 |
|------|--------|-------------|-----------|
| Clone | `byText(".ant-dropdown-menu-item", "Clone")` | enabled | **完整页面**(见下方) |
| Create Snapshot | `byText(".ant-dropdown-menu-item", "Create Snapshot")` | enabled | 表单(见下方) |
| Snapshot Rollback | `byText(".ant-dropdown-menu-item", "Snapshot Rollback")` | disabled | - |
| Edit Tags | `byText(".ant-dropdown-menu-item", "Edit Tags")` | enabled | 输入框: Type to search..., 最多 20 个标签 |

#### Create Snapshot 对话框

- 提示: "建议在关机状态或 I/O 非繁忙时段创建"
- **Snapshot Name** (必填, 1-128 字符)
- **Description** (可选)

#### Clone Instance(完整页面)

- **Basic Configuration**: Source Instance Name/Flavor (disabled), AZ (必填)
- **Network Configuration**: Virtual NIC, Type (IPv4/IPv6/Dual Stack), Network (必填), IPv4 Subnet (必填)
- **System Configuration**: Clone Instance Name, SSH Key, Password, Specify Compute Node
- **Number of Clones**: 数字定位方式
- **Quota** 链接

### Network(网络管理)

| 操作 | 定位方式 | Active 状态 | 弹窗/字段 |
|------|--------|-------------|-----------|
| Associate Floating IP | `byText(".ant-dropdown-menu-item", "Associate Floating IP")` | enabled | 表单(见下方) |
| Disassociate Floating IP | `byText(".ant-dropdown-menu-item", "Disassociate Floating IP")` | enabled | 确认对话框 |
| Associate Network | `byText(".ant-dropdown-menu-item", "Associate Network")` | enabled | 表单 |
| Disassociate Network | `byText(".ant-dropdown-menu-item", "Disassociate Network")` | enabled | 确认对话框 |
| Edit Security Group | `byText(".ant-dropdown-menu-item", "Edit Security Group")` | enabled | 穿梭框(见下方) |
| Manage Virtual IP | `byText(".ant-dropdown-menu-item", "Manage Virtual IP")` | enabled | 表单 |

#### Associate Floating IP 对话框

- 提示: "需要路由器设置网关"
- **Instance Name** (disabled, 预填)
- **Instance Nic** (必填, 页面显示 `<INSTANCE_VNIC>: <PRIVATE_IP>`)
- **Floating IP** (必填, 下拉选择)

#### Edit Security Groups 对话框

- **双栏穿梭框布局**
- 左栏: 可用安全组列表 (16 项)
- 右栏: 已关联安全组 (1 项)
- 表格列: Security Groups, Stateful, Creation Time
- 操作: 勾选后通过中间箭头按钮在两栏间移动

### Storage(存储管理)

| 操作 | 定位方式 | Active 状态 | 弹窗/字段 |
|------|--------|-------------|-----------|
| Attach Volume | `byText(".ant-dropdown-menu-item", "Attach Volume")` | enabled | 表单(见下方) |
| Detach Volume | `byText(".ant-dropdown-menu-item", "Detach Volume")` | enabled | 确认对话框 |
| Mount ISO | `byText(".ant-dropdown-menu-item", "Mount ISO")` | enabled | 表单 |
| Unmount ISO | `byText(".ant-dropdown-menu-item", "Unmount ISO")` | enabled | 确认对话框 |
| Mount USB Device | `byText(".ant-dropdown-menu-item", "Mount USB Device")` | enabled | 表单 |
| Unmount USB Device | `byText(".ant-dropdown-menu-item", "Unmount USB Device")` | enabled | 确认对话框 |
| Storage Cold Migration | `byText(".ant-dropdown-menu-item", "Storage Cold Migration")` | disabled | - |
| Storage Live Migration | `byText(".ant-dropdown-menu-item", "Storage Live Migration")` | enabled | 表单 |

#### Attach Volume 对话框

- **Instance Name** (disabled, 预填)
- **Volume** (必填, 下拉选择可用卷)

### Maintenance(维护管理)

| 操作 | 定位方式 | Active 状态 | 弹窗 |
|------|--------|-------------|------|
| Cold Migrate | `byText(".ant-dropdown-menu-item", "Cold Migrate")` | enabled | 表单 |
| Live Migrate | `byText(".ant-dropdown-menu-item", "Live Migrate")` | enabled | 表单 |
| Evacuate | `byText(".ant-dropdown-menu-item", "Evacuate")` | enabled | 表单 |
| Reset State | `byText(".ant-dropdown-menu-item", "Reset State")` | enabled | 确认对话框 |
| Lock | `byText(".ant-dropdown-menu-item", "Lock")` | enabled | 确认对话框 |
| Unlock | `byText(".ant-dropdown-menu-item", "Unlock")` | disabled | - |
| Rebuild | `byText(".ant-dropdown-menu-item", "Rebuild")` | enabled | 表单 |

#### Mount ISO 对话框

- 提示: "挂载 ISO 后需要关机再启动才能识别"
- **Instance Name** (disabled)
- **已挂载 ISO 列表**: 如果没有挂载显示 "No mounted ISO"
- **Add** 按钮: 点击后选择 ISO 镜像

#### Mount USB Device 对话框

- 提示: "仅支持 USB 2.0/3.0 存储设备"
- **已挂载 USB 设备列表**: Product Series, Manufacturer, Serial Number, Interface Type, Capacity, Partitions, Mount Status
- **可用 USB 设备列表**: 同上字段
- 选择可用设备后点击 **Mount**

#### Manage Virtual IP 对话框

- 说明: "可为实例绑定的虚拟网卡配置 VIP\uFF0C支持高可用服务"
- **VNIC Name**, **IP Address**, **Virtual IP** 表格
- **Add a virtual IP** 按钮

#### Lock 对话框

- 提示: "锁定的实例无法执行任何其他操作"
- 显示实例数量和列表

#### Cold Migrate 对话框

- 提示: "运行中的实例将被临时关机"
- **Current Node** 信息: Instance Name, UUID, vCPU, RAM, vGPU, GPU, USB, SR-IOV vNIC, RoCE vNIC
- **Select target host**: Auto-Schedule / 手动选择

#### Live Migrate 对话框

- 说明: "不停机迁移实例到其他节点\uFF0C数据盘保持不变"
- 提示: "内存变化过快可能导致超时\uFF0C可启用压缩或 vCPU 限流"
- **Block Migration** 复选框
- **Current Node** 信息
- **Select target host**: Auto-Schedule / 手动选择

#### Storage Live Migration 对话框

- 说明: "不关机迁移系统盘或数据盘到其他存储后端"
- 提示: "并发迁移会占用目标存储集群带宽"
- **Volume 表格**: Volume Name, Volume Type, Size, Used, Current Backend, Target Backend (下拉), Migration Rate (Unlimited/100MB/s/50MB/s)

#### Rebuild 对话框

- 警告: "将删除所有系统分区数据\uFF0C务必先备份"
- 警告: "重建过程中实例将关机\uFF0C完成后恢复原始状态"
- 警告: "数据盘不受影响"
- 警告: "重建后需要重新配置自定义设置"
- **Image** (必填, 下拉选择)
- **Confirm Password** (必填)

### Deletion(删除)

| 操作 | 定位方式 | Active 状态 | 弹窗 |
|------|--------|-------------|------|
| Delete | `byText(".ant-dropdown-menu-item", "Delete")` | enabled | 确认对话框(见下方) |

#### Delete Instance 对话框

- 两种删除策略:
  - **Remove to Recycle Bin** (默认): 保留 24 小时,可恢复
  - **Force Delete**: 完全删除,不可恢复
- 显示 Root Disk 和 Data Disk 数量信息
- 注意事项关于根磁盘和数据盘的删除行为
