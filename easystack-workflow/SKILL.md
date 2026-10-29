---
name: easystack-workflow
description: "Use when developing or reviewing EasyStack code, documenting changed behavior, assessing cross-project contracts, or planning version-aware verification. Routes implementation, tests, debugging, and delivery. For standalone CI, resource tests, Web E2E, or incident analysis, select the matching specialist."
---

# EasyStack Workflow

## Purpose And Scope 用途与范围

作为 EasyStack 开发的统一入口, 连接项目影响分析、代码修改、完整代码 Review、
前后端开发规范和功能验收, 包括服务、API 网关、公共库、operator 与部署衔接.
必需的开发、验证、调试和交付规则均在本目录内, 仅分发本目录即可使用.
其他 skill 是可选增强, 不要求安装或读取其文件; 实际执行仍需目标源码、环境访问和相应工具.

当前用户需求、有效授权、项目规则和 `AGENTS.md` 优先. 已确认范围内继续执行,
不重复逐阶段确认. 中大型任务沿用有效 OpenSpec; 不另建同用途的 Plan 或 R2C 文档.
子 Agent、模型与并发策略服从当前会话, 不固定工具、模型或机器路径.

## Quick Reference 快速参考

只读取当前任务需要的文件. 本目录全部文档如下:

| 需要做什么 | 阅读 |
|------------|------|
| 了解用途、文件组成和最小用法 | [README.md](README.md) |
| 生成或更新功能产品文档 | [product-documentation.md](product-documentation.md) |
| 识别项目关系和必要的跨仓库修改 | [project-relationships.md](project-relationships.md) |
| 开发后端服务、API、公共库或 operator | [backend-development.md](backend-development.md) |
| 选择后端回归、CI 和真实资源验证 | [backend-testing.md](backend-testing.md) |
| 按完整提示词进行 Review, 精简输出 P0-P3 发现 | [code-review.md](code-review.md) |
| 修改前端页面、数据层和接线 | [frontend-design.md](frontend-design.md) |
| 验证前端改动和真实业务效果 | [frontend-testing.md](frontend-testing.md) |
| 在线调查、整项目环境调试、部署验证或离线日志分析 | [runtime-debugging.md](runtime-debugging.md) |
| 检查交付范围、生成提交信息及授权的 Git / Gerrit 操作 | [delivery.md](delivery.md) |

## Entry Selection 入口选择

开发请求先按下方业务域索引定位项目及候选关联仓库, 再判断单仓库或跨仓库实施路径.

| 当前意图 | 执行路径 |
|----------|----------|
| 全栈需求或跨仓库修改 | 业务域索引 -> 关联仓库与证据 -> 开发流程, 按实际影响选择前后端规范 |
| 后端新增或修改代码 | 开发流程 + `backend-development.md` + `backend-testing.md` |
| 前端新增或修改代码 | 开发流程 + `frontend-design.md` + `frontend-testing.md` |
| 只读代码 Review | 主 Agent 读取 `code-review.md`, 新建独立审查会话并传递设计和功能边界; 审查 Agent 直接执行 |
| 仅测试前端改动 | 直接读取 `frontend-testing.md`, 确认被测版本和环境 |
| 仅测试后端改动 | 读取 `backend-testing.md`, 按目标栈和验证层次选择入口 |
| 远端 CI 异常与 recheck | 先按 `backend-testing.md` 读取失败日志和核对版本, 仅满足证据、授权、去重及一次上限时按 `delivery.md` 发布顶层 Reply, 再查新 run 结果 |
| 故障调查 | 读取 `runtime-debugging.md`, 按现场状态、时间窗和证据选择在线或离线路径 |
| 前端修改后联调 | 按 `frontend-design.md` 本地启动并代理目标环境, 按 `frontend-testing.md` 验证代码来源和业务链路 |
| 为本次新增或修改编写产品文档 | 需求确认后形成初稿, 使用 [product-documentation.md](product-documentation.md) 并在验证前整理测试顺序 |
| 后端修改后环境调试 | 读取 `runtime-debugging.md`, 以完整项目运行代码或构建产物更新, 无需先构造故障 |
| Git 交付或仅检查交付准备 | EasyStack 项目必须使用 `easystack.cn` 公司账户; 先读 `project-relationships.md` 的公司默认站点、提交身份与交付约定, 再按本目录 `delivery.md` 执行 |

不要将只读 Review 或纯测试请求改成实施任务, 也不要为每个请求运行全部测试和调试流程.
使用任何执行工具时传递当前目标、范围、已有授权和禁止动作; 纯测试不启动自动改码循环.
交付是首次请求时也必须读取已有公司约定, 不因实际 remote 或本地身份缺失就声称默认值未记录.

## Business Domains 业务域索引

