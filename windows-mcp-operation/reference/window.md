# 窗口控制

Use this file for launching, switching, resizing, or closing Windows applications. Use [observation.md](observation.md) first when the current window state is unknown.

## App

启动、切换、调整窗口。三种模式:

| 模式 | 用途 | 示例 |
|------|------|------|
| `launch` | 启动应用(需开始菜单中的完整名称) | `{"mode": "launch", "name": "Microsoft Edge"}` |
| `switch` | 切换窗口到前台(支持部分名称匹配) | `{"mode": "switch", "name": "PowerShell"}` |
| `resize` | 调整窗口大小/位置(省略 name 操作活动窗口) | `{"mode": "resize", "name": "Notepad", "window_size": [1200, 760], "window_loc": [100, 80]}` |

### 规则

- 操作前先 `Snapshot` 确认目标窗口
- 无 close 模式, 关闭窗口用 `PowerShell` 的 `Stop-Process` 或 `Shortcut` `alt+F4`
- launch 失败返回 `X not found in start menu.`, 需使用完整名称(如 "Microsoft Edge" 而非 "edge")

### 注意事项

- 远程桌面中 `SetForegroundWindow` 可能被系统拒绝, 日志警告不影响工具返回值
- 若窗口未实际获得焦点, 可用 `PowerShell` 或 `Shortcut` `alt+tab` 替代
