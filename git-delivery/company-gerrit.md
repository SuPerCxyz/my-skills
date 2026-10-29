# Company Gerrit Rules 公司 Gerrit 项目规则

## 提交方式与目标分支

公司项目使用:

```bash
git review -R -r origin -t <JIRA-KEY> <branch>
```

EasyStack 上传必须显式携带 `-t`; `<JIRA-KEY>` 是本次 Patch 对应的 Jira key 本身,
例如 `EAS-123456`, 不带 `#` 或 `Related-Task` 等 footer 标签.
非 EasyStack 且没有 Jira 关联的项目可以省略 Topic, 但 EasyStack 不得裸上传.

默认必须同时携带 `-R`、remote 和真实目标分支。`-R` 禁止上传前隐含 rebase, 不修改全局配置。不得把 `<branch>` 字面量
直接传给命令。执行前必须解析出真实目标分支, 例如:

```bash
git review -R -r origin -t <JIRA-KEY> master
git review -R -r origin -t <JIRA-KEY> stable/2026.1
git review -R -r origin -t <JIRA-KEY> feature/example
```

目标分支识别优先级:

1. 用户明确指定的目标分支
2. 仓库规则或任务文档指定的目标分支
3. 当前 Gerrit Change 已有的目标分支
4. 当前分支配置的 upstream 对应分支
5. 当前开发分支明确对应的基础分支
6. 仓库历史中稳定且无歧义的默认评审分支

不得无条件把当前本地分支名称作为 Gerrit 目标分支。按需检查:

```bash
git branch --show-current
git branch -vv
git remote -v
git config --get-regexp '^branch\..*'
```

无法可靠确定时, 不得执行 `git review`, 应简短列出当前检测结果并请求用户确认
目标分支。

## Gerrit Topic

Gerrit Topic 必须等于本次 Patch 对应的 Jira key 本身, 例如 `EAS-123456`, 不带 `#`
或 footer 标签. `Closes-Bug`、`Related-Task` 等 footer、提交标题和本地分支名都不能
代替 Gerrit Topic. 上传参数及非 EasyStack 项目的例外见上节; 命令中的 Jira key、用户、
Change 和分支占位符须先核实替换. 上传后通过 Gerrit API 或页面读取实际 `topic` 字段,
确认等于本次 Patch 对应的 Jira key, 不以命令参数代替核验.

已有 Change 且没有新 Patch Set 时, 带 `-t` 的上传也可能被 Gerrit 以 `no new changes`
拒绝; 若被拒绝, Topic 不会因此更新. 不得为设置 Topic 制造新 Patch Set. 仅在已有明确授权覆盖
该目标 Change 的 Topic 元数据更新时, 可执行以下独立入口; 不从上传授权推导该写入权限:

```bash
ssh -p 29418 <user>@review.easystack.cn \
  gerrit set-topic <change> --topic <JIRA-KEY>
```

设置后回读实际 `topic` 字段, 并分别报告 Topic 更新结果与本次未产生新 Patch Set 的事实.
无匹配授权、更新失败或无法核实时如实报告, 不自动补做其他写入.

## Commit SHA 与 Change-Id 的区别

Git commit SHA 标识一次具体的 Git 提交对象。执行 `git commit --amend`、
`git rebase`、`git cherry-pick` 后通常会变化。

Gerrit `Change-Id` 标识同一个代码评审 Change, 示例:

```text
Change-Id: I1234567890abcdef1234567890abcdef12345678
```

同一个 Gerrit Change 在继续修改和上传新的 Patch Set 时, 应保持原 `Change-Id`。
Git commit SHA 会变化, Gerrit 中生成新的 Patch Set。

用户所说"继续提交到之前的提交"、"commit id 不变", 应正确理解为: 保持原 Gerrit
`Change-Id` 不变, 通过 amend 生成新的 Git commit, 再用
`git review -R -r origin -t <JIRA-KEY> <branch>` 上传到原 Change。不得声称 amend 后 Git commit
SHA 保持不变。

## 更新原 Change 与创建新 Change

更新原 Gerrit Change 需同时满足: 原 Change 尚未 merged、原 Change 仍可继续
更新、当前修改属于原 Change 的同一逻辑功能或 bug 修复、目标仓库未变化、目标
分支未变化、当前修改不需要独立评审、当前修改不需要独立回滚、用户没有明确要求
拆分为新 Change。

以下为可能需要的完整流程, 每项写操作仍须有当前会话有效授权, 未授权动作不得补做:

