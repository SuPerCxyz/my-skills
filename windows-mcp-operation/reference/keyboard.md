# 键盘与剪贴板

Use this file for text input, shortcuts, and clipboard operations. For mouse positioning or drag actions, use [mouse.md](mouse.md); for waiting, use [wait.md](wait.md).

## Type

在指定位置输入文本。**必须提供 `loc` 或 `label`**(`label` 为整数 ID, 非字符串)。

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `loc` | [int, int] | 输入位置坐标 |
| `label` | int | UI 元素 ID(整数) |
| `text` | string | 输入内容 |
| `clear` | bool | 先清空已有文本 |
| `press_enter` | bool | 输入后按回车 |
| `caret_position` | string | `start` / `end` / `idle` |

### Type 典型调用

```json
{"loc": [600, 500], "text": "hello", "press_enter": true}
```

### 已知错误

- `Either loc or label must be provided.` — 缺少定位参数
- `Input should be a valid integer` — label 传了字符串而非整数

## Shortcut

模拟快捷键组合。

### Shortcut 典型调用

```json
{"shortcut": "ctrl+c"}
{"shortcut": "alt+tab"}
{"shortcut": "win+r"}
{"shortcut": "ctrl+shift+esc"}
```

支持的修饰键:`ctrl`, `alt`, `shift`, `win`。
注:`Click` 不支持 `modifiers` 参数, 需要 modifier+click 时组合 `Shortcut` + `Click`。

## Clipboard

读写剪贴板。

| mode | 用途 |
|------|------|
| `get` | 读取剪贴板内容 |
| `set` | 设置剪贴板内容 |

### Clipboard 典型调用

```json
{"mode": "get"}
{"mode": "set", "text": "copied text"}
```
