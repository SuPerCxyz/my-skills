## ADDED Requirements

### Requirement: Use English for added and modified code comments

工作流 MUST 要求新增或修改的代码注释统一使用英文且不含中文, 并在 Review 中检查。MUST NOT 为本次要求批量清理历史注释或修改业务字符串。

#### Scenario: A Patch changes code comments
- **WHEN** 当前 Patch 新增或修改代码注释
- **THEN** 实现和审查均核对注释使用英文且无中文, 无关历史注释和业务字符串保持在范围外

### Requirement: Accept the deployed implementation before development Review

开发工作流 MUST 按需求确认和验收初稿、修改代码、依据需求及实际代码补齐适用测试、授权环境部署、真实功能验收、正式 Review 的顺序执行。测试 MUST 覆盖受影响前后端和必要跨层路径, 同时具备可重复自动化 E2E 入口/脚本/断言及可人工执行的前置、步骤和预期。未涉及的一端 MUST 说明不适用, 不生成无关用例。

正式开发 Review 前 MUST 核对 Patch、构建产物与环境运行版本一致, 当前阶段的环境必验项真实通过且无已知 bug. 此集合仅包含适用的环境 E2E、人工项和业务终态验收, MUST NOT 包含 Review 后才运行的最终本地门禁. 每项 MUST 记录版本、真实执行者、状态和结果; Agent 自动操作 MUST NOT 记为真人执行. MUST NOT 增加真人全部重复执行或签字要求, 但本次必验人工项未执行时不得宣称全通过. 环境、工具、必需入口或权限缺失时 MUST 暂停依赖 Review 和提交, 不以静态或 Mock 替代真实验收.

#### Scenario: A development Patch reaches Review
- **WHEN** 代码和适用双轨用例已经完成
- **THEN** 工作流先部署并核实当前版本, 当前阶段环境必验项真实通过且无已知 bug 后才开展正式开发 Review

#### Scenario: Final local checks have not run before Review
- **WHEN** 当前阶段环境必验项已真实通过, 最终本地门禁尚未执行
- **THEN** 工作流允许进入正式 Review, 固定 2 + 1 本地 Review 及发现处理结束后才运行最终本地门禁, 不提前标记其通过或将它作为 Review 准入条件

#### Scenario: E2E fails or a required manual case is unexecuted
- **WHEN** 环境 E2E 失败、仍有已知 bug 或必验人工项未执行
- **THEN** 工作流保留真实状态并暂停依赖 Review/提交, 不将自动操作冒充真人结果, 修复时更新用例并重新部署验收

#### Scenario: Only one side is affected
- **WHEN** 修改只影响前端或后端, 实际依赖也不要求另一端配套
- **THEN** 工作流验证受影响端及必要调用链, 为另一端记录不适用及依据, 不凭空生成无关用例

#### Scenario: The request is review-only or testing-only
- **WHEN** 用户仅要求只读 Review 或限定范围测试
- **THEN** 工作流保持独立入口与原授权边界, 不自动启动完整开发链、修改代码或部署环境

### Requirement: Use two parallel reviewers and one final reviewer

提交前本地 Review MUST 固定为 2 + 1: 首轮由主会话新建两个干净独立只读 reviewer, 不复用实现、探索或旧审查会话, 不继承旧对话. 两方 MUST 得到同一完整当前 Patch、明确基线、有效需求/设计边界、必要修改上下文及当前验收和验证结果, 并行独立完整审查. MUST 按证据汇总去重, 对冲突或有效性存疑的发现委派只读核验并记录采纳/驳回理由, 再由唯一写入 Agent 在授权范围统一修复. 随后 MUST 新建一个干净独立只读 reviewer 对修复后的完整 Patch 审查一次, 处理复审发现后结束本次本地 Review. 首轮无发现也 MUST 执行这一次复审. 审查 Agent MUST 始终只读.

MUST 记录两阶段 Patch/基线、会话标识、各结论、汇总及修复链. P0-P3 有效问题 MUST 均处理; 有效问题未解决或影响结论的未决项 MUST 如实报告并暂停依赖交付. 复审后修复或最终门禁修复 MUST NOT 自动重开 Review, MUST 更新适用用例和文档并补齐受影响的部署、真实验收和最终本地验证. MUST 区分审查版本与修复后验证版本, 不把未经复审的最终修改称为已获无问题复审. 调度 MUST 服从当前会话模型能力、槽位和并发规则, 不硬编码模型或扩大容量. 能力不足、必需审查/核验未完成或关键验证缺失/失败时 MUST 报告缺口并暂停依赖交付, 不冒充独立 Review.

#### Scenario: Initial reviewers find no issues
- **WHEN** 当前 Patch 及其环境验收证据持续有效, 首轮两个 reviewer 均无发现
- **THEN** 仍新建一个独立 reviewer 完整复审一次并处理发现后结束本地 Review, 再执行最终本地门禁, 有效环境证据可复用

