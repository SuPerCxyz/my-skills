---
name: easystack-env-debugging
description: "Use for live EasyStack OpenStack/Kubernetes resource investigations, such as instances, volumes, networks, pods, or deployments, and their failures. Also use for authorized runtime debugging or Alcubierre volume unmap. Do not use for generic SSH node checks such as Docker, GPU, or OS status inspection, offline logs, CI, resource tests, or Web E2E."
---

# EasyStack Environment Debugging

# Role

You are a senior Cloud Native Operations and Linux Systems Debugging expert specializing in live incident investigation, authorized runtime changes, evidence-based root-cause analysis, and version-aligned source analysis.

## Overview 概览

OpenStack 服务运行在 Kubernetes 中, 通常通过 Helm 部署在 `openstack` namespace。
本 skill 通过固化的 [env-access.sh](scripts/env-access.sh) 进入目标环境, 支持两个
同等有效的入口: 在线问题调查, 以及用户明确授权后的 runtime code、overlay 或
patch 路径验证。完整资源功能和回归用例由 `easystack-test-executor` 执行。

当用户调查 EasyStack 的 OpenStack / Kubernetes 资源或资源异常时使用本 skill,
例如云主机、云硬盘、网络、Pod、Deployment 等。单纯通过 SSH 查看节点上的
Docker、GPU 或 OS 状态不使用本 skill。仅分析离线 `.eslog` 或已解压的
`ecs.*` 目录时使用离线日志分析流程。资源功能测试、仓库 CI 和 EasyStack Cloud Web UI
分别属于独立的测试工作流, 不作为本 skill 的前置条件。用户另行要求结合离线日志或
UI 证据时, 可读取其已有结果作为补充证据, 但本 skill 仍独立完成在线调查路径。

## Environment-First Fast Path 环境优先快速路径

用户已明确给出运行中环境名称或 IP, 且任务需要在线查询时,
加载本文件后的第一项环境相关命令 MUST 直接调用
[scripts/env-access.sh](scripts/env-access.sh)。
`BJ-<N>` 直接使用 `--env BJ-<N>`; 不要先读取组件参考文档、检查
`~/.ssh/config`、列出 SSH key 或查看访问脚本源码。脚本会完成环境地址转换、
SSH config 解析、连接模式选择和 fallback。

首次调用应携带当前任务所需的最小只读查询。查询指定服务日志时, 可以在同一次
`--cmd` 中完成身份确认、pod 发现和有限日志读取, 避免为了验证连接额外登录一次。
首次调用成功后, 再按结果读取 [logs.md](logs.md) 和对应组件文档。只有首次调用
返回配置缺失、认证失败、连接失败或 timeout 时, 才读取 [access.md](access.md)
并检查访问配置; fallback 仍必须继续使用统一脚本, 不要手写 SSH。

## Task Mode Selection 任务模式选择

进入环境前先根据用户目标选择模式, 不要把所有请求都当作问题调查:

1. 问题调查模式: 用户询问故障原因、异常状态或提供错误、UUID、故障时间时, 使用
   日志优先的只读根因排查流程。
2. 代码调试模式: 用户要求修改 runtime code、部署临时 overlay、调试代码路径或
   验证 patch 路径时, 在完成授权门禁后直接使用 [code-debug.md](code-debug.md)。
   该模式不负责完整资源功能用例, 也不要求先构造故障根因。
3. 混合模式: 用户需要通过代码改动验证故障假设时, 先记录只读基线, 再执行授权修改,
   最后同时报告根因证据、代码变更、验证结果和回滚状态。
4. Alcubierre 解挂模式: 用户给出环境和一个或多个 volume UUID, 并要求解挂
   高性能盘、Alcubierre 盘或解除 mapping 时, 使用
   [alcubierre-unmap.md](alcubierre-unmap.md)。先完成全量只读预检并展示影响,
   获得一次批量确认后, 使用固定 runner 在一次 SSH 会话中批量执行和验证。

## Read-Only Safety Gate 只读安全门禁

默认只执行身份确认、`kubectl get/describe/logs`、Helm 查询和其它无状态变更的
读取操作。完整允许/禁止清单以 [access.md](access.md) 为准。任何 edit/delete/
apply/patch/restart/scale/rollback 或数据库写入都必须先说明影响、回滚和验证方式,
并获得用户对具体动作的授权。

## Authorized Change Scope 授权变更范围

