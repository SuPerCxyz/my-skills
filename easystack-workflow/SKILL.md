---
name: easystack-workflow
description: "Use when developing or reviewing EasyStack backend or frontend changes, mapping related repositories, checking coordinated updates, or planning version-aware coding and functional verification. Routes CI, resource tests, Web E2E, debugging, and authorized Git delivery to available skills."
---

# EasyStack Workflow

## Purpose And Scope 用途与范围

作为 EasyStack 开发的统一入口, 连接项目影响分析、代码修改、完整代码 Review、
前后端开发规范和功能验收, 包括服务、API 网关、公共库、operator 与部署衔接.
本 skill 组织工作, 专用 skill 执行各自任务.

当前用户需求、有效授权、项目规则和 `AGENTS.md` 优先. 已确认范围内继续执行,
不重复逐阶段确认. 中大型任务沿用有效 OpenSpec; 不另建同用途的 Plan 或 R2C 文档.
子 Agent、模型与并发策略服从当前会话, 不固定工具、模型或机器路径.

## Quick Reference 快速参考

只读取当前任务需要的文件. 本目录全部文档如下:

| 需要做什么 | 阅读 |
|------------|------|
| 了解用途、文件组成和最小用法 | [README.md](README.md) |
| 识别项目关系和必要的跨仓库修改 | [project-relationships.md](project-relationships.md) |
| 开发后端服务、API、公共库或 operator | [backend-development.md](backend-development.md) |
| 选择后端回归、CI 和真实资源验证 | [backend-testing.md](backend-testing.md) |
| 按完整提示词进行 Review, 精简输出 P0-P3 发现 | [code-review.md](code-review.md) |
| 修改前端页面、数据层和接线 | [frontend-design.md](frontend-design.md) |
| 验证前端改动和真实业务效果 | [frontend-testing.md](frontend-testing.md) |
| 后端整项目环境调试或明确要求的部署验证 | [code-debug.md](../easystack-env-debugging/code-debug.md), 通过环境调试能力进入 |

## Entry Selection 入口选择

开发请求先按下方业务域索引定位项目及候选关联仓库, 再判断单仓库或跨仓库实施路径.

| 当前意图 | 执行路径 |
|----------|----------|
| 全栈需求或跨仓库修改 | 业务域索引 -> 关联仓库与证据 -> 开发流程, 按实际影响选择前后端规范 |
| 后端新增或修改代码 | 开发流程 + `backend-development.md` + `backend-testing.md` |
| 前端新增或修改代码 | 开发流程 + `frontend-design.md` + `frontend-testing.md` |
| 只读代码 Review | 直接读取 `code-review.md`, 按需核查关联项目 |
| 仅测试前端改动 | 直接读取 `frontend-testing.md`, 确认被测版本和环境 |
| 仅测试后端改动 | 读取 `backend-testing.md`, 按目标栈和验证层次选择入口 |
| 故障调查 | 选择环境或离线分析能力 |
| 前端修改后联调 | 按 `frontend-design.md` 本地启动并代理目标环境, 按 `frontend-testing.md` 验证代码来源和业务链路 |
| 后端修改后环境调试 | 进入 `easystack-env-debugging` 的代码调试模式, 以完整项目运行代码或构建产物更新, 无需先构造故障 |
| Git 交付或仅检查交付准备 | 先读 `project-relationships.md` 的公司默认站点、提交身份与交付约定, 再进入 `git-delivery` |

不要将只读 Review 或纯测试请求改成实施任务, 也不要为每个请求运行全部测试和调试流程.
向专用能力传递当前目标、范围、已有授权和禁止动作; 纯测试不启动自动改码循环.
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
2. **判断项目影响.** 按 `project-relationships.md` 确认目标仓库、分支和版本, 追踪
   API、共享状态、权限及必要配置路径. 输出各相关仓库的必改、需查证或不需改及证据,
   不因项目有关联就同步修改全部仓库.
3. **按证据实现.** 保留已有修改, 在确认范围内完成业务闭环. 后端先读
   `backend-development.md`, 核对实际语言/依赖、API/RPC/object、持久化和生命周期;
   前端读 `frontend-design.md`, 接通入口、请求、状态和反馈. 工具或接口事实缺失时
   查真实代码和契约; 关键不确定性无法消除时澄清, 不靠猜测补接口或业务语义.
