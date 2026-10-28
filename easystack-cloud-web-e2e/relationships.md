# Relationships

Use this file when a UI test spans multiple resource types, such as instance plus volume, instance plus floating IP, or network plus router. For the actual browser action, switch to the corresponding `patterns/*-ops.md` file.

## Resource Relationships 核心关系图

```
                         ┌──────────────────────────────────────┐
                         │           云主机 (Instance)            │
                         │                                      │
                         │  创建向导 Step 1: 基础配置             │
                         │  ├─ Flavor (vCPU / 内存)              │
                         │  ├─ Root Disk ───────────────────────┼──→ 云硬盘 (Volume)
                         │  └─ Data Disk (0~24 块) ─────────────┼──→ 云硬盘 (Volume)
                         │                                      │
                         │  创建向导 Step 2: 网络配置             │
                         │  ├─ vNIC #1 ─────────────────────────┼──→ 网络 (Network) + 子网 (Subnet)
                         │  ├─ vNIC #2 (可选, 最多 12 块) ──────┼──→ 网络 (Network) + 子网 (Subnet)
                         │  └─ Security Group                   │
                         │                                      │
                         │  More → Network:                     │
                         │  ├─ Associate Floating IP ───────────┼──→ 浮动 IP (Floating IP)
                         │  ├─ Disassociate Floating IP         │
                         │  ├─ Associate Network ───────────────┼──→ 额外网络
                         │  └─ Disassociate Network             │
                         │                                      │
                         │  More → Storage:                     │
                         │  ├─ Attach Volume ───────────────────┼──→ 云硬盘 (Volume)
                         │  └─ Detach Volume                    │
                         │                                      │
                         │  详情页标签页:                         │
                         │  ├─ Summary   → 基本信息 + 监控 + VNC │
                         │  ├─ Storage   → Root Disk + Data Disk │
                         │  └─ Networks  → vNIC + IP + SG        │
                         └──────────────────────────────────────┘
```

## Instance Networks 1. 云主机 ↔ 网络 (Instance → Network)

**关联方式:vNIC(虚拟网卡)**

### Network Attachment 网络绑定 / 解绑操作

| 场景 | 操作入口 | 说明 |
|------|----------|------|
| 创建时绑定 | 创建向导 Step 2: Network Configuration | 选择 Network + Subnet,自动创建 vNIC |
| 创建后绑定额外网络 | More → Associate Network | 新增一个 vNIC |
| 创建后解绑网络 | More → Disassociate Network | 移除指定 vNIC |

### Network Rules 网络关键规则

- 一个实例可绑定**最多 12 个 vNIC**
- 每个 vNIC 连接**一个网络 + 一个子网**
- 每个 vNIC 自动分配一个 **IPv4 地址**(从子网 CIDR 中分配)
- vNIC 创建后出现在 vNIC 页面(`/ens/nics`)
- vNIC 可通过 vNIC 页面的 **Attach to resource / Detach from resource** 迁移到其他实例

### Network Wizard Fields 创建向导 Step 2 字段

| 字段 | 组件 | 说明 |
|------|------|------|
| Network | `ant-select`(可搜索) | 选择网络 |
| Subnet | `ant-select`(自动填充) | 选择子网 |
| IP 分配 | Radio | `Automatically assign IPv4 address`(默认) |
| 剩余 IP | 显示文本 | `Remaining IP Available: N` |

### Network Examples 可用网络示例

- `<PRIVATE_NETWORK>` (Project Exclusive, AZ: `<AZ>`)
- `<EXTERNAL_NETWORK>` (Project Exclusive, AZ: `<AZ>`)
- `<VPC_NETWORK>` (Project Exclusive, AZ: `<AZ>`)

---

## Instance Floating IPs 2. 云主机 ↔ 公网 IP (Instance → Floating IP)

**关联方式:Floating IP 绑定到 vNIC**