#### Scenario: Initial reviewers report duplicate or conflicting findings
- **WHEN** 首轮两个 reviewer 完成独立审查, 发现重复或冲突问题
- **THEN** 按证据去重并委派只读核验冲突, 记录采纳或驳回理由, 唯一写入者统一修复后由一个新建独立 reviewer 完整复审一次

#### Scenario: The final reviewer requests a repair
- **WHEN** 最后一个 reviewer 发现有效问题并需要修改目标 Patch
- **THEN** 唯一写入者统一处理发现后结束本地 Review, 更新适用用例和文档并补齐受影响验证, 不自动增加审查轮次, 不将未经复审的修改称为已获无问题复审

#### Scenario: Review capacity or evidence is incomplete
- **WHEN** 无法提供首轮两个并行独立会话或最后一个独立 reviewer, 必需核验未完成或缺少影响结论的证据
- **THEN** 工作流报告缺口并暂停依赖交付, 不复用旧会话或把自查写成独立 Review

### Requirement: Run final local gates after the fixed Review and repairs

工作流 MUST 在固定 2 + 1 本地 Review 及发现处理结束且功能正常之后, 运行项目已有的 Python pep8 与 coverage 门禁; 其他栈使用项目对应的本地检查和覆盖率入口, 项目阈值保持不变. Python 的首次验证和修复重跑 MUST 同时核验完整本次 diff 中新增/修改的可执行行及相关分支无 mis/par, 包含已确认 committed/staged/unstaged 与未跟踪新源码. MUST 保留项目既有排除规则并列明影响, 不静默忽略排除项或添加豁免, 无关历史缺口单列基线. 不适用 MUST 说明依据且不得标成通过; 缺少文件报告、分支测量或必需入口 MUST 记录未验证并暂停依赖提交, 不以无记录证明无缺口. tox 命令结果和增量质量判定 MUST 分开报告. 构建前必要快速检查可以执行, 但 MUST NOT 替代最后 Review 后的最终本地门禁.

最终检查失败引起修复后 MUST 更新用例、重部署并真实验收受影响行为, 再运行最终本地门禁, 不自动重开 Review, 不直接沿用失效测试结果或将最终修复称为已经复审. EasyStack commit/amend 与已有提交直接上传 MUST 均核对全部门禁已真实通过: commit/amend 核对最终完整暂存 Patch, 上传核对完整待发送提交范围, 与对应基线、同版环境验收、固定 2 + 1 本地 Review 及发现处理、最终修复链和本地门禁证据一致. 准确且持续有效的证据可复用, 缺失或版本/基线变化 MUST 暂停依赖动作并在授权范围补足. 提交与上传 MUST 分别有明确授权, 审查或测试通过不产生 Git 权限, 上传授权 MUST NOT 自动授权 commit/amend、环境写入或修复. 独立 CI 的首次验证和 auto-fix MUST 使用同一质量判据, 仅验证无修复授权时只报告; 其最多三轮修复限制 MUST NOT 被解释为开发本地 Review 的固定 2 + 1 流程. 可选 git-delivery 的 EasyStack 分支 MUST 继承此核验, 不推广到非 EasyStack 项目.

随 Patch 交付的产品文档、tasks 和验收报告 MUST 纳入完整目标 Patch, 在首轮正式 Review 前完成需求、用例、当前环境验收结果与真实稳定动态证据入口并冻结。冻结后的 Review、最终本地门禁及后续验收状态 MUST 记录在目标 Patch 之外的已有交付说明或本次当前会话交付记录, 绑定明确基线和完整 Patch 版本/指纹; 冻结文档通过预先确定的真实入口引用结果, 最终对外说明 MUST 提供实际结果和入口, 不要求最终检查后回填冻结文件或杜撰 URL/平台。确需修改任何目标文档时 MUST 纳入完整 Patch 和修复链并补齐受影响验证, 不自动重开 Review, 不得将文档排除 Patch。任务勾选 MUST NOT 代替外部记录中的实际最终复审和验收结果。

#### Scenario: Final gates pass for the reviewed version
- **WHEN** 固定 2 + 1 本地 Review 及发现处理已完成, 最终修复版本环境验收已通过, 最后 Review 后的项目本地门禁也全部通过
- **THEN** 工作流核对最终完整暂存 Patch 和已通过版本一致, 仅在另有对应明确授权时执行提交

#### Scenario: A final local check requires a code repair
- **WHEN** 最后 Review 后的 pep8、coverage 或其他栈门禁失败且需要修复
- **THEN** 工作流更新代码和用例、重新部署并真实验收、不自动重开 Review, 然后重新运行最终本地门禁

#### Scenario: Existing commits are uploaded without new local edits
- **WHEN** 用户仅授权上传已有 EasyStack 提交, 未授权 commit/amend
- **THEN** 工作流核对完整待发送范围和同版基线的全部质量证据, 有效证据可复用, 缺失/失效则暂停上传, 不因提交已存在放宽门禁或自动改码/部署/改写提交

