# Create Wizard

> 来源:`easystack-cloud-web-e2e/instance/instance.md`,按原文标题边界拆分。

## Create Instance Wizard 创建实例向导(4 步)

> ⚠️ **重要:** Name 字段在 **Step 3 (System Configuration)** 中,不在 Step 1!

### Wizard Navigation 向导导航按钮

| 步骤 | Next 按钮 | Previous 按钮 |
|------|-----------|---------------|
| Step 1 | `buttonByText("Next: Network Configuration")` | - |
| Step 2 | `buttonByText("Next: System Configuration")` | `buttonByText("Prev: Basic Configuration")` |
| Step 3 | `byText(".steps-action button.ant-btn-primary", "Confirm")` | `buttonByText("Prev: Network Configuration")` |
| Step 4 | 最终 `byText("button.ant-btn-primary", "Confirm")` | - |

### Wizard Footer 底部栏(始终显示)

- **Quantity**: `nz-input-number.instance-number` — 批量创建数量
- **Quota**: 显示当前配额使用情况
- **导航按钮**: Next / Previous / Confirm

### Step 1: Basic Configuration(基础配置)

#### 1.1 Region / Project(只读显示)
- **Region:** `Local Cloud`(不可编辑)
- **Project:** 当前 Project(不可编辑)

#### 1.2 Availability Zone(可用域)
- **定位方式:** `#available_zone nz-select`
- **默认值:** `default-az`
- **选项:** 仅 1 个(default-az)

#### 1.3 Boot Source(启动源)⭐ 必填

**组件:** `nz-radio-group.ant-radio-group`(实心按钮组)

| 选项 | 定位方式 | 说明 |
|------|--------|------|
| **Image** | `byText("label.ant-radio-button-wrapper", "Image")` | 默认,从镜像启动 |
| **Instance Snapshot** | `byText("label.ant-radio-button-wrapper", "Instance Snapshot")` | 从实例快照启动 |
| **Bootable Volume** | `byText("label.ant-radio-button-wrapper", "Bootable Volume")` | 从可启动卷启动 |

#### 1.4 OS Category(操作系统分类)

**组件:** `.system-icon-wrap nz-radio-group` — 图标式单选按钮组

| 类别 | 说明 |
|------|------|
| cirros | 测试镜像 |
| CentOS | CentOS |
| Fedora | Fedora |
| Ubuntu | Ubuntu |
| Windows | Windows |
| Others | 其他 |

#### 1.5 Tag / Description

| 字段 | 定位方式 | 说明 |
|------|--------|------|
| Tag | tag input | 最多 20 个标签 |
| Description | text input | 描述(可选) |

> ⚠️ Name 字段在 Step 3 (System Configuration) 中,详见 3.1

#### 1.6 Image 表格(Boot Source=Image 时)

**定位方式:** 第一个 `table` in `.steps-content`

**表格列:** Name, Tag, Description, OS Category, CPU Architecture, Minimum Root Disk, Minimum Memory, Access Control, Format, Image Size

**当前环境镜像(8 个):**

| Name | OS Category | CPU Arch | Min Root Disk | Min Memory | Access | Format | Size |
|------|------------|----------|---------------|------------|--------|--------|------|
| **TestVM** | cirros | Arm | 1 GiB | 1 GiB | Public | raw | 108.00 MiB |
| centos-qga | CentOS | Arm | 10 GiB | 2 GiB | Public | raw | 10.00 GiB |
| containerd-kubernetes-node-image-621-arm | Fedora | Arm | 20 GiB | 4 GiB | Public | raw | 20.00 GiB |
| containerd-kubernetes-node-image-621-x86 | fedora-atomic | - | 0 GiB | 0 MiB | Public | raw | 20.00 GiB |
| loadbalancer-image-7.0.1-aarch64 | Others | Arm | 0 GiB | 0 MiB | Private | raw | 20.00 GiB |
| loadbalancer-image-7.0.1-x86_64 | Others | x86 | 0 GiB | 0 MiB | Private | raw | 20.00 GiB |
| testbed-network-multicast-ubuntu-2204 | Ubuntu | Arm | 15 GiB | 2 GiB | Public | raw | 15.00 GiB |
| ubuntu_22 | Ubuntu | Arm | 15 GiB | 2 GiB | Public | raw | 10.00 GiB |

**选择镜像:** 点击表格中的行 `rowByText("TestVM")`。选择后底部显示 `Selected boot source: Image | TestVM`

#### 1.7 Flavor 表格

**分类标签页(水平列表):**

| 分类 | 说明 |
|------|------|
| General Computing | 通用计算(默认) |
| Computing Optimized | 计算优化 |
| Network Optimized | 网络优化 |
| Computing Network Optimized | 计算网络优化 |
| GPU-accelerated | GPU 加速 |

**表格列:** Flavor Name, vCPU, Memory, Access Control, vCPU Model

**General Computing 分类下的 Flavor(前 10 个,共约 30-40 个):**

| Flavor Name | vCPU | Memory |
|-------------|------|--------|
| **1C-1G** | 1 | 1 GiB |
| 1C-2G | 1 | 2 GiB |
| 1C-4G | 1 | 4 GiB |
| 2C-1G | 2 | 1 GiB |
| 2C-2G | 2 | 2 GiB |
| 2C-4G | 2 | 4 GiB |
| 2C-8G | 2 | 8 GiB |

