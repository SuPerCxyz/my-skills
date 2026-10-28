# 定时等待

Use this file when an action needs fixed or conditional waiting. Prefer condition-based waiting when a visible UI state, text, or window can be observed.

## Wait

固定等待指定秒数。

```json
{"duration": 2}
```

用于:等待应用启动、UI 动画完成、页面渲染等。

## WaitFor

轮询等待 UI 条件满足。

### 支持条件

| condition | 说明 | 所需参数 |
|-----------|------|----------|
| `text_exists` | 等待文本出现 | `text` |
| `active_window` | 等待窗口激活 | `window_name` |
| `element_exists` | 等待元素出现 | `text` 或 `label` |
| `element_enabled` | 等待元素可用 | `text` 或 `label` |
| `focused_element` | 等待元素获得焦点 | — |

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `condition` | string | 条件类型 |
| `text` | string | 匹配文本 |
| `window_name` | string | 窗口名过滤 |
| `timeout` | number | 超时秒数(默认 10) |
| `interval` | number | 轮询间隔(默认 0.25s) |
| `use_dom` | bool | 浏览器 DOM 文本 |

### 典型调用

```json
{"condition": "text_exists", "text": "PowerShell", "timeout": 5}
```

### 已知问题

- `element_exists` + `window_name` 组合可能匹配失败, 优先用 `text_exists`
