# EasyStack Cloud Web E2E

EasyStack 云平台 Web UI 端到端自动化测试 Skill。基于 `agent-browser` 提供可复用的
原子操作、页面知识库和测试编排规范, 支持云主机、云硬盘、网络等核心资源的 UI
操作自动化。UI 失败需要 backend 根因证据时, 可将独立获取的 backend 证据作为补充;
离线 eslog 分析和代码仓库 CI 也属于可选的独立工作流, 不影响本 skill 的前端测试执行。

## Overview 概述

本 skill 可供支持 Agent Skills 的客户端使用, 用于通过 `agent-browser` 对 EasyStack Cloud Web 页面执行 UI 自动化操作和端到端测试。核心设计原则:

- **统一入口**:所有 UI 操作统一通过 `agent-browser` CLI 执行,不混合其他浏览器自动化框架。
- **原子操作库**:页面交互封装为可复用的原子操作(`patterns/`),返回结构化结果。
- **页面知识库**:按资源域维护页面字段、定位方式和交互细节(`instance/`、`volume/`、`network/`、`image/`)。
- **测试编排**:定义测试用例结构、编排流程和结果约定(`patterns.md`、`execution.md`)。
- **减少 token 消耗**:多步骤页面动作合并为批量调用,不逐步依赖 snapshot。

## Documentation Structure 文档结构

| 区域 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | 顶层入口:硬规则、入口路由、决策路径 |
| [connection.md](connection.md), [navigation.md](navigation.md), [interactions.md](interactions.md), [execution.md](execution.md) | 连接登录、页面导航、组件交互、执行规范 |
| [patterns.md](patterns.md), `patterns/` | 测试编排规范与原子操作库 |
| [relationships.md](relationships.md) | 资源关联关系与跨资源测试关注点 |
| [scripts/validate-patterns.py](scripts/validate-patterns.py) | 校验 operation 的 terminal 和 submitted 语义 |
| [tests/README.md](tests/README.md) | 真实文档 helper 的离线行为回归及未验证边界 |
| [patterns/image-ops.md](patterns/image-ops.md) | VM 镜像和容器镜像的独立入口与上传契约 |
| `instance/`, `volume/`, `network/`, `image/` | 页面知识库, 各目录内的 `*-details/` 存放详情页字段、弹窗和测试场景 |

完整文件入口以 [SKILL.md](SKILL.md) 的 Quick Reference 为准, README 不维护逐文件目录树,
避免子目录拆分后索引过期。

## Quick Start 快速开始

### Prerequisites 前置条件

- `agent-browser` CLI(如未安装, 报告建议命令并等待用户确认后安装)
- EasyStack 云平台访问地址和凭据
- 环境配置文件 `/tmp/easystack-env.json`

### Minimal Configuration 最小环境配置

```json
{
  "platform": {
    "url": "https://your-easystack-platform.local",
    "username": "admin",
    "password": "your-password"
  }
}
```

### Typical Workflow 典型使用流程

1. **加载 Skill**:在当前客户端中调用 `easystack-cloud-web-e2e` skill。
2. **准备环境**:确保 `agent-browser` 可用,加载版本匹配说明。
3. **配置登录**:读取 `/tmp/easystack-env.json`,执行登录或复用会话。
4. **选择操作**:根据任务从 `patterns/quick-reference.md` 选择原子操作。
5. **执行用例**:按 `execution.md` 和 `patterns.md` 编排测试流程。
6. **报告结果**:记录资源映射、执行结果和截图路径。

### Example 示例

```bash
# 1. 确保 agent-browser 可用
agent-browser skills get core

# 2. 读取环境配置
PLATFORM_URL=$(python3 - <<'PYCONFIG'
import json
from pathlib import Path
config = json.loads(Path('/tmp/easystack-env.json').read_text())
missing = [key for key in ('url', 'username', 'password') if not config.get('platform', {}).get(key)]
if missing:
    raise SystemExit('missing platform fields: ' + ', '.join(missing))
print(config['platform']['url'])
PYCONFIG
)

# 3. 打开登录页面
agent-browser --args '--no-sandbox' --ignore-https-errors open "$PLATFORM_URL/auth_login/"
```

