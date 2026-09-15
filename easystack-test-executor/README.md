# EasyStack Test Executor

用于准备 EasyStack OpenStack Compute、Storage、Network、Image、Security、
Bare Metal 及跨服务测试计划, 并在 live 环境中统一执行资源操作、worker logs、
用例状态机、资源证据、清理和结果输出。

## Features 功能

- 从改动点展开关联组件、生命周期、消费者、不支持路径和发散测试义务。
- 首次将 Compute、Storage、Network 环境 profile 固化到外部 runtime profile store,
  后续定向验证后复用。
- 按需查询 OpenStack operation catalog; Server 使用 Boot Volume、Floating IP、
  force delete, 测试 Image 默认为 `public`。
- 将原始计划转换为统一用例, 默认串行处理依赖、失败隔离和重试。
- 按用例需要动态覆盖 Kubernetes 相关 Pod/Container 和实际 worker 日志。
- 使用带 offset 的本地时间记录步骤和资源, 保留 UTC 原始 timestamp。
- 用脱敏日志证明 API/UI 不可见的内部路径。
- 输出中文 Markdown 详细结果, 通过索引跳转到各用例, 页面只显示 `成功` 或 `失败`。
- 索引强制使用中文用例名称和一句简短测试需求, 原技术组合保留为 scenario key。
- 顶层结果只跟随 Functional status, 时间、日志归档和清理异常独立显示为告警。
- 步骤时间或关键日志异常时, 在执行结果下附一条简短说明。
- V3 contract 冻结 profile、impact、authorization、argv、capture 和 checks。
- Event ledger 自动投影 command/resource, 校验 artifact hash, context 压缩后从磁盘恢复。

默认不执行 OpenStack Backup 测试, 除非测试计划明确包含 Backup。

## Quick Start 快速开始

1. 提供目标环境、改动点和原始测试计划。
2. 展开测试义务, 复用环境 profile, 标准化已授权用例。
3. 确认清理策略、破坏性操作和结果目录。
4. 用 `python3 scripts/compile-plan.py --profile ...` 编译 V3 contract。
5. 只执行 `python3 scripts/checkpoint.py next` 返回的 `launcher_argv`。
6. 自动派生 verdict/result, 生成报告并通过 validator。

## Files 文件说明

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 触发范围、工作流、安全门禁和文件索引 |
| [references/openstack-feature-impact.md](references/openstack-feature-impact.md) | OpenStack 功能影响分析和发散测试义务 |
| [references/impact-compute.md](references/impact-compute.md) | Compute 功能和回归影响矩阵 |
| [references/impact-storage.md](references/impact-storage.md) | Storage、backend 和 encryption 影响矩阵 |
| [references/impact-network-image-security.md](references/impact-network-image-security.md) | Network、Image 和 Security 影响矩阵 |
| [references/impact-cross-service.md](references/impact-cross-service.md) | 跨服务依赖图和发散算法 |
| [references/upstream-references.md](references/upstream-references.md) | OpenStack 组件文档、API 和 support matrix 入口 |
| [references/environment-discovery.md](references/environment-discovery.md) | 最小环境确认和 EasyStack 服务发现 |
| [references/environment-profile-cache.md](references/environment-profile-cache.md) | 环境 profile 固化、复用和刷新 |
| [references/common-operations.md](references/common-operations.md) | Compute、Storage、Network、Image、Security 常用操作模板 |
| [references/case-normalization.md](references/case-normalization.md) | 用例标准化、依赖和歧义处理 |
| [references/execution-lifecycle.md](references/execution-lifecycle.md) | 状态机、串并行、失败和重试 |
| [references/resumable-execution.md](references/resumable-execution.md) | 长时间运行、自动记录、断点恢复和完成校验 |
| [references/log-evidence.md](references/log-evidence.md) | 日志窗口、多副本采集和关联证据 |
| [references/reporting.md](references/reporting.md) | 结果状态、输出目录、资源台账和清理 |
| [references/report-format.md](references/report-format.md) | 中文 Markdown 严格输出格式 |
| [examples/environment-profile.example.yaml](examples/environment-profile.example.yaml) | 环境 profile 示例 |
| [examples/test-case.example.yaml](examples/test-case.example.yaml) | 标准化用例示例 |
| [examples/result-template.md](examples/result-template.md) | 严格中文 Markdown 报告示例 |
| [evals/README.md](evals/README.md) | Model eval 定义、重复执行和结果校验 |
| [catalogs/](catalogs/) | 按 domain 查询的 OpenStack operation catalog |
| [examples/](examples/) | V3 profile、plan 和报告示例 |
| [scripts/compile-plan.py](scripts/compile-plan.py) | 编译 immutable V3 contract |
| [scripts/checkpoint.py](scripts/checkpoint.py) | 返回唯一动作并推进状态机 |
| [scripts/run-action.py](scripts/run-action.py) | 执行绑定 argv 并自动记录结果 |
| [scripts/collect-logs.py](scripts/collect-logs.py) | 快照 Pod 并收集严格关联日志 |
| [scripts/finalize-case.py](scripts/finalize-case.py) | 两阶段派生 verdict 和 result |
| [scripts/render-report.py](scripts/render-report.py) | 生成固定中文 Markdown |
| [scripts/validate-run.py](scripts/validate-run.py) | 校验 contract、events、artifacts 和报告 |
| [scripts/validate-evals.py](scripts/validate-evals.py) | 校验 model eval 定义和重复输出完整性 |
| [schemas/](schemas/) | Plan、Profile 和 Observation schema |
| [tests/](tests/) | deterministic harness tests |

## Safety 安全

环境访问优先复用 `easystack-env-debugging/scripts/env-access.sh`, 调用时使用
`bash <path>/scripts/env-access.sh`; standalone 模式只使用用户
提供且已授权的等价入口。环境发现默认只读, 用例外变更必须明确授权。结果文件不得
记录密码、Token、Secret payload、私钥或完整密钥材料。
