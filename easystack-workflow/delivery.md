# EasyStack Delivery

## Scope And Authorization 范围与授权

本文件包含本目录开发流程必需的 Git 交付规则, 不依赖其他 skill. 公司默认站点、
身份及 master 约定以 [project-relationships.md](project-relationships.md) 为准;
后端验证见 [backend-testing.md](backend-testing.md), 前端验证见
[frontend-testing.md](frontend-testing.md). 项目当前规则与用户有效要求优先,
关键冲突在写入前说明并确认. 本文件中的命令是执行入口, 不是已执行记录.

默认只读检查并生成可审阅的提交信息和交付范围, 然后询问是否执行具体操作.
开发、测试通过、生成提交信息或要求整理交付均不代表 Git 写入授权.
创建 Jira 必须获得用户针对本次创建的明确授权; 缺少编号或用户通常要求创建 Jira
不构成授权. 创建授权不包含 Git 写入、Jira 状态流转、关闭或评论等其他操作.

| 用户明确授权 | 可执行范围 | 不包含 |
|--------------|------------|--------|
| commit / 提交当前修改 | 检查并仅暂存本轮逻辑范围, 普通 commit | amend、上传、push |
| amend / 修改当前提交 | 核对归属并更新已确认的 HEAD 提交 | 上传、push、修改非 HEAD 提交 |
| 提交到 Gerrit / git review / 更新评审或 Patch Set | 对已核实的提交执行 Gerrit 上传 | 自动补做 commit 或 amend |
| push | 向已确认 remote 和分支普通推送 | commit、amend、force push |

commit、amend、git review、push 必须各有明确独立授权. 已确认且仍有效的具体授权
按原范围执行, 不逐文件重问; 一个动作的授权不延伸到下一动作. 完成后报告真实结果,
未授权的下一动作停止并询问. 失败不改用另一交付动作, 不扩大范围或自动重试写历史.
rebase、squash、重排、cherry-pick、merge、force push、删除分支或远程 Change、
abandon 等须另获针对目标和影响的明确授权. 不自动修改 Git 配置、remote 或环境.

## Repository And Scope 仓库与范围

先核对任务仓库、实际 remote、分支、HEAD、目标基线及已有修改. 按需只读执行:

```bash
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git branch -vv
git rev-parse HEAD
git status --short
git diff --stat
git diff --cached --stat
git log -n 20 --format='%h %s'
```

按明确文件路径读取完整 unstaged/staged diff, 同时检查未跟踪文件内容. remote
若含凭据只报告脱敏结果. 不以目录名、本地分支名或网页站点替代真实 remote 和版本.
已有修改默认为用户或协作者所有, 记录本轮范围与既有差异; 不覆盖、回退、删除、
擅自暂存或提交无关内容. 同文件混有无关修改时只纳入已核实的本轮 hunks,
不能安全隔离时停止写入并说明冲突.

一个提交对应可描述、可验证、可评审和可回滚的逻辑变更, 可含直接测试和必要文档.
无关修复、格式化、依赖升级不混入. 逐仓明确文件、hunks、提交和依赖边界,
不能从多仓开发推导多仓交付授权.

## Delivery Mode 交付模式

识别顺序为用户明确说明、仓库规则和贡献文档、近期提交 EAS 编号、实际 remote
及历史交付方式、Change-Id、路径中独立 ES 标识. 例如只读检查近期任务信号:

```bash
git log -n 20 --format='%s %b' | rg -i 'EAS-[0-9]+'
```

EAS 任务编号是强公司信号, 不能用源码变量或普通单词推断. `.gitreview`、Change-Id
或路径仅是辅助证据, `tests`、`services` 中的 es 不构成公司标识. 冲突或无法可靠
判断时可继续只读检查和生成候选信息, 在任何交付写入前确认模式.

公司默认值沿用 project-relationships 的已记录约定, 不因本地信息缺失声称没有默认.
评审网页不替代 Git remote, 不自动修正 remote. 个人 my-skills 不套用公司默认身份;
rainbow-doc 保留 GitLab 实际入口和交付方式, 不机械执行 git review.

个人 Git 遵循目标仓库的分支、PR/MR 和提交风格; 已采用 Conventional Commits
时沿用, 否则使用简明 summary 和必要正文. 默认不添加 EAS、Change-Id 或
Gerrit Depends-On. amend 还须确认最近提交归属、共享状态、协作者影响及仓库允许.

## Baseline And Change 基线与评审归属

