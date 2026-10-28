## Context

本仓库分发通用 Skill。现有 OpenSpec 数据和 CLI 可直接创建 change, 无需生成任何客户端工具配置。用户已确认本轮只修复通用 Skill 和验证材料。

## Goals / Non-Goals

目标是使文档与现行契约一致, 命令示例可在离线 fixture 中复核, 触发与排除边界明确, 并如实报告验证层次。保持最小充分修改和现有独立分发能力。

不修改任何 AGENTS.md、外部客户端或安装目录, 不创建平台指令、plugin、adapter 或初始化文件, 不执行模型、云资源和 Git 写操作, 不建立通用平台框架。

## Decisions

1. 复用各 Skill 的既有边界和索引, 将相关 Skill 的加载放在实际任务或阶段转换处; 已加载且未变化的内容不重复读取。context-efficient-rules 保持 OpenCode/Codex 等宿主通用的上下文规则, 完全不定义子 Agent 策略, 委派由有效 AGENTS.md 负责。缺少工具时按实际能力报告或采用已有等价入口, 不安装补齐。
2. 从本次 cover/pep8 及继承的 tox.ini 配置读取明确 Python major, 2 映射 CI 2.7、3 映射 CI 3.9; 未知、动态或多 major 冲突时报告并停下, 不默认 3.9。独立 AUX_PYTHON 固定为已核实的 Python 3 绝对路径, 以 `-I -S -B` 运行辅助入口; 激活 CI 环境后取得实际 CI_PYTHON, 辅助脚本通过无 shell 且仅用内建 sys 的 Python 2.7/3 兼容版本查询执行门禁, 缺少显式 CI 路径或版本不符时拒绝。ready_for_ci 仅表示该版本门禁通过, 原 tox 显式 minor 和项目约束另行核验, 不擅改 tox.ini。覆盖范围包含确认 HEAD/base 到最终工作树的全部新增/修改可执行行和分支, 合并 committed、staged、unstaged 和确认范围内未跟踪新源码; 未跟踪源码只读枚举并生成全新增 diff, 不擅自暂存。历史未改缺口仍为 baseline。
3. 日志示例明确从解压根检索, 先枚举真实文件再读取, 空文件集不回退到 stdin。负查询只证明对应文件和时间窗未命中; 实际重试时间来自时间戳与目标版本。
4. 交付示例显式禁用 git-review 的测试 rebase, 所有写入仍受既有授权约束。用户已有 Jira 条款保持原语义。
5. 在 docs/skill-evaluation 维护小型正负场景集, 复用常见 prompt/expected_output/expectations 结构。离线验证不填写模型成功率; 未来真实评估必须独立保存输出并语义评分。

6. 远端 CI 先读 job 日志, 只有证实非代码的 CI 自身异常才可在有效授权内自动重跑。发送前核对当前 Change/revision 和消息/队列, 同 Patch Set 本轮最多一次; 顶层 review message 仅含 recheck, 不投票或上传。回复成功、CI 新 run 排队/运行及最终结果分开记录, 失败或未知不盲重试。使用可用已认证入口, 不依赖固定 MCP、其他 Skill 或新 runner。

## Risks / Trade-offs

- 文档示例与真实部署版本可能不同: 用实际配置优先和未验证项限制结论。
- 过宽的触发可能增加上下文: 加载匹配 Skill, 近邻任务明确排除, 阶段变化重新判断。
- 并行写入冲突: 各组独占目录, 根 README 和 OpenSpec 由一个执行者集成; 不覆盖用户已有改动。

## Validation

运行与改动匹配的安全离线 fixture、已有定向测试、元数据/标题/标点/链接检查、共享模板一致性和 OpenSpec 校验。不把这些结果称为实际模型触发率、客户端生效或真实业务验收。