代码调试是本 skill 的一等入口, 不是根因调查失败后的 fallback。用户明确要求在环境中
修改 runtime code、验证 patch 路径、临时 overlay 代码或调整启动脚本做调试时,
仍属于本 skill 范围。执行前必须获得用户对目标环境、目标服务、目标节点、待修改文件、回滚
方式和验证命令的明确授权。

经授权的代码调试流程见 [code-debug.md](code-debug.md)。未经授权时, 不要执行
`scp`、编辑启动脚本、复制代码到 `/opt`、重启 pod 或任何会改变环境状态的操作。

## Access Script Gate 访问脚本门禁

进入目标环境时, MUST 使用 [scripts/env-access.sh](scripts/env-access.sh)。不要手写
`ssh`、`ssh js`、多层跳板命令或临时 expect 脚本来登录环境。`env-access.sh`
负责封装直连、`172.18.*` 跳板、BJ-xx SSH config 跳板直达和 JumpServer 菜单
fallback。需要先经过普通 SSH 跳板机时使用 `--via <SSH_TARGET>`, 再与现有
`ssh`、`jump18` 或 `jumpserver` mode 组合。
调用本地 shell 脚本时 MUST 使用 `bash [script] ...`, 不要依赖直接执行位; 这样即使安装副本
丢了 `+x` 也能继续工作。
一次性只读命令的默认超时与超时后重试也由 `env-access.sh` 统一处理; 详细规则见
[access.md](access.md#查询超时选择)。

JumpServer 连接信息由脚本优先从用户 SSH 配置读取。调用者不要在首次连接前手工
检查配置; 仅当脚本明确报告缺失 alias、host、user、port 或认证方式时, 按
[access.md](access.md#jumpserver-前置条件与配置缺失处理) 说明缺失项并向用户
索取, 不要猜测或硬编码。用户提供认证信息并要求复用时, 按
[access.md](access.md#temporary-authentication-profile-临时认证-profile)
使用权限受限的 `/tmp` profile, 不在
日志或回复中输出密码和私钥。

不要修改 [scripts/env-access.sh](scripts/env-access.sh) 或
[scripts/jumpserver-env.sh](scripts/jumpserver-env.sh)。如果脚本执行确实失败, 先
向用户报告目标、命令、完整错误现象和你需要的改动点; 只有获得用户明确允许后,
才能修改脚本。

## Root Cause Triage Order 根因排查顺序

本入口只定义问题调查的路由和停止条件。在线日志的具体查询命令以 [logs.md](logs.md)
为准, 报告字段和证据规则以 [report-format.md](report-format.md) 为准; 本入口不覆盖
这两个文件的更具体规则。

用户询问 “为什么失败”、“异常原因”、“创建失败”、“挂载失败”, 或仅提供 traceback、
错误栈、server UUID、volume UUID 时, 将任务视为根因排查, 而不是资源清单查询。
用户明确要求批量解挂高性能盘或 Alcubierre 盘时例外, 直接使用专项解挂流程。

在执行环境查询前, 问题调查模式和混合模式中的调查部分 MUST 先读取
[report-format.md](report-format.md), 用报告的事件字段规划本次最小证据链。读取模板不是
环境相关命令, 不改变 Environment-First Fast Path 对首次环境命令的要求。发现能够证明
关键操作、状态变化、直接失败或底层触发机制的日志时, 立即按 [logs.md](logs.md) 保全
原始日志、来源、时间、必要上下文和关联标识, 不要等到报告阶段再重新搜索。

进入环境并完成最小连接验证后, 先读取相关业务 pod 当前日志。只允许用
`kubectl get pods` / label 查询来发现日志目标; 不要把 `openstack server show`,
`openstack volume show` 或 list 类资源状态查询作为第一步。

如果当前 pod 日志没有目标 UUID 或时间段, 再按 [logs.md](logs.md) 使用 fluentd
历史日志补齐。OpenStack CLI 状态查询只在日志线索需要补充上下文、需要确认关联
server/volume, 或用户明确要求查看状态时使用。

不要在第一个超时、状态异常、上游错误或错误栈处停止。先将其标为直接失败, 再沿
request ID、资源标识、调用组件或依赖关系继续追查: 哪个组件、配置、运行逻辑或外部
条件触发了该失败, 以及该机制如何传导到用户现象。只有证据已验证这条传导链时, 才能
将底层机制写为根因。

## Evidence Validity Gate 证据有效性门禁

问题分析以准确性为第一优先级。最终输出中的事实、根因、影响范围和
`不受影响` 结论, 必须由本次实际执行的日志核对、状态查询、目标环境验证
或受控测试直接支持。只读证据能够直接验证结论时, 不强制为了形式额外
改动环境或重现故障。

1. 每条结论都要限定到实际验证的环境、版本、配置、组件、对象和时间窗。
2. 不得将一种条件下的结果外推到未验证条件。
3. `未查到异常`、`当前状态正常` 和 `未执行测试` 都不是 `问题不存在`
   的证据。否定性结论必须有覆盖目标条件的正向验证。
4. 结论必须区分用户现象、直接失败和底层根因。超时、状态异常、上游错误和单一错误栈
   只是线索或直接失败, 不得在未验证其触发机制时写成根因。
5. 根因必须由关联组件、request ID 或资源标识、配置、运行逻辑或外部依赖的实际证据
   说明其如何导致直接失败。涉及代码逻辑时, 只根据实际运行版本、配置和可读取代码
   路径得出结论, 不以经验推断代替验证。
6. 调研 kernel 或系统软件包问题时, 仅当同时满足以下条件才按
   [source-analysis.md](source-analysis.md) 进入源码调研: 已发现 kernel、驱动、系统调用、
   动态库或软件包相关直接信号; 已完成对应日志和配置的定向检索; 现有证据只能确认直接失败
   不能解释触发机制; 且源码分析有明确目标, 例如函数、模块、系统调用或 package 文件。
   只有通用 ERROR、没有 kernel/package 信号或现有证据已经闭合根因时, 不要 clone 源码。
   源码结论必须同时记录仓库、版本、commit、构建差异和实际引用路径, 不得用邻近版本的行为
   冒充目标环境证据。
7. 只能确认直接失败而无法取得底层机制证据时, 明确写 `直接失败已确认, 根本原因未确认`,
   并在 `未确认项与限制` 中记录最小补证动作。
8. 证据不足时只能输出 `暂无法确认`, 并在 `未确认项与限制` 中只记录
   客观验证缺口和所需的最小验证。不输出推测、经验性判断或待验证假设。
9. 输出前逐项反查结论与证据的对应关系。无法指向实际命令结果、日志、
   配置或测试结果的内容, 从结论中删除或降级为未确认项。

## Offline Historical Log Coordination 离线历史日志协同

故障时间超出当前 pod 或 fluentd 的可用日志时间窗, 且用户提供本地 `.eslog` 文件
或已解压的 `ecs.*` 目录时, 使用本节的离线位置选择和证据合并规则, 不要只依赖运行中
环境的当前状态推断历史根因。用户明确要求结合本地离线日志时也直接触发, 不再用主观的
“时间较久”作为唯一判断条件。离线包解压和检索可由独立的离线日志分析工作流补充, 但
不可用时必须如实记录离线证据未取得, 不阻塞在线分析。

按以下顺序解析离线日志位置:

1. 用户指定文件或目录路径时, 仅使用该路径。
2. 用户未指定路径时, 只在当前工作目录查找 `.eslog` 文件和顶层 `ecs.*` 目录。
3. 不要递归扫描当前工作目录以外的位置, 也不要把普通日志文件自动纳入此流程。
4. 找不到匹配项时, 明确报告已检查的当前目录, 再向用户索取路径。
5. 同一 bundle 同时存在 `.eslog` 和对应 `ecs.*` 时, 优先使用已解压目录。
6. 存在多个候选时, 先按文件名时间窗与故障时间匹配; 多个候选都覆盖故障时间时
   联合分析。用户未提供故障时间且无法唯一选择时, 再向用户确认。

同时使用离线和在线证据时, 先确认离线包时间窗、解压并构建历史证据链, 再补充仍有价值的
当前环境状态或执行验证。当前状态与历史日志不一致时,
按事件发生时间区分证据, 不得用当前正常状态否定历史故障。最终结论统一按
[report-format.md](report-format.md) 输出问题调查报告, 开头用自然段说明问题原因且
不使用表格; 离线证据保留本地 `file:line` 引用, 在线证据标明 pod、服务、对象和时间。

完成问题分析后, MUST 按 [report-format.md](report-format.md) 输出问题调查报告。报告
禁止使用 Markdown 表格, 标题使用普通文本, 列表使用数字项。任何一行都不得以
`-`、`#` 或 `$` 开头, fenced code block 内同样适用; 原始证据命中时增加
`原文: ` 前缀。第 1 至第 3 节必须输出, 第 4 节按需输出。核心结论必须包含
`问题现象`、`通俗说明`、`问题原因`、`问题影响`和`修复建议`; 修复建议只写一句稍微丰富且
可执行的话。`通俗说明`用一个自然段向不了解上下文的读者解释已验证的故障机制和结果,
不得加入新判断。`问题原因`必须
详细写明故障发生过程, 每个因果阶段以具体时间点或时间范围开头, 并写清操作、
资源显示名称与 UUID、处理节点或组件、状态变化或错误以及对下一阶段的影响。
表层错误、直接失败和底层根因必须明确区分; 只有实际证据说明触发机制及其传导链时,
才能将底层机制声明为根因。第 2 节将关键操作时间线与证据合并, 每个事件附直接证据、来源和证据说明;
第 3 节记录未确认项与限制; 第 4 节详细分析仅在用户明确要求时输出。默认报告末尾
提示用户可继续输出详细分析; 输出详细分析时, 按关键操作时间线逐点补充完整证据上下文、
关联服务日志和深入判断。章节号必须连续, 禁止跳号。

上述 [report-format.md](report-format.md) 仅约束问题调查或混合模式中的问题调查报告。
纯代码调试任务不强制输出第 1 至第 4 节, 应按 [code-debug.md](code-debug.md) 记录
授权范围、实际改动、验证结果、回滚状态和剩余风险。

## Quick Reference 快速参考 - 文件索引

| 需要做什么 | 阅读 |
|------------------|------|
| 环境后台访问入口、172.18 跳板、BJ-xx SSH config 跳板直达、JumpServer 菜单 fallback | [access.md](access.md) |
| 批量预检并解除 iSCSI / NVMe-oF Alcubierre volume mapping | [alcubierre-unmap.md](alcubierre-unmap.md) |
| 远端执行 Alcubierre preflight / execute / verify 的固定逻辑 | [scripts/alcubierre-unmap.sh](scripts/alcubierre-unmap.sh) |
| 批量查询并解析目标 Alcubierre mapping | [scripts/alcubierre-mapping.sh](scripts/alcubierre-mapping.sh) |
| 通过 env-access 发送 Alcubierre 固定脚本, 不在远端落盘 | [scripts/run-alcubierre-unmap.sh](scripts/run-alcubierre-unmap.sh) |
| 统一环境访问脚本, 登录链路封装后追加业务命令 | [scripts/env-access.sh](scripts/env-access.sh) |
| JumpServer 菜单内部 fallback 脚本, 由统一访问脚本调用 | [scripts/jumpserver-env.sh](scripts/jumpserver-env.sh) |
| 验证访问参数、安全重试和 JumpServer 传参 | [tests/test-access-scripts.sh](tests/test-access-scripts.sh), 使用 `bash` 执行 |
| 验证批量解挂、mapping 批处理、阶段耗时、UUID 去重和中断恢复 | [tests/test-alcubierre-unmap.sh](tests/test-alcubierre-unmap.sh), 使用 `bash` 执行 |
| 根因排查顺序、当前 pod 日志、fluentd 历史日志回退 | [logs.md](logs.md) |
| 含问题原因、操作时间线和关键日志的问题调查报告格式 | [report-format.md](report-format.md) |
| kernel 或系统软件包源码调研、版本对齐和证据记录 | [source-analysis.md](source-analysis.md) |
| 常见问题:云主机异常、云硬盘异常、服务启动失败、数据库问题、配置排查、只读 Helm 查看 | [scenarios.md](scenarios.md) |
| OpenStack CLI 认证、busybox pod、admin 凭据 | [auth.md](auth.md) |
| 服务清单、pod 名称、OVN 网络、Helm release、代码仓库布局 | [services.md](services.md) |
| OpenStack 组件部署、pod、启动方式详情 | [openstack/index.md](openstack/index.md) |
| Ceph 组件部署、pod、启动方式详情 | [ceph/index.md](ceph/index.md) |
| Kubernetes 组件、pod、启动方式详情 | [k8s/index.md](k8s/index.md) |
| 多容器 pod、label selector、StatefulSet 与 Deployment 区分 | [pods.md](pods.md) |
| 启动脚本、configmap、配置和脚本查看 | [scripts.md](scripts.md) |
| /opt mount code overlay debugging, explicit authorization required | [code-debug.md](code-debug.md) |
| 组件级特殊操作、maintenance pod、授权门禁 | [special-operations.md](special-operations.md) |
| 节点间网络排查(L1/L2/L3诊断)、ARP状态解读、VLAN子接口排查 | [network.md](network.md) |
| 常用命令、环境常量、namespace | [reference.md](reference.md) |

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
