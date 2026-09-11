# 我的 Skills

个人 Skill 仓库，用于保存和分享自定义的 AI 编程助手 skills。

## Skills 列表

| Skill | 描述 |
|-------|------|
| [context-efficient-rules](context-efficient-rules/) | 上下文精简 Agent 规则 - 适用于 Claude Code / Router / ccswitch, 通过输出预防、先过滤再截断、渐进读取、搜索限流、MCP/子 Agent 约束和 Autocompact 恢复摘要减少 token 消耗 |
| [easystack-ci-test](easystack-ci-test/) | EasyStack OpenStack 项目 CI 验证与定向修复, 通过后按授权 amend 当前 Gerrit change 并用指定 remote 续提 |
| [easystack-cloud-web-e2e](easystack-cloud-web-e2e/) | EasyStack 云平台 Web UI 端到端自动化测试 — 基于 agent-browser 的原子操作库、页面知识库与测试编排规范，支持云主机 / 云硬盘 / 网络等资源操作的 UI 自动化 |
| [easystack-env-debugging](easystack-env-debugging/) | EasyStack OpenStack/Kubernetes 资源故障调查、授权调试和 Alcubierre 批量解挂, 支持普通跳板与 JumpServer 访问 |
| [easystack-log-analysis](easystack-log-analysis/) | EasyStack `.eslog` 安全解压、跨服务跨节点根因定位, 与 env-debugging 使用相同的行首安全、无表格报告格式 |
| [easystack-test-executor](easystack-test-executor/) | EasyStack OpenStack Compute、Storage、Network、Image、Security、Bare Metal 影响分析, 基于 immutable contract 的确定性执行器、worker 日志证据和中文 Markdown 报告 |
| [feature-parity](feature-parity/) | 参考项目功能对齐与复刻 - 证据驱动的行为分解、parity matrix 追踪、实现门禁与差分验证, 将参考项目视为可执行行为规范复现到目标项目 |
| [git-delivery](git-delivery/) | 个人 Git 项目和公司 Gerrit 项目的统一代码提交与交付, 自动识别项目类型, 执行通用门禁, 区分授权边界, 生成规范提交信息并按授权执行 commit / amend / git review / push |
| [kvm-test-vm-ops](kvm-test-vm-ops/) | 项目级 KVM/libvirt 测试 VM 复用、创建、调整和验证, 按 VM 计划执行资源与磁盘操作, IPv4 首选、IPv6 保底, 验证 QGA 和 SSH 就绪状态 |
| [media-library-organizer](media-library-organizer/) | 媒体库 TMDB 刮削、重命名、NFO 和图片整理, 默认 dry-run 并为全部本次修改生成回滚计划 |
| [windows-mcp-operation](windows-mcp-operation/) | 通过 windows-mcp 操作真实 Windows 桌面和系统工具, 浏览器页面操作交由 agent-browser |

> 目录下 `docs/superpowers/` 为 superpowers 工作流产生的 plan/spec 设计文档存档，并非 skill，仅作参考留档。

## 使用方法

将本仓库 clone 到本地，在 AI 编程助手中引用 skill 路径即可使用。

```bash
# SSH(推荐，对应仓库 remote)
git clone ssh://git@git.soocoo.xyz:10022/superc/my-skills.git

# HTTPS
git clone https://git.soocoo.xyz/superc/my-skills.git
```

## 添加新 Skill

在本仓库根目录下新建 skill 文件夹，按统一约定编写:

- `SKILL.md`(必需):开头 YAML frontmatter，包含 `name` 与双引号包裹的 `description`(建议以 "Use when..." 句式描述触发场景)
- `README.md`(推荐):该 skill 的用途、文件说明与快速开始
- 其余参考文档按需放在同目录下，并在 `SKILL.md` / `README.md` 的文件索引表中登记
