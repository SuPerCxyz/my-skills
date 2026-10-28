# Platform Info

Use this file for stable platform facts, canonical page paths, and historical path aliases. Do not use it as an execution plan; combine it with [navigation.md](../navigation.md) and the relevant operation file.

| 项目 | 值 |
|------|-----|
| 平台名称 | EasyStack Cloud |
| 技术栈 | Angular + Ant Design (NG-ZORRO) |
| 证书 | 自签名 SSL 证书(浏览器上下文需允许忽略 HTTPS 证书错误) |

## Page URLs 页面 URL

| 页面 | 当前主路径 | 历史/别名路径 | 说明 |
|------|------------|---------------|------|
| 登录页 | `/auth_login/?next=<目标路径>` | 无 | 当前资料一致 |
| 概览页 | `/overview` | 无 | 当前资料一致 |
| 云主机页 | `/eec/instances` | 无 | 当前资料一致 |
| 云主机创建页 | `/eec/instances/create-instance` | 无 | 当前资料一致 |
| 云主机回收站 | `/eec/instance-recycle-bin` | 无 | 当前资料一致 |
| 云硬盘页 | `/ebs/volumes` | 无 | 当前资料一致 |
| 云硬盘快照页 | `/ebs/volume-snapshots` | 无 | 当前资料一致 |
| 云硬盘类型页 | `/ebs/volume-types` | 无 | 当前资料一致 |
| 容器镜像页 | `/container-registry/image` | 无 | 容器仓库 |
| VM 镜像页 | 从 Computing -> Instance Image 现场识别 | `/glance/images` 为历史线索 | 入口及字段需现场确认 |
| 网络管理页 | `/ens/networks` | `/neutron/networks` | 默认执行入口使用当前主路径 |
| 虚拟网卡页 | `/ens/nics` | 无 | 当前资料一致 |
| 路由器页 | `/ens/routers` | `/neutron/routers` | 默认执行入口使用当前主路径 |
| 浮动 IP 页 | `/ens/floatingIPs` | `/eec/floating-ips`、`/neutron/floatingips` | 默认执行入口使用当前主路径 |
| 计算节点页 | `/eec/hosts` | 无 | 当前控制台通过 Service Catalog -> Computing -> Compute Node 进入 |
| 用户管理页 | `/iam/users` | 无 | 当前控制台通过 Service Catalog -> Identity & Access Management -> User Management 进入 |

## Observed Catalog Groups 当前控制台模块分组

实际探索到的 `Service Catalog` 一级分组:

- Computing
- Product Service Management
- Block Storage
- Observability
- Configurations
- Network
- Operation
- Identity & Access Management
- Monitor & Management