## Capability Status 能力状态

原子操作按验证成熟度分为三级:

| 状态 | 含义 |
|------|------|
| `ready-validated` | 当前修订有平台版本、日期、用例和脱敏结果证据; 仍须核实现场兼容性 |
| `ready-template` | 已补齐操作模板但尚未完成真实用例闭环验证,执行时需现场确认页面状态 |
| `planned` | 仅保留操作名称清单,不作为当前可执行入口 |

### Current Templates 当前可用模板 (真实 UI 未验证)

- 创建云主机 (`create_instance`)
- 挂载云硬盘 (`attach_volume`)
- 创建云硬盘 (`create_volume`)
- 卸载云硬盘 (`detach_volume`)
- 删除云硬盘 (`delete_volume`)
- 回滚云硬盘快照 (`rollback_volume_snapshot`)
- 删除云硬盘快照 (`delete_volume_snapshot`)
- 分配浮动 IP (`allocate_floating_ip`)
- 绑定浮动 IP (`associate_floating_ip`)

这些操作在当前修订中均为 `ready-template`, 历史运行记录不证明修订后的示例已通过.
完整列表见 `patterns/quick-reference.md`. `ready-validated` 只授予附有版本、日期、用例
与脱敏结果引用的当前修订; 本地 fixture 不替代真实 UI 证据.

## Core Conventions 关键规范

### Hard Rules 执行硬规则

- 所有 UI 操作统一通过 `agent-browser` 执行,不混合其他框架。
- 多步骤页面动作优先批量执行; 按实际页面和异步边界短段执行并逐段回读, 不逐步向用户确认.
- 不逐步依赖 snapshot 驱动操作;snapshot 只用于必要诊断。
- 每个测试用例必须创建新的测试资源,不复用历史资源。
- 资源创建提交后先回读页面和后台状态; 仍未确认时最多使用新 run id 重试 1 次, 第二次
  仍未确认则记为 `creation_unconfirmed` 并停止创建, 不自动清理。
- 清理资源前必须先向用户说明待清理清单,得到确认后才执行。

### Resource Naming 资源命名

用例中 `vm1`、`volume1` 等逻辑名映射为唯一资源名:
`<case-id>-<resource-type>-<runid>`

报告中同时记录逻辑名和实际资源名。

### Result Contract 返回值约定

所有原子操作返回统一结构化对象:

```json
{
  "ok": true,
  "terminal": true,
  "submitted": true,
  "resource": "volume",
  "action": "create",
  "name": "tc-vol001-volume1-abc123",
  "status": "Available",
  "message": "volume created",
  "url": "https://platform.local/ebs/volumes"
}
```

## Maintenance 维护指南

### New Operations 新增原子操作

1. 按 `patterns/operation-template.md` 补齐操作文档。
2. 沉淀到对应资源域的 `patterns/*-ops.md`。
3. 同步更新 `patterns/quick-reference.md` 索引。

### Operation Extraction 操作沉淀触发条件

执行过程中发现以下情况时, 先在报告中记录 `skill_improvements`; 当前任务明确包含
skill 维护或用户确认更新后, 再修改 skill 文档:

- 同一页面动作可能被多个用例复用
- 操作包含 3 步以上稳定页面交互
- 操作会创建、修改、删除或绑定平台资源

### Background Tasks 后台任务

长耗时用例后台任务策略:
- skill 不固定模型名称或推理等级; 后台任务按当前会话 `AGENTS.md`、用户要求和
  平台可用能力选择。

后台任务只负责执行用例和写报告,发现可沉淀操作时记录 `skill_improvements`,由主会话统一更新。
