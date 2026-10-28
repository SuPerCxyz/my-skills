---
name: feature-parity
description: "Use when reproducing, porting, synchronizing, or matching functionality from another codebase. Discover observable behavior, track evidence and gaps, implement requested parity, and verify against a pinned reference revision. Not for architecture explanation or comparison without a request to reproduce behavior."
license: MIT
compatibility: Requires source access to the reference and target projects, plus their actual test/runtime tools.
metadata:
  tags: feature-parity, reverse-engineering, codebase-analysis, reimplementation, migration, porting, verification
---

# Feature Parity

将参考项目作为行为证据, 在目标项目中复现用户要求的可观察功能。相似名称、界面或代码结构不能证明功能对齐。
当前用户需求、有效授权和项目规则优先; 不把参考项目的全部能力自动纳入范围。

## Core Rules 核心规则

1. 实现前先调查参考行为, 建立功能清单和初始 parity matrix。
2. 代码、运行行为和测试是主要证据; 文档与截图用于发现线索。
3. 将功能递归分解到可独立实现和验收的叶子, 不用父项掩盖缺口。
4. 保持目标项目原生架构, 除非行为对齐确实要求改变它。
5. 默认按行为独立实现; 直接复用参考代码须有明确要求及兼容的许可和来源。
6. 验证入口、状态、持久化、副作用、错误恢复和反馈, 不只检查代码存在。
7. 不缩小已确认范围; `Partial` 和 `Blocked` 不计为完成。

## Execution Mode 执行模式

- Compact: 单一、低风险、低耦合功能。必须有持久化 `PARITY_MATRIX.md`, 其他清单、证据、计划和验证可合并到该文件或当前有效 artifact。
- Full: 多功能、跨模块、复杂状态、API/UI 或持久化任务。使用下方模板表达所需信息; 已有有效 OpenSpec / Plan 时复用对应内容, 不创建同用途的平行计划。

模式只影响产物组织, 不减少发现、证据、验证和完成门禁。写入前遵守当前会话确认要求。

## Workflow 工作流

### Step 0: Freeze Scope And Revisions 冻结范围和版本

记录参考仓库、分支/tag、完整 commit SHA, 以及目标仓库、分支和基线 commit。
固定参考 revision 定义本次对齐依据。revision 变化后重新核验相关证据; 只有用户要求跟随上游时才自动重新建立基线。
明确范围、对齐维度、限制和已接受差异, 读取 [范围与证据规则](references/00-scope-and-evidence.md)。

### Step 1: Discover Reference Behavior 调查参考行为

先定位 UI/routes、API/CLI 注册、配置、schema、jobs/events、集成、测试和恢复路径, 再追踪代表性调用链。
读取 [发现流程](references/01-discovery.md)。

### Step 2: Decompose Features 分解功能

按入口、输入、状态、副作用、输出、权限、配置、错误、生命周期及并发边界分解功能。
每个叶子应有独立验收标准。读取 [功能分解](references/02-feature-decomposition.md)。

### Step 3: Build Evidence And Matrix 建立证据和矩阵

为叶子分配稳定 ID, 如 `F-001.1a`, 记录参考证据、目标证据、状态、验证和差异。
状态为 `Missing`、`Partial`、`Implemented`、`Blocked`、`Out-of-scope`、`Intentional divergence`。
`Partial` 只是过渡状态; 尚未满足的独立行为应继续拆分。

Gate A: 每个范围内叶子都有 ID 和实际参考证据, 且目标现状已核查, 才能开始实现。
读取 [矩阵规则](references/03-parity-matrix.md)。

### Step 4: Plan Implementation 规划实现

按依赖规划纵向切片, 对齐功能 ID、验收、原生组件、测试和迁移/兼容性要求。
Compact 可内嵌计划; Full 使用现有有效 artifact 或 `IMPLEMENTATION_PLAN.md`。
读取 [实施纪律](references/04-implementation.md)。

### Step 5: Implement And Reconcile 实现并对账

逐切片核对参考证据, 完成最小充分实现、测试和可执行的行为检查, 更新目标证据和矩阵。
相关新发现新增叶子, 不隐藏在旧行内; 超出已确认范围时遵守需求确认门禁。
Gate B: 仅有代码不能声明完成对齐。

