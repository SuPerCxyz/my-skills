## 1. Planning 规划

- [x] 1.1 按确认范围完成 proposal、规格和 design, 核对实际 CLI 的 Apply 指令。

## 2. Workflow Documentation 工作流文档

- [x] 2.1 统一 SKILL、README、backend-development 的开发顺序, 保留英文注释与独立入口。
- [x] 2.2 更新 backend-testing、frontend-testing 和 product-documentation 的双轨用例、版本/执行者/结果及最终本地门禁。
- [x] 2.3 连接 runtime 环境验收证据、code-review 三 Agent 审查和 delivery 提交门禁, 闭环修复与清零规则。

## 3. Static Validation 静态验证

- [x] 3.1 检查 diff、新增行标点、frontmatter、内部链接和 OpenSpec strict。
- [x] 3.2 静态走查正常路径及 E2E 失败、Review 修复、最终门禁失败、权限/能力缺失、单端不适用和只读 Review 场景, 如实记录未执行的真实业务验证。

## 4. Independent Review And Acceptance 独立审查与验收

- [x] 4.1 开展干净只读 Agent 审查、交叉核验并修复有效反馈; 最终版本的新一轮干净复审结果在本次当前会话交付记录中按基线和完整 Patch 指纹提供。
- [x] 4.2 完成确认需求与实现对账, 固定本次当前会话交付记录为最终复审和验收的真实证据入口; 仓内勾选不代替该入口的实际最终结果, 未真实通过不放行提交。

## 5. Gate Consistency 门禁衔接修复

- [x] 5.1 同步本轮已确认范围和规格, 区分 Review 前环境必验集合与 Review 后本地门禁, 消除重复定义的循环.
- [x] 5.2 补齐适用 Bug 的上传后 Review Links 集合核验、字段授权、安全合并/去重/回读及未完成状态.
- [x] 5.3 将已有提交直接上传纳入同版完整质量证据核验, 对齐 git-delivery 的 EasyStack 条件分支.
- [x] 5.4 统一首次验证与修复重跑的增量覆盖判据, 区分 tox 结果、质量失败和证据缺口, 保留授权与历史范围边界.
- [x] 5.5 区分 Jira 尚未核实与可信核实后详情不可读, 对齐入口和普通 Review 的继续/阻断条件.

## 6. Follow-up Validation 本轮验证

- [x] 6.1 完成受影响文档格式、标点、frontmatter、索引、链接/锚点、diff 空白和 OpenSpec strict 校验.
- [x] 6.2 按本轮五项确认场景走查输入、阶段、门禁及结果, 核对写入范围并如实记录运行时未验证项.
- [x] 6.3 独立只读复核本轮最终修改并处理有效反馈, 由主会话依据实际证据组织最终验收.

旧章节勾选仅记录原轮次, 不表示本轮五项修复或独立复核已完成.

## Validation Record 验证记录

### Follow-up Validation 本轮五项修复验证

- 2026-11-05: 本轮确认范围已实现, 修改限于 18 个授权 Markdown 文件, 未修改脚本、根配置、安装副本或其他 change.
- `python3 -I -S -B` 内存检查覆盖受影响文档的末尾换行、代码围栏、全角字符、128 个本地链接和 18 个锚点, 以及 3 个 skill frontmatter. 两个已修改 SKILL 的参考文档索引完整. 扩展索引检查发现 git-delivery 原有 README 漏索引, 与 HEAD 对照确认入口未改且问题既有; 本轮未越界修复.
- `git diff --check` 通过. `openspec validate enforce-test-first-review-delivery-cycle --type change --strict --no-interactive --json` 通过, issues 为空.
- 五组静态场景已按输入、阶段、门禁与结果走查: Review 前后集合、Review Links 合并/权限/未知结果、已有提交同版证据复用/失效、首次/修复覆盖判据及 Jira 未核实/详情缺失分流. 保留纯测试、只读 Review 和独立写入授权边界.
- 独立只读复核发现辅助覆盖脚本将既有排除并入 uncovered_lines 的 P2. 已仅在 coverage/auto-fix 原段落补足原始结果保留与分类判定, 不改脚本或新增豁免; 两文件格式、9 个本地链接/锚点和 diff 空白复验通过. 合法既有排除、真实缺口、未知排除和缺测量四分支静态走查完成, 独立复核确认五项无剩余阻断.
- 本次为规则文档修复, 未执行真实 EasyStack 部署、项目 tox/E2E、Jira/Gerrit 写入、Git 提交/推送或 share-skills 同步; 静态验证不代表运行时行为或模型遵循已获验证. 当前 change 保持未归档.

### Previous Validation 原轮次验证

- 2026-10-30 P2 修复后复验: `git diff --check` 通过; Python 3 内存检查九份 skill 文档的 215 个新增行及四份新 change 文档, 无新增全角字符。主入口 frontmatter、文件索引和 Execution Feedback 保留, 84 个内部链接及锚点全部可达。
- `openspec validate enforce-test-first-review-delivery-cycle --type change --strict --no-interactive --json` 退出码 0, 一个 change 通过且 issues 为空。
- 根据修复后文档静态走查正常路径、E2E 失败/必验人工项未执行、Review 修复、最终本地检查失败修复、权限/工具/入口/审查容量缺失、单端不适用及只读 Review/纯测试入口, 顺序、阻断与恢复闭环一致。仓内产品文档在首轮 Review 前冻结, 后续审查和最终门禁真实结果由 Patch 外的当前会话记录按基线与完整版本承接, 不要求回填而再次改动 Patch; 若确需修改目标文档仍清零重走闭环。独立 CI 最多三轮修复未与三轮审查通过计数混用。
- 本轮仅实现文档规则并完成静态验证, 真实业务部署、项目 E2E、人工验收、pep8/coverage 未执行且不适用此次文档任务, 不据此声称业务验证通过。独立干净会话 `/root/clean_initial_review` 原初审未发现有效问题, 后续三个干净 Agent 独立审查及交叉核验确认最终结果回填仓内文档导致版本无法收敛的 P2, 主会话采纳后已修复冻结记录约定。4.1/4.2 记录已开展审查、处理反馈、需求与实现对账及固定本次当前会话交付记录为证据入口; 修复版本的新一轮干净复审和最终验收尚待实际完成, 后续结果仅在该入口按明确基线和完整 Patch 指纹报告, 不回填冻结文件或以勾选替代最终通过。未执行 Git 写操作或 Archive。
