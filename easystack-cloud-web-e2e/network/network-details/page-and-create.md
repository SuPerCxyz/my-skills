# Page And Create

> 来源:`easystack-cloud-web-e2e/network/network.md`,按原文标题边界拆分。

## Page Information 页面信息

| 项目 | 值 |
|------|-----|
| URL | 当前主路径:`https://<IP>/ens/networks` |
| 历史/别名路径 | `https://<IP>/neutron/networks` |
| 导航路径 | Network → Network |
| 页面标题 | Network |

## Page Description 页面说明

网络为用户创建了二层隔离的私有网络环境,可在其中定义三层子网。这些三层子网用于管理云主机、裸金属、容器等网络平面,提供 CIDR 管理、网关、DHCP 等服务。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Network | `buttonByText("Create Network")` | 始终可用(蓝色主按钮) |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Delete Network | `buttonByText("Delete Network")` | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## Filter Fields 过滤器字段

定位方式:`input[placeholder="Click here for filters."]`

| 过滤字段 |
|----------|
| Name |
| Tags |
| Domain |
| Project |
| Availability Zone |
| Network Type |
| Visibility |
| IPv4 Subnets |
| IPv6 Subnets |
| Network Mode |
| Layer 2 Bridging |
| ID |
| Creation Time |

## Table Columns 表格列(10 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 网络名称,点击进入详情 |
| Tags | ❌ | 标签信息 |
| Availability Zone | ✅ | 可用区,如 default-az |
| IP Address | ❌ | IPv4 CIDR 和 IPv6 地址 |
| Network Mode / ID | ❌ | 网络模式(Geneve / VLAN / Flat)和 ID |
| Layer 2 Bridging | ✅ | 二层桥接信息 |
| Domain / Project | ❌ | 域和项目 |
| Creation Time | ✅ | 创建时间 |
| Action | ❌ | 行内操作:Edit、Edit Tags、Delete |

## Setup 列配置

可配置列:Name、Tags、Availability Zone、IP Address、Network Mode / ID、Layer 2 Bridging、Domain / Project、Creation Time、Action

按钮:Restore Defaults、Select All、Cancel、Confirm

## Create Network 页面

URL:当前主路径 `/ens/networks/creator`(独立页面,非弹窗)

历史/别名路径:`/neutron/networks/create`(仅作旧路径对照,不作为默认执行入口)

### Basic Fields 基础字段

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| Network Type | ✅ | 单选 | Internal Network / External Network / Container Network |
| Name | ✅ | 文本输入 | 1-128 字符 |
| Availability Zone | ✅ | 下拉选择 | 默认 default-az |
| Visibility | ✅ | 单选 | Project Exclusive / Global Sharing |
| Network Mode | ✅ | 单选 | Geneve / VLAN / Flat(No VLAN) |
| Physical Network | ❌ | 文本输入 | 物理网络名称 |
| GENEVE VNI / VLAN ID | ❌ | 自动分配 | Automatic Allocation |
| Multicast | ❌ | 开关 | 启用/禁用组播 |
| Tag | ❌ | 标签输入 | 最多 20 个 |

### Subnet Configuration 子网配置(Subnet)

| 字段 | 必填 | 说明 |
|------|------|------|
| IPv4 Subnet Name | ✅ | 子网名称 |
| IPv4 Subnet CIDR | ✅ | 子网 CIDR |
| Gateway | ❌ | 启用网关地址 / 连接路由器 / 创建路由器 |
| DHCP Service | ❌ | DHCP 服务开关 |
| DNS Server Address | ❌ | DNS 服务器地址 |
| Address Pool Range | ❌ | 地址池范围 |
| Host Routes | ❌ | 主机路由 |

支持 Add IPv4 Subnet / Add IPv6 Subnet 添加多个子网。

### Action Buttons 操作按钮

Cancel、Create Network(初始禁用,填写必填项后启用)

## Pagination 分页

| 项目 | 值 |
|------|-----|
| 默认每页 | 10 条 |
| 每页定位方式 | 下拉,"10 / page" |
| 总数显示 | "Total N items, last updated [timestamp]" |
| 翻页 | 上一页/下一页、页码按钮 |
