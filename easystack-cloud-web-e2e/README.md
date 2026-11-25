# EasyStack Cloud Web E2E

通过 `agent-browser` 执行 EasyStack Cloud Web 页面操作, 验证实际业务状态, 沉淀复用的
原子操作和页面知识。

## Quick Reference 快速参考

| 文件或区域 | 内容 |
|------------|------|
| [SKILL.md](SKILL.md) | 入口、执行硬规则和完整文档索引 |
| [connection.md](connection.md), [navigation.md](navigation.md), [interactions.md](interactions.md) | 会话、导航和组件交互 |
| [execution.md](execution.md), [patterns.md](patterns.md) | 执行、取证方法和结果约定 |
| [patterns/quick-reference.md](patterns/quick-reference.md), [relationships.md](relationships.md) | 资源操作索引及业务关联 |
| [patterns/image-ops.md](patterns/image-ops.md) | VM 镜像和容器镜像操作 |
| `instance/`, `volume/`, `network/`, `image/` | 页面知识库和历史场景 |
| [scripts/validate-patterns.py](scripts/validate-patterns.py), [tests/README.md](tests/README.md) | 离线回归与覆盖边界 |

## Quick Start 快速开始

1. 加载本 skill, 检查 `agent-browser` 并读取当前版本操作说明。
2. 按 [连接说明](connection.md) 登录或复用会话, 核对目标项目和目标资源。
3. 通过 [原子操作索引](patterns/quick-reference.md) 选择操作, 执行并回读终态。
4. 返回实际观察、资源 ID 和证据路径。执行指定用例或发布计划时加载
   `easystack-release-test`, 再由它调用本 skill。

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