EasyStack 无明确代码依赖的 Patch 基于 master 独立提交, 不叠加之前未合入 Patch.
同需求、topic、任务编号或修改先后不构成依赖. 必要依赖记录具体 Patch、代码位置、
无法独立的原因及是否已合入 master; 已合入不保留多余提交链或 Depends-On.
按核实的本地或远程跟踪基线检查父提交、提交范围和 diff, 例如基线确认为
origin/master 时:

```bash
git log --oneline origin/master..HEAD
git diff --stat origin/master...HEAD
git show -s --format='%H %P%n%B' HEAD
```

按文件查看完整基线 diff, 不只看统计. 本地跟踪引用不能证明远端最新状态,
无法确认时报告缺口. 不为满足基线要求擅自切换、清理分支或改写历史.

多提交时检查提交图和逐提交信息, 将每个 SHA、Change-Id、EAS 及依赖对应清楚:

```bash
git log --oneline --decorate --graph -n 30
git log -n 30 --format=fuller
```

当前修改只能进入所属 Change. 目标不在 HEAD 时停止直接 amend, 报告提交关系和
安全处理方案, 另获历史改写授权后处理. 上传或 push 前检查完整待发送提交范围,
避免携带无关提交, 不只核对 HEAD.

更新原 Gerrit Change 须核实同仓库、同目标分支、同一逻辑范围, 原 Change 未 merged
且仍可更新, 不需独立评审或回滚, 用户没有要求新 Change. 保留正确 Change-Id,
amend 后 SHA 会变, 不声称 SHA 不变. 已 merged、不宜恢复的关闭 Change、独立
功能、仓库或目标分支变化应创建新 Change, 不复用其他 Change-Id.
通过实际可用只读入口核实远端 open/merged/abandoned 状态及归属, 不能仅凭本地
Change-Id 判定. 无法访问时披露限制; 新建和 amend 均有明显风险时先确认.

## Message And Identity 信息与身份

公司 summary 不超过 50 字符, 动宾或祈使结构, 无句末句号, 默认不用 feat:/fix:.
空一行写必要正文, 每行不超过 72 字符, 说明实际问题、修改、兼容影响及真实验证.
根据确认需求、完整范围 diff、根因和测试生成信息, 不只复述最初需求.

每个 EasyStack Patch 的提交信息必须关联与修改内容对应的真实 Jira 号,
例如 `EAS-123456`; 多个相关 Patch 可共用一个 Jira. 根据用户提供的信息或实际查询
核实编号及问题范围, 不照抄无关历史编号. 新建/更新 Patch 和完整待上传范围均逐项
核对关联, 不只检查 HEAD. 缺少对应编号时告知用户, 暂停相关 commit/amend/上传;
已授权且不依赖编号的分析和实现可继续.

Jira 描述必须包含问题原因、复现步骤、解决办法三项. 原因未知时标明待查证;
未能复现时记录已知条件、实际尝试和结果, 不虚构复现过程. 解决办法区分拟实施方案
和已验证结果, 未知或未验证项如实标明. 用户明确授权创建后, 使用实际可用工具核实
目标项目、Issue 类型、必填项和当前 Jira 登录用户身份, 默认指派该用户本人,
不从 Git 姓名或邮箱推断 Jira 账号. 身份或必填信息无法核实时报告缺口并暂停创建,
不猜测或绕过.

创建后核实真实编号、URL 和指派结果, 再将真实编号关联 Patch. 创建或指派失败、
结果不明确时, 如实报告已创建/未创建/待核实状态及剩余项, 暂停依赖该结果的交付,
先查证结果, 不将部分成功声称为完成或重复建单. 无可用工具或缺少创建权限时, 提供含上述三项的
可复制草稿, 明确尚未创建; 待取得真实编号后再继续相关交付. 不自动安装工具或配置凭据.

Footer 仅使用有依据的真实编号, 放在信息末尾:

```text
Partial-Bug: #EAS-123456
Related-Bug: #EAS-123456
Related-Task: #EAS-123456
Closes-Bug: #EAS-123456
Depends-On: I<已核实的依赖 Change-Id>
Change-Id: I<由 hook 生成或原 Change 保留的标识>
```

上述是格式示意, 不直接复制占位符或全部 footer. 部分完成用 Partial-Bug,
确认对应 Bug 范围完整解决才用 Closes-Bug, 仅相关用 Related-Bug/Related-Task.
不无依据升级关闭语义, 不虚构任务或依赖. 新 Change 由 Gerrit commit-msg hook
生成合法新 Change-Id, 不手写随机标识. hook 缺失或失败时停止相关操作并报告,
不自动安装、修改环境或追加未经授权的 amend.

