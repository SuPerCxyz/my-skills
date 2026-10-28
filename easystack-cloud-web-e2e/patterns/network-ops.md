# Network Ops

本文件定义网络域原子操作。所有 `ready-template`
操作遵循 `patterns/operation-template.md`,并面向 `agent-browser` 的批量执行示例。

示例依赖 [interactions.md](../interactions.md) 的资源身份和按钮 helper; 将 helper 与
调用片段放在同一次 eval 中.
从当前 UI 定义可验证的全局 `readSelectionCount` 探针, 无法核实跨页选择时停止批量动作.
先核实 domain/project 或项目 UUID、名称和可用资源 UUID; 有其他已选资源或身份不唯一时停止.

## Usage 使用约定

- 配置默认值统一来自 `/tmp/easystack-env.json`
- 执行入口路径遵循 `navigation.md` 的当前主路径
- 进入本域前应先执行 `patterns/login.md` 的登录契约
- `ready-template` 操作已补齐模板但执行时仍需现场确认
- 所有当前可用操作必须触发页面动作并验证目标状态
- 返回值统一包含 `ok/resource/action/name/status/message/url`

## Migration Status 迁移状态

- `allocate_floating_ip`: `ready-template`
- `associate_floating_ip`: `ready-template`
- `disassociate_floating_ip`: `ready-template`
- `release_floating_ip`: `ready-template`
- `create_network`: `ready-template`
- `create_router`: `ready-template`
- 其他 network 操作: `planned`

## allocate_floating_ip 分配浮动 IP

