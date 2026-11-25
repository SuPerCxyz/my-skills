# EasyStack Release Test

把 EasyStack 发布变更和回归风险转为可审查的用例清单, 通过 Web E2E 执行并汇总实际结果。

## Capabilities 功能

- 从已指定的 MeterSphere 计划或本地材料发现用例, 按版本、变更和回归风险梳理范围。
- 审查并展示用例前置条件、完整步骤和预期, 记录需修订的用例问题。
- 核对当前环境与资源, 通过 `easystack-cloud-web-e2e` 执行并保留证据。
- 写用例报告和计划汇总, 跟踪覆盖、阻塞、复测和已有准出条件。

## Quick Reference 快速参考

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | 适用场景和入口 |
| [execution.md](execution.md) | 用例发现、执行流程、E2E 交接与报告模板 |
| [environment-intake.md](environment-intake.md) | 账号、资源、配额与授权检查 |
| [environment.template.json](environment.template.json) | 平台和静态测试资源配置模板 |
| [iam-provisioning.md](iam-provisioning.md) | 已授权的测试账号、项目与配额准备 |
| [execution-summary.md](execution-summary.md) | 计划、证据、覆盖及复测汇总 |

## Quick Start 快速开始

1. 提供待测版本、变更说明、目标环境和用例来源, 例如 MeterSphere 测试计划或本地用例文件。
2. 加载本 skill 整理发布范围并展示用例。执行 Web 用例时, 同一客户端须可发现
   `easystack-cloud-web-e2e` 且能使用 `agent-browser`。
3. 根据 [执行说明](execution.md) 核对资源, 执行已授权用例并输出报告。计划执行时维护
   `EXECUTION-SUMMARY.md`。
