# 鼠标操作

Use this file for click, hover, movement, drag, scroll, and multi-select actions after observation has identified coordinates or UI element IDs.

## Click

鼠标点击。可通过坐标 (`loc`) 或 UI 元素 ID (`label`) 定位。

### Click 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `loc` | [int, int] | 目标坐标 `[x, y]` |
| `label` | int | UI 元素 ID(SnapShot 返回的整数, 非字符串) |
| `button` | string | `left` / `right` / `middle` |
| `clicks` | int | 0=悬停, 1=单击, 2=双击 |

### Click 典型调用

```json
{"loc": [500, 400], "clicks": 1, "button": "left"}
{"loc": [600, 500], "clicks": 2}
```

## Move

鼠标移动或拖拽。

### Move 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `loc` | [int, int] | 目标坐标 |
| `label` | int | UI 元素 ID |
| `drag` | bool | true=从当前位置拖拽到目标 |

### Move 典型调用

```json
{"loc": [500, 400]}
{"loc": [700, 500], "drag": true}
```

## Scroll

滚动内容。

### Scroll 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `direction` | string | `up` / `down` / `left` / `right` |
| `type` | string | `vertical` / `horizontal` |
| `wheel_times` | int | 滚动量(1 wheel ≈ 3-5 行) |
| `loc` | [int, int] | 滚动位置坐标 |
| `label` | int | UI 元素 ID |

### Scroll 典型调用

```json
{"direction": "down", "loc": [500, 400], "wheel_times": 2}
```

## MultiSelect

多选 UI 元素(如文件、复选框)。

### MultiSelect 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `locs` | [[int, int], ...] | 坐标列表 |
| `labels` | [int, ...] | 标签列表 |
| `press_ctrl` | bool | 是否按住 Ctrl 多选 |

### MultiSelect 典型调用

```json
{"locs": [[100, 200], [100, 250]], "press_ctrl": true}
```
