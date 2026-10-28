## Why

全量只读审查发现部分 Skill 的标题、链接和触发边界不一致, CI 解释器与覆盖率说明、日志搜索示例及交付命令会产生错误或越界行为。Skill 可发现不等于模型已经加载或遵循, 需要可复核的通用场景与行为验证。

## What Changes

- 修复现有 12 个 Skill 的格式、索引、链接、触发和排除边界, 只在任务确实匹配时加载相关 Skill。
- 将上下文核心规则保持为平台无关的通用 Skill 内容, 适用于 OpenCode/Codex 等宿主; 不定义任何子 Agent 策略, 委派规则完全由有效 AGENTS.md 负责。
- CI 按 tox.ini 明确 major 映射 2 -> 2.7、3 -> 3.9, Python 3 辅助工具与实际 CI 解释器分离, 核验原 tox 目标约束; 覆盖确认范围内全部新增/修改可执行行及分支(含未跟踪源码), 为命令示例增加安全离线 fixture。
- 修复离线日志的路径、glob、ERE、空输入、时间窗口与证据边界, 保持共享报告格式一致。
- workflow 增加有证据且非代码导致的 CI 自身异常 recheck: 当前 revision、有效授权、同 Patch Set 本轮一次、去重与新 run 结果复查, 不实际触发远程 CI。
- 修复交付命令的隐含 rebase、网络和 Pod 生命周期的绝对推断, 保留用户已有 Jira 规则。
- 修复 Web 精确选目标、等待终态、凭据和镜像输入契约, 区分已验证操作与场景成熟度。
- 修复 parity 空/非法 ID 和占位值校验、KVM no-op 不关机及 mutation 前全量预检。
- 修复媒体匹配 unknown/provenance、Windows 真实工具名称和 Git 会话授权持续性。
- 补充通用正负触发场景与评估说明, 区分静态检查、行为 fixture 和真实模型评估。

## Capabilities

### New Capabilities
- `portable-skill-quality`: 通用 Skill 的触发边界、文档质量和可复核评估。

### Modified Capabilities
- `offline-log-analysis-workflow`: 复用完整解压结果, 搜索示例正确且负结果不冒充不存在。
- `easystack-development-workflow`: 交付命令不得隐含未授权的 rebase。

## Impact

修改现有 Skill、根 README、docs/skill-evaluation 通用场景和本 change 的 artifacts。保护当前 workflow 的 Jira 授权修改。明确排除任何 AGENTS.md、客户端配置、安装副本、plugin/adapter、平台初始化、收费模型调用、真实业务资源和 Git 写入; 不保证模型触发率。
