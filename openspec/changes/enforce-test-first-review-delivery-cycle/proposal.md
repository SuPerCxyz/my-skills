## Why

当前开发入口先 Review 再验证, 还允许实现阶段 Review 先于环境部署, 无法保证审查对象已经完成真实功能验收。需要将用户确认的英文注释、双轨测试、环境验收、三 Agent 审查和最终本地门禁连接成一致的交付闭环。

## What Changes

- 新增或修改的代码注释统一使用英文, 禁止中文; 不批量清理历史注释或业务字符串。
- 需求确认后形成验收初稿, 修改代码后依据确认需求与实际实现补齐适用的前后端及必要跨层测试, 同时提供可重复自动化 E2E 入口/脚本/断言和可人工执行的前置、步骤、预期。
- 正式开发 Review 前完成授权环境部署、Patch/产物/运行版本核对和全部必验项的真实验收, 无已知 bug; 记录真实执行者与结果, 不把 Agent 操作记为真人执行。
- 提交前每轮新建 3 个不继承旧对话的只读 Agent, 各自完整审查同一 Patch 后交叉核验, 主会话汇总; 同一最终 Patch 连续三轮无有效问题才放行后续门禁。
- 最后 Review 后在同版代码运行 Python pep8/coverage 或其他栈对应的项目门禁, 阈值沿用项目配置。Review 或最终检查失败引起修复后, 更新用例、重新部署验收并重新完成三轮 Review, 再执行最终本地门禁。
- 保留普通只读 Review、纯测试的独立入口, 以及版本适配、部署备份恢复、资源保护、Jira/Git 授权和 self-contained 约束。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `easystack-development-workflow`: 统一开发与交付顺序, 明确双轨测试、正式 Review 前环境验收、三 Agent 连续三轮审查、英文注释与最终本地质量门禁。

## Impact

仅修改 `easystack-workflow` 内已确认的九份文档及本 change 的 proposal/specs/design/tasks 和 CLI 元数据。不修改 AGENTS、CLAUDE、根配置、旧 change、归档、主 Spec 或其他 skill; 不安装、初始化、实际部署业务、执行项目 E2E/pep8/coverage 或进行 Git 写操作。本次验证限于文档和规格的静态检查, 不宣称真实业务验收已通过。
