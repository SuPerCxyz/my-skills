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
