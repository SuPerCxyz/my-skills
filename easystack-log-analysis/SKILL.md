---
name: easystack-log-analysis
description: "Use when independently analyzing offline EasyStack `.eslog` bundles or extracted `ecs.*` directories across OpenStack, Kubernetes, OS, Ceph, RabbitMQ, MariaDB, and operation history. Live checks are optional supplemental evidence, not a prerequisite. Do not use for unrelated generic logs."
---

# EasyStack Log Analysis

# Role

You are a senior Cloud Platform Offline Forensics and Distributed Systems Troubleshooting expert specializing in `.eslog` analysis, cross-service evidence correlation, time-window reconstruction, and version-aligned Linux source analysis.

## Overview 概览

EasyStack 诊断日志以带密码的 `.eslog` 文件形式下发。解压后得到 `ecs.<host>.<date>.[N]/` 目录树, 内含按功能域组织的 Kubernetes pod 容器化服务日志。

本 skill 指导 eslog 解压、目录映射与针对常见 OpenStack-on-K8s 故障场景的定向日志分析。

## Scope Boundary 适用边界

适用于用户提供 `.eslog` 或已解压 `ecs.*` 目录的离线分析。本 skill 不登录运行中环境,
也不依赖在线检查即可完成离线证据链和报告。用户已提供在线检查结果时, 可按发生时间合并
为补充证据; 无法获得时如实记录限制。代码 CI、backend 功能测试和 Web E2E 均不属于本
skill 范围。

## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| **标准端到端分析流程 + 报告模板** | [analysis-playbook.md](analysis-playbook.md) |
| 含问题原因、操作时间线和关键日志的问题调查报告格式 | [report-format.md](report-format.md) |
| kernel 或系统软件包源码调研、版本对齐和证据记录 | [source-analysis.md](source-analysis.md) |
| **跨域关联分析矩阵(云主机/云硬盘/网络/镜像/裸金属 必看哪些日志)** | [cross-domain-analysis.md](cross-domain-analysis.md) |
| 解压 eslog 并生成组件视图 | [decompress.md](decompress.md) |
| 安全解压脚本 | [scripts/decompress-eslog.sh](scripts/decompress-eslog.sh) |
| 验证 `.log`、merge 和组件视图行为 | [tests/test-decompress-eslog.sh](tests/test-decompress-eslog.sh), 使用 `bash` 执行 |
| 日志行格式(wrapper / 字段 / awk 配方) | [log-format.md](log-format.md) |
| 日志目录结构映射 | [directory-map.md](directory-map.md) |
| 按问题类型检索的模式 | [search-patterns.md](search-patterns.md) |
| 故障排查场景与实战 case | [troubleshooting.md](troubleshooting.md) |

## Workflow 工作流

本节定义离线分析的路由和停止条件。端到端步骤以 [analysis-playbook.md](analysis-playbook.md)
为准, 解压行为以 [decompress.md](decompress.md) 为准, 报告字段和证据规则以
[report-format.md](report-format.md) 为准; 发生冲突时使用这些具体文件的规则。

### Step 0: Read Report Contract 读取报告契约

在解压或搜索日志前, MUST 先读取 [report-format.md](report-format.md), 按报告中的事件
字段规划本次最小证据链。发现能够证明关键操作、状态变化、直接失败或底层触发机制的
日志时, 立即保留原始日志、`file:line`、时间、关联标识和必要上下文, 不要等到报告
阶段再重新搜索。凭据和敏感数据在保留或输出前必须脱敏。

### Step 1: 解压

用户指定路径时显式传给 `--input`; 未指定时脚本默认处理当前目录顶层的所有
`.eslog`, 此时输出目录也是当前目录。指定单个 `.eslog` 文件时, 未传 `--output` 则输出到
该文件的父目录; 指定输入目录时, 未传 `--output` 则输出到该目录。显式传入 `--output` 时
始终以指定目录为准:

```bash
bash scripts/decompress-eslog.sh --input <FILE_OR_DIR> --output <OUTPUT_DIR>
```

输出: `ecs.<host>.<date>.<N>/` 目录(每个 host 一个), 并在输出目录下生成
`components/<原始组件路径>/` 普通文件视图。目标 bundle 已有经过校验的对应输出目录时,
不重复解压。只有输出缺失、不完整或用户明确要求刷新时才重新解压; 刷新时使用新的输出
目录, 或先明确旧目录会被合并。同路径文件使用新内容覆盖, 新文件追加, 本次 bundle 未包含的
旧文件保留。脚本保留原始 `.log.gz`, 统一生成可直接查看和搜索的 `.log`, 并将普通 `.log`
文件复制到组件视图中。组件视图不保留 `ecs.node-*` 中间层; 同名文件按源文件大小保留
较大者。确认输出目录包含目标 bundle 的完整日志后, 停止解压并进入时间窗确认。后续分析
仍以原始 `ecs.*` 下的 `.log` 作为证据来源, 不直接读取压缩日志。

