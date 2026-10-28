# 安全规则

Use this file before actions that can close apps, kill processes, delete files, change registry values, or run impactful PowerShell commands. It supplements the tool-specific reference files.

## 操作前需确认

| 工具 | 危险操作 |
|------|----------|
| `Click` | 未知位置的双击、右键菜单中的危险选项 |
| `Type` + `press_enter` | 执行破坏性命令 |
| `Shortcut` | `alt+F4`, `ctrl+shift+esc` 等可能关闭/中断应用 |
| `PowerShell` | `rm`, `del`, `Stop-Process`, 修改系统/网络配置 |
| `Process` `mode=kill` | 非用户启动的进程 |
| `FileSystem` `delete` | 非临时文件 |
| `FileSystem` `write` | 覆盖已有重要文件 |
| `Registry` `set`/`delete` | 任何注册表修改 |
| `App` `mode=launch` | 安装程序、未知应用 |

## 安全原则

- 状态变更统一执行 `Observe -> Act -> Wait -> Verify`; 验证必须独立回读目标状态
- 读操作(`list` / `get` / `info` / `read` / `search`)可自由执行
- 用户明确要求启动已知普通应用时, 该请求即视为 `launch` 授权; 安装程序、未知应用
  或可能触发系统变更的启动仍需单独确认
- `write` / `set` / `delete` / `kill` 等影响状态的操作需确认具体目标和影响
- 禁止输入密钥、密码、token, 除非用户明确提供并要求
- 不确定操作后果时先询问

## 接口注意事项

- `Type` / `Move` / `Click` 的 `label` 必须是整数(UI 元素 ID), 不能是字符串
- `FileSystem` 的 `path` 相对于 Desktop, 用 `.` 表示 Desktop 本身
- `FileSystem` `read` 读 UTF-16 文件需要 `encoding: "utf-16"`
- `FileSystem` `write` 的 `overwrite=false` 不阻止覆盖; 写入前必须先执行 `info` 或
  `read` 检查目标, 已存在时仅在用户明确允许覆盖后写入
- `PowerShell` 的 Status Code 始终为 0, 需检查输出判断实际结果
- `PowerShell` 写操作完成后还需用独立查询命令验证, 不能只检查命令输出
- `App` `launch` 需要开始菜单中的完整名称
- `WaitFor` 的 `element_exists` + `window_name` 组合可能无法匹配, 优先用 `text_exists`
- `Click` 不支持 `modifiers` 参数, 需要 modifier+click 时组合 `Shortcut` + `Click`

## 环境要求

- 缺少 `mss` 时先报告安装命令和影响, 等待用户明确确认后再安装
- 远程桌面会话中窗口枚举可能不稳定, UI 树通常可用
- `App` `resize` 省略 `name` 时操作系统前台窗口