EasyStack 项目提交代码必须使用 `easystack.cn` 公司账户. 新提交的 Author/Committer
及 amend 的当前 Committer 按 [project-relationships.md](project-relationships.md)
的邮箱约定核实, 姓名不猜测. 新建提交前只读检查 `git var GIT_AUTHOR_IDENT` 和
`git var GIT_COMMITTER_IDENT`; amend 前另核对原提交保留的 Author 与最终生效的
Committer, 不只检查 `user.email`.
上传前逐一核对实际待交付提交的 Author/Committer, 不只检查当前配置或 HEAD.
身份不符合公司账户及上述邮箱约定, 或无法核实时, 暂停相关交付并报告差异,
明确处理方式后再继续已授权动作. amend 保留作者归属; 原 Author 邮箱不符时,
先明确具体提交、作者归属和处理方式, 不自动 `--reset-author` 或批量改署历史.
身份约定本身不授权修改配置或提交.

## Verification And Staging 验证与暂存

执行授权动作前, 将确认行为与实际实现、Review、有效 artifact 和测试结果逐项对账.
按项目已有入口核对相关测试、lint、类型检查、构建和强制检查, 不机械全跑,
不把静态检查或 Mock 当实际业务验收. 失败须区分本轮、既有和环境原因;
修复后重验, 不隐藏关键失败或未经明确要求跳过关键失败远程交付.
关键验证无法执行时报告原因、替代检查和剩余风险, 不声称完整通过或可交付.

检查所有候选内容含未跟踪文件, 排除日志、缓存、构建产物、调试临时文件和无关
编辑器文件; 根配置、CI、依赖、环境模板变化须有相应范围授权. 检查凭据、Token、
API Key、私钥及敏感数据, 发现疑似泄露停止纳入提交并脱敏报告, 不输出完整秘密.

仅在 commit/amend 已授权后按明确路径或已核实 hunks 暂存, 不使用 git add .
或其他无差别暂存. 不为隔离本轮修改撤销他人暂存. 若索引已有无关内容,
先保留并说明, 无法安全保证只提交本轮范围时暂停提交, 不直接 commit 整个索引.
暂存后检查完整 `git diff --cached`, 使用 `git diff --cached --check` 检查空白错误,
确认最终索引和提交信息一致, 只提交本轮范围.
禁止 reset --hard、clean -fd、直接修改 .git 内部文件或为清理删除用户修改.

## Authorized Commands 授权后的命令

以下各动作独立授权, 不是自动连续执行的脚本. 路径、消息文件、remote 和分支均须
先解析为核实值, 不将占位符原样执行, 不将不可信输入拼接成 Shell 代码.
多行信息写入安全临时文件后使用 -F, 不用易触发命令替换的拼接方式.

```bash
git add -- <本轮已核实文件路径>
git diff --cached
git commit -F <已审阅的提交信息文件>
```

amend 授权且目标确为 HEAD 时, 信息仍准确可执行 `git commit --amend --no-edit`;
范围、根因或验证变化时使用 `git commit --amend -F <已审阅的信息文件>`, 保留正确
Change-Id. 操作后核实实际 SHA、身份、信息、提交 diff 和剩余状态.

公司 Gerrit 目标分支按用户要求、仓库规则、原 Change 目标、upstream、明确基础
分支和稳定历史惯例依次判断, 不直接用本地工作分支名. 核实 origin 指向目标项目,
目标不明或 origin 不符时停止上传并确认, 不改 remote.
新建 Change 和更新已有 Change 的 Patch Set 均须显式将真实 Gerrit Topic 设为该 Patch
对应的 Jira key 本身, 例如 `EAS-123456`, 不加 `#` 或 footer 标签,
不以提交标题或 footer 代替 Topic 元数据. 同 Jira 的 Patch 使用一致 Topic,
仍遵循 master 独立 Patch 和真实代码依赖规则.
单 Patch 关联多个 Jira 且用户未明确主号时先确认; 一次上传涉及不同目标 Topic 时,
先确认上传范围, 不任取编号或用一个 `-t` 覆盖不同 Topic 的 Change. 缺号沿用前述门禁.
确认发送范围、Jira 与 Topic 对应关系、EAS footer、Change-Id、新 Change/新 Patch Set
归属和验证后, 在单独上传授权下执行:

