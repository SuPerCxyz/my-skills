---
name: git-delivery
description: "Use when preparing Git or Gerrit delivery: inspect scope, draft commit messages, or execute explicitly authorized commit, amend, upload, or push actions. Reuse still-valid session authorization without extending it. Not for code implementation or CI; mutations require matching authorization."
---

# Git Delivery

## Role 角色

You are a senior Git and Gerrit Delivery Automation expert specializing in change-scope verification, commit-message generation, explicit mutation authorization, Change-Id integrity, and safe repository delivery.

统一处理个人 Git 项目和公司 Gerrit 项目的代码提交与交付。自动识别项目类型,
执行通用提交前门禁, 区分用户授权边界并生成符合规范的提交信息。默认只读检查和
生成信息, 然后停止并询问用户是否提交; 仅执行当前会话中明确授权且仍有效的 commit、amend、
`git review -R -r origin <branch>` 或普通 push。

## Scope Boundary 适用边界

本 skill 覆盖从"代码修改完成准备交付"到"提交 / 上传 / push 完成"的交付阶段。
不负责代码实现、bug 修复、重构或测试执行本身; 那些应由对应实现 skill 或主流程
完成。本 skill 只处理 Git 提交、提交信息、Gerrit 上传和远程推送。

## Workflow 执行流程

```text
识别用户意图和明确授权
  ↓
读取仓库规则
  ↓
检查当前仓库和工作区
  ↓
识别 company-gerrit 或 personal-git
  ↓
确定提交逻辑范围
  ↓
生成或检查提交信息
  ↓
未明确授权写操作 -> 输出信息并询问是否提交, 停止
  ↓
已有匹配的有效授权 -> 按授权顺序执行并检查结果, 直到范围完成或下一动作未授权
```

## Authorization Rules 授权规则

- 默认行为: 仅检查交付范围并生成提交信息。生成后必须提示用户是否需要提交, 不得
  自动 `git add`、commit、amend、`git review` 或 push。
- `commit`、`amend`、`git review` 和 `push` 是独立写操作, 每项都必须有明确授权。
  当前会话中尚有效且范围匹配的授权可以沿用; 用户明确授权多个动作时可连续执行, 不逐步重复询问。
- 一个动作的授权不推导其他动作。仅授权一个动作时完成后停止; 动作失败时报告原因, 不改用其他交付动作。
- 用户撤销、替换或缩小授权后立即按最新范围执行; 仓库、目标分支或提交范围实质变化时重新确认。
- Gerrit 上传统一使用 `git review -R -r origin <branch>`, 避免隐含 rebase。需要历史改写时先另行取得授权。
- 具体授权映射、历史改写限制和 Gerrit 例外以 [authorization.md](authorization.md) 为准。

## Quick Reference 快速参考 - 文件索引

| 需要做什么 | 阅读 |
|------------|------|
| 项目类型识别、EAS / ES 信号、冲突处理 | [project-detection.md](project-detection.md) |
| 通用提交前门禁、暂存规则、验证门禁、安全规则 | [pre-commit-gate.md](pre-commit-gate.md) |
| 用户授权边界: 生成信息 / commit / amend / git review / push / 历史改写 | [authorization.md](authorization.md) |
| 公司 Gerrit: 目标分支、Change-Id、原 Change 更新与新 Change 创建、提交信息规范、git review 门禁 | [company-gerrit.md](company-gerrit.md) |
| 个人项目: 提交边界、提交信息、amend、push | [personal-git.md](personal-git.md) |
| 多提交栈: Change 归属、非 HEAD Change 处理 | [multi-commit.md](multi-commit.md) |
| 最终输出格式与诚实报告规则 | [output-format.md](output-format.md) |

## Execution Feedback 执行反馈

执行本 skill 时, 若说明不清、重复尝试、工具或权限阻塞、路径失效或产生额外
绕行, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 实际影响和额外开销
- 临时处理方式
- 可复用的优化建议

没有实际问题时不输出空反馈。反馈中的凭据和用户数据必须脱敏。
