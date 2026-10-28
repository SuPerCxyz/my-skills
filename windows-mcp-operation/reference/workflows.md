# 推荐工作流

Use this file for common multi-tool sequences. For parameter details, switch to the specific reference file linked by each step.

所有会改变状态的工作流都必须执行 `Observe -> Act -> Wait -> Verify`。最终
`Verify` 必须重新读取目标状态, 不能复用执行动作本身的返回值。

## 获取桌面状态

1. 调用 `Snapshot` `{"use_vision": true}`
2. 总结可见窗口和应用状态
3. 若需 UI 元素坐标, 改用 `Snapshot` `{"use_ui_tree": true}`
4. 降级(截屏偶发失败时):
   - `Snapshot` `{"use_ui_tree": true, "use_vision": false}` — 仅 UI 树
   - `PowerShell` 获取窗口列表作为最终降级

## 启动并操作应用

1. `App` `mode=launch` 启动目标应用
2. `Wait` 等待启动(2-3 秒)
3. `WaitFor` `text_exists` 等待应用标题出现
4. `App` `mode=resize` 调整到合适大小
5. `Snapshot` 确认状态
6. `Click` / `Type` / `Shortcut` 执行操作
7. `WaitFor` 等待预期 UI 状态
8. 再次 `Snapshot` 回读并确认最终状态

## 填写 Windows 表单

1. `Snapshot` `{"use_ui_tree": true}` 获取字段标签和坐标
2. 优先 `MultiEdit` `labels` 模式
3. 标签不可用时用 `Type` + 坐标
4. `Shortcut` `ctrl+s` 或 `Click` 保存按钮
5. `WaitFor` 等待成功提示、目标值或稳定页面状态
6. 再次 `Snapshot` 回读已保存字段; 无法回读时报告未确认, 不判定成功

## 关闭应用

`App` 无 close 模式, 使用:
- `PowerShell`:`Stop-Process -Name <process_name> -Force`
- 或 `Shortcut` `alt+F4`

关闭前先确认目标应用和未保存内容。用户没有明确要求关闭或终止时, 不执行上述操作。

## 键盘驱动操作

1. `App` `mode=switch` 切换目标窗口
2. `Shortcut` 使用快捷键(`alt+F` 打开菜单等)
3. `Type` 输入文本 + `press_enter`
4. `Wait` / `WaitFor` 等待响应
5. `Snapshot` 回读结果并确认预期状态