```bash
git review -R -r origin -t <已核实的Jira号> <已核实的目标分支>
```

例如目标确为 master 且 Jira 为 EAS-123456 时执行
`git review -R -r origin -t EAS-123456 master`. 不用裸 git review,
`-R/--no-rebase` 显式禁用 git-review 的测试 rebase, 避免其内部 rebase/reset 恢复动作.
不以上传授权推导历史整理授权; 工具要求超出授权的操作时停止并报告.

已有 Change 且没有新 Patch Set 时, 带 `-t` 的上传也可能被 Gerrit 以 `no new changes`
拒绝; 若被拒绝, Topic 不会因此更新. 不得为设置 Topic 制造新 Patch Set. 仅在已有明确授权覆盖
该目标 Change 的 Topic 元数据更新时使用以下独立入口, 不从上传授权推导该写入权限:

```bash
ssh -p 29418 <user>@review.easystack.cn \
  gerrit set-topic <change> --topic <Jira号>
```

先核实并替换用户、Change 和真实 Jira 号占位符, 设置后通过实际 API 或页面回读 Topic,
确认等于对应 Jira key, 分别报告 Topic 结果和本次未产生新 Patch Set 的事实.
无匹配授权、更新失败或无法核实时如实报告, 不自动补写 Topic 或执行其他写入.

个人 Git 在单独 push 授权下, 核实 remote、目标分支、待推送提交及远端历史影响后:

```bash
git push <已核实的remote> HEAD:refs/heads/<已核实的目标分支>
```

不默认 force push. 拒绝、冲突、权限、hook 或分支错误均根据真实输出处理,
不切换目标、不绕过 hook、不自动 amend/rebase/push 替代失败动作.

## CI Recheck Reply CI 重跑回复

CI 重跑属于独立远程写入, 只在 [backend-testing.md](backend-testing.md#remote-ci-recheck-远端-ci-重跑)
规定的证据、当前 revision、有效授权、去重及一次上限全部满足后执行. 不从上传、
开发或本地测试授权推导 recheck 授权; 已明确允许本条件规则的授权按原范围执行.

使用实际可用的 Gerrit 能力或已认证等价入口, 在已核实 Change 的当前准确 revision
上发布顶层 Reply/review message, 消息仅为 `recheck`. API 入口为
`POST /changes/{change-id}/revisions/{revision-id}/review`, 请求体仅含
`{"message": "recheck"}`; 路径值来自核实结果并按入口正确编码, 不原样执行占位符.
使用封装工具时显式传入已核实 change_id、revision_id 和 message, 不依赖默认 current.
不要调用行内评论接口, 不传 labels、ready 或 work_in_progress, 不投票、不切换
WIP/ready、不上传 Patch Set、不合并. 发送前若 revision 已变化则停止并重新核对.

回复成功只说明消息已提交. 按测试文档查询新 run 的排队、运行及最终结果; 网络中断
或提交结果不明时先回读消息并查证, 不盲目重试. 无工具或权限时报告未发送与剩余项,
不安装 MCP 或切换到未经授权的入口.

协议参考: [Gerrit Set Review](https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#set-review)
与 [Zuul Gerrit trigger](https://zuul-ci.org/docs/zuul/latest/drivers/gerrit.html).
具体触发取决于目标站点已确认的 pipeline 配置, 协议支持顶层消息不等于站点支持 recheck.

## Results And Feedback 结果与反馈

报告路径、范围、实际验证与未验证项、真实执行的 Git 动作及成功/失败/未执行状态.
commit 成功不等于上传成功, 单仓成功不等于多仓完成. Change 链接和 Patch Set 编号
只取自实际输出或已核实远端; 没有就标记未取得, 不虚构命令、退出码、测试或评审状态.
上传后通过实际可用的远端只读入口逐项核对每个 Change 的真实 Topic 与对应 Jira key
一致, 不以命令参数或上传成功代替元数据核验. 分别报告上传状态与 Topic 设置/核验状态;
设置失败、Topic 不符或无法核实时说明剩余项, 不声称完整交付,
不自动改历史、补写 Topic 或执行其他写入.
多仓仅在用户要求时逐仓汇总 remote、目标分支、依赖、验证与整体剩余项.

执行中若出现说明不清、重复尝试、工具或权限阻塞、失效路径或额外绕行, 结束时报告
触发位置、现象、实际影响、临时处理和优化建议. 没有实际问题时不输出空反馈,
凭据和用户数据必须脱敏.