#### 1.8 Root Disk 配置

**容器:** `.row.system-disk`

| 字段 | 组件 | 说明 |
|------|------|------|
| Volume Type | nz-select 下拉 | 默认 `hdd` |
| Size | nz-input-number.storage-size | 容量(GiB),默认 1 |
| Delete with Instance | checkbox | 是否随实例删除 |

#### 1.9 Data Disk 配置

- 显示文本: `You have selected 0 data disks and can select 24 more.`
- **添加按钮:** `.add-datadisk-container`(点击文本链接)
- 最多可添加 24 块数据盘
- 每块可配置: Volume Type, Size, Delete with Instance
- ⚠️ **注意:** 创建云主机时添加的数据盘无法自定义名称,名称由系统自动生成

### Step 2: Network Configuration(网络配置)

#### 2.1 vNIC 配置

**容器:** `.network-container`(ant-card)

| 字段 | 组件 | 说明 |
|------|------|------|
| Network | `.network-select`(ant-select,可搜索) | 选择网络 |
| Subnet | `.subnet-select`(自动填充) | 选择子网 |
| IP 分配 | Radio | `Automatically assign IPv4 address`(默认) |
| 剩余 IP | 显示文本 | `Remainning IP Available: 65527` |

**添加 vNIC:** 点击文本链接添加,最多 12 块
**删除 vNIC:** `.network-delete`(悬停显示)

**可用网络(示例):**
- `<PRIVATE_NETWORK_A>` (Project Exclusive, AZ: `<AZ>`)
- network_normal_user (Project Exclusive, AZ: default-az)
- public_net_2 (Project Exclusive, AZ: default-az)
- vpc-b-1 (Project Exclusive, AZ: default-az)
- `<PRIVATE_NETWORK_B>` (Project Exclusive, AZ: `<AZ>`)

#### 2.2 Security Group 配置

**容器:** `.security-group-container`(ant-card)

| 字段 | 组件 | 说明 |
|------|------|------|
| Type | Radio | `Stateful`(默认)/ `Stateless` |
| Security Group | `.security-group-select`(ant-select,可搜索,支持多选) | 安全组 |
| View Rules | 链接 | 打开详情面板,显示 Ingress/Egress Rules |

**安全组规则表列:** Type, Protocol, Port Range, Source

### Step 3: System Configuration(系统配置)

#### 3.1 Name(必填)

- **定位方式:** `input[name="config.name"]`
- **占位符:** `Enter 1 to 128 characters in length`

#### 3.2 Login Credentials(登录凭证)⭐ 必填

**三个单选选项:**

| 选项 | 说明 |
|------|------|
| SSH Key Pair | 推荐。选择已有密钥对 |
| Password | 设置密码 |
| Both | 同时设置密钥对和密码 |

**SSH Key Pair 模式:**
- 下拉选择已有密钥对(如 `pgc`)
- 提示: "SSH key pair is recommended. Please keep the private key secure."

**Password 模式:**
- `Password` 输入框(type: password)
- `Confirm Password` 输入框(type: password)

**Both 模式:**
- SSH Key Pair 下拉 + Password 输入框
- 用户名显示: `root`(只读)

#### 3.3 Tags

- Tag 输入区域,最多 20 个标签

#### 3.4 Advanced Options(高级选项,默认折叠)

**展开/折叠:** 点击 `agent-browser find text "Show" click` /
`agent-browser find text "Hide" click`

| 字段 | 类型 | 说明 |
|------|------|------|
| Compute Node | Radio | `Intelligent scheduling`(默认)/ `Specify manually` |
| Instance Group | 下拉 | 选择实例组(亲和/反亲和) |
| Instance Start Mode | Radio | `BIOS`(默认)/ `UEFI` |
| User Data | Radio + Textarea | `As text` / `As file`;最大 16KiB |
| Mount ISO | 添加按钮 | 点击 "Add" 挂载 ISO |
| Mount USB | 提示文本 | 需手动指定物理节点 |
| Boot Order | 输入框 | 默认 `1` |
| Root Disk | 显示 | 显示已选根盘信息 |
| Instance Monitor | checkbox | "Enable instance detailed monitor" |

### Step 4: Confirm(确认)

显示 **Configuration Overview** 摘要,分 3 个区域:

#### Basic Configuration 区域
- Resource Pool, Availability Zone, Project
- Boot Source, Boot Source Name
- Flavor(含分类、vCPU、内存)
- Root Disk, Data Disk

#### Network Configuration 区域
- vNIC(网络、子网、CIDR)
- IPv4 Address 分配方式
- Security Group

#### System Configuration 区域
- Name, Instance Group
- Boot Order(Root Disk)
- Login Credentials
- Tag, Chipset Type, Start Mode
- ISO/USB Mounted, Compute Node
- Instance Monitor

**每个区域有 "edit" 链接**,点击可跳转回对应步骤修改。

**最终操作按钮:** `byText("button.ant-btn-primary", "Confirm")` — 点击创建实例。
