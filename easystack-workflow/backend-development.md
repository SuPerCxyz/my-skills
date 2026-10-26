# EasyStack Backend Development

## Baseline And Scope 基线与范围

本文件用于后端实现, 验证见 [backend-testing.md](backend-testing.md), 项目定位见
[project-relationships.md](project-relationships.md). 沿用当前需求确认、有效 OpenSpec
和授权, 不为每一层重复确认, 不把只读 Review 变成开发任务.

1. 固定目标仓库、origin、分支、Commit/Patch 基线、HEAD SHA 和已有修改; 同一 origin
   的多个目录分别识别, 不按目录名或 `master` 推定版本, 不合并或清除开发副本.
2. 读取实际生效的项目规则、HACKING、相关 contributor 文档、setup/package 配置、
   tox/Makefile、依赖与 constraints. 确认语言、框架和测试版本, 再选择实现方式.
   本地源码、构建产物和部署版本分别记录; 修改必须在哪个版本组合生效应明确.
3. 还原需求或 Issue 的触发条件、修改前行为和验收结果. 缺陷先定位根因, 尽量建立
   修复前失败的针对性用例; 需求新增则明确成功、失败及适用的反向操作.
4. 从实际入口追踪调用和状态, 将相关项目分为必改、需查证、不需改并给出证据.
   发版分组、相同 Issue 或项目名称相近本身不构成联动修改依据.

规则与实现冲突时先说明约束、代码证据及影响, 在受影响实施前取得明确方向.
例如强制文档要求 Alembic, 当前代码却使用 sqlalchemy-migrate, 不得静默忽略硬规则,
也不得借此任务迁移整套数据库框架. 不依赖该冲突的已授权工作可以继续.

## Implementation Path 实现路径

按实际功能选取下列层次, 补齐必要连接点; 无关层不机械展开:

`入口/调用方 -> API/权限/参数 -> SDK/RPC/调度 -> manager/driver -> 数据与状态 -> 结果反馈`

| 涉及层次 | 实施和核对重点 |
|----------|----------------|
| API、网关、SDK | 真实路由、请求/响应、校验、分页/过滤及错误约定, 上层字段映射和最低支持版本 |
| policy、context | 角色、项目/租户、对象归属和跨服务 context 传递; 可见性与实际操作权限一致 |
| RPC、调度、manager | call/cast 的完成语义、参数和异常, 调度能力、服务版本及操作实际执行位置 |
| driver、connector | 接口前置条件、返回值和副作用, 公共实现与特定后端边界, 上层如何消费结果 |
| DB、object、状态 | 持久化格式、事务边界、并发更新、状态转换和重启恢复, 读写双方兼容 |
| 配置、部署、反馈 | 配置注册与默认值、服务实际消费、镜像/包版本, 通知、轮询或页面反馈闭环 |

只在存在具体契约或风险线索时扩展相关模块和仓库, 不扫描全部项目. 同一修复涉及
多个仓库时列出配套变更、兼容窗口、部署先后及逐项验收, 不能只完成当前 Diff.
上层页面有变化时同时使用 [frontend-design.md](frontend-design.md), 不将 API 成功
当作页面或资源操作已经闭环.

## Project Conventions 项目规范

- 遵循当前 HACKING、代码邻域和检查入口. 按实际 Python 版本选择语法, 不统一引入
  f-string、类型注解、pytest 或新版 SQLAlchemy API, 不因参考文档较新就升级依赖.
- 使用项目已有的日志、异常、i18n、序列化和请求 context 机制; OpenStack 项目优先
  复用其 oslo 和项目封装. 日志与用户错误消息按各自翻译规则处理, 不统一给日志加 `_()`.
  异常保留错误语义及必要上下文, 不吞掉失败或将失败转换成成功结果.
- 配置按项目既有注册、分组和采样机制接入, 保持默认行为和必要兼容. 依赖遵守当前
  requirements/constraints 或 go.mod, 不为实现方便顺手加依赖、改 CI 或全局环境.
- 复用项目 privsep/rootwrap 等提权入口, 核对参数与权限边界; Shell、外部数据和
  序列化输入使用已有安全机制. 日志、异常和 Review 证据不输出凭据或完整敏感对象.
- 仅在本次变化需要时更新接口说明、配置样例、部署消费和 release notes. 范围外历史
  问题单独报告, 不夹带重构或修复.

## Compatibility And Data 兼容与数据

三种版本契约分别核查, 按实际变化更新, 不因修改一个字段就机械递增全部版本:

| 契约 | 核对内容 |
|------|----------|
| API microversion | 项目是否使用 microversion、可观察行为是否变化、请求选择、旧响应、SDK/网关消费及测试 |
| RPC version/cap | 发起方与接收方的参数和方法支持、升级中混合版本、cap/downgrade 及回退路径 |
| object VERSION | 新旧字段和序列化语义、`obj_make_compatible`、对象版本测试及旧节点读写能力 |

