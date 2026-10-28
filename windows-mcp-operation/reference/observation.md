# 观察类工具

Use this file before acting on the desktop, when coordinates, UI element IDs, window state, or screenshots are needed.

## Snapshot

桌面截屏 + UI 元素树检查, 提供光标位置、窗口列表和交互元素坐标。

### Snapshot 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `use_vision` | bool | 返回截图图片 |
| `use_ui_tree` | bool | 返回交互元素元数据(含坐标和 action) |
| `use_annotation` | bool | 在截图上绘制元素边框 |
| `display` | int[] | 指定显示器索引, 如 `[0]` |
| `width_reference_line` | int | 添加垂直网格线 |
| `height_reference_line` | int | 添加水平网格线 |
| `use_dom` | bool | 浏览器 DOM 提取(非桌面 UI) |

### Snapshot 典型调用

```json
{"use_vision": true, "use_ui_tree": false}
```

需要 UI 元素坐标时:
```json
{"use_vision": true, "use_ui_tree": true}
```

### 注意事项

- **截图后端**:需安装 `mss`(`uv tool install windows-mcp --with mss --force`), `pillow` 在远程桌面中可能不稳定
- 远程桌面会话中窗口枚举可能返回空列表, 但 UI 树通常可用
- `use_ui_tree: true` + `use_vision: false` 可仅获取 UI 树(更快)

## Screenshot

快速截图, 跳过 UI 树构建。比 `Snapshot` 快, 适合只需截图的场景。

### 与 Snapshot 的区别

| | Snapshot | Screenshot |
|--|----------|------------|
| UI 树 | 支持 | 不支持 |
| 速度 | 较慢 | 较快 |
| 适用 | 需要元素坐标时 | 纯快速截屏 |

**建议**:需要交互时优先 `Snapshot`;纯截屏用 `Screenshot`。

## Scrape

网页只读抓取工具, 支持 HTTP 请求和浏览器 DOM 两种模式。仅在任务需要观察
Windows 会话中的页面内容时使用。导航、填表、点击、登录和页面状态变更统一使用
`agent-browser`; 不要用 `Scrape` 建立另一套浏览器自动化流程。

### Scrape 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `url` | string | 目标 URL |
| `query` | string | 聚焦提取特定信息 |
| `use_dom` | bool | true=从浏览器 DOM 提取(需 Chrome/Edge/Firefox) |
| `use_sampling` | bool | false=获取原始内容(不经过 LLM 处理) |

### Scrape 典型调用

```json
{"url": "https://httpbin.org/get"}
{"url": "https://example.com", "query": "page heading", "use_dom": true}
```
