# EasyStack Workflow

为 EasyStack 常用项目提供前后端开发工作流入口, 判断跨仓库联动,
连接版本适配、代码 Review、开发规范和真实功能验收.
必需规则均包含在本目录, 可单独复制到 Hermes 等支持 skill 的客户端, 无需同时安装其他 skill.

## Capabilities 功能

- 根据用户确认的项目关系和实际调用链确定必要修改范围, 区分事实、推断和待查证项.
- 为每次新增功能或修改生成/更新产品文档, 记录功能边界、异常场景及按依赖排序的测试步骤.
- 覆盖核心服务、API 网关、公共库、operator、部署与镜像项目, 按实际版本和工具开发后端.
- 新增或修改的代码注释统一使用英文并纳入 Review, 不批量清理历史注释或业务字符串.
- 代码修改后依据需求与实现补齐适用的自动化 E2E 和人工用例, 授权部署并真实验收后再 Review.
- 普通只读 Review 每次新建独立会话; 提交前每轮新建 3 个干净只读 Agent 完整审查并互相核验,
  主会话汇总, 同一 Patch 连续三轮无有效问题后运行同版最终本地门禁, 全通过才可已授权提交.
  任一修改清零计数, Review 或最终门禁失败引起修复后重新更新用例、部署验收并 Review.
- 无明确代码依赖的 Patch 基于 `master` 独立提交, 不叠加之前未合入的 Patch.
- 提交/更新 Patch 前在有效授权内维护真实关联 Jira 的 Conclusion 并回读核实, 上传前复核完整范围; 未完成不放行依赖交付.
- 将 Angular 前端的组件、数据层、路由、权限、i18n 和交互规范接入实现流程, 沿用统一设计并禁止随意硬编码样式.
- 前端代码修改后构建并部署到已授权验收环境, 验证实际页面版本、业务和视觉效果, 直接说明改动位置和查看步骤.
- 远端 CI 日志证实非代码的 CI 自身异常时, 在有效授权内核对当前版本、去重并最多自动 recheck 一次, 复查新 run 结果.
- 区分静态检查、构建与真实功能验收, 按影响调用现有测试、调试和交付能力.
- 代码修改后按需进入授权环境调试, 用参数化模板发现挂载与消费者、暂存并对账完整项目,
  现场选择生效方式, 逐目标验证与恢复; 前端 Host、入口或资源回退异常按证据检查实际路由.

## Files 文件说明

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 触发条件、意图路由、开发流程和完成门禁 |
| [product-documentation.md](product-documentation.md) | 产品文档生成时点、内容结构与依赖排序的测试步骤 |
| [project-relationships.md](project-relationships.md) | 项目矩阵、跨仓库修改判定和证据要求 |
| [backend-development.md](backend-development.md) | 后端开发流程、规范来源、兼容性和生命周期 |
| [backend-testing.md](backend-testing.md) | 后端回归、CI、契约、真实资源验证及 recheck 判断/复查 |
| [code-review.md](code-review.md) | 完整 Review 提示词、提交前三 Agent 连续三轮门禁及精简输出约定 |
| [frontend-design.md](frontend-design.md) | 前端实现、设计规范、来源与可选工具边界 |
| [frontend-testing.md](frontend-testing.md) | 前端静态检查、真实功能验收与结果记录 |
| [runtime-debugging.md](runtime-debugging.md) | 在线调查、完整项目调试操作模板与恢复、离线日志和问题结论 |
| [delivery.md](delivery.md) | 独立 Patch、交付范围、Git / Gerrit 授权、提交及顶层 recheck Reply |

## Quick Start 快速开始

1. 在支持 skill 的客户端加载 `easystack-workflow`, 提供目标项目、需求或待 Review 的改动范围.
2. 修改任务先识别仓库和相关实现, 按当前会话规则完成需求确认和项目影响分析.
   已确认的任务直接继续; 只读 Review 或纯测试从对应入口开始.
3. 按目标栈完成代码修改, 依据需求与实际代码补齐受影响前后端及必要跨层测试,
   提供可重复自动化 E2E 入口/脚本/断言和可人工执行的前置、步骤、预期; 未涉及的一端说明不适用.
4. 按依赖呈现测试顺序, 使用 `runtime-debugging.md` 的已有授权、版本、备份和恢复机制完成
   环境部署, 按前后端测试文档执行 E2E 与本次必验项. 全部真实通过且无已知 bug 后才 Review;
   执行者、版本和结果写入产品文档, Agent 操作不冒充真人, 必验人工项未执行不得全通过.
5. 按 `code-review.md` 完成三 Agent 连续三轮审查, 最后 Review 后运行同版最终本地门禁.
   Review 或最终检查失败引起修复时, 更新用例、重新部署验收并清零重做三轮 Review,
   再运行最终本地门禁. 工具、环境或权限缺失时报告并暂停依赖流程, 不降低门禁.
6. 需要提交且全部门禁通过时先读取项目关系文档中的公司默认值, 再按实际授权执行本目录 `delivery.md`;
   加载本 skill 不代表授权 Git 或环境写操作.

例如: 修改云硬盘列表字段时, 先核对 `ebs-dashboard` 到 `golem`、`cinder` 的实际数据路径,
逐仓库说明是否需要修改, 再验证页面请求、数据展示和相关交互. 这不是预设三个仓库都要改.

例如: 修改卷连接行为时, 从 Nova/Cinder 的真实调用与 os-brick 契约核查设备、状态、
版本和失败恢复; 对已满足契约的调用方给出不需改的证据, 不自动修改全部存储项目.

## Dependencies And Distribution 依赖与分发

分发单位是整个 `easystack-workflow/` 目录, 包括 `SKILL.md` 和上表列出的参考文档,
不只复制 `SKILL.md`. 本目录没有必须从相邻 skill 目录读取的文件, 不附带第三方工具、
浏览器、OpenStack 客户端或目标项目的源码和凭据.

其他 EasyStack 测试/调试 skill、`git-delivery`、`es-frontend` 和 `agent-browser` 均可选.
没有它们时按本目录规则, 从目标项目的 README、HACKING、配置和实际命令选择执行入口;
浏览器交互使用平台提供的浏览器能力或项目已有 E2E 工具, Git 操作直接遵循 `delivery.md`.
不以缺少某个 skill 名称为理由要求复制其他目录, 也不自动安装工具、配置访问或启动服务.
实际运行所需的源码、环境、权限或工具不可用时明确未执行项, 自包含文档不等于已具备运行环境.

后端规则参考的官方文档和前端 `es-frontend` 0.6.0 来源只说明规则出处, 不要求安装来源 skill
或取得归档. 实际 API、组件和命令以目标项目锁定版本、源码和配置为准,
不猜接口或将静态检查、Mock 和工具返回成功冒充真实业务验收.
