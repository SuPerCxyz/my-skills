# Proposal

## Why

Web E2E 同时维护页面原子操作、发布用例编排和汇总格式。单次页面操作需要精简的执行入口, 发布测试需要完整的用例和结果管理。

## What Changes

- 新增 `easystack-release-test`, 负责发布范围、用例发现与审查、开测前展示、资源预检、用例结论和复测汇总。
- 将 `easystack-cloud-web-e2e` 收敛为可独立使用的页面操作与优化入口。旧入口收到用例或测试计划时引导加载发布测试 skill。
- 发布测试通过现有原子操作和结果结构执行 Web 用例, 延续已确认的报告、证据、资源管理与授权规则。

## Capabilities

### New Capabilities

- `easystack-release-testing`: 发现、审查和执行发布用例, 复用 Web E2E, 输出可追踪的验证结果。

### Modified Capabilities

## Impact

影响两个 skill 的入口、参考文档及根 README。现有浏览器操作、工具、运行时配置字段和结果目录继续适用。实施及验证范围为本地 skill 文档与离线检查。