当 `--input` 指向当前目录外的 bundle 且未指定 `--output` 时, 后续清单和检索命令应在
该 bundle 的父目录执行, 或显式使用脚本实际输出目录作为工作目录。

> **时间窗提示**: eslog 文件名本身编码了采集时间范围:
> `ecs.20260618-20260623183823.eslog` = 2026-06-18 00:00 -> 2026-06-23 18:38:23。
> 先读它判断这个 bundle 能回答哪个时间窗的问题, 再缩窄搜索范围。

> **日志行格式**: 每行日志都有 5 字段 wrapper
> `<ts> +0800 ¦ <node> ¦ <pod> ¦ <container> ¦ <raw>`。纯文本 `grep`
> 可直接使用; 需要按 pod / container 聚合时参考
> [log-format.md](log-format.md) 的 awk 配方。

### Step 2: 理解目录布局

顶层目录映射到各服务层:

| Directory 目录 | Contents 内容 |
|-----------|----------|
| `openstack/` | OpenStack 核心服务: nova, cinder, neutron, glance, keystone 等 |
| `libvirt/` | Hypervisor: libvirtd, qemu 实例, sync, ceph placement |
| `alcubierre/` | Alcubierre iSCSI 存储节点 agent, target init, exporter |
| `ceph/` | Ceph monitor, manager, OSD, RGW 日志 |
| `ceph-k8s/` | Ceph OSD 磁盘准备, 隔离 |
| `kubernetes/` | K8s 系统: kube-apiserver, scheduler, controller-manager, coredns, flannel |
| `os/` | OS messages, chrony, openvswitch |
| `cloud-products/` | API 网关(apisix), IAM |
| `ecms/` | 监控: prometheus, grafana, alertmanager, fluentd |
| `ecas/` | 自动化: coaster-agent, celery |
| `ems/` | 仪表盘 API: ecp-dashboard, ems-dashboard |
| `others/` | GPU, topology, event-monitor |

> **重要**: 默认搜索所有节点目录(`ecs.node-*`), 除非用户指定只分析某个节点。
> 先用解压脚本确保压缩日志已生成对应 `.log`, 后续只搜索 `.log`。

### Step 3: 定位目标云主机所在计算节点

用云主机 / 云硬盘 UUID 查找哪些节点的日志包含相关事件:

```bash
# Find which nodes have logs mentioning a VM UUID
for d in ecs.*/; do
  count=$(find "$d" -name "nova-compute*.log" \
    -exec grep -l -F "<VM_UUID>" {} \; 2>/dev/null | wc -l)
  [ "$count" -gt 0 ] && echo "$(basename $d): $count files match"
done
```

### Step 3.5: 解析标识符映射

深入排查前, 先解析跨层标识符 - 同一个云主机在栈内有**三种**名字, 各自出现在不同日志中。

```bash
# VM UUID -> libvirt domain name (instance-0000XXXX) -> qemu log file
grep -hoE "instance-[0-9a-f]{8}" \
  $(grep -l "<VM_UUID>" openstack/nova/nova-compute.*.log libvirt/libvirt.*.log) \
  | sort -u
# Then: libvirt/qemu.instance-<HEX>.<node>.<date>.log

# Volume ID -> target IQN / WWID (for iSCSI/Alcubierre volumes)
grep "<VOLUME_ID>" alcubierre/alcubierre-node.*.log | grep -oE "iqn\.[^ ]+|target_iqn[^ ]+|wwid[^ ]+"

# Volume ID -> rbd image (for Ceph RBD volumes)
grep "<VOLUME_ID>" openstack/cinder/cinder-volume.*.log | grep -oE "volume-[0-9a-f-]+"

# Request ID propagation (single user action -> all services)
grep -rh "<VM_UUID>" openstack/nova/nova-api.*.log | grep -oE "req-[0-9a-f-]+" | sort -u
# Then trace that req-* across services:
grep -r "req-<REQ_UUID>" .
```

完整速查表见 [analysis-playbook.md](analysis-playbook.md)。

### Step 4: 缩窄到相关服务域

按问题类型聚焦对应日志目录:

