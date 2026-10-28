## ADDED Requirements

### Requirement: CI 按 tox major 选择环境且完整覆盖修改行

CI SHALL 从本次 cover/pep8 及其继承的 tox.ini 配置读取明确 Python major,
2 映射 CI Python 2.7, 3 映射 CI Python 3.9。未知、动态未解析或多 major 冲突时
SHALL 报告并停止, MUST NOT 默认 3.9。辅助工具 SHALL 独立使用固定绝对路径的 Python 3,
以 `-I -S -B` 隔离项目路径、PYTHONPATH 和 site 配置, 通过显式指定的实际 CI 解释器
执行仅用内建 sys 的 Python 2.7/3 兼容无 shell 版本查询; 未指定或版本
不符时 SHALL 拒绝 CI 门禁, 不得以辅助进程自身版本冒充 CI 版本。原 tox 显式 minor
目标及项目约束 SHALL 保留并核验, 不擅改 tox.ini 或安装依赖。版本门禁通过不得被描述为
全部 tox 目标和依赖已准备完成。

覆盖范围 SHALL 包含确认 HEAD/base 到最终工作树的全部新增/修改可执行行及分支,
包括 committed、staged、unstaged 和确认范围内未跟踪新源码。未改历史缺口仍为
baseline, 删除和注释不得伪作新增可执行行。

#### Scenario: Python major 映射与实际 CI 门禁
- **WHEN** 所选 tox 环境明确为 Python 2 或 Python 3
- **THEN** 分别要求实际 CI Python 2.7 或 3.9, 由独立 Python 3 辅助工具核验显式 CI 路径, 实际不符时停止

#### Scenario: 同名模块不能伪造门禁结果
- **WHEN** 项目目录或 PYTHONPATH 含同名 json.py
- **THEN** 辅助入口和 CI 版本查询不导入该文件, 使用实际 CI 版本判定门禁

#### Scenario: 未知动态或冲突配置
- **WHEN** 所选配置缺少明确 major、包含未解析因素或多个冲突 major
- **THEN** 报告来源和缺口并停止, 不猜测版本、不自动安装

#### Scenario: 多文件和未提交修改并存
- **WHEN** 确认范围同时含提交修改、staged、unstaged 和未跟踪新源码
- **THEN** 检查完整最终 diff 的所有文件和 hunk, 不只选择部分修改行

### Requirement: 通用 Skill 明确任务触发与排除边界

Skill SHALL 用元数据和入口说明匹配任务及相邻任务的排除边界。任务或阶段改变时 SHALL 重新选择相关 Skill; 已加载且未变化的内容 MUST NOT 为形式重复读取。用户明确点名的 Skill SHALL 先核对其说明, 但加载本身不得扩大用户授权。

#### Scenario: 匹配任务和近邻任务
- **WHEN** 用户提出明确领域任务或相邻领域任务
- **THEN** Agent 选择匹配的 Skill, 不无差别加载所有 Skill, 不把近邻任务误判为同一执行流程

#### Scenario: 用户点名与阶段切换
- **WHEN** 用户点名 Skill 或当前任务切换到另一执行阶段
- **THEN** Agent 核对被点名或新阶段相关 Skill, 复用仍有效的已读内容并保持原授权边界

### Requirement: 上下文 Skill 不定义委派策略

context-efficient-rules SHALL 保持平台无关, 适用于 OpenCode/Codex 等宿主;
MUST NOT 定义子 Agent 的触发、数量、分工、返回或恢复策略, 委派规则由有效 AGENTS.md 负责。

#### Scenario: 使用上下文 Skill
- **WHEN** 宿主加载上下文规则以控制读取和输出规模
- **THEN** 仅应用上下文预算规则, 不由 Skill 改变子 Agent 策略或偏向特定宿主

### Requirement: Skill 文档和示例可复核

Skill SHALL 满足仓库的元数据、标题、标点、索引和内部链接约定, 命令示例 SHALL 明确输入、执行根、版本前提及失败含义。代码、日志和数据示例的必要原文 SHALL 保持语义。

#### Scenario: 搜索为空或命令前提不满足
- **WHEN** 示例的输入文件不存在、解释器约束不明或命令返回失败
- **THEN** Agent 报告对应缺口, 不回退为隐式 stdin、默认版本或成功结论

### Requirement: 验证层次如实区分

通用场景集 SHALL 覆盖现有 12 个 Skill 的正负触发、用户点名、阶段重选和已加载内容去重。静态检查和行为 fixture MUST NOT 被描述为真实模型触发率、客户端加载验证或真实业务验收。

#### Scenario: 本地离线检查完成
- **WHEN** 只执行了结构校验和行为 fixture
- **THEN** 报告实际命令与结果, 明确没有执行真实模型和业务环境评估

### Requirement: Web 操作精确选目标并验证终态

Web Skill SHALL 使用真实资源身份精确选择目标, 遵守凭据和镜像输入契约, 等待实际终态并核对业务效果。文档 SHALL 区分已验证原子操作、场景能力和未验证范围。

#### Scenario: 相似名称与异步资源
- **WHEN** 页面存在相似名称或操作仍在处理中
- **THEN** Agent 核实精确对象且不以 toast、名称出现或中间态宣称成功

### Requirement: Parity 标识和占位值有效

Parity 校验 SHALL 拒绝空 ID、非法 ID 和未解决的占位值, 不破坏正常 matrix 的读取及统计。

#### Scenario: 输入含无效标识
- **WHEN** matrix 中存在空 ID、非法 ID 或占位值
- **THEN** 校验返回明确失败, 不作为完成项统计

### Requirement: KVM 变更先预检且 no-op 不关机

KVM Skill SHALL 在任何 mutation 前完成全部必需预检, 没有实际变化时 MUST NOT 关机或重启。

#### Scenario: 配置已满足目标
- **WHEN** 当前配置与目标相同
- **THEN** 操作作为 no-op 返回, 不改变 VM 运行状态

### Requirement: 匹配来源和工具契约真实

媒体 Skill SHALL 明确 unknown 结果及 provenance, 不伪造匹配来源; Windows Skill SHALL 使用实际工具名称和能力。Git Skill SHALL 沿用会话中仍有效的已确认授权, 不重复索取同一动作权限。

#### Scenario: 未知匹配或已有授权
- **WHEN** 无法确认媒体匹配, 或 Git 动作已有范围匹配的会话授权
- **THEN** 前者保留 unknown 与真实来源, 后者按已授权范围继续; 仅新增动作或越界时补充确认
