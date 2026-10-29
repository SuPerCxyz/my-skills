## ADDED Requirements

### Requirement: 上传命令不得隐含未授权的历史操作

Gerrit 上传示例 SHALL 显式禁用 git-review 的测试 rebase。上传授权 MUST NOT 被解释为授权 rebase、reset 或其它历史整理; 用户已有 Jira 关联、创建和交付授权规则 SHALL 保持有效。

#### Scenario: 仅授权上传当前 Change
- **WHEN** 用户仅授权上传已核实的提交
- **THEN** 示例使用明确 remote、分支及 no-rebase 选项, 不自动执行历史整理或补做 commit/amend

### Requirement: 证据与授权约束的 CI recheck

Workflow SHALL 先读取失败 job 日志, 仅当明确证据确认异常来自 CI 自身且非代码导致,
并核对失败 run 属于当前 Change 与当前 Patch Set/revision、站点支持触发且有效授权
允许远程回复时, 才可发布顶层 recheck review message。MUST NOT 投票、上传或合并。
同一 Patch Set 本轮自动重跑 SHALL 最多一次, 发送前 SHALL 核对消息与队列并避免重复。

#### Scenario: 确认基础设施故障且条件满足
- **WHEN** 日志证明 CI 自身故障且非代码导致, 当前版本、授权、站点触发和去重检查均通过
- **THEN** 向明确 revision 发布一次顶层 recheck, 不附 labels 或 ready/WIP 变更, 再检查对应新 run

#### Scenario: 代码故障或原因未知
- **WHEN** 日志指向代码失败或不足以确认是 CI 自身异常
- **THEN** 不发送 recheck, 报告诊断证据或缺口

#### Scenario: 旧版本、只读或重复触发风险
- **WHEN** 失败 run 不属于当前版本、任务只读或禁止远程写、已有重跑排队/运行、本轮一次已用或提交结果不明
- **THEN** 不重复发送, 先查证可消除的不确定性, 无法核实时如实报告

### Requirement: 新 CI run 的独立结果证据

Workflow SHALL 分开记录回复提交、新 run 排队/运行和最终结果, 通过 Change、revision、
时间和新 run/job 标识关联本次重跑。旧 Verified 或旧 job SHALL NOT 证明本次通过。

#### Scenario: 回复成功但没有新 run
- **WHEN** 回复已提交但有界等待后没有对应新 run 或工具不足以核实
- **THEN** 报告已提交和未验证状态, 不声称 CI 通过也不盲目重发

#### Scenario: 新 run 失败
- **WHEN** 本次新 run 终态失败而旧 Verified 仍成功
- **THEN** 读取新日志并报告本次失败, 不冒充通过, 不再次自动重跑

### Requirement: 遵循现有前端统一设计

Frontend changes SHALL identify and reuse the target project's existing Design System,
component library, theme/tokens, shared style variables and established page patterns.
They MUST NOT introduce arbitrary scattered design literals for colors, typography, spacing,
radii, shadows or stacking levels, or bypass conventions through inline styles or local
variables wrapping arbitrary constants. Meaningful structural layout values and necessary
runtime calculations MAY follow existing conventions without bypassing design or theme rules.
Necessary new design values SHALL be maintained centrally under project conventions and
matching authorization. The workflow MUST NOT introduce a new design system or dependency.

#### Scenario: A frontend change introduces styles
- **WHEN** implementation or review encounters changed frontend styles
- **THEN** it checks actual design sources and reuse, rejects arbitrary hardcoding and disguised constants, and verifies affected visual states and applicable supported themes

#### Scenario: A layout or runtime value is required
- **WHEN** a value has clear structural layout semantics or is calculated from actual runtime state
- **THEN** it may follow the project's established pattern without being rejected solely for containing a literal or binding, while arbitrary design constants remain prohibited

#### Scenario: An existing design value does not cover the need
- **WHEN** a necessary design value is missing from the project's established design sources
- **THEN** it is maintained centrally according to project conventions within authorized scope, or the missing basis or authorization is reported before proceeding

## MODIFIED Requirements

### Requirement: Default frontend debugging to local development

Frontend development debugging SHALL use the target project's local development entrypoint
and authorized API proxy by default, solely for development and preliminary verification.
It MUST distinguish standalone SPA and Host Remote loading and identify the actual code and
API source. Every frontend code modification SHALL then be built from the confirmed source,
deployed through the project's existing entrypoint to an authorized acceptance environment,
and verified in the actual environment page for version, business behavior and visual/theme
effects. Local development MUST NOT replace required deployment and acceptance verification.
The workflow SHALL preserve deployment/configuration baselines, backups and other people's
overlays, use matching existing authorization without repeatedly asking, and MUST NOT infer
arbitrary production, restart or configuration-overwrite permission. Missing environment or
authorization SHALL leave deployment explicitly incomplete while independent work proceeds.
It SHALL report build, deployment and actual acceptance states separately and MUST NOT claim
complete delivery when deployment or required verification remains incomplete.

#### Scenario: Frontend code is debugged against an environment
- **WHEN** a frontend change needs runtime debugging with environment APIs
- **THEN** the workflow discovers the project's actual scripts, serve path, local address and proxy, verifies local code and API provenance for preliminary testing, then completes the required authorized environment deployment and acceptance checks

#### Scenario: An environment page is reached through a tunnel
- **WHEN** the browser can open a tunneled environment page or receives HTTP 200
- **THEN** that alone proves neither changed local code nor the required deployment is loaded; the workflow checks actual bundle/remote/chunk source, entrypoint and base path, cache, content type, host mapping, API target and session/tenant

#### Scenario: No browser or local runtime is available
- **WHEN** the local code and API chain cannot be exercised
- **THEN** static checks are reported separately and local runtime validation remains unverified; the required deployment and actual environment-page acceptance remain explicit requirements and any unavailable verification is reported without claiming complete delivery

#### Scenario: A frontend build is ready for deployment
- **WHEN** the confirmed frontend source and task changes build successfully for the authorized acceptance environment
- **THEN** the workflow records source/artifact/version correspondence, confirms target and compatibility, backs up the effective deployment and recovery baseline, preserves environment configuration and existing overlays, deploys the complete matching artifact through the existing mechanism and verifies actual page code, API source, business and visual/theme effects

#### Scenario: The environment or deployment permission is missing
- **WHEN** the acceptance target, deployment scope or matching action authorization cannot be confirmed
- **THEN** the workflow reports the gap and deployment as incomplete, pauses dependent steps and continues independent work without substituting local testing, assuming production permission or claiming complete delivery

#### Scenario: The build or deployment fails
- **WHEN** the frontend build or environment deployment fails
- **THEN** a failed build cannot be replaced with an old package presented as current; a failed deployment stops expanding impact and uses the preconfirmed recovery plan, with recovery and remaining risks reported truthfully

#### Scenario: The user needs to inspect the frontend change
- **WHEN** the workflow reports frontend code changes to the user
- **THEN** the final response directly gives environment URL and actual version, page entrypoint, changed location, viewing steps, expected results, risks and unverified items by reusing the existing product document; a code-file list or document link alone is insufficient

#### Scenario: There is no visible frontend behavior change
- **WHEN** a frontend code modification has no visible UI change
- **THEN** deployment and applicable verification still remain required, while the workflow describes actual impact and verification without inventing changed interface elements
