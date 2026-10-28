# Interactions

EasyStack Cloud 使用 Angular + NG-ZORRO 组件库。本文件只记录可嵌入
`agent-browser` 的定位方式和交互模式。

## Table of Contents 目录

[使用约定](#使用约定) | [按钮](#按钮) | [文本输入](#文本输入) |
[下拉选择框](#下拉选择框) | [弹窗](#弹窗) | [表格](#表格) |
[数字输入框](#数字输入框) | [标签页](#标签页) | [消息与通知](#消息与通知) |
[确认对话框](#确认对话框) | [加载状态](#加载状态) | [截图](#截图)

<a id="使用约定"></a>

## Usage 使用约定

- 示例均为 `agent-browser` CLI 或可放入 `agent-browser eval --stdin` 的定位方式知识。
- 优先合并为单次 `agent-browser eval --stdin` 或 `agent-browser batch`,减少 snapshot 和 token 消耗。
- 固定等待只作为动画兜底;成功判定应依赖 URL、目标元素或状态文本。
- 业务操作优先复用 `patterns/*-ops.md`,本文件只提供组件级 helper。
- `agent-browser` 不是 Playwright,不能直接使用 `:has-text()`、`text=` 等
  Playwright 风格伪选择器。CLI 文本定位使用 `agent-browser find text ...`;
  `eval --stdin` 内使用下方 helper。
- EasyStack Cloud 前端大量使用 Angular + NG-ZORRO。不要把页面按钮、modal
  footer 按钮、form submit 按钮、checkbox 当成同一种元素处理。
- 打开/关闭 modal、切页、刷新表格、切换步骤后,旧 ref 默认失效;必须重新
  snapshot 或重新查询可见 DOM。
- 列表实时刷新、高频新增、切换排序/筛选后,旧行号、旧位置判断、旧 checkbox ref
  也默认失效;不要依赖“第 1 行/第 2 行”这类位置假设。
- `Service Catalog`、dropdown、`More` 菜单、首页配置区块等覆盖层打开后,会遮挡
  原页面元素;此时先处理覆盖层,不要继续点被遮挡元素。

<a id="按钮"></a>

## Buttons 按钮

```bash
agent-browser find text "Create Volume" click
agent-browser click 'button.ant-btn-primary'
agent-browser is enabled 'button.ant-btn-primary'
```

`agent-browser eval --stdin` 中按文本定位元素:

```javascript
const textOf = (node) => (node?.innerText || node?.textContent || '')
  .trim().replace(/\s+/g, ' ');
const byText = (selector, value, root = document) => {
  const nodes = [...root.querySelectorAll(selector)];
  return nodes.find((node) => textOf(node) === value) ||
    nodes.find((node) => textOf(node).includes(value));
};
const buttonByText = (value, root = document) => byText('button', value, root);
const formItemByLabel = (label, root = document) =>
  [...root.querySelectorAll('.ant-form-item')]
    .find((node) => textOf(node).includes(label));
const fieldInput = (label, selector = 'input, textarea', root = document) =>
  formItemByLabel(label, root)?.querySelector(selector);
const visible = (node) => {
  if (!node) return false;
  const style = window.getComputedStyle(node);
  const rect = node.getBoundingClientRect();
  return style.display !== 'none' &&
    style.visibility !== 'hidden' &&
    rect.width > 0 &&
    rect.height > 0;
};
const enabled = (node) => Boolean(node && !node.disabled && node.getAttribute('aria-disabled') !== 'true');
const visibleButtons = (root = document) =>
  [...root.querySelectorAll('button')].filter((node) => visible(node));
const topModal = () => {
  const wraps = [...document.querySelectorAll('.ant-modal-wrap, nz-modal-container')]
    .filter((node) => visible(node));
  const wrap = wraps.at(-1) || null;
  return wrap?.querySelector('.ant-modal, .ant-modal-content') || wrap;
};
const modalButtonByText = (value) => {
  const modal = topModal();
  if (!modal) return null;
  return visibleButtons(modal).find((node) => textOf(node) === value && enabled(node)) ||
    visibleButtons(modal).find((node) => textOf(node).includes(value) && enabled(node));
};
const clickWithMouse = (node) => {
  if (!node || !visible(node) || !enabled(node)) return false;
  for (const type of ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
    node.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
  }
  return true;
};
const submitNearestForm = (node) => {
  const form = node?.closest('form') || topModal()?.querySelector('form') || document.querySelector('form');
  if (!form) return false;
  if (typeof form.requestSubmit === 'function') {
    form.requestSubmit();
    return true;
  }
  form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  return true;
};
```

列表页按钮在页面刚打开后可能先渲染为 `disabled`,随后由权限、配额或数据
加载结果异步放开。例如实例列表的 `Create Instance` 按钮可能需要等待数秒
才可点击。执行操作前必须轮询目标按钮进入 enabled 状态,不能仅凭首次
探测到 disabled 就判定无权限或配额不足。

```bash
agent-browser wait --fn "Array.from(document.querySelectorAll('button')).some((b) => b.innerText.trim() === 'Create Instance' && !b.disabled)"
```

`agent-browser eval --stdin` 中推荐使用通用等待:

```javascript
const waitButtonEnabledOnce = (text) => {
  const button = [...document.querySelectorAll('button')]
    .find((item) => item.innerText.trim() === text);
  return Boolean(button && !button.disabled);
};
```

长等待不要放进单次 `eval`,否则容易触发 CDP evaluate 超时。需要等待超过
数秒时,优先使用 `agent-browser wait --fn`,或在 shell 层做短轮询:

```bash
for i in $(seq 1 30); do
  agent-browser eval --stdin <<'JS' | grep '"enabled": true' && break
(() => {
  const button = [...document.querySelectorAll('button')]
    .find((item) => item.innerText.trim() === 'Create Instance');
  return { enabled: Boolean(button && !button.disabled) };
})()
JS
  sleep 1
done
```

等待规则补充:

- 普通页面交互默认只做短等待,不允许把“按钮启用”“下拉加载”“modal 提交后列表刷新”
  这类动作写成长时间循环。
- 如果按钮连续数次检查仍 disabled,先停止等待,回查:
  - 必填输入/下拉是否都已满足
  - 是否有校验错误、配额提示、遮挡层或项目不对
  - 当前动作是否实际位于 `More` 菜单而不是顶部工具栏
- 如果点击后没有任何跳转、提示或网络请求,也要回查隐藏字段、登录类型、权限提示或
  当前动作是否实际受覆盖层阻挡。
- 只有迁移、数据拷贝、`fio`、用户明确说明的后台长任务,才允许扩大等待预算。

如果必须在页面上下文中短等待,控制在几秒内:

```javascript
const waitButtonEnabledBriefly = async (text, timeoutMs = 5000) => {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const found = [...document.querySelectorAll('button')]
      .find((button) => button.innerText.trim() === text);
    if (found && !found.disabled) return true;
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  return false;
};
```

| 按钮类型 | 定位方式 | 说明 |
|----------|--------|------|
| 主要按钮 | `button.ant-btn-primary` | 主题色按钮 |
| 次要按钮 | `button.ant-btn-default` | 默认按钮 |
| 危险按钮 | `button.ant-btn-dangerous` | 危险操作按钮 |
| 禁用按钮 | `button.ant-btn[disabled]` | 禁用状态 |

按钮点击优先级:

1. `agent-browser click <ref/selector>` 做真实点击
2. modal 内按钮使用 `modalButtonByText()` 限定当前最上层弹窗
3. 表单提交优先 `form.requestSubmit()`
4. 仅在以上都不可用时,才用 `clickWithMouse()` 作为兜底

不要直接对全局 `document.querySelectorAll('button')` 的第一个同名按钮做 `.click()`。

入口类型补充:

- 顶部工具栏按钮通常要求目标行已选中。
- `More` 菜单动作通常也要求目标行已选中,然后再展开菜单选择动作。
- 行名称、详情链接、行内链接通常不依赖 checkbox 选中。
- 也有例外页面采用“纯行内动作”模式,例如计算节点、浮动 IP;这些页面很多操作不在
  顶部工具栏,而在每行的 Action 列。
- 执行动作前先判断当前入口类型,避免把“行内入口”当成“批量工具栏动作”,或反过来。

主操作按钮规则:

- 对 `Create`、`Confirm`、`Associate`、`Attach`、`Save` 这类主操作按钮,
  先检查按钮是否 disabled。
- 如果按钮 disabled,优先检查当前页面或弹窗内:
  - 必填输入是否已填值
  - 必填下拉是否已选中
  - 联动字段是否已刷新完成
  - 页面是否有校验错误或配额提示
- 只有在必填项满足、按钮变 enabled 后,才执行点击或提交。

<a id="文本输入"></a>

## Text Inputs 文本输入

```bash
agent-browser fill '#id_username' "$USERNAME"
agent-browser fill 'input[placeholder="Enter 1 to 128 characters in length"]' "$NAME"
agent-browser fill 'textarea[placeholder*="description"]' "$DESCRIPTION"
```

按表单标签填写时使用 `eval --stdin`:

```bash
agent-browser eval --stdin <<'JS'
const value = '<volume-name>';
const textOf = (node) => (node?.innerText || node?.textContent || '').trim();
const item = [...document.querySelectorAll('.ant-form-item')]
  .find((node) => textOf(node).includes('Volume Name'));
const input = item?.querySelector('input, textarea');
if (input) {
  input.value = value;
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new Event('blur', { bubbles: true }));
}
Boolean(input);
JS
```

<a id="下拉选择框"></a>

## Select Controls 下拉选择框

NG-ZORRO Select 不是原生 `<select>`。优先点击当前可见下拉,再从未隐藏的
dropdown 中选项。

```javascript
const selectOption = (formItemText, optionText) => {
  const text = (e) => (e.innerText || e.textContent || '').trim();
  const formItem = [...document.querySelectorAll('.ant-form-item')]
    .find((item) => text(item).includes(formItemText));
  clickWithMouse(formItem?.querySelector('.ant-select, nz-select'));
  setTimeout(() => {
    clickWithMouse(
      [...document.querySelectorAll('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option')]
        .find((item) => text(item).includes(optionText))
    );
  }, 300);
};
```

下拉选择完成后,必须回读当前展示值;如果展示值没有切换到目标值,就视为选择失败,
不得继续提交后续操作。

筛选输入补充:

- 列表上 `Click here for filters.` 这类控件,很多页面是“打开筛选条件面板”的入口,
  不是立即按名称过滤的数据搜索框。
- 如果填入文本后列表没有立刻收窄,不要继续等待“结果自己出现”;应先确认该控件
  是否需要额外的筛选字段、确认按钮、回车提交,或改用真正的列筛选/分页定位。
- 不要把“文本已经输入到筛选框”误判为“筛选已经生效”。
- 表格列筛选会影响当前列表展示的数据集合,不只是某一个单元格;一旦启用列筛选,
  后续定位、分页、状态判断都必须基于筛选后的整张表重新判断。
- 某些列表页的 `Click here for filters.` 只是筛选入口,但不是立即过滤框;
  某些页面填入文本后不会立刻变更结果集。

获取当前值:

```javascript
const selectedText = document
  .querySelector('.ant-form-item .ant-select-selection-item')
  ?.textContent?.trim();
```

列表与通知判定补充:

- toast / notification 只能说明“前端收到了提交结果”或“后台开始处理”,不能替代
  列表稳定态判定。
- 如果 toast 仍显示 `creating`,但列表或详情页已经进入目标稳定态,应以列表或详情页
  的当前状态为准。
- 某些权限不足的动作不会打开 modal,而是直接在正文区域给出文本提示;这属于产品
  权限反馈,不应误判为 click 失败。

搜索并选择:

```javascript
const searchAndSelect = (formItemText, searchText, optionText) => {
  const text = (e) => (e.innerText || e.textContent || '').trim();
  const formItem = [...document.querySelectorAll('.ant-form-item')]
    .find((item) => text(item).includes(formItemText));
  clickWithMouse(formItem?.querySelector('.ant-select, nz-select'));
  const search = document.querySelector('.ant-select-dropdown:not(.ant-select-dropdown-hidden) input');
  if (search) {
    search.value = searchText;
    search.dispatchEvent(new Event('input', { bubbles: true }));
  }
  setTimeout(() => {
    clickWithMouse(
      [...document.querySelectorAll('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option')]
        .find((item) => text(item).includes(optionText))
    );
  }, 300);
};
```

<a id="弹窗"></a>

## Dialogs 弹窗

```javascript
const modal = topModal();
const title = modal?.querySelector('.ant-modal-title')?.textContent?.trim();
const primary = modalButtonByText('Confirm') ||
  modalButtonByText('Create') ||
  modalButtonByText('Associate') ||
  modal?.querySelector('.ant-modal-footer .ant-btn-primary:not([disabled])');
if (primary) {
  clickWithMouse(primary);
}
```

弹窗操作规则:

- 只在当前最上层可见 modal 内查找按钮。
- 双确认弹窗点完第一层后,必须重新获取 `topModal()`,不能复用旧按钮引用。
- 如果按钮语义是 `triggerOk()` / `nzModalRef.triggerOk()`,仍按真实点击该按钮处理;
  不要试图越过 UI 直接找组件实例。
- 对带表单的 modal,优先填值后提交 form;不要先全局搜索 `Create/Confirm`。

表单优先提交:

```javascript
const modal = topModal();
const submitted = submitNearestForm(modal?.querySelector('button.ant-btn-primary'));
if (!submitted) {
  const primary = modal?.querySelector('.ant-modal-footer .ant-btn-primary:not([disabled])');
  clickWithMouse(primary);
}
```

填写弹窗表单:

```javascript
const fillModalField = (label, value) => {
  const text = (e) => (e.innerText || e.textContent || '').trim();
  const item = [...document.querySelectorAll('.ant-modal .ant-form-item')]
    .find((node) => text(node).includes(label));
  const input = item?.querySelector('input, textarea');
  if (!input) return false;
  input.value = String(value);
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new Event('blur', { bubbles: true }));
  return true;
};
```

<a id="表格"></a>

## Tables 表格

资源操作必须在已确认的项目和唯一可见表格内精确定位名称列. 不在整行文本中做
`includes(name)` 匹配. 名称相同且不能由项目或 UUID 消除歧义时停止, 不取第一行.
有资源 UUID 时跨刷新继续使用同一 UUID; 调用方指定 UUID 而页面无法核实则停止.

将下面 helper 与资源调用片段放进同一次 `eval --stdin`; 不假设变量跨调用保留.
表格应由现场观察选择, 不用“第一张表”代替资源域判断.

<!-- resource-contract:start -->
```javascript
const resourceText = (node) => (node?.innerText || node?.textContent || '').trim();
const resourceTable = () => {
  const tables = [...document.querySelectorAll('.ant-table')].filter((node) => node.getClientRects().length > 0);
  if (tables.length !== 1) throw new Error('resource_table_unavailable_or_ambiguous');
  return tables[0];
};
const resourceRows = (table) => [...table.querySelectorAll('.ant-table-tbody tr')]
  .filter((row) => row.querySelectorAll('td').length > 1);
const identityFromHref = (href) => href.match(/(?:^|[/?#=&])([0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}|[0-9a-f]{32})(?=$|[/?#=&])/i)?.[1] || null;
const resourceIdentity = (table, row) => {
  const headers = [...table.querySelectorAll('thead th')]
    .map((node) => resourceText(node).replace(/\s+/g, ' ').replace(/\s*\/\s*/g, '/'));
  const cells = [...row.querySelectorAll('td')];
  const cell = (labels) => cells[headers.findIndex((header) => labels.includes(header))];
  const nameCell = cell(['Name', 'IP Address']);
  const projectCell = cell(['Project', 'Domain/Project']);
  const projectParts = resourceText(projectCell).split(/\n|\s+\/\s+/).map((s) => s.trim()).filter(Boolean);
  const href = nameCell?.querySelector('a[href]')?.getAttribute('href') || '';
  const uuid = identityFromHref(href);
  return {
    name: resourceText(nameCell?.querySelector('a') || nameCell),
    project: projectParts.at(-1) || '',
    domain: projectParts.length > 1 ? projectParts[0] : resourceText(cell(['Domain'])),
    projectId: identityFromHref(projectCell?.querySelector('a[href]')?.getAttribute('href') || ''),
    id: row.getAttribute('data-resource-id') || resourceText(cell(['UUID', 'ID'])) || uuid || null
  };
};
const resolveResource = (table, expected) => {
  if (!table || !expected.name || !expected.project || (!expected.domain && !expected.projectId)) throw new Error('resource_identity_required');
  const currentProject = resourceText(document.querySelector('.projects-switch-wrapper'));
  if (currentProject !== expected.project) throw new Error('project_mismatch');
  const matches = resourceRows(table).map((row) => ({ row, identity: resourceIdentity(table, row) }))
    .filter(({ identity }) => identity.name === expected.name && identity.project === expected.project &&
      (!expected.domain || identity.domain === expected.domain) &&
      (!expected.projectId || identity.projectId === expected.projectId) &&
      (!expected.id || identity.id === expected.id));
  if (matches.length !== 1) throw new Error(matches.length ? 'ambiguous_resource' : 'resource_not_found');
  return matches[0];
};
const resourceSelected = (row) => {
  const input = row.querySelector('input[type="checkbox"]');
  return Boolean(input?.checked || row.getAttribute('aria-selected') === 'true');
};
const selectOnlyResource = async (table, row, readSelectionCount, timeoutMs = 2000) => {
  if (!Number.isFinite(timeoutMs) || timeoutMs < 0) throw new Error('invalid_timeout');
  if (typeof readSelectionCount !== 'function') throw new Error('global_selection_probe_required');
  if (!resourceRows(table).includes(row)) throw new Error('resource_row_stale');
  const original = resourceIdentity(table, row);
  const live = () => {
    if (resourceTable() !== table) throw new Error('resource_table_stale');
    if (!resourceRows(table).includes(row)) throw new Error('resource_row_stale');
    if (JSON.stringify(resourceIdentity(table, row)) !== JSON.stringify(original)) throw new Error('resource_identity_changed');
    if (resourceText(document.querySelector('.projects-switch-wrapper')) !== original.project) throw new Error('project_mismatch');
    if (resourceRows(table).some((item) => item !== row && resourceSelected(item))) throw new Error('other_resources_selected');
  };
  const count = () => {
    const value = readSelectionCount();
    if (!Number.isInteger(value) || value < 0) throw new Error('global_selection_unconfirmed');
    return value;
  };
  live();
  if (count() !== (resourceSelected(row) ? 1 : 0)) throw new Error('other_resources_selected');
  if (!resourceSelected(row)) {
    const control = row.querySelector('label.ant-checkbox-wrapper, .ant-checkbox-wrapper');
    if (!control || control.getAttribute('aria-disabled') === 'true') throw new Error('selection_unavailable');
    control.click();
  }
  const deadline = Date.now() + timeoutMs;
  while (true) {
    live();
    const selectedCount = count();
    if (selectedCount > 1) throw new Error('other_resources_selected');
    if (resourceSelected(row) && selectedCount === 1) return row;
    if (Date.now() >= deadline) throw new Error('selection_unconfirmed');
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
};
const uniqueButton = (root, label, selector = 'button') => {
  const matches = [...root.querySelectorAll(selector)].filter((node) =>
    resourceText(node) === label && node.getClientRects().length > 0 &&
    !node.disabled && node.getAttribute('aria-disabled') !== 'true');
  if (matches.length !== 1) throw new Error('action_unavailable_or_ambiguous');
  return matches[0];
};
const actionButton = (root, action) => {
  const labels = { start: 'Start', stop: 'Shutoff', reboot: 'Reboot', allocate_floating_ip: 'Apply For IP To Project' };
  if (!Object.hasOwn(labels, action)) throw new Error('unsupported_action');
  return uniqueButton(root, labels[action]);
};
```
<!-- resource-contract:end -->

`resourceIdentity` 的列名是当前英文基线. 语言、列配置或 DOM 不同时先现场校准
读取方式, 不回退为全文模糊匹配. `Domain/Project` 必须可明确拆出项目; 单元格无法
区分时先打开资源详情核实身份. `selectOnlyResource` 不切换已选目标. `readSelectionCount` 必须从当前 UI 可验证的
全局选择汇总读取跨页/筛选后的总选择数, 不能只统计可见行或硬编码 0/1. 无法观测
时停止批量动作, 或按当前 UI 的明确清除入口清除后重新核实; 不编造 selector.
资源项目使用 project UUID 或 domain/name 消歧, 同名项目的显示文本不足以证明租户
身份. 缺少这些字段时先通过当前页面/详情核实, 无法核实则停止. 包装元素点击未生效时返回失败, 再用当前 snapshot 的真实
checkbox ref 点击并回读, 不跳过选择校验.

```javascript
const { row, identity } = resolveResource(table, { name: '<name>', project: '<project>', domain: '<domain>', id: null });
await selectOnlyResource(table, row, readSelectionCount);
```

表格选择规则:

- 优先点击 `label.ant-checkbox-wrapper` 或可见的包装元素,不要默认只点
  `input[type="checkbox"]`。
- 点击后验证 `checked`、`aria-checked="true"` 或行进入 selected 状态。
- 如果列表刷新、筛选、翻页后 DOM 重建,必须重新定位目标行。

读取行状态:

```javascript
const { row, identity } = resolveResource(table, { name: '<name>', project: '<project>', domain: '<domain>', id: '<uuid>' });
const observedStatus = resourceText(row.querySelector('<observed-status-cell-selector>'));
const reached = observedStatus === '<target-status>';
```

搜索表格:

```javascript
const search = document.querySelector('.ant-input-search input, input[placeholder*="Search"]');
search.value = '<keyword>';
search.dispatchEvent(new Event('input', { bubbles: true }));
search.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
```

<a id="数字输入框"></a>

## Number Inputs 数字输入框

NG-ZORRO 数字输入框有时需要触发 `input` 和 `change` 事件。

```javascript
const setNumberInput = (selector, value) => {
  const input = document.querySelector(selector);
  if (!input) return false;
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(input, String(value));
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new Event('blur', { bubbles: true }));
  return true;
};
```

<a id="标签页"></a>

## Tabs 标签页

```javascript
const tab = [...document.querySelectorAll('.ant-tabs-tab')]
  .find((item) => item.innerText.includes('<tab-name>'));
clickWithMouse(tab);
```

<a id="消息与通知"></a>

## Notifications 消息与通知

```javascript
const success = document.querySelector('.ant-message-success, .ant-notification-notice-success');
Boolean(success);
```

清理遮挡通知:

```javascript
document.querySelectorAll('.ant-notification-notice').forEach((node) => node.remove());
```

<a id="确认对话框"></a>

## Confirmation Dialogs 确认对话框

```javascript
clickWithMouse(document.querySelector('.ant-modal-confirm-btns .ant-btn-primary'));
```

<a id="加载状态"></a>

## Loading States 加载状态

```javascript
const loading = document.querySelector('.ant-spin-spinning');
Boolean(!loading);
```

<a id="截图"></a>

## Screenshots 截图

```bash
agent-browser screenshot "/tmp/easystack-screenshots/<case-name>/result.png"
```
