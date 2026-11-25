---
name: easystack-release-test
description: "Use when planning or running EasyStack product release tests or Web UI regression cases and plans: discover and review cases, preview full steps, execute via Web E2E, and summarize coverage, blockers and retests."
---

# EasyStack Release Test

## Scope Boundary 适用边界

负责发布和回归测试的用例发现、梳理、执行与汇总。支持仅审查用例、执行单条用例或执行
测试计划。按本轮授权选择动作, 从当前用例来源保留原始步骤和预期。

执行 Web 用例时, 按当前客户端的 skill 发现机制加载 `easystack-cloud-web-e2e`。
仓库 CI、后端资源测试或后台调查按任务转接可用专项能力。

## Workflow 执行流程

1. 记录待测版本、目标环境、变更范围和用例来源。按发布风险、变更及缺陷回归选择用例。
2. 审查前置、步骤和预期, 保留原始编号。先向用户展示完整用例。执行时加载相关能力,
   预检对应项目、角色、资源、配额和授权。测试计划开测前建立执行汇总。
3. 按原始业务断言调用 Web E2E 原子操作。记录实际结果、终态和证据, 按用例预期判定。
4. 保存用例报告和资源清单。批量执行时更新全量计划汇总, 列出覆盖、阻塞原因和复测结果。

## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| 了解用途、执行依赖和快速开始 | [README.md](README.md) |
| 发现与审查用例、开测前总览、E2E 交接、报告及复测 | [execution.md](execution.md) |
| 核对账号、授权、用例资源和配额 | [environment-intake.md](environment-intake.md) |
| 准备平台连接及静态资源配置 | [environment.template.json](environment.template.json) |
| 已授权的部门、项目、账号与配额准备 | [iam-provisioning.md](iam-provisioning.md) |
| 维护测试计划结果、覆盖和复测汇总 | [execution-summary.md](execution-summary.md) |

## Execution Feedback 执行反馈

遇到说明不清、重复尝试、工具或权限阻塞、失效路径或额外绕行时, 报告触发位置、
问题现象、实际影响、临时处理和优化建议。没有实际问题时省略。反馈须脱敏。
