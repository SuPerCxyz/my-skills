# Authorization Boundary 用户授权边界

必须区分不同请求所代表的授权范围, 不得越权执行。当前会话中明确授权且范围未变、未被撤销或替代的动作可以继续执行; 不要求每个动作都在最新消息中重复出现。用户明确授权动作序列时按顺序完成, 未授权的动作不自动补做。目标或范围实质变化时重新确认。

## 仅生成提交信息

用户要求"生成提交信息"、"整理 commit message"时, 只允许检查 diff、分析逻辑范围、
生成提交信息。不代表授权 `git add`、`git commit`、`git commit --amend`、
`git review` 或 `git push`。生成后必须停止, 明确询问用户是否需要提交。

## 提交当前修改

用户明确要求"提交代码"、"帮我 commit"、"提交当前修改"时, 可以视为授权检查并
暂存本次任务文件、执行普通 `git commit`。不代表授权 `git commit --amend`、
`git review`、`git push`、rebase、merge、cherry-pick 或 force push。完成 commit
后仅在后续动作没有匹配授权时停止。

## Amend 当前提交

只有用户明确要求"amend"、"修改当前提交"或等价表述时, 才可执行
`git commit --amend`。不得将"提交代码"、"提交到 Gerrit"或生成提交信息解释为
amend 授权。完成 amend 后仅在后续动作没有匹配授权时停止。

## 提交到 Gerrit

用户明确要求"提交到 Gerrit"、"执行 git review"、"更新原评审"、"上传新的
Patch Set"时, 只授权执行 `git review -R -r origin <branch>`。如果上传前需要 commit 或
amend, 必须已有对应的明确授权; 不得自动补做。已有多个动作授权时可连续执行。
不自动授权 interactive rebase、squash、重排提交、merge、cherry-pick、force push、
abandon 或删除远程 Change。

## Push

只有用户明确要求 push 时, 才能执行普通 push。不得把"commit"或"提交代码"自动
解释为 push。完成已授权的 push 后报告结果。

## 历史改写

以下操作必须获得用户明确授权: `git rebase`、interactive rebase、squash、重排
提交、cherry-pick、force push、修改非 HEAD 提交、合并多个 Gerrit Change、拆分
已有 Gerrit Change。

上传默认携带 `-R` / `--no-rebase`, 不以“上传授权”推导历史改写权限。需要 rebase、解决冲突或重排提交时先报告具体影响并取得对应授权。