### Floating IP Association 公网 IP 绑定 / 解绑操作

| 场景 | 操作入口 | 前置条件 |
|------|----------|----------|
| 绑定公网 IP | More → Associate Floating IP | 路由器需设置网关 |
| 解绑公网 IP | More → Disassociate Floating IP | 已有绑定的 Floating IP |

### Associate Floating IP 弹窗字段

| 字段 | 必填 | 说明 |
|------|------|------|
| Instance Name | ❌ | 只读,预填当前实例名 |
| Instance Nic | ✅ | 下拉选择实例的 vNIC(显示 `网卡名: IP`) |
| Floating IP | ✅ | 下拉选择可用的 Floating IP(状态为 Unbound) |

### Floating IP Rules 公网 IP 关键规则

- Floating IP 绑定到**特定 vNIC**,不是绑定到实例整体
- 一个 vNIC 只能绑定**一个** Floating IP
- 多 vNIC 场景下可为**不同 vNIC 绑定不同** Floating IP
- 绑定 Floating IP **需要路由器已设置网关**
- Floating IP 本身在 Floating IP 页面(`/ens/floatingIPs`)独立管理
- 删除实例时 Floating IP **自动解绑**(不删除)

### Data Flow 数据流

```
用户 → Floating IP (公网) → 路由器网关 → 外部网络
                                         ↓
实例 ← vNIC (私网 IP) ← 子网 ← 路由器 ← Floating IP
```

---

## Instance Volumes 3. 云主机 ↔ 云硬盘 (Instance → Volume)

**关联方式:Root Disk / Data Disk + Attach / Detach**

### Volume Attachment 挂载 / 卸载操作

| 场景 | 操作入口 | 说明 |
|------|----------|------|
| 创建时挂载系统盘 | 创建向导 Step 1: Root Disk | 配置 Type + Size |
| 创建时挂载数据盘 | 创建向导 Step 1: Data Disk | 最多添加 24 块 |
| 创建后挂载数据盘 | More → Attach Volume | 选择 Available 状态的卷 |
| 创建后卸载数据盘 | More → Detach Volume | 热卸载,数据不丢失 |

### Attach Volume 弹窗字段

| 字段 | 必填 | 说明 |
|------|------|------|
| Instance Name | ❌ | 只读,预填当前实例名 |
| Volume | ✅ | 下拉选择可用卷(状态为 Available) |

### Root Disk vs Data Disk 系统盘与数据盘

| 属性 | Root Disk(系统盘) | Data Disk(数据盘) |
|------|---------------------|---------------------|
| 创建时机 | 创建实例时 | 创建实例时 / 后续挂载 |
| 数量 | 1 块 | 0~24 块 |
| 在线卸载 | ❌ 不支持 | ✅ 支持热插拔 |
| 删除行为 | 受 `Delete with Instance` 控制 | 受 `Delete with Instance` 控制 |
| 来源 | Image / Instance Snapshot / Volume Snapshot | Empty Volume / Image / Snapshot |

### Volume Rules 云硬盘关键规则

- 云硬盘创建后状态为 **Available**,才能被挂载
- 挂载后状态变为 **In use**
- 卸载后状态恢复为 **Available**
- `Delete with Instance` 勾选后,删除实例时云硬盘**一并删除**
- 云硬盘在云硬盘页面(`/ebs/volumes`)独立管理

### Volume Sources 创建云硬盘来源

| 来源 | 说明 | 额外字段 |
|------|------|----------|
| Empty Volume | 空白卷 | 无 |
| Image | 从镜像创建 | 选择镜像 |
| Instance Snapshot | 从实例快照创建 | 选择快照 |
| Volume Snapshot | 从卷快照创建 | 选择快照 |

---

## Lifecycle Changes 4. 完整生命周期中的关联变化

### Create Instance 创建实例

