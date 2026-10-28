# KVM Test VM Operations

用于在已授权的 KVM/libvirt 节点上复用、创建、调整或验证项目测试 VM. IPv4 为首选访问路径, IPv6 仅作为验证后的保底路径.

## Features 功能

- 按 `inspect/reuse`、`provision`、`resize/reconfigure`、`verify-only` 模式路由操作.
- 项目架构、节点、模板、资源和网络均动态发现, 不预设技术栈或 VM role.
- 使用唯一的标准命令执行克隆、资源调整、磁盘和客户机扩容以及 QGA/SSH 验证.
- 将真实环境和 VM 清单保存在当前项目根目录, 并验证记录是否新鲜以及是否被 Git 忽略.

## Files 文件说明

| 文件 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | 触发边界、模式路由、安全和完成门禁 |
| [references/discovery.md](references/discovery.md) | 项目标识、VM 计划、状态刷新和资源发现 |
| [references/clone-and-resize.md](references/clone-and-resize.md) | 标准克隆、计算资源、磁盘和客户机变更命令 |
| [references/verification.md](references/verification.md) | 标准 QGA、IPv4/IPv6、SSH 和验收命令 |
| [environment.example.yaml](environment.example.yaml) | 项目环境配置模板, 不含真实敏感值 |
| [environment-discovery.md](environment-discovery.md) | 环境记录结构、刷新规则和变量映射 |
| [tests/test_command_gates.py](tests/test_command_gates.py) | 本地 mock 检查无差异不关机、预检先于变更 |
| `project-root/environment.local.yaml` | 当前项目的测试环境事实和凭据来源, 不提交 |
| `project-root/vm-inventory.local.yaml` | 当前项目创建的 VM、地址和就绪状态清单, 不提交 |

## Quick Start 快速开始

1. 确认当前项目根目录和操作模式.
2. 从 `environment.example.yaml` 准备项目根目录的 `environment.local.yaml`, 确认本地状态文件已被 Git 忽略, 并按 `environment-discovery.md` 的变量映射加载环境变量.
3. 按 `SKILL.md` 路由到需要的参考文档; 变更前确认 VM 计划和授权.
4. 创建或调整任务按授权写回 `vm-inventory.local.yaml`; 纯只读检查默认仅报告, 不自动创建或更新本地文件.

不要把项目根目录的 `environment.local.yaml`、`vm-inventory.local.yaml`、密码、私钥或 token 值提交到 Git.

本地回归: `python3 -B -m unittest discover -s <skill-directory>/tests -p 'test_*.py'`。测试不连接真实宿主机或客户机。
