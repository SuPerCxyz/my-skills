## Why

开发流程需要将用户确认的英文注释、双轨测试、环境验收、固定 2 + 1 本地审查和最终本地门禁连接成一致的交付闭环. 继续修复已确认的五项规则缺口: Review 前后必验集合混用、上传后 Review Links 缺少核验、已有提交直接上传的质量证据继承不明、首次验证与失败修复的覆盖判据不同, 以及 Jira 尚未核实与仅详情不可读未分流.

## What Changes

- 新增或修改的代码注释统一使用英文, 禁止中文; 不批量清理历史注释或业务字符串。
- 需求确认后形成验收初稿, 修改代码后依据确认需求与实际实现补齐适用的前后端及必要跨层测试, 同时提供可重复自动化 E2E 入口/脚本/断言和可人工执行的前置、步骤、预期。
- 正式开发 Review 前完成授权环境部署、Patch/产物/运行版本核对和当前阶段环境必验项的真实验收, 无已知 bug; Review 后的最终本地门禁不属于此前置集合. 记录真实执行者与结果, 不把 Agent 操作记为真人执行.
- 本地代码 Review 首轮两个干净独立只读 reviewer 并行完整审查, 汇总去重和核验冲突后由唯一写入 Agent 统一修复; 再新建一个独立只读 reviewer 对修复后的完整 Patch 审查一次, 处理发现后结束本次本地 Review. 记录审查版本及修复链, 不把最终未复审修改称为已获无问题复审.
- 固定 Review 及发现处理结束后在最终版本代码运行 Python pep8/coverage 或其他栈对应的项目门禁, 项目阈值保持不变. Python 首次验证和修复重跑均核验完整本次 diff 的新增/修改可执行行及相关分支无 mis/par; 这是将既有 auto-fix 判据收紧为普通验证要求, 不把 tox 命令成功等同于增量覆盖通过. Review 或最终检查失败引起修复后, 更新用例、重新部署验收受影响行为, 不自动重开 Review, 再执行最终本地门禁.
- EasyStack commit/amend 和已有提交直接上传均核对完整目标范围、基线和同版质量证据; 准确且有效的证据可复用, 缺失或失效时暂停依赖动作, 不扩大验证或 Git 权限.
- 上传后对适用公司 Bug 规范的 Jira 核验所有相关仓库/版本的 Review Links; 仅在匹配字段授权内合并、去重并回读, 未完成不声称完整交付. Jira 未核实仍保留前置门禁, 已核实但详情不可读的普通 Review 按关键证据缺口分流.
- 保留普通只读 Review、纯测试的独立入口, 以及版本适配、部署备份恢复、资源保护、Jira/Git 授权和 self-contained 约束。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `easystack-development-workflow`: 统一开发与交付顺序, 明确双轨测试、正式 Review 前环境验收、固定 2 + 1 本地审查、英文注释、最终本地质量门禁和 Jira 交付核验; 对齐可选 CI/Git 能力的 EasyStack 入口.

## Impact

仅修改 `easystack-workflow` 内相关九份文档、`easystack-ci-test` 的 SKILL/README/coverage/auto-fix、`git-delivery/company-gerrit.md` 的 EasyStack 条件分支及本 change 的 proposal/specs/design/tasks. 不修改 AGENTS、CLAUDE、根配置、其他 change、归档、主 Spec、脚本或已安装副本; 不安装、初始化、同步 share-skills、实际操作 Jira/Gerrit/部署业务、执行项目 E2E/pep8/coverage 或进行 Git 写操作. 本次验证限于文档和规格的静态检查, 不宣称真实业务验收已通过.
