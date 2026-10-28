# Instance Ops

本文件是实例域原子操作索引。所有 `ready-template`
操作必须遵循 `patterns/operation-template.md`,并统一面向 `agent-browser`
的批量执行示例。

## Usage 使用约定

- 配置默认值统一来自 `/tmp/easystack-env.json`
- 显式参数优先于环境默认值
- 进入实例域前应先执行 `patterns/login.md` 的登录契约
- 当前修订的操作模板尚无真实 UI 验证证据
- `ready-template` 操作已补齐模板但执行时仍需现场确认
- 每个当前可用操作必须验证目标状态,而不是只验证点击成功
- 返回值统一使用结构化对象,并包含 `ok/resource/action/status/message/url`

## Migration Status 迁移状态

| 操作 | 状态 | 文档 |
|------|------|------|
| `create_instance` | `ready-template` | [instance-ops/create-instance.md](instance-ops/create-instance.md) |
| `delete_instance` | `ready-template` | [instance-ops/delete-instance.md](instance-ops/delete-instance.md) |
| `attach_volume` | `ready-template` | [instance-ops/attach-volume.md](instance-ops/attach-volume.md) |
| `rename_instance` | `ready-template` | [instance-ops/rename-instance.md](instance-ops/rename-instance.md) |
| `start_stop_reboot_instance` | `ready-template` | [instance-ops/start-stop-reboot.md](instance-ops/start-stop-reboot.md) |
| `create_instance_snapshot` | `ready-template` | [instance-ops/create-snapshot.md](instance-ops/create-snapshot.md) |
| 其他实例操作 | `planned` | 本文件待迁移操作清单 |

## Planned Operations 待迁移操作

以下名称当前仅保留为待迁移操作清单(`planned`),不作为当前可执行入口:

- `resize_instance`
- `suspend_or_pause_instance`
- `reset_instance_password`
- `clone_instance`
- `lock_instance`
- `unlock_instance`
- `rollback_instance_snapshot`
- `delete_instance_snapshot`
- `create_keypair`
- `delete_keypair`
