## Why

现有 `easystack-workflow` 已有前端规范和通用流程, 但缺少后端开发与验证细则,
项目地图也未覆盖本地实际使用的服务、API 网关、公共库、operator 和部署项目.
用户已确认扩展为前后端工作流, 并要求基于实际项目关系判断必要的同步修改.

## What Changes

- 新增后端开发和测试参考, 按目标仓库的版本、架构和工具选择规范与验证入口.
- 基于 `~/EScode` 的 26 个 Git 目录、25 个不同 origin 和已核对源码扩充项目地图,
  区分运行时调用、包依赖、部署消费、发版分组和待验证连接.
- 更新 skill 入口、索引、快速开始和根 README, 连接后端、前端、Review 与按授权交付.
- 保留完整 Review 分析流程、精简输出、P0-P3 和现有前端规则.
- 通过文档检查和服务、operator、共享库、备份等场景走查验证工作流行为.

## Capabilities

### New Capabilities

- `easystack-development-workflow`: 有证据的项目关系与前后端开发/验证路由,
  覆盖目标版本适配、后端兼容与异常闭环、验证分层和现有 Review 约束.

### Modified Capabilities

无. 现有四个 spec 的要求均不改变.

## Impact

仅修改 `easystack-workflow/` 的相关文档、根 README 和本 OpenSpec change.
业务仓库只读, 不清理目录、不安装外部 skill 或工具、不修改 AGENTS.md,
不执行 Git 提交/上传. Gerrit MCP 查询被平台权限拦截; 指定网页可达,
但匿名列表为空且现有 SSH 路径未完成主机校验, 本地清单不宣称覆盖完整远端目录.
本次验证针对文档和工作流, 不冒充业务 CI、资源功能测试或 UI E2E.
