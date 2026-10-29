## 1. 通用规则和格式

- [x] 1.1 修复 context-efficient-rules 的通用核心、边界和索引; 完全移除子 Agent 策略, 委派由有效 AGENTS.md 负责, 不偏向特定宿主。
- [x] 1.2 修复非 EasyStack Skill 的触发、权限、格式、链接与回滚边界。
- [x] 1.3 修复 Web E2E Skill 的格式、链接、触发与验证边界。
- [x] 1.4 修复其余 EasyStack Skill 的格式、触发与参考文档一致性。

## 2. 命令和行为

- [x] 2.1 按 tox major 选择 CI 2.7/3.9, 分离辅助 Python 3 与实际 CI 解释器并核验原目标, 保留完整改动行及分支覆盖, 更新定向 fixture。
- [x] 2.2 修复日志路径、glob、ERE、时间和负证据说明, 验证共享报告一致。
- [x] 2.3 收敛环境网络/Pod 推断, 修复 workflow 上传示例且保留既有 Jira 条款。
- [x] 2.4 验证 Web 精确目标、终态、凭据、镜像契约及场景成熟度说明。
- [x] 2.5 验证 parity 空/非法 ID 和占位值被拒绝, 正常 matrix 仍可处理。
- [x] 2.6 验证 KVM 无变化不关机, 全部预检先于任何 mutation。
- [x] 2.7 验证 media unknown/provenance 与 Windows 工具名称一致。
- [x] 2.8 验证 Git 已确认会话授权持续有效, 仅新增动作或越界时再确认。

## 3. 集成和验收

- [x] 3.1 增加覆盖 12 个 Skill 的通用正负触发场景及阶段重选/去重/用户点名场景。
- [x] 3.2 集成根 README 描述、文件说明和验证入口。
- [x] 3.3 执行相称的本地测试、格式/链接/元数据及 OpenSpec 校验。
- [x] 3.4 主 Agent 核验全部确认范围、用户改动保护和未验证项, 更新任务事实。


## Previous Validation Record 前一修订验证记录

以下 78 项及固定 3.9 门禁测试是前一修订的真实历史事实, 不作为本轮 major 映射修订的成绩。

- 2026-10-28: 使用已存在的 Python 3.9.25, 以 `-I -S -B` 分别执行
  `easystack-ci-test/tests/test-discover-python.py` 和 `test-diff-coverage.py`, 各 9 项通过.
  覆盖 3.9 允许/3.8 与 3.11 拒绝的门禁、动态约束、完整多文件/hunk、未跟踪新文件、
  缺报告/字段/分支测量、combined diff 和逐文件缺 hunk 的反例.
- `easystack-log-analysis/tests/test-search-examples.py`: 9 项通过, 包括无文件/无命中、
  symlink 来源校验、20 KiB 输出限额及真实文档 ERE/glob 片段. 独立只读复核无剩余阻断.
- 当前集成快照: 12 个 SKILL 主入口元数据/双语标题/索引/执行反馈通过, 206 个 Markdown
  的 691 个内链无错误, 递归全角字符为 0; 45 个 Python AST、11 个 JSON、9 个 Bash 和
  1 个 Node 文件语法通过. 27 个通用 eval 定义覆盖 12 个正负对和 3 个会话行为场景.
- KVM 最终修复后补充增量检查: test_command_gates.py 的 Python 3.9 grammar 通过,
  KVM 47 个内链无错误. 真实 live/persistent 对齐、no-op 和预检门禁经独立交叉审查闭环.
- 全轮离线回归共 78 项: KVM 14、parity 7、media 7、cloud Node 15/Python 8、CI 9+9、
  log 9. CI 的 18 项使用已有真实 Python 3.9.25, 不是模拟解释器运行结果.
- 主 Agent 已完成最终需求对账和保护核验: 原 Jira 22 条非空新增行完整保留,
  AGENTS/全局 AGENTS/OpenCode 配置 hash 不变, 156 个变更路径均在授权范围.
- OpenSpec strict validation、共享报告 cmp 与 git diff --check 通过; 本 change 保留未归档.
- 未运行真实 tox、OpenStack/KVM/Windows/浏览器业务环境或收费模型, 没有模型触发率.
  未修改 AGENTS.md、客户端/安装副本/平台配置, 未执行 Git 写入或 Archive.

## Current Validation Record 当前修订验证记录