例如 Nova 的 attachment 调用可能要求 Cinder 最低 microversion, connector 字段也可能
经过 Nova、Cinder 与 os-brick; 应查目标分支的真实生产者和消费者, 不只查依赖下限.
共享状态、事件或存储格式变更同样需核对旧数据和混合版本, 不能仅依赖 API 版本.

DB 变更使用目标仓库实际采用的 migration 机制, 确认版本链、数据迁移和升级顺序.
Nova/Cinder、Ironic/Neutron、Glance、Keystone 的迁移布局可能不同; 不统一假设
Alembic、单链或只有新增操作. 按该项目规则处理 expand/data/contract、历史数据和
部署兼容, 检查迁移测试, 不修改已发布迁移来掩盖版本链问题.

事务沿用当前 enginefacade/session 方式. 修改共享状态时核对条件更新、唯一约束、锁
和并发调用; 不让长时间外部 I/O 无依据地占住事务. 提交数据库状态并不证明下游已完成,
需明确异步中间态、终态及失败后的可恢复状态.

## Lifecycle And Native Components 生命周期与原生组件

按改动风险落实超时、重试、重复请求、部分成功、取消、补偿和清理. 异步返回需有
可观测状态与结果; 重试不能重复创建或释放资源, 失败不能遗留永远无法继续的状态.
并发和锁需核对持有范围、锁顺序、释放及服务重启, 保留项目实际使用的线程/协程模型.

卷连接、迁移、扩容或故障恢复变化, 定向检查 connection_info、设备路径、多路径、
force detach 和资源清理的真实消费者. 涉及 fencing 时同时检查控制面锁与数据面
写入隔离, 不以状态更新、锁返回或 RPC 成功替代设备及 I/O 效果.

| 项目类型 | 适用实现要求 |
|----------|--------------|
| Go operator | 根据实际 Go/controller-runtime/SDK 版本实现 reconcile 重入、状态条件、finalizer 和删除恢复; 核对 CRD、RBAC、SDK 调用的并发与幂等, 不照搬新版框架 API |
| C/Go 服务 | 以实际 Makefile/common.mk、头文件和协议入口为准; 核对进程/线程、内存和资源释放、超时及 C/Go 边界, 不套 Python/tox 模板 |
| Helm/Kolla 等部署项目 | 查真实 values/template、镜像或包消费、配置传递及升级路径; 业务代码实现与部署落地分别验证, 不默认具备发布授权 |

例如 etcdlock-manager 的 Unix socket、C 到 Go HTTP、etcd lease/事务和存储预留属于
不同边界. 改哪一段就追踪其受影响调用和故障恢复, 不因有关联就默认所有组件必改.

## Review And Delivery 审查与交付

按 [code-review.md](code-review.md) 保留完整问题、功能和跨项目分析, 输出保持精简,
严重性使用 P0-P3. 按 [backend-testing.md](backend-testing.md) 完成对应验证, 修复后
复验受影响行为, 将实际结果与确认的需求及有效 artifact 逐项对账.

交付说明区分已改、无需改、待查证的仓库及原因, 列明被测版本、未验证项和部署依赖.
Git 操作转 [delivery.md](delivery.md), 仅执行当前明确授权的操作;
开发授权不推导 commit、amend、上传、发布或删除权限.

## Sources And Adaptation 来源与适配

目标仓库当前 HACKING、依赖、测试和 contributor 文档优先确定实现事实; 以下仅辅助
检查维度. `latest` 文档不能替代项目锁定版本, 差异须按前述冲突规则处理.

| 参考 | 借鉴范围 |
|------|----------|
| [OpenStack Hacking](https://docs.openstack.org/hacking/latest/user/hacking.html) | 公共风格与检查原则, 项目额外规则以当前代码和配置为准 |
| [Cinder API microversion](https://docs.openstack.org/cinder/latest/contributor/api_microversion_dev.html) | API 可观察行为和版本兼容, 不推广为所有 schema 改动必增版本 |
| [oslo.versionedobjects usage](https://docs.openstack.org/oslo.versionedobjects/latest/user/usage.html) | 对象版本与兼容, 对照实际安装版本和项目对象测试 |
| [社区 Nova Review skill](https://github.com/sbauza/openstack-agentic-workflows/blob/f61218fccd713e6ce7f3a4b1e9660f10bd4e5d6f/workflows/nova-review/.claude/skills/nova-code-review/SKILL.md) | 版本、架构、测试检查维度, 不照搬绝对迁移/导入规则或自动评论流程 |
| [社区 Go code-style skill](https://github.com/openstack-k8s-operators/devskills/blob/2c903127003ead9d265b80860365e4a24ba35a66/skills/code-style/SKILL.md) | 仅用于版本匹配的 Go operator, 不作为 Python 规范 |

社区 skill 为只读参考, 不要求安装, 不继承其固定 Agent、工具、Jira 层级或远端写入流程.
