## Why

全局审查与免费模型实测发现, 纯交付入口漏读公司默认值, CI 内嵌交付步骤与统一交付规则冲突,
完成门禁与只读测试的适用范围不清. 用户同时要求把环境代码注入经验提炼为跨环境、跨服务的方法.

## What Changes

- 修正意图路由、CI 修复授权和完成门禁, 交付统一进入 `git-delivery` 并先读取 EasyStack 默认值.
- 保留完整 Review 分析和精简报告, 明确缓存等临时写入也违反只读要求.
- 以前端实际变更行为确定验收边界, 防止文案变更被扩大为创建资源功能.
- 改写现有授权调试文档, 覆盖基线发现、注入方式选择、生效验证和回滚, 保留条件化 Cinder 案例.
- 从全栈工作流及前后端验证入口衔接环境调试, 不复制访问脚本或另建注入教程.

## Capabilities

### New Capabilities

无.

### Modified Capabilities

- `easystack-development-workflow`: 意图门禁、交付策略、只读验证与通用环境调试衔接.

## Impact

用户已确认修改 workflow 的入口、README、后端测试、前端测试、Review 文档,
env-debugging 的入口与 code-debug 文档, CI 的入口与交付转接文档, 共 9 个文件.
补充当前 OpenSpec change 和相应 spec. 不修改访问脚本、AGENTS.md、全局配置或历史归档,
不连接真实环境, 不执行 Git 提交、上传或同步发布.