- 2026-10-28: tox major 映射改动的 `test-discover-python.py` 以现成真实 Python 3.9.25
  加 `-I -S -B` 执行, 13 项通过. 覆盖 2 -> 2.7、3 -> 3.9、所选环境/继承、
  未知/动态/多 major 停止、缺显式 CI 路径/实际版本不符拒绝、无 shell 版本查询,
  项目同名 json.py 不能伪造版本, 以及真实 setup 门禁片段在恶意 PYTHONPATH 下隔离
  辅助导入、调用同一 mock CI 解释器的 `-m tox` 链路. workflow 自包含 CI 入口也固定
  实际解释器绝对路径并用同一解释器执行 tox.
- `test-diff-coverage.py` 以系统 Python 3.14.4 加 `-I -S -B` 执行, 9 项通过.
  全部新增/修改可执行行及分支、未跟踪源码和历史 baseline 规则保持不变.
- 真实跨版本只读 CLI 查询: 系统辅助 Python 3.14.4 -> 现成 CI Python 3.9.25
  门禁 exit 0; 辅助 Python 3.9.25 -> 系统 CI Python 3.14.4 门禁 exit 2.
  两条查询均在含项目同名 json.py 的临时目录执行, 未导入该项目模块.
  检查的系统、Miniconda 和 pyenv 位置未发现已有 Python 2.7; 2.7 版本查询及文档
  门禁链路使用 mock, 不声称真实 2.7 runtime 或 tox 已验证, 未安装环境.
- 定向 19 个 Markdown 的 70 个内链、全角字符、CI 主入口元数据及 quick_validate
  通过; 4 个 CI Python 文件的 Python 3.9 grammar、setup 门禁 Bash 语法和 27 个通用
  eval 定义结构通过. OpenSpec strict validation 和 git diff --check 通过.
- 当前修订共 22 项 CI 离线测试, 另有上述 2 条实际跨版本门禁查询; 不合并为前一修订
  78 项的重新运行成绩. 未运行真实 tox、业务环境或模型, 未执行 Git 写入或 Archive.
- 独立只读审查已闭环, 无剩余阻断; 审查者另外重放更新文档下的恶意 cwd/PYTHONPATH
  fixture, 真实辅助 3.14 -> CI 3.9 门禁成功且未导入项目 json.py. 主 Agent 已完成 3.4 验收.

## 4. Authorized CI Recheck 已确认的 CI 重跑补充

- [x] 4.1 同步 workflow 入口、README、测试与交付文档, 保留 Jira 和前轮 CI/context 规则。
- [x] 4.2 增加 9 个离线语义场景, 覆盖证据、版本、授权、去重、提交未知及新结果边界。
- [x] 4.3 定向格式、链接、元数据、场景结构和 OpenSpec strict 验证。
- [x] 4.4 主 Agent 独立审查及最终需求验收; 不执行实际远程触发或 Git 写入。

## Recheck Validation Record 重跑规则修订验证记录

- 2026-10-28: 定向 19 个 Markdown 的全角字符检查、78 个本地链接及锚点、workflow
  frontmatter/Execution Feedback 和 36 个唯一场景定义结构通过. 其中新增 9 个 recheck
  离线语义场景, 未执行真实模型, 不声称场景遵循率或行为运行结果.
- `openspec validate harden-skill-quality-and-loading --strict --no-interactive` 通过;
  本轮路径的 `git diff --check` 通过. 前轮验证历史保留, 不冒充本轮重跑成绩.
- 仅只读核实可用 Gerrit 工具元数据, 未调用实际远端工具. 未运行真实 tox、Gerrit、
  CI、云或 VM, 未安装依赖、修改客户端或 AGENTS、执行 Git 写入或 Archive.
- 完整 recheck 运行闭环、站点触发能力和真实模型遵循仍未验证, 本轮仅交付文档规则与
  离线场景定义; 独立只读审查及主 Agent 最终需求验收已完成, 无剩余必须修复项.

## 5. Frontend Design And Deployment 前端统一设计与部署验收

- [x] 5.1 就地同步七份 workflow 文档, 串联统一设计、实现、Review、部署和视觉/主题验证。
- [x] 5.2 将本地联调限于开发/预验证, 明确改后构建、已授权环境部署、版本与配置保护、备份恢复和用户直接查看清单。
- [x] 5.3 同步当前 change 的 proposal/design 及相关 MODIFIED requirement, 保留原场景名称并补充必要验收场景。
- [x] 5.4 执行定向文档格式/链接/元数据、需求与场景语义走查、OpenSpec strict 和 diff 检查, 如实记录验证。
- [x] 5.5 主 Agent 独立审查并逐项验收本轮确认需求, 不执行真实部署或 Git 写入。

