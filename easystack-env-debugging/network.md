# Network Diagnostics 网络排查

访问环境确认后, 如需检查网络问题, 阅读本文件。内容聚焦节点连通性、ARP、
VLAN 子接口以及相关只读诊断。

节点间网络连通性排查的方法论,适用于 EasyStack 环境中的多网平面场景。

## Network Planes 网络平面速查

EasyStack 环境中常见的网桥及其用途:

| 网桥名称 | 典型用途 | 说明 |
|----------|---------|------|
| `br-mgmt` | 管理网 | 节点管理、OpenStack 内部 API 通信 |
| `br-pub` | 公网/外部网络 | 外网流量、云主机浮动 IP |
| `br-storage` | 存储后端网 | Ceph/RBD 后端存储流量 |
| `br-storagepub` | 存储公网 | 存储对外通信 |
| `br-vxlan` | VXLAN 隧道网 | Overlay 网络 |
| `br-roller` | 部署/运维网 | Ansible/Roller 部署通信 |
| `br-ipmi` | IPMI/带外网 | BMC 管理 |
| `br-ex` | 外部网络 | Provider 网络出口 |

## Network Diagnosis 节点间排查流程

### Step 1: 确认本机网络身份

```bash
# 查看所有 IP
hostname -I

# 查看本机名
hostname

# 确认核心网络接口和 IP
for iface in $(ip -o link show | grep -vE 'veth|tap|cali|tunl|cni' | \
  awk -F': ' '{print $2}'); do
  echo "--- $iface ---"
  ip addr show $iface 2>/dev/null | grep -w inet
done
```

### Step 2: 确认对端可达性

> ⚠️ **重要: 确认对端节点可达性时使用节点名称, 不直接使用 IP。**
> 原因: 节点有多个 IP 分布在不同的网平面(管理网、存储网、VXLAN 等),
> `/etc/hosts` 由部署工具维护,解析到**当前可用的正确网络**。
> 如果直接使用 IP,可能无意间指定了当前有问题的网络,导致误判。
> 只有在不知道节点名称与 IP 的对应关系、或正在排查某个明确 IP/网段时, 才使用 IP。

```bash
# ✅ 正确: 通过主机名访问 — 自动选择可达网络
ping -c 2 -W 2 node-<xxx>

# 仅在不知道节点名称与 IP 对应关系时使用 IP
ping -c 2 -W 2 <目标IP>
```

如果主机名能 ping 通,说明:
- DNS/hosts 解析正常
- 至少有一条网络路径可达
- 对端节点在线

### Step 3: 检查目标网络的接口状态

```bash
# 物理网卡状态
ip link show | grep -E 'enp|eth'

# VLAN 子接口/专用接口状态
ip -d link show <interface-name>
```

关注标志:
- `UP` + `LOWER_UP` = 物理链路正常
- `UP` + `NO-CARRIER` = 接口 config 了但没有线或对端不通
- `DOWN` = 接口被 admin down

### Step 4: 检查目标网络的路由

```bash
ip route show | grep <目标网段>
```

确认路由指向正确的设备。

### Step 5: 🔑 ARP 诊断(最关键)

```bash
# 查看特定 IP 的 ARP 状态
ip neigh show | grep <目标IP>

# 或者过滤特定网段
ip neigh show | grep <网段前缀>
```

**ARP 状态解读:**

| ARP 状态 | 含义 | 诊断结论 |
|----------|------|---------|
| `REACHABLE` | 最近通信成功 | ✅ L2 正常 |
| `STALE` | 缓存需重新确认 | 不能单凭缓存判断当前连通性 |
| `INCOMPLETE` | 发送了 ARP 请求但未收到响应 | ⚠️ L2 可能有问题 |
| `FAILED` | 邻居发现尝试未成功 | 检查目标、接口、二层路径和过滤, 不直接归因 |

