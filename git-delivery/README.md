# Git Delivery

统一处理个人 Git 项目和公司 Gerrit 项目的代码提交与交付。自动识别项目类型,
执行通用提交前门禁, 区分用户授权边界并生成符合规范的提交信息。默认只读生成信息,
然后询问是否提交; `commit`、amend、`git review` 与 push 均需明确授权; 当前会话有效授权可沿用, 明确授权的动作序列可以连续完成。

## 功能列表

- 自动识别 `company-gerrit` 与 `personal-git` 项目类型
- 通用提交前门禁: 仓库、分支、工作区、staged diff、无关文件、敏感信息
- 用户授权边界: 区分生成提交信息、commit、amend、git review、push、历史改写
- 公司 Gerrit: OpenStack / Gerrit 提交信息规范, `git review -R -r origin <branch>`
- 原 Change 更新与新 Change 创建判断
- 个人项目: 遵循仓库既有风格, 普通 commit 和 push
- 验证与交付门禁, 如实报告命令、测试和远程操作结果

## 文件说明

| 文件 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | skill 主入口, 含执行流程与文件索引 |
| [project-detection.md](project-detection.md) | 项目类型识别、EAS / ES 信号、冲突处理 |
| [pre-commit-gate.md](pre-commit-gate.md) | 通用提交前门禁、暂存规则、验证门禁、安全规则 |
| [authorization.md](authorization.md) | 用户授权边界 |
| [company-gerrit.md](company-gerrit.md) | 公司 Gerrit 规则、Change-Id、提交信息规范、git review 门禁 |
| [personal-git.md](personal-git.md) | 个人项目提交、amend、push 规则 |
| [multi-commit.md](multi-commit.md) | 多提交栈处理 |
| [output-format.md](output-format.md) | 最终输出格式与诚实报告规则 |

## 快速开始

1. 代码修改完成并准备进入交付阶段时, 加载本 skill。
2. Skill 自动识别项目类型并执行通用门禁。
3. 未明确授权写操作时, 输出提交信息并询问是否需要提交。
4. 按当前会话有效授权完成对应动作或动作序列, 检查结果; 未授权动作或失败处停止。
