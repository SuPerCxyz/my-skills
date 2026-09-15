# 安全与回滚

Use this file whenever a plan may move, rename, write, delete, or roll back files. It is the safety reference for mapping, conflict handling, path boundaries, and rollback verification.

## 校验策略

- 默认记录 `size` + `mtime`
- mapping 中使用 `hash_type` + `hash` 字段，不固定使用 sha256
- `hash_type` 取值:`none` / `quick_hash` / `sha256`
- 小于 1GB 的文件可计算完整 sha256(`hash_type=sha256`)
- 大于 1GB 的文件默认使用 quick_hash，读取文件头尾各 64MB(`hash_type=quick_hash`)
- 用户设置 `full_hash=true` 时统一使用 sha256
- 如果只记录 size + mtime:`hash_type=none`, `hash=null`

## 回滚要求

- `_rename_mapping.json` 必须记录用户确认的 `plan_id`
- 所有计划修改必须先写入 `_rename_mapping.json`, 再生成 `_rollback.sh`
- `_rollback.sh` 必须通过 `bash _rollback.sh` 调用, 不依赖脚本执行位
- operation 支持 `rename`、`move`、`create`、`replace_backup`、`rmdir`
- 每项记录 `status=pending|completed|failed`; 真实操作成功后原子更新状态
- `create` 回滚只删除状态为 `completed`、由本次运行创建且 hash 匹配的文件
- `replace_backup` 回滚从本次备份恢复; `rmdir` 回滚重建本次删除的空目录
- 如果路径被其他文件占用或 hash 不匹配, 回滚中止并提示人工处理
- 回滚脚本必须在任何真实修改前生成并支持 dry-run

## `_rename_mapping.json` 格式

```json
{
  "plan_id": "sha256:<CURRENT_PREVIEW_HASH>",
  "timestamp": "2026-06-15T18:00:00",
  "source": "/data/media/video/综艺/原始目录",
  "files": [
    {
      "old": "/data/media/video/综艺/原始目录/old_name.mp4",
      "new": "/data/media/video/综艺/新目录/Season-01/新名称.mp4",
      "hash_type": "quick_hash",
      "hash": "abc123...",
      "size": 1234567890,
      "mtime": "2026-06-15T12:00:00",
      "operation": "rename",
      "status": "pending"
    }
  ]
}
```

## 冲突处理策略

- 目标路径已存在时默认禁止覆盖
- 自动生成冲突报告
- 可选策略:
  1. `skip`:跳过(默认)
  2. `suffix`:追加 `-dup1` / `-dup2`
  3. `replace`:仅当 dry-run plan 已列出备份操作且用户确认对应 `plan_id` 时允许覆盖

## 附属文件备份规则

- 已存在的 NFO 不允许直接覆盖
- 已存在的 `poster.jpg` / `fanart.jpg` / `banner.jpg` / `clearlogo.png` 不允许直接覆盖
- 如果需要生成同名文件，默认跳过
- 如果用户明确允许 `replace`，则覆盖前必须先备份
- 备份目录为 `_backup_before_rename_{timestamp}`
- 备份文件路径必须写入 `_rename_mapping.json`
- 回滚时只恢复本次备份的文件，不删除用户后来新增的文件

## 路径安全规则

- 禁止处理系统根目录 `/`
- 禁止处理用户 home 根目录
- 禁止处理 `/bin`、`/etc`、`/usr`、`/var`、`/boot`、`/dev`、`/proc`、`/sys`
- 禁止跟随符号链接到输入路径之外
- 所有目标路径必须位于用户指定的媒体库根目录或 staging 目录内
- 对所有路径执行 `realpath` 校验，避免 `../` 路径逃逸
- 删除空目录前必须确认该目录内没有非本次处理文件
