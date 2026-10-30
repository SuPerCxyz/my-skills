## ADDED Requirements

### Requirement: Use English for added and modified code comments

工作流 MUST 要求新增或修改的代码注释统一使用英文且不含中文, 并在 Review 中检查。MUST NOT 为本次要求批量清理历史注释或修改业务字符串。

#### Scenario: A Patch changes code comments
- **WHEN** 当前 Patch 新增或修改代码注释
- **THEN** 实现和审查均核对注释使用英文且无中文, 无关历史注释和业务字符串保持在范围外

### Requirement: Accept the deployed implementation before development Review

开发工作流 MUST 按需求确认和验收初稿、修改代码、依据需求及实际代码补齐适用测试、授权环境部署、真实功能验收、正式 Review 的顺序执行。测试 MUST 覆盖受影响前后端和必要跨层路径, 同时具备可重复自动化 E2E 入口/脚本/断言及可人工执行的前置、步骤和预期。未涉及的一端 MUST 说明不适用, 不生成无关用例。

正式开发 Review 前 MUST 核对 Patch、构建产物与环境运行版本一致, E2E 和本次全部必验项真实通过且无已知 bug。每项 MUST 记录版本、真实执行者、状态和结果; Agent 自动操作 MUST NOT 记为真人执行。MUST NOT 增加真人全部重复执行或签字要求, 但本次必验人工项未执行时不得宣称全通过。环境、工具、必需入口或权限缺失时 MUST 暂停依赖 Review 和提交, 不以静态或 Mock 替代真实验收。

#### Scenario: A development Patch reaches Review
- **WHEN** 代码和适用双轨用例已经完成
- **THEN** 工作流先部署并核实当前版本, 全部必验项真实通过且无已知 bug 后才开展正式开发 Review

#### Scenario: E2E fails or a required manual case is unexecuted
- **WHEN** 环境 E2E 失败、仍有已知 bug 或必验人工项未执行
- **THEN** 工作流保留真实状态并暂停依赖 Review/提交, 不将自动操作冒充真人结果, 修复时更新用例并重新部署验收

#### Scenario: Only one side is affected
- **WHEN** 修改只影响前端或后端, 实际依赖也不要求另一端配套
- **THEN** 工作流验证受影响端及必要调用链, 为另一端记录不适用及依据, 不凭空生成无关用例

#### Scenario: The request is review-only or testing-only
- **WHEN** 用户仅要求只读 Review 或限定范围测试
- **THEN** 工作流保持独立入口与原授权边界, 不自动启动完整开发链、修改代码或部署环境

### Requirement: Require three fresh reviewers for three consecutive clean rounds

提交前每轮 MUST 由主会话新建 3 个干净只读 Agent, 不复用实现、探索或旧审查会话, 不继承旧对话。各 Agent MUST 得到同一完整当前 Patch、明确基线、有效需求/设计边界、必要修改上下文及当前验收和验证结果, 先独立完整审查再互相核验发现, 由主会话按证据汇总。MUST 记录每轮 Patch/基线、3 个会话标识、各结论、交叉核验及主会话汇总。

只有同一最终 Patch 连续三轮无任何有效问题且无影响结论的未决项, 才能进入最终本地门禁。P0-P3 有效问题 MUST 均处理, 任一目标 Patch 修改或有效问题 MUST 清零连续通过计数。需修复时 MUST 退出只读审查组后在已授权范围唯一串行写入, 更新用例并重新部署验收, 再使用 3 个全新 Agent 开始下一轮。调度 MUST 服从当前会话模型能力、槽位和并发规则, 不硬编码模型或扩大容量; 可逻辑退役空闲实现会话腾出审查槽位。能力不足或任一环节未完成时 MUST 报告缺口并暂停提交, 不降低门禁或冒充独立 Review。

#### Scenario: Three rounds review an unchanged accepted Patch
- **WHEN** 当前 Patch 及其环境验收证据持续有效且没有修改
- **THEN** 每轮使用 3 个全新只读会话完成独立审查和交叉核验, 连续三轮无有效问题后进入最终本地门禁, 不机械重复部署三次

