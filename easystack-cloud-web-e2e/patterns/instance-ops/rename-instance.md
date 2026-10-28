# rename_instance

> 来源:`patterns/instance-ops.md`,按原子操作拆分。

示例依赖 [interactions.md](../../interactions.md) 的资源身份和按钮 helper; 将 helper 与
调用片段放在同一次 eval 中. 实例子文件的相对路径为 `../../interactions.md`.
从当前 UI 定义可验证的全局 `readSelectionCount` 探针, 无法核实跨页选择时停止批量动作.
先核实 domain/project 或项目 UUID、名称和可用资源 UUID; 有其他已选资源或身份不唯一时停止.

## rename_instance 修改云主机名称

### Purpose 用途

修改实例名称,并验证实例列表中出现新名称。

### Parameters 参数

- 必填参数: `instance`
- 必填参数: `new_name`

### Prerequisites 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标实例当前出现在实例列表中

### Success Criteria 成功判定

- 编辑提交完成
- 列表中出现 `new_name`

### Operation Notes 操作注意

- 行选择优先点击可见 checkbox wrapper,不要默认只点隐藏 input。
- 提交时必须限定在编辑弹窗内;如果弹窗内存在 form,优先提交 form。

### Operation Steps 执行步骤概览

- 打开实例列表页并确认未跳回登录页
- 选中目标实例
- 通过 More / Edit 进入编辑弹窗
- 填写新名称并提交
- 轮询实例列表直到新名称出现

### Failure Signals 失败信号

- 缺少实例名、新名称或平台地址
- 页面跳回登录页
- 目标实例不可见
- 编辑入口或名称输入框不可见
- 轮询超时后新名称仍未出现

### Result Contract 返回值约定

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"instance","action":"rename","name":"<new-name>","status":"renamed","message":"instance renamed","url":"<current-url>"}
```

### Browser Example `agent-browser eval --stdin` 示例

```js
(async () => {
  try {
    const input = { instance: '<old-name>', newName: '<new-name>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.instance, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'instance', action: 'rename', name: input.newName, status: 'missing', message: 'instance not found', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      uniqueButton(document, 'More').click();
      return { ok: null, terminal: false, submitted: false, resource: 'instance', action: 'rename', name: input.newName, status: 'menu_opened', message: 'click Edit, fill new name, submit, then poll /eec/instances until new name appears', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'instance', action: 'rename', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```