### Step 6: Verify Behavior 验证行为

优先差分黑盒、契约和真实场景, 无法执行时明确标记 inspection-only, 不冒充运行验证。
按叶子记录结果与剩余差异。读取 [验证规则](references/05-verification.md); UI 任务同时读取 [UI 对齐](references/06-ui-parity.md)。
环境具备浏览器或专项测试能力时按真实项目使用, 不强制安装特定工具。

### Step 7: Audit Omissions 反向检查遗漏

独立于现有矩阵分类, 重新扫描注册面、配置、迁移、异步任务、集成、测试、错误恢复和文档线索。
未覆盖的范围内行为新增矩阵行并重新实现。
Gate C: 无未解释的 `Missing` / `Partial`; 每个 `Blocked` 写明阻塞、影响和所需解决方式。
`Blocked` 仍属未完成, 用户接受的永久差异须显式重分类为 `Intentional divergence`。

### Step 8: Report Parity 输出对齐结果

报告各状态数量、验证和重要差异。只有所有范围内叶子均有证据, 非有意差异叶子已验证 `Implemented`, 无 `Blocked`, 且遗漏审计完成时才声明完整对齐。

## Matrix Audit 矩阵校验

脚本路径相对于本 `SKILL.md` 所在目录解析, 不相对于目标项目。显式传入实际矩阵路径:

```bash
python3 <skill-directory>/scripts/parity_audit.py <matrix-path>
```

初建矩阵、批量修改结构/状态后, 以及 Gate B、Gate C 和完成前执行。矩阵未变化可复用最近成功结果。
退出 `0` 表示结构检查通过, `1` 表示结构/一致性问题, `2` 表示文件不可用。失败后修复并重跑。
结构通过不能证明证据真实或行为已对齐; 人工证据与行为门禁仍须完成。

## Subagents 子 Agent

委派服从当前会话规则。主 Agent 维护范围、稳定 ID、权威矩阵和最终判断, 子任务返回具体证据。
读取 [编排规则](references/07-subagent-orchestration.md), 不用多个会话各维护一份权威矩阵。

## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| 用途与快速开始 | [README.md](README.md) |
| 范围、版本和证据 | [00-scope-and-evidence.md](references/00-scope-and-evidence.md) |
| 调查参考注册面与调用链 | [01-discovery.md](references/01-discovery.md) |
| 拆分可验收功能叶子 | [02-feature-decomposition.md](references/02-feature-decomposition.md) |
| 矩阵状态和不变量 | [03-parity-matrix.md](references/03-parity-matrix.md) |
| 实施与来源边界 | [04-implementation.md](references/04-implementation.md) |
| 行为验证 | [05-verification.md](references/05-verification.md) |
| UI 行为和视觉对齐 | [06-ui-parity.md](references/06-ui-parity.md) |
| 子任务与独立审计 | [07-subagent-orchestration.md](references/07-subagent-orchestration.md) |
| 功能清单模板 | [FEATURE_INVENTORY.md](templates/FEATURE_INVENTORY.md) |
| 证据模板 | [EVIDENCE_MAP.md](templates/EVIDENCE_MAP.md) |
| 矩阵模板 | [PARITY_MATRIX.md](templates/PARITY_MATRIX.md) |
| 实施计划模板 | [IMPLEMENTATION_PLAN.md](templates/IMPLEMENTATION_PLAN.md) |
| 验证报告模板 | [VERIFICATION_REPORT.md](templates/VERIFICATION_REPORT.md) |
| 方法来源与许可 | [ATTRIBUTION.md](ATTRIBUTION.md), [LICENSE](LICENSE) |
| 结构校验与回归测试 | [parity_audit.py](scripts/parity_audit.py), [test_parity_audit.py](tests/test_parity_audit.py) |

## Execution Feedback 执行反馈

出现说明不清、重复失败、工具/权限阻塞、路径失效或额外绕行时, 结束时报告触发位置、现象、影响、临时处理和优化建议。
没有实际问题时不输出空反馈; 凭据和用户数据必须脱敏。