用途:分配一个浮动 IP,并验证浮动 IP 列表出现新记录。
参数:可选 `bandwidth=1`;环境默认 `project -> resources.project_name`、`resource_pool -> resources.external_network`。
前置条件:`platform.url` 存在,当前会话已登录,浮动 IP 页面可访问。
成功判定:提交分配后,列表中出现新的浮动 IP 行。
失败信号:会话失效、分配入口不可见、提交失败、轮询后列表无新增记录。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"floating_ip","action":"allocate","name":"<allocated-ip>","status":"allocated","message":"floating ip allocated","url":"<current-url>"}
```

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const allocateButton = actionButton(document, 'allocate_floating_ip');
    if (!allocateButton) {
      return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'allocate', name: null, status: 'button_unavailable', message: 'Allocate button unavailable', url: location.href };
    } else {
      allocateButton.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return { ok: null, terminal: false, submitted: false, resource: 'floating_ip', action: 'allocate', name: '<allocated-ip>', status: 'dialog_opened', message: 'set bandwidth, submit dialog, then poll list until a new floating IP row appears', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'allocate', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

## create_network 创建网络

用途:创建网络,并验证目标网络在网络列表中出现。
参数:必填 `name`;可选 `type='Internal Network'`、`visibility='Project Exclusive'`、`mode='Geneve'`.
默认创建页要求 `subnet_name` 与 `subnet_cidr`; 没有明确值且无已确认的页面默认值时停止,
不随意生成业务网段. 页面若支持无子网网络, 仅在用例明确选择该分支时省略.
前置条件:`platform.url` 存在,当前会话已登录,网络创建入口可访问。
成功判定:创建提交成功,返回网络列表后出现目标网络。
失败信号:缺少名称、会话失效、入口不可访问、创建后目标网络未出现。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"network","action":"create","name":"<network-name>","status":"created","message":"network created","url":"<current-url>"}
```

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { name: '<network-name>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const createButton = uniqueButton(document, 'Create Network');
    if (!createButton) {
      return { ok: false, terminal: true, submitted: false, resource: 'network', action: 'create', name: input.name, status: 'button_unavailable', message: 'Create button unavailable', url: location.href };
    } else {
      createButton.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return { ok: null, terminal: false, submitted: false, resource: 'network', action: 'create', name: input.name, status: 'dialog_opened', message: 'fill network form, submit, then poll /ens/networks until row appears', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'network', action: 'create', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

## associate_floating_ip 绑定浮动 IP

用途:将空闲浮动 IP 绑定到实例的 vNIC,并验证实例列表显示该浮动 IP。
参数:必填 `instance`、`private_ip`;可选 `floating_ip`,不传时使用本次 `allocate_floating_ip` 已确认并记录的实际 IP; 无唯一映射时停止,
不挑选列表第一个空闲地址.
前置条件:当前会话已登录,浮动 IP 页面 `/ens/floatingIPs` 可访问,目标实例
已有私网 IP,且存在空闲浮动 IP。
成功判定:实例列表中目标实例的 IP Address 显示目标 Floating IP。
失败信号:目标浮动 IP 不空闲、目标实例不可选、vNIC 下拉没有目标私网 IP、
Associate 按钮不可用或验证超时。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"floating_ip","action":"associate","name":"<floating-ip>","status":"associated","message":"floating ip associated","url":"<current-url>"}
```

操作规则:

- 路径使用 `/ens/floatingIPs`。
- 空闲 IP 行点击 `Bind to resource`。
- 资源类型保持 `Virtual NIC`。
- 先选目标实例,再选包含目标私网 IP 的 vNIC;vNIC 下拉依赖实例选择。
- 提交时必须限定在 `Bind to resource` 弹窗内点击 `Associate`。
- 如果弹窗内存在 form,优先提交 form;否则只点击当前最上层 modal footer
  中的 `Associate` 主按钮。
- `Resource` 下拉选中实例后,等待 vNIC 下拉刷新;不要在 vNIC 仍 disabled 或仍显示
  `Select a vNIC` 时提交。
- 目标私网 IP 只在 vNIC 选项中出现,不一定在资源选项中出现;选择逻辑应分两步
  分别匹配 `instance` 和 `private_ip`。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { instance: '<instance-name>', privateIp: '<private-ip>', floatingIp: '<optional-floating-ip>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    if (!input.floatingIp || input.floatingIp === '<optional-floating-ip>') throw new Error('allocated_floating_ip_identity_required');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.floatingIp, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'associate', name: input.floatingIp || null, status: 'missing_free_ip', message: 'free floating ip not found', url: location.href };
    } else {
      const ip = identity.name;
      uniqueButton(row, 'Bind to resource', 'a,button').click();
      return { ok: null, terminal: false, submitted: false, resource: 'floating_ip', action: 'associate', name: ip, status: 'dialog_opened', message: 'select instance and vNIC containing private_ip, then click Associate in dialog', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'associate', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

## create_router 创建路由器

用途:创建路由器,并验证目标路由器在路由器列表中出现。
参数:必填 `name`;可选 `type='Regular Router'`、`set_gateway=false`。
前置条件:`platform.url` 存在,当前会话已登录,路由器创建入口可访问。
成功判定:创建提交成功,返回路由器列表后出现目标路由器。
失败信号:缺少名称、会话失效、入口不可访问、创建后目标路由器未出现。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"router","action":"create","name":"<router-name>","status":"created","message":"router created","url":"<current-url>"}
```

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { name: '<router-name>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const createButton = uniqueButton(document, 'Create Router');
    if (!createButton) {
      return { ok: false, terminal: true, submitted: false, resource: 'router', action: 'create', name: input.name, status: 'button_unavailable', message: 'Create button unavailable', url: location.href };
    } else {
      createButton.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return { ok: null, terminal: false, submitted: false, resource: 'router', action: 'create', name: input.name, status: 'dialog_opened', message: 'fill router form, submit, then poll /ens/routers until row appears', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'router', action: 'create', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

## disassociate_floating_ip 解绑浮动 IP

用途:解绑浮动 IP 与实例/vNIC 的关联,并验证浮动 IP 变为空闲。
参数:必填 `floating_ip`;可选 `instance`。
前置条件:当前会话已登录,目标浮动 IP 在 `/ens/floatingIPs` 可见且已绑定。
成功判定:目标浮动 IP 行不再显示实例名,Action 显示 `Bind to resource`。
失败信号:目标 IP 不存在、未绑定、Disassociate 入口不可见、确认后仍绑定。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"floating_ip","action":"disassociate","name":"<floating-ip>","status":"free","message":"floating ip disassociated","url":"<current-url>"}
```

操作规则:

- 清理前必须已获得用户确认;未确认时只在报告写 `cleanup: recommended`。
- 只解绑本次用例创建或明确映射的浮动 IP。
- 点击目标行 `Disassociate`,处理确认弹窗后轮询行状态。
- 确认按钮必须限定在当前最上层 modal 内;如果出现二次确认,重新获取 modal。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { floatingIp: '<floating-ip>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.floatingIp, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'disassociate', name: input.floatingIp, status: 'missing', message: 'floating ip not found', url: location.href };
    } else {
      const action = uniqueButton(row, 'Disassociate', 'a,button');
      action.click();
      return { ok: null, terminal: false, submitted: false, resource: 'floating_ip', action: 'disassociate', name: input.floatingIp, status: 'confirm_needed', message: 'confirm dialog, then poll until Bind to resource appears', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'disassociate', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

## release_floating_ip 释放浮动 IP

用途:释放空闲浮动 IP,并验证浮动 IP 列表中不再出现该地址。
参数:必填 `floating_ip`。
前置条件:当前会话已登录,目标浮动 IP 在 `/ens/floatingIPs` 可见且空闲。
成功判定:提交释放后,列表中不再出现目标 IP。
失败信号:目标 IP 不存在、仍绑定资源、Release 入口不可见、二次确认失败、
轮询后仍存在。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"floating_ip","action":"release","name":"<floating-ip>","status":"released","message":"floating ip released","url":"<current-url>"}
```

操作规则:

- 清理前必须已获得用户确认;未确认时只在报告写 `cleanup: recommended`。
- 只释放本次用例创建或明确映射的浮动 IP。
- 释放前必须确认行内 Attach Resource 为空或显示 `Bind to resource`。
- 如果释放弹窗出现二次确认,按弹窗主按钮继续确认后再轮询。
- 不要使用页面底层 `Release` 工具栏按钮完成确认;只处理弹窗内按钮。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { floatingIp: '<floating-ip>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.floatingIp, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'release', name: input.floatingIp, status: 'missing', message: 'floating ip not found', url: location.href };
    } else if (text(row).includes('Instance:')) {
      return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'release', name: input.floatingIp, status: 'still_associated', message: 'disassociate before release', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      uniqueButton(document, 'Release Floating IPs').click();
      return { ok: null, terminal: false, submitted: false, resource: 'floating_ip', action: 'release', name: input.floatingIp, status: 'confirm_needed', message: 'confirm release dialog, then poll until row disappears', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'floating_ip', action: 'release', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

## Planned Operations 待迁移操作

以下名称当前仅保留为待迁移操作清单(`planned`),不作为当前可执行入口:

- `associate_network`
- `disassociate_network`
- `edit_security_group`
