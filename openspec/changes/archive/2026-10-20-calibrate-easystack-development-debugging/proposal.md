## Why

用户最新要求将前端本地联调与后端整项目环境调试分开. 旧调试记录中的单文件覆盖、
目录合并和环境前端 dist 替换不能代表该流程, 当前运行配置也与历史示例不同.

## What Changes

- 前端默认使用项目本地 dev-server 和代理, 核实浏览器代码来源及 API 目标环境.
- 后端以完整项目运行代码或匹配构建产物为更新、备份和回滚单元, 覆盖新增、修改和删除.
- 发现实际消费工作负载、旧覆盖优先级和环境生成配置, 分别验证相关副本、运行版本和行为.
- 保留环境、动作授权和功能验收边界, 使用当前校准事实说明示例的适用限制.

## Capabilities

### New Capabilities

无.

### Modified Capabilities

- `easystack-development-workflow`: 区分前端本地联调与后端整项目运行代码替换的流程要求.

## Impact

仅修改 `easystack-workflow/SKILL.md`、`frontend-design.md`、`frontend-testing.md`、
`backend-testing.md` 和 `easystack-env-debugging/code-debug.md`, 以及本 change 和对应 spec.
复用原生子 Agent 单独编写代码调试参考, 主 Agent 串行整合其余文档和验证.
不修改业务仓库、全局配置或注入脚本, 不部署、重启或执行 Git 交付.