**`FAILED` 只能说明本轮邻居发现未成功:**
- 先核对目标是否在预期链路、接口和路由是否选择正确。
- 对端离线、VLAN、链路、桥接/ARP 过滤或短时状态都可能相关, 需交叉取证。
- 传统 IP 层规则不直接处理 ARP, 但不能据此排除所有过滤机制或断言 VLAN 根因。

### Step 6: Ping 验证

```bash
# 优先 ping 节点名称
ping -c 3 -W 2 node-<xxx>

# 排查特定网段或不知道节点/IP 对应关系时再 ping IP
ping -c 3 -W 2 <目标IP>
```

邻居缓存状态可能在下一次探测时改变。结合本轮 ping 的目标、路由和实时邻居状态判断。
ARP 成功但 ICMP 失败还需核对对端 ICMP 策略、路径、过滤和丢包, 不直接限定为某一层根因。

### Step 7: 对端交叉验证

通过统一访问脚本进入环境后, 从当前节点 SSH 到对端节点, 在对方也执行同样的检查:

```bash
ssh node-<xxx> 'ip neigh show | grep <目标网段>'
ssh node-<xxx> 'ip -d link show ipsan-0'
ssh node-<xxx> 'ping -c 2 -W 2 <本机IP>'
```

确保两边现象对称(单通还是双不通)。

### Step 8: 查看 VLAN 配置(只读)

```bash
# 查看 VLAN 子接口的 VID
ip -d link show <vlan-interface>

# 查看 ifcfg 配置(只读)
cat /etc/sysconfig/network-scripts/ifcfg-<interface-name>
```

cat 命令如果被安全模块拦截禁止,说明环境有命令审计/过滤机制。

## VLAN 子接口排查

VLAN 子接口在输出中显示为 `@物理接口`,例如 `ipsan-0@enp130s0f0np0`。

检查要点:
```bash
# 确认 VLAN ID
ip -d link show ipsan-0 | grep vlan
# 应看到: vlan protocol 802.1Q id <VID> <REORDER_HDR>

# 确认 ifcfg 中的 VID 与对端一致
cat /etc/sysconfig/network-scripts/ifcfg-ipsan-0
# 关注: VID, PHYSDEV, IPADDR, PREFIX, MTU
```

两侧节点的以下参数必须**一致**:
- VLAN ID (VID)
- MTU
- 网络类型(802.1Q)
- 网段/Prefix

## Cause Candidates 原因候选

| 现象 | 可能原因 |
|------|---------|
| 物理接口 `NO-CARRIER` | 网线/光模块/交换机端口故障 |
| 物理接口 `UP`, ARP `FAILED` | 目标离线、VLAN/链路、接口选择或过滤等候选, 需两端核对 |
| ARP `REACHABLE`,ping 100% loss | 防火墙/iptables/路由 ACL |
| 本端 ARP `FAILED`, 对端 ARP `REACHABLE` | 核对缓存时间和实时双向探测, 不直接判定单通 |
| 接口 `UP` 但 `ip addr` 无 IP | 接口未配 IP 或 DHCP 失败 |
| `cat ifcfg-*` 被拦截 | 环境有命令审计/安全模块 |
| VLAN 接口 `DOWN` | 父接口未 UP 或 VLAN 模块未加载 |

## Diagnostic Output 诊断输出

建议将诊断输出保存到文件以备后续分析:

```bash
# 一次性收集网络诊断信息
{
  echo "=== HOSTNAME ===" && hostname
  echo "=== IPs ===" && hostname -I
  echo "=== INTERFACES ===" && ip link show | grep -E '^[0-9]+:' | grep -vE 'veth|tap|cali'
  echo "=== ADDRS ===" && ip addr show | grep -E 'inet '
  echo "=== ROUTE ===" && ip route show
  echo "=== ARP ===" && ip neigh show
  echo "=== ERRORS ===" && ip -s link show | grep -E 'errors' -A1
} > /tmp/netdiag_$(hostname -s).txt
```
