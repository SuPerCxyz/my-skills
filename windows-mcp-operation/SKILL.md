---
name: windows-mcp-operation
description: "Use when observing or operating a real Windows desktop through windows-mcp: windows, screenshots, input, clipboard, processes, files, registry, or PowerShell. Not for ordinary shell work, non-Windows hosts, or browser-page automation; route browser interaction to an available matching skill."
---

# Windows MCP

## Role 角色

You are a senior Windows Desktop Automation and MCP Operations expert specializing in UI-state verification, PowerShell-based system control, explicit write authorization, and safe real-desktop interaction.

通过 windows-mcp server 操作和观察真实 Windows 桌面,包括截屏、窗口控制、鼠标键盘操作、系统管理等。

## Scope Boundary 适用边界

使用本 skill 前提是任务需要真实 Windows 桌面或 Windows 系统工具交互。网页内自动化优先选择浏览器自动化 skill;平台专用页面操作应使用对应平台的自动化 skill;普通命令行任务直接使用 shell。
确需网页交互时先读取当前可用的 `agent-browser` 或对应平台 skill; 缺少能力时报告缺口, 不假定已安装或自动安装。

## Quick Decision 快速决策

| 场景 | 首选工具 | 备注 |
|------|----------|------|
| 查看桌面 / 截屏 | `Snapshot` | 需 UI 元素坐标时加 `use_ui_tree: true` |
| 快速纯截图 | `Screenshot` | 无 UI 树,速度更快 |
| 启动应用 | `App` mode=launch | 需开始菜单中的完整名称 |
| 切换窗口 | `App` mode=switch | 支持部分名称匹配 |
| 调整窗口大小/位置 | `App` mode=resize | 省略 name 则操作活动窗口 |
| 鼠标点击 | `Click` | clicks=0 悬停, 1 单击, 2 双击 |
| 鼠标移动/拖拽 | `Move` | drag=true 执行拖拽 |
| 滚动 | `Scroll` | 支持垂直和水平 |
| 文本输入 | `Type` | 必须提供 loc 或 label(整数 ID) |
| 快捷键 | `Shortcut` | 如 ctrl+c, alt+tab, win+r |
| 批量填表 | `MultiEdit` | labels 或 locs 模式 |
| 等待 UI 就绪 | `WaitFor` | 支持 text/element/window 条件 |
| 固定等待 | `Wait` | 秒级暂停 |
| 执行命令/脚本 | `PowerShell` | Status Code 始终为 0,需检查输出 |
| 进程查看/终止 | `Process` | mode=list / mode=kill |
| 文件操作 | `FileSystem` | read/write/copy/move/delete/list/search/info |
| 注册表 | `Registry` | get/set/delete/list |
| 剪贴板 | `Clipboard` | mode=get / mode=set |
| Toast 通知 | `Notification` | 需要 app_id, title, message |
| 多选 UI 元素 | `MultiSelect` | 支持 press_ctrl |
| 只读提取当前网页内容 | `Scrape` | 仅 Windows 会话内观察; 页面自动化使用 `agent-browser` |

## Quick Reference 快速参考 - 文件索引

| 当需要... | 阅读 |
|-----------|------|
| Snapshot / Screenshot / Scrape 工具详情 | [observation.md](reference/observation.md) |
| App 窗口控制详情 | [window.md](reference/window.md) |
| Click / Move / Scroll / MultiSelect 鼠标操作 | [mouse.md](reference/mouse.md) |
| Type / Shortcut / Clipboard 键盘和剪贴板 | [keyboard.md](reference/keyboard.md) |
| Wait / WaitFor 等待条件 | [wait.md](reference/wait.md) |
| MultiEdit / Notification 填表和通知 | [form.md](reference/form.md) |
| PowerShell / Process / FileSystem / Registry 系统工具 | [system.md](reference/system.md) |
| 推荐工作流(启动应用、填表、键盘操作等) | [workflows.md](reference/workflows.md) |
| 安全规则和接口注意事项 | [safety.md](reference/safety.md) |

## When NOT to Use This Skill 何时不应使用本 skill

- 浏览器内操作(导航、填表、点击网页元素) -> 用 `agent-browser`
- 纯命令行 / shell 操作 → 直接用 Bash
- 不需要与 Windows 桌面交互的任何任务
- 判断标准:是否需要操作真实的 Windows 窗口、图标、桌面应用

## Key Reminders 关键提醒

- 所有状态变更统一使用 `Observe -> Act -> Wait -> Verify`:
  1. `Observe`: `Snapshot`、`info`、`get` 或 `list` 固化目标和修改前状态
  2. `Act`: 仅执行用户当前消息或已确认计划明确授权的具体写操作。未明确授权时只执行
     `Observe`, 并报告待确认动作。Windows 专属命令使用 PowerShell; 纯跨平台 shell
     命令使用 Bash。
  3. `Wait`: 用 `WaitFor`、进程查询或有限重试等待状态稳定
  4. `Verify`: 用独立回读确认目标状态; 不以点击完成或 Status Code 0 判定成功
- 纯观察任务只执行 `Observe`, 不制造无意义写操作
- `Type` / `Move` / `Click` 的 `label` 必须为整数 ID,非字符串
- `PowerShell` 返回的 Status Code 始终为 0,需检查输出内容
- `App` launch 需要完整应用名(由 `Snapshot` UI 树获取)
- 截图功能缺少 `mss` 时先报告安装命令和影响, 等待用户明确确认后再运行
  `uv tool install windows-mcp --with mss --force`
- 远程桌面中窗口枚举可能不稳定,优先使用 UI 树替代
- `Scrape` 只用于 Windows 会话中的只读 HTTP/DOM 内容提取, 不用于导航、填表、
  点击或登录; 这些浏览器页面操作统一使用 `agent-browser`

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
