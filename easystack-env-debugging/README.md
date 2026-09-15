# EasyStack OSINOS 环境调试

通过统一访问脚本进入 K8s 环境, 对运行在 Kubernetes 上的 OpenStack 服务进行问题
调查或授权代码调试。问题调查优先读取业务 pod 日志; 代码调试可直接用于运行时代码
overlay 和 patch 路径验证, 不要求先完成根因排查。完整资源功能和回归测试使用
独立的 backend 功能测试工作流; 它们不影响本 skill 的在线调查。历史故障需要本地日志时,
可将已取得的离线分析结果作为补充证据, 无需依赖其它 skill 才能开始。

## Features 功能

- 通过统一脚本处理直连、跳板机和 JumpServer 环境访问
- 通过 `--via` 在普通 SSH 跳板机后组合 direct、jump18 或 JumpServer
- 使用权限受限的 `/tmp` profile 复用 JumpServer 密码和私钥
- 批量预检并解除 iSCSI / NVMe-oF Alcubierre volume mapping
- Alcubierre 批次中断后可原样重跑, 无 mapping 的云硬盘自动跳过
- Alcubierre 批次复用 volume 快照, 避免按 UUID 重复全量扫描
- Alcubierre mapping 目标批处理和阶段耗时, 减少 Manul pod exec 往返
- 按当前 pod -> fluentd 历史日志顺序定位运行时故障
- 联合本地 `.eslog` / `ecs.*` 构建历史证据链
- 在用户明确授权后执行 runtime code、overlay 和 patch 路径验证
- 使用含完整核心结论及带具体日志操作时间线的问题调查报告格式

## Quick Start 快速开始

1. 先说明目标是问题调查、代码调试, 还是通过代码改动验证故障假设。
2. 问题调查提供故障时间、资源 UUID 或错误信息; 代码调试提供目标服务、文件、预期
   改动、验证方式和回滚要求。
3. 历史故障需要离线日志时可提供 `.eslog` / `ecs.*` 路径; 未指定路径时只检查
   当前工作目录。
4. Agent 通过 `bash scripts/env-access.sh` 完成最小连接验证, 再进入对应模式。
5. 涉及环境变更时, Agent 先说明影响、回滚和验证方式并等待明确授权。
6. 解挂高性能盘时提供环境和一个或多个 volume UUID; Agent 预检后一次确认,
   再逐盘解挂和验证。

## 文件说明

完整文件索引以 [SKILL.md](SKILL.md) 的 Quick Reference 为准。常用入口:

| 入口 | 用途 |
|------|------|
| [access.md](access.md) | 环境后台访问和统一脚本入口 |
| [alcubierre-unmap.md](alcubierre-unmap.md) | 批量解除 Alcubierre iSCSI / NVMe-oF mapping |
| [scenarios.md](scenarios.md) | 常见云主机、云硬盘、服务启动故障 |
| [logs.md](logs.md) | pod 当前日志和 fluentd 历史日志 |
| [report-format.md](report-format.md) | 含完整核心结论及带具体日志时间线的调查报告格式 |
| [source-analysis.md](source-analysis.md) | kernel 和系统软件包源码调研、版本对齐与证据记录 |
| [auth.md](auth.md) | OpenStack CLI 认证和 busybox |
| [code-debug.md](code-debug.md) | 授权后的 runtime code、overlay 和 patch 路径调试 |
| [openstack/index.md](openstack/index.md) | OpenStack 组件详情索引 |
| [ceph/index.md](ceph/index.md) | Ceph 组件详情 |
| [k8s/index.md](k8s/index.md) | Kubernetes 组件详情 |
| [tests/test-access-scripts.sh](tests/test-access-scripts.sh) | 访问参数、安全重试和 JumpServer 传参回归测试 |
| [scripts/alcubierre-mapping.sh](scripts/alcubierre-mapping.sh) | 目标 mapping 批量查询和结果解析 |
| [scripts/alcubierre-unmap.sh](scripts/alcubierre-unmap.sh) | Alcubierre 远端批量预检、执行和验证 |
| [scripts/run-alcubierre-unmap.sh](scripts/run-alcubierre-unmap.sh) | 通过 env-access 发送固定解挂脚本 |
| [tests/test-alcubierre-unmap.sh](tests/test-alcubierre-unmap.sh) | 批量解挂和中断恢复回归测试 |
