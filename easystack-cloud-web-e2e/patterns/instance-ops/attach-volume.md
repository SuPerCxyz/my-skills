# attach_volume

> 来源:`patterns/instance-ops.md`,按原子操作拆分。

示例依赖 [interactions.md](../../interactions.md) 的资源身份和按钮 helper; 将 helper 与
调用片段放在同一次 eval 中. 实例子文件的相对路径为 `../../interactions.md`.
从当前 UI 定义可验证的全局 `readSelectionCount` 探针, 无法核实跨页选择时停止批量动作.
先核实 domain/project 或项目 UUID、名称和可用资源 UUID; 有其他已选资源或身份不唯一时停止.

## attach_volume 挂载云硬盘

### Purpose 用途

将一块云硬盘挂载到目标实例,并验证卷状态变为 `In use`。

### Parameters 参数

- 必填参数: `instance`
- 必填参数: `volume`
- 环境默认参数: 无
- 显式可选参数: `expected_status`,默认 `In use`

### Prerequisites 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标实例存在,目标卷处于可挂载状态

### Success Criteria 成功判定

- 已在实例操作中完成挂载提交流程
- 目标卷显示为 `expected_status`

### Operation Steps 执行步骤概览

- 打开云硬盘列表页并确认当前会话仍处于已登录状态
- 定位目标云硬盘行,选中该行
- 点击列表页 `Attach` 打开挂载弹窗
- 在挂载弹窗内选择目标实例
- 点击挂载弹窗内的 `Attach` 按钮,不要点击列表页同名按钮
- 轮询云硬盘列表,直到目标卷状态达到 `expected_status`

### Failure Signals 失败信号

- 缺少实例名、卷名或平台地址等必填输入
- 页面跳转到登录页,说明当前会话失效
- 实例列表中找不到目标实例,或弹窗里无法选择目标卷
- 多次轮询后目标卷仍未达到预期状态

### Result Contract 返回值约定

```json
{
  "ok": true,
  "terminal": true,
  "submitted": true,
  "resource": "volume",
  "action": "attach",
  "name": "<volume-name>",
  "status": "In use",
  "message": "volume attached to instance",
  "url": "<current-url>"
}
```

### Operation Notes 操作注意

- 云硬盘列表页和弹窗内都有 `Attach` 文案,提交时必须限定在
  `Attach Volume` 弹窗内找按钮。
- 选择实例后必须确认弹窗内实例下拉展示目标实例,且弹窗内 `Attach` 按钮
  已 enabled。
- 如果弹窗内存在 form,优先提交 form;否则只点击当前最上层 modal 内的
  `Attach` 主按钮。
- 成功判定以云硬盘列表为准:目标卷状态 `In use`,Attachments 显示
  `<instance>: /dev/vdb` 或下一个可用设备名。

### Browser Example `agent-browser eval --stdin` 示例

```js
(async () => {
  try {
    const input = { instance: '<instance-name>', volume: '<volume-name>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.volume, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'attach', name: input.volume, status: 'missing_volume', message: 'volume not found', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      uniqueButton(document, 'Attach').click();
      return { ok: null, terminal: false, submitted: false, resource: 'volume', action: 'attach', name: input.volume, status: 'dialog_opened', message: 'select instance in Attach Volume dialog, then click dialog Attach', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'attach', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```