```
创建实例
  ├─ Root Disk:    创建 Volume → 自动挂载
  ├─ Data Disk:    创建 Volume → 自动挂载
  └─ vNIC #1:      创建 vNIC → 绑定 Network + Subnet
```

### Running Instance Actions 运行中操作

```
运行中 (Active)
  ├─ More → Attach Volume         → 挂载新 Data Disk
  ├─ More → Detach Volume         → 卸载 Data Disk
  ├─ More → Associate Floating IP → 绑定公网 IP 到 vNIC
  ├─ More → Disassociate Floating IP → 解绑公网 IP
  ├─ More → Associate Network     → 创建 vNIC #2
  ├─ More → Disassociate Network  → 移除 vNIC #2
  └─ More → Edit Security Group   → 修改安全组规则
```

### Delete Instance 删除实例

```
删除实例(默认:移入回收站)
  ├─ Floating IP:  自动解绑
  ├─ Data Disk:    自动解绑(保留,不删除)
  ├─ vNIC:         删除
  └─ Root Disk:    根据 Delete with Instance 决定

Force Delete(强制删除)
  ├─ Floating IP:  自动解绑
  ├─ Data Disk:    不删除(保留)
  ├─ vNIC:         随实例删除
  └─ Root Disk:    根据 Delete with Instance 决定
```

### Restore Instance 回收站恢复

```
恢复实例
  ├─ vNIC:         重新激活
  ├─ Data Disk:    重新挂载
  └─ Floating IP:  不自动恢复(需手动重新绑定)
```

---

## Resource Pages 5. 资源页面入口对照

| 资源 | 页面 URL | 管理操作 |
|------|----------|----------|
| 云主机 | `/eec/instances` | 创建、删除、挂载、网络绑定 |
| 云硬盘 | `/ebs/volumes` | 创建、删除、快照 |
| 网络 | 当前主路径:`/ens/networks`;历史/别名路径:`/neutron/networks` | 创建、子网管理 |
| vNIC | 当前主路径:`/ens/nics`;历史/别名路径:无 | 创建、挂载/卸载到实例 |
| 路由器 | 当前主路径:`/ens/routers`;历史/别名路径:`/neutron/routers` | 创建、网关设置、子网连接 |
| 浮动 IP | 当前主路径:`/ens/floatingIPs`;历史/别名路径:`/eec/floating-ips`、`/neutron/floatingips` | 分配、释放、绑定/解绑 |
| 安全组 | Access Control 菜单 | 规则管理 |

---

## Test Focus 6. 测试关注点

### Cross Resource Cases 跨模块联动测试

| 测试场景 | 涉及模块 | 关键验证点 |
|----------|----------|------------|
| 创建多网卡实例 | Instance + Network | 2+ vNIC 分别绑定不同网络 |
| 绑定公网 IP 后访问 | Instance + Floating IP + Router | 路由器网关 → Floating IP → vNIC 链路 |
| 热挂载数据盘 | Instance + Volume | Attach 后实例内可见新磁盘 |
| 热卸载数据盘 | Instance + Volume | Detach 后数据不丢失 |
| 回收站恢复后关联 | Recycle Bin + Network + Volume | 恢复后 vNIC/Volume 状态恢复 |
| 多 vNIC 绑定不同 Floating IP | Instance + vNIC + Floating IP | 每个 vNIC 独立绑定 |
| 删除实例后资源清理 | Instance + Volume + Floating IP | 验证解绑/保留行为 |
| 从可启动卷创建实例 | Instance + Volume | Bootable Volume 作为启动源 |

### Prerequisite Checks 前置条件检查

| 联动测试 | 前置条件 |
|----------|----------|
| 绑定 Floating IP | 需要路由器已设置网关 + 有可用 Floating IP |
| Attach Volume | 需要有 Available 状态的云硬盘 |
| Associate Network | 需要有可用的网络 + 子网 |
| 创建多网卡实例 | 需要有多个网络 + 子网可用 |
