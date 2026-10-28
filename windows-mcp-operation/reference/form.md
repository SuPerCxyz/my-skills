# 批量填表与通知

Use this file for MultiEdit and notification tasks after a Snapshot identifies the target fields or notification payload. For single text entry, use [keyboard.md](keyboard.md).

## MultiEdit

批量填写多个输入框。

### 两种定位模式

| 模式 | 格式 | 示例 |
|------|------|------|
| `labels` | `[[label, text], ...]` | `[["Server URL", "http://127.0.0.1:8080"]]` |
| `locs` | `[[x, y, text], ...]` | `[[420, 315, "http://127.0.0.1:8080"]]` |

### MultiEdit 规则

- 操作前先 `Snapshot`(`use_ui_tree: true`)确认字段位置
- 优先用 `labels` 模式, `locs` 仅在标签不可用时使用
- 空数组 `[]` 为安全 no-op
- 禁止输入密钥 / 密码 / 破坏性命令

## Notification

发送 Windows Toast 通知。

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `app_id` | string | 应用标识(如 `"Windows PowerShell"`) |
| `title` | string | 通知标题 |
| `message` | string | 通知正文 |

### 典型调用

```json
{"app_id": "Windows PowerShell", "title": "Build done", "message": "All tests passed."}
```

### Notification 规则

- title/message 保持简短
- `app_id` 使用真实或可见的应用名
- 不替代最终回复消息
