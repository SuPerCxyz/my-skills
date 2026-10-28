# start_stop_reboot_instance

> 来源:`patterns/instance-ops.md`,按原子操作拆分。

示例依赖 [interactions.md](../../interactions.md) 的资源身份和按钮 helper; 将 helper 与
调用片段放在同一次 eval 中. 实例子文件的相对路径为 `../../interactions.md`.
从当前 UI 定义可验证的全局 `readSelectionCount` 探针, 无法核实跨页选择时停止批量动作.
先核实 domain/project 或项目 UUID、名称和可用资源 UUID; 有其他已选资源或身份不唯一时停止.

## start_stop_reboot_instance 启动关机与重启

### Purpose 用途

对实例执行启动、关机或重启,并验证实例状态达到预期。

### Parameters 参数

- 必填参数: `name`
- 必填参数: `action`,可选值为 `start`、`stop`、`reboot`
- 显式可选参数: `target_status`

### Prerequisites 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标实例当前出现在实例列表中

### Success Criteria 成功判定

- 操作提交成功
- 实例状态达到 `target_status`;未显式传入时,`start` 对应 `Active`,`stop` 对应 `Shutoff`,`reboot` 对应 `Active`

重启前记录实例 UUID、当前状态和可取得的任务/启动标识. `reboot` 不能仅凭原有
Active 状态判成功; 必须观察本次任务完成或 Rebooting -> Active 的变化, 并在用例
要求时验证 VM 启动时间/业务恢复. 看不到任务或变化时保持未确认, 不重复发送重启.

### Operation Steps 执行步骤概览

- 打开实例列表页并确认未跳回登录页
- 选中目标实例
- 点击对应操作按钮或 More 菜单项
- 处理确认弹窗
- 轮询实例列表直到目标状态出现

### Operation Notes 操作注意事项

- 实例列表可能先渲染导航和标题,表格稍后才出现;必须等目标实例名称在
  `document.body.innerText` 或 snapshot 中可见后再解析 refs。
- 行复选框优先使用 `agent-browser snapshot` 中目标行的 `LabelText [ref=...]`
  做真实点击;单纯 DOM `.click()` 可能不会触发 ng-zorro 表格选择状态。
- 点击 `Start` 后确认弹窗里的主按钮文本仍为 `Start`,不是 `Confirm`;点击时
  必须限定在弹窗内或使用弹窗里的最后一个 `Start` ref。
- 如果弹窗内带 form,优先提交 form;否则只点击当前最上层 modal 内的主按钮。
- 如果选中后目标动作按钮仍 disabled,重新获取 snapshot;不要继续空轮询状态,
  因为操作可能根本没有提交。

### Failure Signals 失败信号

- 缺少实例名、动作或平台地址
- 动作不在允许列表中
- 页面跳回登录页
- 目标实例不可见
- 操作入口不可见或状态轮询超时

### Result Contract 返回值约定

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"instance","action":"reboot","name":"<instance-name>","status":"Active","message":"instance action completed","url":"<current-url>"}
```

### Browser Example `agent-browser eval --stdin` 示例

```js
(async () => {
  try {
    const input = { name: '<instance-name>', action: 'reboot', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.name, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'instance', action: input.action, name: input.name, status: 'missing', message: 'instance not found', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      const direct = actionButton(document, input.action);
      direct?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return { ok: null, terminal: false, submitted: false, resource: 'instance', action: input.action, name: input.name, status: 'confirm_needed', message: 'use direct button or More menu, confirm dialog, then poll instance status', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'instance', action: 'reboot', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```