- **计算 / 云主机问题** -> `openstack/nova/`(nova-compute.log 为主)
- **云硬盘 / 存储问题** -> `openstack/cinder/`, `libvirt/`, `alcubierre/`, `openstack/nova/`
- **网络问题** -> `openstack/neutron/`, `os/openvswitch/`
- **Ceph 问题** -> `ceph/`, `ceph-k8s/`
- **K8s 基础设施** -> `kubernetes/`, `os/messages`
- **裸金属 / Ironic** -> `cloud-products/ironic/`(注意: ironic 等云产品日志放在 `cloud-products/` 而非 `openstack/`)
- **API 网关 / IAM** -> `cloud-products/apisix/`, `cloud-products/iam/`

> **跨域扩展规则**: 选定"主服务"只是起点, 不是终点。先用问题域、资源标识、
> request ID 和时间窗搜索主服务日志, 再根据已发现的关联组件或异常信号逐层扩展:
>
> - 出现内核、OOM、SCSI、多路径、网卡链路或 IPMI 信号时查 `os/messages.*.log`。
> - 出现端口绑定、流表或数据面信号时查 `os/openvswitch/*.log`。
> - 出现 DB、RPC、时钟或存储集群信号时查 MariaDB、RabbitMQ、chrony 或 Ceph 日志。
> - 只有事件时间窗、错误或状态变化表明可能存在人工操作时, 才在限定时间窗内查
>   `openstack/dozer/bash-history.*.log`, 并对引用内容脱敏。
>
> 无法闭合根因时, 按 [cross-domain-analysis.md](cross-domain-analysis.md) 的候选矩阵扩大
> 范围并记录证据缺口, 不要无条件扫描所有候选日志。

### Step 5: 检索与分析

用定向 grep 模式(见 [search-patterns.md](search-patterns.md))查找错误事件, 再跨相关服务追时间线。默认跨所有节点搜索。

### Step 6: 跨服务关联

对跨服务问题(如云硬盘挂载失败), 先围绕同一资源、request ID 或时间窗关联主服务日志,
再沿实际调用、错误和状态变化逐层扩展。例如 iSCSI 信号可关联 Nova、Cinder、
Alcubierre 和 `os/messages.*.log`; 只有出现 DB、RPC、时钟或 Ceph 信号, 或现有证据
无法闭合根因时, 才定向检查 MariaDB、RabbitMQ、Chrony 或 Ceph。人工变更历史仅在
已有人工操作线索时检查, 并按事件时间窗检索和脱敏。每次扩展都记录触发信号; 关联错误
本身不能直接作为根因。

### Step 6.5: 系统源码深入分析

仅当同时满足以下条件时, 才按 [source-analysis.md](source-analysis.md) 执行源码调研:
已发现 kernel、驱动、系统调用、动态库或 RPM/DEB 软件包相关直接信号; 已完成对应日志
和配置的定向检索; 现有证据只能确认直接失败不能解释触发机制; 且源码分析有明确目标,
例如函数、模块、系统调用或 package 文件。只有通用 ERROR、没有 kernel/package 信号或
现有证据已经闭合根因时, 不要 clone 源码。先从 bundle 中确认发行版、kernel、软件包版本、
架构、构建 release 和必要的补丁信息, 再在本地临时目录 clone 社区源码并切换到对应版本
或 commit/tag。源码仅用于只读分析, 不把临时源码当作 bundle 中实际运行的代码; 版本、
commit、补丁和构建差异未对齐时, 只能将结果写为辅助线索或未确认项。

### Step 7: Report 汇总报告

MUST 使用 [report-format.md](report-format.md) 的无表格问题调查报告结构。标题后直接
用自然段说明问题原因, 不输出一句话总结标签。第 1 至第 3 节必须输出, 第 4 节按需
输出。核心结论必须依次包含`问题现象`、`通俗说明`、`问题原因`、`问题影响`和
`修复建议`; `通俗说明`只用自然语言解释已验证的故障机制和结果。`问题原因`必须
区分用户现象、直接失败和底层根因, 并用实际证据说明触发机制如何导致直接失败。
只能确认直接失败时, 明确写`直接失败已确认, 根本原因未确认`, 并在第 3 节记录最小
补证动作。第 2 节将关键操作时间线与证据合并, 每个项目使用`事件 N`标签, 附直接证据、
来源和证据说明; 不使用与章节号冲突的裸数字序号。第 4 节详细分析仅在用户
明确要求时输出。报告格式、字段顺序、禁用行首和离线 `path/to/file:line` 引证均以
[report-format.md](report-format.md) 为准, 不在本入口维护另一套完整模板。

同时使用在线补充证据时仍使用相同模板, 不切换为表格或其他报告结构。

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
