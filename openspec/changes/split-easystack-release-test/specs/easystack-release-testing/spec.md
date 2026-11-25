# Spec Delta

## Purpose

为 EasyStack 产品发布测试提供可追溯的用例发现、审查、Web 执行、结果归因和复测流程, 使页面操作能力可以独立复用。

## ADDED Requirements

### Requirement: Route UI operations and release cases to their owners

系统 SHALL 支持独立 Web UI 操作和发布测试入口, 并使用现有原子操作结果约定。

#### Scenario: Run a standalone page action

- **WHEN** 用户仅请求登录、探索、精确查找或执行一次页面操作
- **THEN** Web E2E 核对操作相关的会话、项目和资源, 返回观察与证据, 无须建立发布计划产物

#### Scenario: Start a case from the existing entry

- **WHEN** 用户从 Web E2E 入口要求执行明确用例或测试计划
- **THEN** 加载发布测试 skill 并复用 Web E2E 原子操作, 所需执行能力缺失时记录实际限制

### Requirement: Review release scope and preserve original cases

发布测试 SHALL 记录版本、环境、变更、纳入范围和用例来源, 逐项梳理前置、操作、预期及用例问题。

#### Scenario: Prepare a Web case

- **WHEN** 已选择一个有可追溯来源的 Web 用例
- **THEN** 开测前展示完整前置和步骤及预期, 按用例预检资源与授权, 保持原始编号和业务断言

#### Scenario: Find an issue during case review

- **WHEN** 原始用例步骤、关键输入或预期缺失或冲突
- **THEN** 保留原始证据并记录用例问题, 对改变被测业务或入口的修订保留授权与原因

### Requirement: Interpret observations at case level

发布测试 SHALL 用已确认的原始预期解释实际观察, 维护既有报告格式和结果目录。

#### Scenario: Verify an expected rejection

- **WHEN** Web E2E 观察到业务失败或拒绝且这正是用例预期
- **THEN** 按具体断言判断符合性, 记录真实观察、资源身份和有关证据

#### Scenario: Finish a release plan

- **WHEN** 计划运行结束或部分用例未能执行
- **THEN** 汇总全部用例和原因, 记录覆盖、有效结论、复测及已有准出条件下的阻断项