| 业务域 | 关联仓库入口 |
|--------|--------------|
| [Nova 计算](project-relationships.md#nova) | `nova-dashboard` / `nova-dashboard-api` / `nova` / `ark-nova` / `nova-operator` |
| [Cinder 云硬盘](project-relationships.md#cinder) | `ebs-dashboard` / `golem` / `cinder` / `ark-cinder` |
| [Thor 备份](project-relationships.md#backup) | `yak` / `golem` / `cinder` 的 backup 模块 / `ark-thor` |
| [Ironic 裸金属](project-relationships.md#ironic) | `ironic-dashboard` / `ironic-dashboard-api` / `ironic` / `ark-ironic` |
| [Glance 镜像](project-relationships.md#glance) | `glance` / `ark-glance` |
| [Neutron / Proton 网络](project-relationships.md#network) | 分别定位 `neutron`、`proton`, 不因模块同名推定相互调用 |

索引表示候选调查范围, 不代表全部必改. 先读对应职责、调用或部署证据, 再逐仓库判断
必改、需查证或不需改. 例如 Nova 卷挂载按实际契约扩展到 Cinder/os-brick,
不能将整组计算或存储仓库固定为每次同步修改清单.

## Development Flow 开发流程

1. **明确需求和验收.** 读取相关实现, 做功能完整性审查, 将用户要求与必要补全纳入
   Requirement Review. 建议补全经确认后纳入, 范围外能力不顺带实现. 是否需要确认按
   当前 `AGENTS.md` 和本会话有效授权判断; 范围实质变化时重新 Review.
   同时核实对应的真实 Jira 号和问题范围; 缺号时告知用户, 按本目录
   [delivery.md](delivery.md) 处理, 仅经用户明确授权创建 Jira.
   确认后为本次新增功能或修改生成/更新产品文档初稿, 逐项记录可观察行为; 无可见行为
   变化时说明修改影响, 不虚构用户功能. 文档格式、位置和测试步骤见
   [product-documentation.md](product-documentation.md).
2. **判断项目影响.** 按 `project-relationships.md` 确认目标仓库、分支和版本, 追踪
   API、共享状态、权限及必要配置路径. 输出各相关仓库的必改、需查证或不需改及证据,
   不因项目有关联就同步修改全部仓库. 无明确代码依赖的 Patch 基于 `master` 独立提交,
   不叠加之前未合入的 Patch; 确有依赖时记录具体代码证据和原因, 不擅自改写 Git 历史.
3. **按证据实现.** 保留已有修改, 在确认范围内完成业务闭环. 后端先读
   `backend-development.md`, 核对实际语言/依赖、API/RPC/object、持久化和生命周期;
   前端读 `frontend-design.md`, 沿用项目统一设计, 禁止随意硬编码样式, 接通入口、请求、状态和反馈.
   工具或接口事实缺失时
   查真实代码和契约; 关键不确定性无法消除时澄清, 不靠猜测补接口或业务语义.
4. **完成代码 Review.** 每次由主 Agent 按 `code-review.md` 新建独立审查会话, 不复用旧会话或
   继承旧对话; 传递当前有效需求、设计边界、功能范围与排除项、目标 Patch 和基线、
   证据入口及只读权限. 检查实际调用链、跨仓库一致性和业务触发条件是否可达,
   保留完整分析过程. 发现统一使用 P0/P1/P2/P3, 面向用户的结果保持精简.
   审查 Agent 直接执行, 不递归创建审查会话. 主 Agent 核对证据, 修复后的新一轮 Review
   也使用新会话; 工具不支持时报告独立审查缺口, 不将自行复核声称为独立 Review.
5. **按影响验证.** 验证前先整理并呈现完整测试顺序, 按功能依赖和业务生命周期安排,
   集中准备共享前置条件并复用有效资源和结果; 被依赖功能先测, 不为减少重复而删掉
   边界或异常覆盖. 使用确认的行为清单选择验证入口. 后端按 `backend-testing.md`
   区分回归、CI、契约和真实资源验证, Go/C 等项目用自身入口;
   远端 CI 仅在日志证实非代码的 CI 自身异常、当前版本和有效授权匹配时, 按测试文档
   的去重与一次上限执行 recheck, 分开记录回复、排队/运行与新 run 最终结果;
   前端本地 dev-server + 代理仅作开发和预验证; 代码修改后必须按 `frontend-testing.md`
   完成构建、已授权验收环境部署及页面版本、业务与视觉验证. 部署规则见
   `runtime-debugging.md`; 环境或权限缺失时保留部署未完成项, 不以本地联调代替.
   后端需环境调试时, 按
   [runtime-debugging.md](runtime-debugging.md) 发现运行基线, 以完整项目运行代码
   或匹配构建产物更新、备份和回滚, 保留环境配置, 验证相关工作负载及副本.
   环境写入和激活动作须有范围匹配的具体授权, 不从代码修改推导生产或额外配置覆盖权限;
   失败或限制如实记录, 不将编译、渲染或 Mock 演示当作实际业务验收.
6. **对账并交付.** 核对每个相关仓库的实现、Review、验证、产品文档和有效 artifact,
   将实际行为、测试结果、未验证项及文档链接同步到交付说明, 再说明剩余项.
   前端直接向用户提供 `product-documentation.md` 规定的环境、版本及页面查看验收清单,
   不只列代码文件或文档链接.
   交付先读取 `project-relationships.md` 的公司约定, 再按本目录 `delivery.md` 执行,
   新建/更新 EasyStack Patch 及完整待上传范围逐项核对 Jira 关联, Gerrit Topic 与对应
   Jira key 一致; 缺号时暂停相关交付,
   仅执行实际授权的操作, 不从实现授权推导上传授权.

## Capability Routing 能力路由

必需流程按下表读取本目录文档, 不依赖相邻 skill 目录或安装清单.

| 任务 | 本目录执行依据 |
|------|----------------|
| 后端实现规范、版本兼容和生命周期 | [backend-development.md](backend-development.md) |
| 产品文档结构、内容和测试步骤 | [product-documentation.md](product-documentation.md) |
| Angular 子应用组件、页面实现和静态检查 | [frontend-design.md](frontend-design.md) 与 [frontend-testing.md](frontend-testing.md) |
| EasyStack Cloud Web UI 功能和 E2E | [frontend-testing.md](frontend-testing.md), 使用实际可用的浏览器工具或项目测试入口 |
| OpenStack 资源后端功能测试 | [backend-testing.md](backend-testing.md); Backup 默认排除, 明确需要时核实支持路径 |
| OpenStack 仓库 tox、cover、pep8 | [backend-testing.md](backend-testing.md), 不代替前端构建或功能验收 |
| 在线故障、授权 runtime 调试与离线日志分析 | [runtime-debugging.md](runtime-debugging.md) |
| 提交信息、commit、amend、Gerrit 或 push | [delivery.md](delivery.md), 公司默认值见 [project-relationships.md](project-relationships.md) |

环境实际提供 `easystack-ci-test`、`easystack-cloud-web-e2e`、`easystack-test-executor`、
`easystack-env-debugging`、`easystack-log-analysis` 或 `git-delivery` 时, 可在同一已授权范围
复用其专用自动化; 实际阶段匹配且能力可用时先加载对应 Skill, 不因已熟悉任务跳过.
已加载且未变化的内容不重复读取, 切换任务或阶段时重新核对边界, 不无差别加载.
它们均为可选增强, 缺失时直接按本目录规则使用实际工具执行,
不要求复制、安装或读取外部 skill. `es-frontend`、`agent-browser` 等同样不是必装项.
不自动安装、注册 MCP 或启动无关服务; 源码、运行环境、浏览器或 Git 工具确实不可用时,
报告受影响步骤和未验证项, 不降低完成门禁或宣称业务验证通过.

## Completion Gate 完成门禁

以下实现对账和完整交付门禁适用于开发任务. 纯 Review 以 `code-review.md` 的目标、证据和
结论完成; 纯测试以对应测试文档的已执行项、结果和缺口完成, 不要求另行实现或全套 Review.
调试任务报告实际运行版本、行为与回滚状态; 完成调试不等于完整功能验收或发布.

- 已确认需求及必要补全逐项对应实现和验证, 相关仓库没有遗漏或无依据的同步修改.
- Review 已按完整流程完成, P0-P3 发现和修复状态真实, 不把简短报告等同于简化分析.
- 行为验证与实际变更版本一致; 失败、未验证项和剩余资源有明确记录.
- 前端代码修改已按本目录规则完成构建、验收环境部署和实际页面验证, 统一设计检查及用户
  查看说明已对账; 未部署或未验证时明确缺口, 不声称完整交付.
- 有效 OpenSpec / Plan 与实现一致; 关键路径未验证时不声称完整交付.
- 本次新增或修改均有对应产品文档, 覆盖功能列表、边界、异常场景和测试内容; 实际
  测试顺序及结果、未验证项与文档链接已对账, 无可见行为变化时未虚构功能.
- 每个 EasyStack Patch 均关联与修改内容对应的真实 Jira 号; 已上传 Gerrit Change 的
  实际 Topic 与对应 Jira key 一致. 新建 Jira 的实际编号和默认指派当前 Jira 登录用户
  本人的结果已核实, 未完成项如实报告, 不虚报建单或交付成功.
- 最终只报告改动、关键证据、验证、剩余风险及实际 Git 操作, 不复述全过程.

## Execution Feedback 执行反馈

执行中若出现说明不清、重复尝试、工具或权限阻塞、失效路径或额外绕行, 结束时
报告触发位置、问题现象、实际影响、临时处理和优化建议. 没有实际问题时不输出空反馈;
凭据与用户数据必须脱敏.
