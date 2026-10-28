# My Skills

个人通用 Agent Skill 仓库, 用于保存和分享可复用的执行规则、领域流程和安全离线验证。

## Skills 技能列表

| Skill | 描述 |
|-------|------|
| [context-efficient-rules](context-efficient-rules/) | 新会话或上下文密集任务的精简规则, 控制检索、读取、输出与恢复摘要, 不代替领域流程 |
| [easystack-ci-test](easystack-ci-test/) | EasyStack OpenStack 仓库 CI 与授权修复, 按 tox.ini major 选择 CI Python 2.7/3.9, 独立使用 Python 3 辅助工具, 检查确认范围内全部新增/修改可执行行及分支(含未跟踪源码); Git 交付另行转接 |
| [easystack-cloud-web-e2e](easystack-cloud-web-e2e/) | EasyStack Cloud Web UI 功能和 E2E 测试, 按实际页面精确选目标并验证业务终态 |
| [easystack-env-debugging](easystack-env-debugging/) | 在线 EasyStack OpenStack/Kubernetes 资源调查、授权 runtime 调试和 Alcubierre 解挂, 不用于通用 SSH/OS/GPU 检查 |
| [easystack-log-analysis](easystack-log-analysis/) | 离线 EasyStack .eslog/ecs.* 日志解压、服务映射、关联证据与问题报告, 不要求先有在线环境 |
| [easystack-test-executor](easystack-test-executor/) | EasyStack 后端资源功能测试计划、确定性执行、worker 证据、清理与中文报告; Backup 仅在明确要求时纳入 |
| [easystack-workflow](easystack-workflow/) | EasyStack 开发、Review、产品行为文档与跨项目契约分析, 按当前阶段选择相关测试、调试和授权交付流程 |
| [feature-parity](feature-parity/) | 固定参考版本, 通过行为分解、证据矩阵和差分验证实现跨代码库功能对齐 |
| [git-delivery](git-delivery/) | 个人 Git 与公司 Gerrit 交付检查、提交信息与授权动作, 沿用有效会话授权并区分 commit/amend/上传/push |
| [kvm-test-vm-ops](kvm-test-vm-ops/) | 已授权项目 KVM/libvirt 测试 VM 的复用、创建与调整, 先完整预检, 无变化不关机, 验证 QGA 和 SSH |
| [media-library-organizer](media-library-organizer/) | 本地影视媒体库 TMDB 匹配、重命名、NFO 与图片整理, 先 dry-run, 保留 unknown/provenance 和回滚依据 |
| [windows-mcp-operation](windows-mcp-operation/) | 通过实际 windows-mcp 工具操作真实 Windows 桌面, 浏览器页面任务按实际浏览器能力处理 |

`docs/` 保存参考与评估材料, 不是 Skill; 其中 `docs/superpowers/` 是历史 plan/spec 存档。
[通用场景评估](docs/skill-evaluation/README.md) 覆盖 12 个 Skill 的正负触发及会话行为。
`openspec/` 保存通用规格和 change, 不代表业务或模型评估已经通过。

## Usage 使用方法

```bash
# SSH clone URL 与本仓库 remote 一致
git clone ssh://git@git.soocoo.xyz:10022/superc/my-skills.git
```

将需要的完整 Skill 目录交给客户端支持的 Skill 发现/读取机制, 保留其脚本和参考文档。
元数据 description 用于判断何时读取正文; 熟悉任务不能代替加载匹配的执行规则。
新会话按 context-efficient-rules 的入口执行, 领域工作只读取当前相关 Skill 和参考部分;
用户点名或任务阶段变化时重新核对边界, 已加载且未变化的内容不重复读取。

加载 Skill 不扩大用户授权。通用 Skill 可以改善可发现性和规则表达, 不能强制宿主调用,
也不能保证模型每次选中或遵循。纯只读、实施、测试及 Git/环境操作权限分别按有效要求判断。

## Validation 验证

静态格式与链接检查、命令行为 fixture 和真实模型/环境评估是不同层次。
本仓库的离线测试不证明模型调用率或真实业务结果。常用定向入口:

```bash
python3 -B easystack-ci-test/tests/test-discover-python.py
python3 -B easystack-ci-test/tests/test-diff-coverage.py
python3 -B easystack-log-analysis/tests/test-search-examples.py
```

这些 fixture 可在现有 Python 3 上验证辅助逻辑, 不执行目标项目 CI; 真正的 EasyStack CI
仍必须按 tox.ini major 映射 2 -> 2.7、3 -> 3.9, 并通过实际 CI 解释器门禁。
Python 3 辅助工具使用独立绝对路径, 不让 CI 2.7 执行它们。其他领域测试见相应 Skill 的文件索引。
真实模型评估按 [评估说明](docs/skill-evaluation/README.md) 单独授权和记录, 不生成虚构成绩。

历史验证: 2026-10-28 前一修订共 78 项离线回归通过, 其中 CI 辅助 fixture 的 18 项使用已有的
真实 Python 3.9.25 执行。另完成静态、链接及独立交叉审查; 未执行真实 tox、业务环境
或模型评估, 这些结果不代表实际资源验收或模型触发率。

当前修订验证: 2026-10-28 的 tox major 映射改动通过 22 项 CI 离线测试,
其中 13 项解释器 fixture 使用真实 Python 3.9.25, 9 项覆盖率 fixture 使用系统
Python 3.14.4。另以真实解释器查询验证辅助 3.14 -> CI 3.9 成功、辅助 3.9 -> CI 3.14
被拒绝, 项目同名 json.py 也不能伪造版本。已检查位置未发现现成 Python 2.7,
2.7 查询与门禁链路仅通过 mock 验证;
未运行真实 tox 或模型。定向格式、内链、元数据和 OpenSpec strict 检查通过。

## Add a Skill 新增技能

在根目录创建独立 Skill 目录, 遵循仓库 AGENTS.md 的命名、格式和权限要求:

- `SKILL.md`: YAML frontmatter 含匹配目录名的 name、双引号 description, 并有完整文件索引与执行反馈规则。
- `README.md`: 用途、功能、文件说明和最小快速开始。
- 参考文档、脚本和 fixture 按需添加并登记, 不将临时环境资料或凭据纳入分发。

根 Skills 列表按字母序维护, 描述与入口实际能力一致。通用评估定义和离线行为测试应
分别记录, 未执行的模型/平台或业务检查如实保留为未验证项。