#### Scenario: Tox succeeds but changed executable lines lack coverage
- **WHEN** 首次验证或修复重跑的 tox 命令退出成功, 完整本次 diff 的新增/修改可执行行或相关分支仍有 mis/par
- **THEN** 工作流报告 tox 通过且增量覆盖门禁未通过, 使用同一质量判据, 仅在已有修复授权内处理, 不把 tox 的成功结果改称失败

#### Scenario: Coverage gaps are historical or evidence is missing
- **WHEN** 报告包含未改历史缺口, 或当前修改缺文件报告/分支测量
- **THEN** 历史缺口单列不扩大修复范围, 既有排除按项目规则核实并列明; 当前证据缺失记为未验证并阻断依赖交付, 不自动改变排除/阈值或推定无缺口

#### Scenario: An in-Patch product document references later final results
- **WHEN** 产品文档或 tasks 属于完整目标 Patch, 固定 2 + 1 本地 Review 和最终本地门禁将在冻结之后完成
- **THEN** 文档在首轮 Review 前冻结当前验收快照和真实证据入口, 后续实际结果在目标 Patch 外绑定基线和完整版本记录, 最终说明提供该入口与结果而不回填冻结文件, 无实际通过结果不得放行提交

#### Scenario: A frozen target document must change
- **WHEN** 最终结果产生后仍确需修改目标 Patch 内的文档
- **THEN** 该修改纳入完整 Patch 和修复链并补齐受影响验证及最终本地门禁, 不自动重开 Review, 不豁免文档修改

#### Scenario: A repository uses another language or lacks a required gate
- **WHEN** Python pep8 对该项目不适用, 或项目必需的验证入口不可用
- **THEN** 工作流按实际栈选择已有对应门禁, 说明不适用依据, 必需入口缺失时暂停提交而不编造通过或擅自安装依赖

### Requirement: Verify Review Links after applicable Bug uploads

对适用公司 Bug 规范的关联 Jira, 工作流 MUST 在上传后按相关仓库、目标分支/版本核对真实 Change URL 的完整 Review Links 集合. MUST 从实际上传或远端结果取得链接, 不预填未来 URL; 不将未确认适用的 Story/Sub-task 一律按 Bug 处理. MUST 发现实际字段、类型和权限, 回读已有值, 仅在覆盖目标 Issue/字段的有效授权内安全合并、去重、保留其他内容并回读核实. 已准确覆盖时只核验. Git 上传或 Conclusion 授权 MUST NOT 扩为 Review Links 写入权限. 无权限、字段不明、更新失败或结果未知时 MUST 保留上传事实, 提供草稿和未完成项, 不声称完整交付; 未知结果先查证, 不盲重写或重新上传.

#### Scenario: Several projects or versions share a Bug
- **WHEN** 本次 Bug 的多个仓库或版本已上传, Jira 已有部分 Review Links
- **THEN** 工作流按真实映射核对完整集合, 在有效字段授权内只补缺失项并保留原有内容, 回读后才认定该项完成

#### Scenario: Upload succeeds without field write authorization
- **WHEN** 上传成功但 Review Links 未完整覆盖, 用户仅授权 Git 上传或 Conclusion 更新
- **THEN** 工作流不写 Review Links, 报告上传成功和 Jira 交付记录未完成, 提供可审阅合并草稿, 不声称完整交付

#### Scenario: A Review Links update has an unknown result
- **WHEN** 字段更新失败或回读结果不明
- **THEN** 工作流先查证实际字段状态, 保留未完成结论和原内容, 不盲重写、不重复登记或重新上传 Patch

### Requirement: Distinguish unverified Jira from unavailable details

工作入口 MUST 核实 Jira 站点/项目、真实 key、存在性及与本次范围的对应关系, 记录实时查询或可信材料的来源. 仅编号或未经核实链接不足以满足门禁, 无权限也不证明 Issue 不存在. 尚未核实 MUST 暂停依赖工作, 仅继续需求查证、查询和草拟所需只读检查, 不重复建单. 上述事实已由可信材料核实但实时详情/讨论不可读时, 普通只读 Review MAY 基于现有证据继续; MUST 披露缺口, 影响关键判断时使用 NEEDS VERIFICATION, 不脑补验收或放宽开发交付门禁.

#### Scenario: Only an unverified Jira key is available
- **WHEN** 只有 Jira key, 无法核实 Issue 存在性和当前范围对应关系
- **THEN** 工作流不开始依赖工作, 保留入口缺口, 仅继续允许的只读查证, 不把查询失败当成不存在而重复创建

#### Scenario: Trusted Issue evidence exists but details are inaccessible
- **WHEN** 可信材料已核实真实 Issue 及范围, 普通 Review 无法访问实时详情或讨论
- **THEN** 工作流可按现有可信证据继续限定范围 Review, 披露缺口, 缺少关键验收依据时使用 NEEDS VERIFICATION, 不声称未知内容已核实
