# Page And Create

> 来源:`easystack-cloud-web-e2e/network/router.md`,按原文标题边界拆分。

## Page Information 页面信息

| 项目 | 值 |
|------|-----|
| URL | 当前主路径:`https://<IP>/ens/routers` |
| 历史/别名路径 | `https://<IP>/neutron/routers` |
| 导航路径 | Network → Router |
| 页面标题 | Routers |

## Page Description 页面说明

路由器由一系列路由规则组成,用于控制子网内外流量的入站和出站路由策略。可在路由器中连接子网、添加静态路由、设置网关,满足三层子网间的业务流量访问需求。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Router | `buttonByText("Create Router")` | 始终可用(蓝色主按钮) |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Delete Router | `buttonByText("Delete Router")` | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## Filter Fields 过滤器字段

定位方式:`input[placeholder="Click here for filters."]`

| 过滤字段 |
|----------|
| Name |
| Tags |
| Availability Zone |
| Node |
| External Network |
| Bandwidth |
| Gateway Firewall |
| NAT Gateway |
| Domain |
| Project |
| Creation Time |

## Table Columns 表格列(11 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 路由器名称,点击进入详情 |
| Tags | ❌ | 标签信息 |
| Availability Zone / Node | ✅ | 可用域和计算节点(两行显示) |
| External Network / IP | ✅ | 外部网络名和 IPv4/IPv6 地址 |
| Bandwidth (Mbps) | ✅ | 带宽,值如 "825" 或 "No limit" |
| Gateway Firewall | ✅ | 网关防火墙状态 |
| NAT Gateway | ✅ | NAT 网关状态 |
| Domain / Project | ❌ | 域和项目 |
| Creation Time | ✅ | 创建时间 |
| Action | ❌ | 行内操作:Clear Gateway / Edit / More |

### Row Actions 行内操作按钮

| 操作 | 说明 |
|------|------|
| Clear Gateway | 清除网关 |
| Edit | 编辑路由器 |
| More | 更多操作(下拉菜单) |

> **注意**:路由器页面没有独立的 Status 列。路由器状态通过外部网络/IP 关联情况、Gateway Firewall / NAT Gateway 列值体现。

## Setup 列配置

可配置列:Name、Tags、Availability Zone / Node、External Network / IP、Bandwidth(Mbps)、Gateway Firewall、NAT Gateway、Domain / Project、Creation Time、Action

按钮:Restore Defaults、Select All、Cancel、Confirm

## Create Router 页面

URL:当前主路径 `/ens/routers/creator`(独立页面,非弹窗)

历史/别名路径:`/neutron/routers/create`(仅作旧路径对照,不作为默认执行入口)

### Basic Fields 基础字段

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| Router Type | ✅ | 单选 | Regular Router / Container Router |
| Name | ✅ | 文本输入 | 1-128 字符 |
| Availability Zone | ✅ | 下拉选择 | 默认 default-az |
| Set the router gateway | ❌ | 开关 | 开启后显示网关配置区域 |

### Gateway Configuration 网关配置区域(开启网关后展开)

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| External Network | ✅ | 下拉选择 | 选择外部网络 |
| Gateway Type | ✅ | 单选 | IPv4 / IPv6 / Dual Stack |
| IPv4 Subnet | ✅ | 单选 | Auto Assign / Manual Selection |
| External IPv4 | ❌ | 文本输入 | 手动选择时填写 |
| IPv6 Subnet | ✅ | 单选 | Auto Assign / Manual Selection |
| External IPv6 | ❌ | 文本输入 | 手动选择时填写 |
| QoS | ❌ | 单选 | Disable / Enable |
| Bandwidth | ❌ | 数字输入 | 启用 QoS 后可设置带宽 |
| Turn on SNAT | ❌ | 开关 | 开启 SNAT |

### Router Connections 路由器连接区域

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| Connect the subnet | ❌ | 开关 | 开启后显示子网连接列表 |
| Subnet List | ❌ | 子网选择 | 选择要连接的子网 |
| Subnet IP | ❌ | 文本输入 | 子网 IP |
| Add Subnet | ❌ | 按钮 | 添加更多子网 |

### Container Router 模式额外字段

选择 Container Router 时,表单切换为 VPC 模式:

| 字段 | 必填 | 说明 |
|------|------|------|
| VPC Name | ❌ | VPC 名称 |
| Connect Subnet List | ❌ | 容器子网列表(Name、CIDR) |
| Add Container Subnet | ❌ | 添加容器子网 |

### Action Buttons 操作按钮

Cancel、Create Router(初始禁用,填写必填项后启用)
