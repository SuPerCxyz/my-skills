# Case Normalization

## Goal 目标

在访问环境或创建资源前, 将自然语言、Markdown、表格或脚本测试计划转换成统一清单。
保留原始计划作为审计来源。

## Required Fields 必需字段

每个用例至少包含:

```text
id
scenario_key
title
requirement_summary
domain
objective
enabled
impact_refs
capability_status
dependencies
actions
verification
log_requirement
log_targets
cleanup_policy
```

`preconditions`、`inputs`、`timeouts`、`retry`、`destructive_operations` 和
`expected_created_resources` 按场景添加。编译前可使用
[`execution-plan.schema.json`](../schemas/execution-plan.schema.json) 做基础 schema
检查, 最终以 `python3 scripts/compile-plan.py` 的语义校验为准。

`domain` 使用 `nova`、`cinder`、`glance`、`neutron` 或 `cross-service`。Security
Group 用例归入 `neutron`。关联服务写入 `log_targets`, 不创建模糊的通用领域。

`impact_refs` 指向 `feature-impact.yaml` 中的测试义务。`capability_status` 使用
`SUPPORTED`、`UNSUPPORTED`、`CONDITIONAL`、`UNKNOWN` 或 `OUT_OF_SCOPE`。

`scenario_key` 保存原始机器化场景标识, 例如 `encrypt-cirros+spec+hdd`。`title`
是 2-40 个字符的中文可读名称, 技术名词可保留英文。`requirement_summary` 是 6-60
个字符的单行中文句子, 简要说明测试动作和关键预期。

## Normalization Rules 标准化规则

1. 保留用户原始编号和预期。机器化原始标题写入 `scenario_key`, 另生成中文 `title`
   和一句简短的 `requirement_summary`, 不丢失原始语义。
2. 关联功能影响项, 区分支持、条件支持和不支持路径。
3. 将准备步骤、核心操作、等待和验证拆开。
4. 为每个步骤定义唯一 Step ID、PREPARE/EXECUTE/WAIT/VERIFY phase 和预期创建资源。
5. 为每个异步操作定义终态、超时和轮询间隔。
6. 明确资源由本用例创建、复用还是依赖其它用例。
7. 明确成功路径、预期失败和允许的错误状态。
8. 设置 `log_requirement=required|optional|none`; 默认按功能目标判断, 不因为存在
   OpenStack 操作就强制收集日志。
9. 声明确实需要日志证明的内部执行分支及匹配信号。
10. 根据操作路径声明日志目标, 不默认收集全部 OpenStack 服务。
11. 将删除、故障注入、重启、主机操作和后端操作列入
   `destructive_operations`。
12. 未声明清理策略时继承运行级 `preserve_on_failure`。
13. 按 [common-operations.md](common-operations.md) 应用 Boot Volume、Floating IP、
    force delete 和 Image `public` 等全局资源默认值。
14. 在执行前完成名称和测试需求标准化。禁止使用 `-`、`N/A`、`TBD`、`unknown`、
    纯英文组合名或空值代替 `title` 和 `requirement_summary`。
15. 每个 verification 定义唯一 Check ID、`check_type=functional|diagnostic|cleanup`、
    `required` 和 `expected`; 每个用例至少一个 required functional check。
16. dependency 必须引用更早的用例, 避免恢复状态机死锁。
17. Action kind 与 executable 必须匹配 compiler allowlist; 禁止 `bash -c`、`sh -c`
    或其它 shell wrapper。Server stop/reboot/migrate 等控制面状态变更也必须绑定
    已授权的 `destructive_operation`。
18. `env_access` 只允许 `bash <path>/env-access.sh ... -- <ARGV...>`, 不允许直接执行该
    script。只读 Action 禁止 `--cmd` opaque string; compiler 无法证明只读时必须绑定
    已授权的 `destructive_operation`。

不得静默删除、合并或改写用例, 也不得替换 Image、Flavor、Volume Type、Backend、
Compute Host、Secret 或预期结果。

## Ambiguity Handling 歧义处理

发现歧义时:

1. 在标准化清单记录原文和歧义。
2. 优先选择不创建、不修改、不删除资源的解释。
3. 歧义影响正确性或安全时将内部执行状态标记为 `BLOCKED`, 最终 `执行结果` 为失败。
4. 继续处理不依赖该歧义的用例。

以下信息缺失通常属于阻塞:

- 目标环境或 Project 不明确。
- 预期结果无法唯一解释。
- 输入资源无法识别。
- 所需删除或故障注入没有授权。
- 用例要求的服务、后端或功能不可用。
- 默认 Server create 缺少 External Network、Floating IP quota 或绑定能力。
- 环境没有可用的 Server force delete 命令。
- Server create 缺少 Image、Boot Volume Type 或 Boot Volume size。

## Dependency Rules 依赖规则

用例执行前状态使用:

```text
READY
BLOCKED
SKIPPED_BY_PLAN
```

依赖资源未成功创建时, 不得执行 hit、clone、snapshot-derived、migration-derived 或
其它依赖用例, 除非原计划明确允许 alternate source。

失败用例只阻塞其传递依赖。其它独立用例继续执行。

## Log Target Mapping 日志目标映射

常见最小目标:

- Volume create、snapshot、clone、migration、retype:
  Primary 为 `cinder-volume`; scheduling 或 Request ID 需要时再加 scheduler/API。
- Server create: Primary 为 `cinder-volume` 和实际目标 `nova-compute`; 默认
  Floating IP 绑定同时添加 `neutron-server` 或 `proton-server` 和实际 L2/OVN worker;
  scheduling 失败时再加 scheduler/conductor/API。
- Volume attach: 相关 `nova-compute` 加 `cinder-volume`。
- Encryption: `cinder-volume` 加 `barbican-api`; 启动或挂载时加 `nova-compute`。
- Live migration: source 和 destination `nova-compute`, 必要时加 conductor。
- Image create、upload、import: 实际 `glance-api` 和配置的 image store。
- Security Group create/rule/delete: `neutron-server` 或 `proton-server`; dataplane
  行为验证加实际 L2/OVN worker 和对应 Compute node。

只在用例实际涉及网络、协议或后端时添加 Neutron、libvirt、multipathd、iscsid、
NVMe、kernel 或 storage driver。

## Output 输出

将标准化清单保存为 YAML 或 JSON, 使用
[`../examples/test-case.example.yaml`](../examples/test-case.example.yaml) 作为结构参考。
运行 `python3 scripts/compile-plan.py` 后, immutable 副本保存为 `normalized-cases.json`。
