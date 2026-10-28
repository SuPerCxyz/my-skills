# Overview

> 来源:`easystack-cloud-web-e2e/instance/instance.md`,按原文标题边界拆分。

## Compute Documents 计算大类文档索引

| 功能 | 文件 |
|------|------|
| 云主机(Instance) | [instance.md](../instance.md) |
| 云主机快照(Instance Snapshot) | [snapshot.md](../snapshot.md) |
| 云主机回收站(Instance Recycle Bin) | [recycle-bin.md](../recycle-bin.md) |
| 云主机分组(Instance Group) | [group.md](../group.md) |
| SSH 密钥对(SSH Key Pair) | [keypair.md](../keypair.md) |
| 实例规格(Instance Flavor) | [flavor.md](../flavor.md) |
| 可用域与主机聚合(AZ & Host Aggregates) | [az.md](../az.md) |
| 计算节点(Compute Node) | [compute-node.md](../compute-node.md) |

## Page Information 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/eec/instances` |
| 创建页 URL | `https://<IP>/eec/instances/create-instance` |
| 导航路径 | Service Catalog → Computing → Instance |
| 页面标题 | EasyStack Cloud |

## Page Description 页面说明

云主机是在安全隔离环境中运行的虚拟服务器,是基础计算单元,由 vCPU、内存、操作系统、网络和云硬盘组成。创建后可以根据需要修改规格,确保高效、可靠、安全的计算环境。

## Page Buttons 页面按钮

| 按钮 | 定位方式 | 状态 | 说明 |
|------|--------|------|------|
| Create Instance | `buttonByText("Create Instance")` | 始终可用 | 创建新实例 |
| Start | `buttonByText("Start")` | 需选择已关机实例 | 启动实例 |
| Shutoff | `buttonByText("Shutoff")` | 需选择运行中实例 | 关闭实例 |
| Reboot | `buttonByText("Reboot")` | 需选择运行中实例 | 重启实例 |
| More | `buttonByText("More")` | 需选择实例 | 更多操作 |

## Table Columns 表格列信息

| 列名 | 说明 |
|------|------|
| Name | 实例名称 |
| Availability Zone / Node | 可用域 / 节点 |
| Status / Monitor | 状态 / 监控 |
| Flavor / Boot Source | 规格 / 启动源 |
| IP Address | IP 地址 |
| Domain / Project | 域 / 项目 |
| Created Time | 创建时间 |
| VNC | VNC 远程连接 |

## Instance States 实例状态

| 状态 | 说明 |
|------|------|
| Active | 运行中 |
| Shutoff | 已关机 |
| Error | 错误状态 |
| Building | 创建中 |
| Rebooting | 重启中 |
| Migrating | 迁移中 |
| Paused | 已暂停 |
| Suspended | 已挂起 |