## Frontend Validation Record 前端规则修订验证记录

- 2026-10-28: Python 3 只读检查本轮 11 个 Markdown 的 57 个本地链接及锚点, 全部可达;
  七份 workflow 文档无全角字符, 主入口 frontmatter、索引和 Execution Feedback 保留。
  检查同时核对 MODIFIED requirement 和三个原场景名各保留一次, 旧额外部署门禁已移除。
  初次链接检查未识别既有 HTML 显式锚点, 补充解析后复验通过, 未改动该既有锚点。
- 逐项语义走查统一设计来源、禁止任意常量/包装绕过、合法布局与运行时计算、新增值集中维护;
  构建失败、目标/授权缺失、备份与配置保护、部署失败恢复、版本/API/缓存与视觉验证、
  用户直接查看清单及无可见变化路径. 实现阶段 Review 不等待部署结果, 纯只读 Review 不部署。
- `openspec validate harden-skill-quality-and-loading --strict --no-interactive` 与
  `git diff --check` 均通过. 独立只读审查无必须修复项; 主 Agent 已完成 5.5 最终验收,
  核对 11 个路径仅含七份文档和当前 change, 点读核心差异、前端专用模板条件及完整场景,
  确认需求闭环且 AGENTS、全局 AGENTS 和 OpenCode 配置 SHA 未变; 根实际 strict 与 diff 检查通过。
- 本轮仅修订规则与当前有效规格, 没有实际前端源码/构建/部署、浏览器或主题验证、模型评估、
  远端 CI/Gerrit、安装、Git 写入或 Archive. 文档检查不能证明实际环境部署和 UI 行为已通过。

## 6. Jira Conclusion Gate Jira 结论交付门禁

- [x] 6.1 就地补充 delivery 的 Jira/授权/上传/结果段落, 覆盖真实字段、完整 Patch 范围、共享内容保护与更新回读门禁。
- [x] 6.2 简短同步 workflow 入口、完成门禁和 README, 保留既有 Jira 创建、Topic、CI、recheck 与前端部署规则。
- [x] 6.3 同步当前 change 的 proposal/design/spec, 加入正确/过期结论、共享冲突、无授权、接口成功但回读失败等离线语义场景。
- [x] 6.4 执行定向格式/元数据/链接及场景语义走查、OpenSpec strict 和 diff 检查, 如实记录验证边界。
- [x] 6.5 主 Agent 独立审查并逐项完成本轮确认需求验收, 不执行实际 Jira 更新或 Git 写入。

## Conclusion Validation Record 结论门禁修订验证记录

- 2026-10-29: Python 3 只读检查七份本轮 Markdown 的 45 个本地链接与锚点, 全部可达;
  三份 workflow 文档无全角字符, 主入口 frontmatter、文件索引覆盖和 Execution Feedback 保留。
  检查新增八个 Conclusion 场景名唯一, diff 恰好为三份文档及当前 change 的四个 artifacts,
  无未跟踪文件; 已提交的 runtime 注入指引未修改。
- 定点阅读最终 diff 与八个场景, 逐项走查新建/更新与完整交付范围、准确结论免重复写、
  过期结论需维护、共享 Issue 与并发冲突、无字段/工具/权限、接口成功但回读失败、提交结果
  未知先查证及资料失败不能 recheck. 结论不要求未来 SHA/URL/Patch Set 编号, 不形成前置循环。
- `openspec validate harden-skill-quality-and-loading --strict --no-interactive` 和
  `git diff --check` 均通过. 独立只读审查无必须修复项, 主 Agent 已完成 6.5 最终验收:
  点读三份文档完整 diff、Conclusion requirement 与八个场景, 确认需求闭环、七个路径无越界,
  AGENTS、全局 AGENTS 和 OpenCode 配置 hash 未变, HEAD 2fdbdf0 的既有 runtime 内容保留;
  根实际 diff 检查通过。
- 当前没有可用 Jira 工具或实际 CI 校验脚本证据, 字段 ID、类型、可写性及站点具体格式
  仍需执行时发现; 本轮没有实际读取/更新 Issue、Git 写入、CI/Gerrit/环境操作、安装或 Archive。
  场景仅作规则语义走查, 未运行真实模型或验证 Jira 更新、回读及 CI 是否通过。
