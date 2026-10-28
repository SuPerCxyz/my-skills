# Page Probes

本文件沉淀跨环境一致的 UI 探测动作。所有操作只读取按钮、表格、字段和
URL,不提交表单、不创建资源、不修改环境。

## Usage 使用约定

- 执行前先按 `patterns/login.md` 准备 `agent-browser` 会话。
- 探测优先使用 `agent-browser eval --stdin` 一次性读取页面结构。
- 探测结果可写入测试报告的 `page_probes[]`,不得写回
  `/tmp/easystack-env.json`。
- 如果探测发现字段或按钮变化,应更新对应页面知识库和本文件。

## Observed Fields 已沉淀字段基线

| 页面 | 字段基线 |
|---|---|
| 创建实例向导 | `instance/instance-details/create-wizard.md` |
| 创建云硬盘弹窗 | `volume/volume-details/form-fields.md` |

## probe_resource_list_pages 探测资源列表

用途:登录后只读探测实例、云硬盘、浮动 IP 页面上的按钮和表格文本,确认
当前 UI 语言、路径和列表结构。

参数:

- 环境默认参数:`platform.url`
- 显式可选参数:`paths`

前置条件:

- 已登录
- 目标页面可访问

成功判定:

- 返回每个页面的 URL、按钮文本、表头文本和前几行表格文本。

失败信号:

- 页面跳回登录页
- 页面主表格不可见
- 探测脚本返回空结果

返回值约定:

```json
{
  "ok": true,
  "terminal": true,
  "submitted": false,
  "resource": "page",
  "action": "probe_resource_list_pages",
  "pages": []
}
```

`agent-browser eval --stdin` 示例:

```bash
agent-browser eval --stdin <<'JS'
(() => {
if (location.pathname.includes('auth_login') || !document.querySelector('.ant-table')) return { ok: false, terminal: true, submitted: false, resource: 'page', action: 'probe_current_page', status: 'page_unavailable', url: location.href };
const pickText = (nodes) => [...nodes].map((n) => n.innerText || n.textContent || '')
  .map((s) => s.trim()).filter(Boolean);

return {
  ok: true,
  terminal: true,
  submitted: false,
  resource: 'page',
  action: 'probe_current_page',
  url: location.href,
  buttons: pickText(document.querySelectorAll('button')).slice(0, 80),
  headers: pickText(document.querySelectorAll('th')).slice(0, 80),
  rows: pickText(document.querySelectorAll('.ant-table-tbody tr')).slice(0, 20)
};
})()
JS
```

## probe_create_instance_page 探测实例创建页

用途:只读探测创建实例页面的向导步骤、底部按钮、表格和关键输入字段。

页面路径:`/eec/instances/create-instance`

字段基线:`instance/instance-details/create-wizard.md`

成功判定:

- 能读取向导步骤按钮。
- 返回当前可见步骤及字段的观察结果; 未进入的步骤不得报告为字段不存在.
- 若 SPA 重定向回列表, 先从真实 Create Instance 入口进入后再探测, 不把列表当向导成功.

只读探测示例:

```bash
agent-browser --args '--no-sandbox' --ignore-https-errors open "$PLATFORM_URL/eec/instances/create-instance"
agent-browser wait 'main, .steps-content'
agent-browser eval --stdin <<'JS'
(() => {
if (!location.pathname.includes('/eec/instances/create-instance') || !document.querySelector('.steps-content')) return { ok: false, terminal: true, submitted: false, resource: 'instance', action: 'probe_create_instance_page', status: 'wizard_unavailable', url: location.href };
const text = (sel) => [...document.querySelectorAll(sel)]
  .map((n) => n.innerText || n.textContent || '').map((s) => s.trim()).filter(Boolean);
const exists = (sel) => Boolean(document.querySelector(sel));

return {
  ok: true,
  terminal: true,
  submitted: false,
  resource: 'instance',
  action: 'probe_create_instance_page',
  url: location.href,
  buttons: text('button').slice(0, 80),
  stepTexts: text('.ant-steps, .steps-content').slice(0, 20),
  tableHeaders: text('th').slice(0, 80),
  fields: {
    name: exists('input[name="config.name"]'),
    quantity: exists('nz-input-number.instance-number'),
    rootDisk: exists('.row.system-disk'),
    networkSelect: exists('.network-select'),
    securityGroupSelect: exists('.security-group-select')
  }
};
})()
JS
```

## probe_create_volume_modal 探测卷创建弹窗

用途:只读打开创建云硬盘弹窗,读取字段、按钮和默认值;探测结束后关闭弹窗。

页面路径:`/ebs/volumes`

字段基线:`volume/volume-details/form-fields.md`

成功判定:

- 能打开创建弹窗。
- 能读取 `Volume Name`、`Volume Source`、`Type`、`Size` 等字段。
- 探测结束关闭弹窗,不提交创建。

只读探测示例:

```bash
agent-browser --args '--no-sandbox' --ignore-https-errors open "$PLATFORM_URL/ebs/volumes"
agent-browser wait 'main, .ant-table'
agent-browser find text "Create Volume" click
agent-browser wait '.ant-modal'
agent-browser eval --stdin <<'JS'
(() => {
if (location.pathname.includes('auth_login') || !document.querySelector('.ant-modal .ant-form-item')) return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'probe_create_volume_modal', status: 'modal_unavailable', url: location.href };
const text = (sel) => [...document.querySelectorAll(sel)]
  .map((n) => n.innerText || n.textContent || '').map((s) => s.trim()).filter(Boolean);
const textOf = (node) => (node?.innerText || node?.textContent || '').trim();
const formItemByLabel = (label) => [...document.querySelectorAll('.ant-modal .ant-form-item')]
  .find((node) => textOf(node).includes(label));
const fieldValue = (label, selector) =>
  formItemByLabel(label)?.querySelector(selector)?.value || '';

return {
  ok: true,
  terminal: true,
  submitted: false,
  resource: 'volume',
  action: 'probe_create_volume_modal',
  url: location.href,
  title: text('.ant-modal-title')[0] || '',
  labels: text('.ant-modal .ant-form-item-label').slice(0, 80),
  buttons: text('.ant-modal button').slice(0, 20),
  defaults: {
    name: fieldValue('Volume Name', 'input'),
    size: fieldValue('Size', '.ant-input-number input')
  }
};
})()
JS
agent-browser find text "Cancel" click
agent-browser wait --fn "!Array.from(document.querySelectorAll('.ant-modal')).some((node) => node.getClientRects().length > 0)"
```
