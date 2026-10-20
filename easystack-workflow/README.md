# EasyStack Workflow

为 EasyStack 常用项目提供前后端开发工作流入口, 判断跨仓库联动,
连接版本适配、代码 Review、开发规范和真实功能验收.

## Capabilities 功能

- 根据用户确认的项目关系和实际调用链确定必要修改范围, 区分事实、推断和待查证项.
- 覆盖核心服务、API 网关、公共库、operator、部署与镜像项目, 按实际版本和工具开发后端.
- 保留完整代码 Review 分析流程, 使用 P0/P1/P2/P3 严重性, 精简最终输出.
- 将 Angular 前端的组件、数据层、路由、权限、i18n 和交互规范接入实现流程.
- 区分静态检查、构建与真实功能验收, 按影响调用现有测试、调试和交付能力.
- 代码修改后按需进入授权环境调试, 现场选择注入和生效方式, 保留版本证据与回滚基线.

## Files 文件说明

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 触发条件、意图路由、开发流程和完成门禁 |
| [project-relationships.md](project-relationships.md) | 项目矩阵、跨仓库修改判定和证据要求 |
| [backend-development.md](backend-development.md) | 后端开发流程、规范来源、兼容性和生命周期 |
| [backend-testing.md](backend-testing.md) | 后端回归、CI、契约和真实资源验证 |
| [code-review.md](code-review.md) | 完整 Review 提示词及精简输出约定 |
| [frontend-design.md](frontend-design.md) | 前端实现、设计规范、来源与可选工具边界 |
| [frontend-testing.md](frontend-testing.md) | 前端静态检查、真实功能验收与结果记录 |
| [code-debug.md](../easystack-env-debugging/code-debug.md) | 通用代码注入、生效检查、回滚与条件化 Cinder 案例 |

## Quick Start 快速开始

1. 在支持 skill 的客户端加载 `easystack-workflow`, 提供目标项目、需求或待 Review 的改动范围.
2. 修改任务先识别仓库和相关实现, 按当前会话规则完成需求确认和项目影响分析.
   已确认的任务直接继续; 只读 Review 或纯测试从对应入口开始.
3. 按目标栈读取后端或前端规范, 完成实现和 Review, 再按行为清单验证,
   分别记录 CI、资源测试、UI E2E 和部署检查的实际结果及缺口.
4. 需要将修改带入环境时, 通过 `easystack-env-debugging` 进入通用代码调试方法;
   先发现实际运行版本、有效文件与挂载, 按具体授权执行, 不要求先有线上故障.
5. 需要提交时先读取项目关系文档中的公司默认值, 再按实际授权进入 `git-delivery`;
   加载本 skill 不代表授权 Git 或环境写操作.

例如: 修改云硬盘列表字段时, 先核对 `ebs-dashboard` 到 `golem`、`cinder` 的实际数据路径,
逐仓库说明是否需要修改, 再验证页面请求、数据展示和相关交互. 这不是预设三个仓库都要改.

例如: 修改卷连接行为时, 从 Nova/Cinder 的真实调用与 os-brick 契约核查设备、状态、
版本和失败恢复; 对已满足契约的调用方给出不需改的证据, 不自动修改全部存储项目.

## Dependencies And Distribution 依赖与分发

本 skill 不附带 `es-frontend` MCP、页面生成器、组件库快照或 R2C 模板.
后端以目标仓库的 HACKING、实际版本和工具为准; OpenStack 官方文档及社区 skill
仅作为有范围的参考, 来源见 `backend-development.md`, 不新增安装依赖.
前端规范参考用户提供的 `es-frontend` 0.6.0, 来源见 `frontend-design.md`.
已提供的工具可按需使用; 缺失时读取目标项目已有实现、组件文档和验证入口,
关键事实不能确认时明确说明缺口, 不猜接口或伪称测试通过.

指向其他 skill 的 `../` 链接用于本仓库浏览. 独立安装时按当前环境实际发现的 skill
和工具定位, 不依赖用户机器上的固定路径, 也不自动安装依赖.