1. 检查当前 `HEAD`
2. 读取当前提交信息
3. 提取原 `Change-Id`
4. 提取对应的 EAS 任务编号
5. 检查当前修改是否属于该 Change
6. 尽可能确认远程 Change 状态
7. 只暂存属于该 Change 的文件
8. 检查 staged diff
9. 执行相关测试或验证
10. 使用 `git commit --amend`
11. 保留原 `Change-Id`
12. 必要时更新 summary 和正文
13. 再次检查提交信息
14. 使用真实目标分支执行 `git review -R -r origin -t <JIRA-KEY> <branch>`
15. 根据真实命令输出判断是否成功
16. 报告上传的是原 Change 的新 Patch Set

原提交信息仍准确时, 可以使用 `git commit --amend --no-edit`。新增改动改变了
实现范围、问题根因、关键逻辑、兼容性影响、测试范围或 EAS 完成范围时, 应更新
提交正文, 但必须保留原有且正确的 `Change-Id`。

以下情况应创建新的 commit 和 Change: 原 Change 已 merged、原 Change 已关闭且
不适合恢复、当前修改属于独立逻辑功能、当前修改需要独立评审、当前修改需要独立
回滚、目标仓库发生变化、目标分支发生变化、用户明确要求拆分、当前改动与原
Change 主题无直接关系。创建新 Change 时不得复用其他 Change 的 `Change-Id`,
应由 Gerrit `commit-msg` hook 生成新的 `Change-Id`, 不得手写伪造随机
`Change-Id`, 应检查是否需要 `Depends-On`, 不得把无关改动塞入已有 Change。

不能因为本地提交中存在 `Change-Id` 就直接认定远程 Change 尚未 merged。应尽可能
确认 Change 是否 open、merged、abandoned、所属仓库、目标分支以及本地提交是否
对应。当前环境无法访问 Gerrit 时, 明确说明无法确认远程状态, 根据本地证据给出
保守判断, 当新建 Change 和 amend 原 Change 都存在明显风险时请求用户确认, 不得
虚构远程状态。

## 提交信息规范

**Summary**: 不超过 50 个字符, 不加句号, 使用祈使句或动宾结构, 描述本次改动
做了什么, 默认不使用 `feat:`、`fix:` 等 Conventional Commit 前缀, 不使用
"update code"、"fix issue" 等模糊描述, 不机械罗列文件名。

**正文**: summary 后空一行。正文每行不超过 72 个字符。按实际需要说明: 为什么
需要修改、原有问题或限制、修改了什么关键逻辑、为什么采用这种实现、兼容性影响、
升级影响、配置影响、API 影响、数据库或持久化影响、执行了哪些测试。不要为了凑
格式写无实际价值的段落。

**Footer**: 放在提交信息最后。常用格式:

```text
Closes-Bug: #EAS-123456
Partial-Bug: #EAS-123456
Related-Bug: #EAS-123456
Related-Task: #EAS-123456

Depends-On: Ixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Change-Id: Ixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

只添加实际适用的 footer。不得虚构 EAS 编号、Bug 或 Task、`Depends-On` 或手写
伪造 `Change-Id`。不得无依据地把 `Partial-Bug` 改为 `Closes-Bug`。

- 当前修改只完成 EAS 的一部分: 优先 `Partial-Bug: #EAS-123456`
- 确认该 Bug 对应范围已完整解决: 使用 `Closes-Bug: #EAS-123456`
- 只是相关修改: 根据仓库惯例使用 `Related-Bug` 或 `Related-Task`

更新已有 Change 时必须保留原有且正确的 `Change-Id`。

生成提交信息前必须分析: 用户确认后的需求、staged diff、必要时的 unstaged
diff、问题根因、修改方式、行为变化、测试结果、兼容性影响、EAS 任务范围、是
完整修复还是部分实现、是新 Change 还是原 Change 的新 Patch Set。提交信息必须
反映实际修改, 不能仅根据用户最初的一句话机械生成。

## git review 门禁

执行 `git review -R -r origin -t <JIRA-KEY> <branch>` 之前必须确认:

1. 已识别为公司 Gerrit 项目
2. 当前仓库正确
3. 当前本地分支正确
4. Gerrit 目标分支明确
5. remote 确实是 `origin`
6. 提交内容仅包含本次逻辑范围
7. 提交信息符合公司规范
8. EAS footer 正确
9. `Change-Id` 正确
10. 已判断是新 Change 还是新 Patch Set
11. 相关验证已经真实执行
12. 用户已经授权执行 `git review`, 并显式携带 `-R` 避免隐含 rebase

上传后必须根据真实输出判断: 命令是否成功、上传的是新 Change 还是新 Patch Set、
是否出现 branch 错误、Change-Id 错误、权限错误、提交冲突或 hook 问题。无法从
命令输出确认 Patch Set 编号时, 不得虚构编号。
