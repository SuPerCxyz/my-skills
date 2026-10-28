# Page

> 来源:`easystack-cloud-web-e2e/network/vnic.md`,按原文标题边界拆分。

## Page Information 页面信息

| 项目 | 值 |
|------|-----|
| URL | 当前主路径:`https://<IP>/ens/nics` |
| 历史/别名路径 | 无 |
| 导航路径 | Network → vNIC |
| 页面标题 | vNIC |

## Page Description 页面说明

vNIC(弹性网络接口)绑定实例到私有网络,可在多个实例间自由迁移。支持在实例上绑定多个 vNIC 实现高可用网络方案,也支持在 vNIC 上绑定双栈地址满足单卡多地址需求。

## Toolbar Buttons 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Creat vNIC | `buttonByText("Creat vNIC")` | 始终可用(注意:按钮文本有拼写错误,应为 Create) |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Attach to resource | `buttonByText("Attach to resource")` | 默认禁用,选中 1+ 行后可用 |
| Detach from resource | `buttonByText("Detach from resource")` | 默认禁用,选中 1+ 行后可用 |
| Delete vNIC | `buttonByText("Delete vNIC")` | 默认禁用,选中 1+ 行后可用 |
| More | `buttonByText("More")` | 默认禁用,选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## Status Filter 状态过滤下拉

定位方式:`nz-select`(含 "All Status" 文本)

| 状态值 | 说明 |
|--------|------|
| All Status | 默认,显示所有状态 |
| Active | 活跃状态 |
| Down | 禁用状态 |

## Filter Fields 过滤器字段

定位方式:`input[placeholder="Click here for filters."]`

| 过滤字段 |
|----------|
| Name |
| Tags |
| Status |
| Bandwidth |
| MAC Address |
| IP Address |
| Attach Resource |
| Floating IPs |
| Domain |
| Project |
| Creation Time |

## Table Columns 表格列(13 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | vNIC 名称,点击进入详情 |
| Tags | ❌ | 标签信息 |
| Status | ✅ | 状态:Active / Down |
| Bandwidth (Mbps) | ✅ | 带宽限制,如 "No limit" |
| MAC Address | ✅ | MAC 地址 |
| IP Address | ❌ | IPv4 和 IPv6 双栈地址 |
| Attach Resource | ✅ | 挂载的资源(如 Instance),可跳转 |
| Floating IPs | ✅ | 浮动 IP 地址 |
| Virtual IP | ❌ | 虚拟 IP 地址 |
| Supplementary private network IP | ❌ | 补充私有网络 IP |
| Domain / Project | ❌ | 域和项目 |
| Creation Time | ✅ | 创建时间 |

### Example Row 示例数据行

```
Name: <INSTANCE_VNIC_NAME>
Tags: -
Status: Down
Bandwidth: No limit
MAC Address: <MAC_ADDRESS>
IP Address: (IPv4) <PRIVATE_IP>, (IPv6) -
Attach Resource: Instance <INSTANCE_NAME>
Floating IPs: -
Virtual IP: -
Supplementary private network IP: -
Domain / Project: <DOMAIN> / <PROJECT>
Creation Time: <LOCAL_TIME>
```

## Setup 列配置

可配置列:Name、Tags、Status、Bandwidth(Mbps)、MAC Address、IP Address、Attach Resource、Floating IPs、Virtual IP、Supplementary private network IP、Domain/Project、Creation Time

按钮:Restore Defaults、Select All、Cancel、Confirm

## Pagination 分页

| 项目 | 值 |
|------|-----|
| 默认每页 | 10 条 |
| 每页定位方式 | 下拉,"10 / page" |
| 总数显示 | "Total N items, last updated [timestamp]" |
| 翻页 | 上一页/下一页、页码按钮 |
