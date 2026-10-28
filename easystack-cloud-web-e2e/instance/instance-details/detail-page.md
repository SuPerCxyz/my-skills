# Detail Page

> 来源:`easystack-cloud-web-e2e/instance/instance.md`,按原文标题边界拆分。

## Details Entry And Tabs 页面入口与标签页

### Details Entry 详情页面入口

- 点击实例列表中的实例名称进入详情页面
- URL: `/eec/instances/<instance-uuid>`

### Details Tabs 详情页面标签页

| 标签 | 定位方式 | 内容 |
|------|--------|------|
| Summary | `byText(".ant-tabs-tab-btn", "Summary")` | 基本信息、监控指标、VNC、详细配置 |
| Storage | `byText(".ant-tabs-tab-btn", "Storage")` | 存储详情(Root Disk、Data Disk) |
| Networks | `byText(".ant-tabs-tab-btn", "Networks")` | 网络详情(vNIC、IP、Security Group) |

### Summary 标签页

- **Basic Information**: 实例基本信息
- **监控指标**: vCPU / Memory / Disk / Network 使用率图表
- **VNC Console**: 嵌入式 VNC 控制台
  - 连接状态: "Connected (encrypted) to: QEMU (instance-0000054e)"
  - VNC 链接: `/eec/vnc/<instance-uuid>`
- **Detailed Configuration**: 详细配置信息

### Storage 标签页

- **Root Disk 详情**:
  - 名称: `<instance-name>_root_disk`
  - 容量: 1 GiB
  - 类型: hdd
  - 状态: In use

### Networks 标签页

- **vNIC 详情**:
  - 状态: Active
  - MAC 地址
  - IPv4 地址
  - Security Group