#### Scenario: Review causes a repair
- **WHEN** 任一审查发现有效问题并需要修改目标 Patch
- **THEN** 主会话汇总证据、退出审查组并清零计数, 唯一写入者在授权范围修复和更新用例, 重新部署验收通过后以全新三 Agent 审查

#### Scenario: Review capacity or evidence is incomplete
- **WHEN** 无法提供三个干净会话、交叉核验未完成或缺少影响结论的证据
- **THEN** 工作流报告缺口并暂停提交, 不减少 Agent/轮次、复用旧会话或把自查写成独立 Review

### Requirement: Run final local gates after the last clean Review

工作流 MUST 在同一最终 Patch 的最后 Review 通过且功能正常之后, 运行项目已有的 Python pep8 与 coverage 门禁; 其他栈使用项目对应的本地检查和覆盖率入口, 阈值沿用实际项目配置。不适用 MUST 说明依据且不得标成通过, 必需入口缺失 MUST 保留缺口并暂停提交。构建前必要快速检查可以执行, 但 MUST NOT 替代最后 Review 后的最终本地门禁。

最终检查失败引起修复后 MUST 回到用例更新、重部署、真实验收和三轮全新 Agent Review, 再运行最终本地门禁, 不直接沿用旧审查或旧测试结果。只有全部门禁真实通过且最终完整暂存 Patch 与通过版本一致时, 才能执行另有明确授权的 commit/amend; 提交与上传 MUST 分别有明确授权, 审查或测试通过不产生 Git 权限。独立 CI 任务的最多三轮修复限制 MUST NOT 被解释为开发 Review 的三轮无问题标准。

随 Patch 交付的产品文档、tasks 和验收报告 MUST 纳入完整目标 Patch, 在首轮正式 Review 前完成需求、用例、当前环境验收结果与真实稳定动态证据入口并冻结。冻结后的 Review、最终本地门禁及后续验收状态 MUST 记录在目标 Patch 之外的已有交付说明或本次当前会话交付记录, 绑定明确基线和完整 Patch 版本/指纹; 冻结文档通过预先确定的真实入口引用结果, 最终对外说明 MUST 提供实际结果和入口, 不要求最终检查后回填冻结文件或杜撰 URL/平台。确需修改任何目标文档时 MUST 按原规则清零重走闭环, 不得豁免文档变化或将文档排除 Patch。任务勾选 MUST NOT 代替外部记录中的实际最终复审和验收结果。

#### Scenario: Final gates pass for the reviewed version
- **WHEN** 同版环境验收及三轮 Review 已通过, 最后 Review 后的项目本地门禁也全部通过
- **THEN** 工作流核对最终完整暂存 Patch 和已通过版本一致, 仅在另有对应明确授权时执行提交

#### Scenario: A final local check requires a code repair
- **WHEN** 最后 Review 后的 pep8、coverage 或其他栈门禁失败且需要修复
- **THEN** 工作流更新代码和用例、重新部署并真实验收、清零并重做三轮 Review, 然后重新运行最终本地门禁

#### Scenario: An in-Patch product document references later final results
- **WHEN** 产品文档或 tasks 属于完整目标 Patch, 三轮 Review 和最终本地门禁将在冻结之后完成
- **THEN** 文档在首轮 Review 前冻结当前验收快照和真实证据入口, 后续实际结果在目标 Patch 外绑定基线和完整版本记录, 最终说明提供该入口与结果而不回填冻结文件, 无实际通过结果不得放行提交

#### Scenario: A frozen target document must change
- **WHEN** 最终结果产生后仍确需修改目标 Patch 内的文档
- **THEN** 该修改清零三轮计数并按原规则重走验收、全新 Agent Review 和最终本地门禁, 不豁免文档修改

#### Scenario: A repository uses another language or lacks a required gate
- **WHEN** Python pep8 对该项目不适用, 或项目必需的验证入口不可用
- **THEN** 工作流按实际栈选择已有对应门禁, 说明不适用依据, 必需入口缺失时暂停提交而不编造通过或擅自安装依赖