4. **完成代码 Review.** 按 `code-review.md` 保留完整分析过程, 检查实际调用链和跨仓库
   一致性. 发现统一使用 P0/P1/P2/P3, 面向用户的结果保持精简. 修复后复核受影响路径.
5. **按影响验证.** 使用确认的行为清单选择验证入口. 后端按 `backend-testing.md`
   区分回归、CI、契约和真实资源验证, Go/C 等项目用自身入口;
   前端默认本地 dev-server + 代理联调, 按 `frontend-testing.md` 核实浏览器加载本地修改、
   API 到达目标环境及真实交互. 后端需环境调试时, 按
   [code-debug.md](../easystack-env-debugging/code-debug.md) 发现运行基线, 以完整项目运行代码
   或匹配构建产物更新、备份和回滚, 保留环境配置, 验证相关工作负载及副本.
   前端环境产物替换仅用于用户明确要求的部署验证. 环境写入和激活动作须有具体授权;
   失败或限制如实记录, 不将编译、渲染或 Mock 演示当作实际业务验收.
6. **对账并交付.** 核对每个相关仓库的实现、Review、验证和有效 artifact, 说明剩余项.
   交付先读取 `project-relationships.md` 的公司约定, 再进入 `git-delivery`,
   仅执行实际授权的操作, 不从实现授权推导上传授权.

## Capability Routing 能力路由

下列相对链接便于同仓库阅读. 独立分发时通过当前环境的 skill / 工具发现能力定位,
不要假设相邻目录存在或将链接当成已安装证明.

| 任务 | 按需使用 |
|------|----------|
| 后端实现规范、版本兼容和生命周期 | 本目录 `backend-development.md`, 验证见 `backend-testing.md` |
| Angular 子应用组件知识、页面生成和静态检查 | 实际提供的 `es-frontend`; 使用边界见 `frontend-design.md` |
| EasyStack Cloud Web UI 功能和 E2E | [easystack-cloud-web-e2e](../easystack-cloud-web-e2e/SKILL.md), 通过 `agent-browser` |
| OpenStack 资源后端功能测试 | [easystack-test-executor](../easystack-test-executor/SKILL.md); Backup 默认排除, 明确需要时再确认支持范围 |
| OpenStack 仓库 tox、cover、pep8 | [easystack-ci-test](../easystack-ci-test/SKILL.md), 不代替前端构建或功能验收 |
| 在线故障或授权 runtime 调试 | [easystack-env-debugging](../easystack-env-debugging/SKILL.md) |
| 离线 `.eslog` 或 `ecs.*` 分析 | [easystack-log-analysis](../easystack-log-analysis/SKILL.md) |
| 提交信息、commit、amend、Gerrit 或 push | 先读 [公司约定](project-relationships.md), 再用 [git-delivery](../git-delivery/SKILL.md); CI 不另行交付 |

只调用实际可用且与目标相关的能力. 缺失时不自动安装、注册 MCP 或启动服务;
先按目标项目真实入口做等价工作. 无法完成关键验证时报告缺口和影响, 不降低完成门禁.

## Completion Gate 完成门禁

以下实现对账和完整交付门禁适用于开发任务. 纯 Review 以 `code-review.md` 的目标、证据和
结论完成; 纯测试以对应测试文档的已执行项、结果和缺口完成, 不要求另行实现或全套 Review.
调试任务报告实际运行版本、行为与回滚状态; 完成调试不等于完整功能验收或发布.

- 已确认需求及必要补全逐项对应实现和验证, 相关仓库没有遗漏或无依据的同步修改.
- Review 已按完整流程完成, P0-P3 发现和修复状态真实, 不把简短报告等同于简化分析.
- 行为验证与实际变更版本一致; 失败、未验证项和剩余资源有明确记录.
- 有效 OpenSpec / Plan 与实现一致; 关键路径未验证时不声称完整交付.
- 最终只报告改动、关键证据、验证、剩余风险及实际 Git 操作, 不复述全过程.

## Execution Feedback 执行反馈

执行中若出现说明不清、重复尝试、工具或权限阻塞、失效路径或额外绕行, 结束时
报告触发位置、问题现象、实际影响、临时处理和优化建议. 没有实际问题时不输出空反馈;
凭据与用户数据必须脱敏.
