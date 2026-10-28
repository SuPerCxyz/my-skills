# Volume Ops

本文件定义块存储操作及保留的 VM 镜像兼容入口. 当前修订均为 `ready-template`,
操作遵循 `patterns/operation-template.md`,并面向
`agent-browser` 的批量执行示例。

示例依赖 [interactions.md](../interactions.md) 的资源身份和按钮 helper; 将 helper 与
调用片段放在同一次 eval 中.
从当前 UI 定义可验证的全局 `readSelectionCount` 探针, 无法核实跨页选择时停止批量动作.
先核实 domain/project 或项目 UUID、名称和可用资源 UUID; 有其他已选资源或身份不唯一时停止.

## Table of Contents 目录

[使用约定](#使用约定) | [迁移状态](#迁移状态) | [`create_volume`](#create_volume) |
[`delete_volume`](#delete_volume) | [`detach_volume`](#detach_volume) |
[`create_volume_snapshot`](#create_volume_snapshot) |
[`rollback_volume_snapshot`](#rollback_volume_snapshot) |
[`delete_volume_snapshot`](#delete_volume_snapshot) | [`upload_image`](#upload_image) |
[`create_volume_from_snapshot`](#create_volume_from_snapshot) | [待迁移操作](#待迁移操作)

<a id="使用约定"></a>

## Usage 使用约定

- 配置默认值统一来自 `/tmp/easystack-env.json`
- 进入本域前应先执行 `patterns/login.md` 的登录契约
- `ready-template` 操作已补齐模板但执行时仍需现场确认
- 所有当前可用操作必须触发页面动作并验证目标状态
- 返回值统一包含 `ok/resource/action/name/status/message/url`

<a id="迁移状态"></a>

## Migration Status 迁移状态

- `create_volume`: `ready-template`
- `delete_volume`: `ready-template`
- `detach_volume`: `ready-template`
- `create_volume_snapshot`: `ready-template`
- `create_volume_from_snapshot`: `ready-template`
- `rollback_volume_snapshot`: `ready-template`
- `delete_volume_snapshot`: `ready-template`
- `upload_image`: `ready-template`
- 其他 volume / image 操作: `planned`

<a id="create_volume"></a>

## create_volume 创建云硬盘

用途:创建云硬盘,并验证目标卷在列表中出现且状态进入 `Available`。
参数:必填 `name`、`size`;环境默认 `vol_type -> resources.volume_type`;
可选 `description`、`target_status='Available'`。
前置条件:`platform.url` 存在,当前会话已登录,目标卷类型可见。
成功判定:提交创建后,卷列表出现目标卷且状态达到 `target_status`。
失败信号:缺少必填参数、会话失效、卷类型不可选、创建按钮不可用、轮询超时。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"volume","action":"create","name":"<volume-name>","status":"Available","message":"volume created","url":"<current-url>"}
```

卷类型规则:

- 显式传入 `vol_type` 时必须选择该卷类型。
- 未显式传入时优先使用 `resources.volume_type`。
- 如果默认卷类型在当前项目不可见,允许使用页面默认卷类型,但返回值必须记录
  实际使用的卷类型。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { name: '<volume-name>', size: 100, volType: '<volume-type>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const setInputValue = (node, value) => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      setter.call(node, String(value));
      node.dispatchEvent(new Event('input', { bubbles: true }));
      node.dispatchEvent(new Event('change', { bubbles: true }));
      node.dispatchEvent(new Event('blur', { bubbles: true }));
    };
    const createButton = uniqueButton(document, 'Create Volume');
    if (!createButton) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'create', name: input.name, status: 'button_unavailable', message: 'Create Volume button unavailable', url: location.href };
    } else {
      createButton.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return { ok: null, terminal: false, submitted: false, resource: 'volume', action: 'create', name: input.name, status: 'dialog_opened', message: 'fill Volume Name, Type, Size in dialog, submit, then poll /ebs/volumes until Available', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'create', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

<a id="delete_volume"></a>

## delete_volume 删除云硬盘

用途:删除云硬盘,并验证目标卷从列表中消失。
参数:必填 `name`。
前置条件:`platform.url` 存在,当前会话已登录,目标卷在列表中可见。
成功判定:确认删除后,列表中不再出现目标卷。
失败信号:缺少卷名、会话失效、目标卷不存在、删除入口不可见、轮询后仍可见。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"volume","action":"delete","name":"<volume-name>","status":"deleted","message":"volume deleted","url":"<current-url>"}
```

操作规则:

- 只删除本次用例创建并已映射的实际卷名,不按逻辑名或近似名匹配。
- 删除前必须确认目标卷为 `Available` 且 `No Attached`。
- 删除入口在 `More -> Delete`;如果顶层按钮状态刚刷新完不稳定,等待按钮
  enabled 后再操作。
- 删除弹窗存在二次确认:第一次点击 `Delete` 后,会出现
  `Unrecoverable after deletion, please confirm again.`,必须再点击 `Confirm`。
- 两层按钮都必须限定在当前最上层可见 modal 内查找;点完第一层后重新获取
  modal,不复用第一次的按钮引用或 ref。
- 提交后轮询 `/ebs/volumes`,直到目标卷行完全消失。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { name: '<volume-name>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.name, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'delete', name: input.name, status: 'missing', message: 'volume not found', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      uniqueButton(document, 'More').click();
      return { ok: null, terminal: false, submitted: false, resource: 'volume', action: 'delete', name: input.name, status: 'menu_opened', message: 'click More -> Delete, then click Delete and second-step Confirm, then poll /ebs/volumes until row disappears', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'delete', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

<a id="detach_volume"></a>

## detach_volume 卸载云硬盘

用途:从云主机卸载云硬盘,并验证目标卷回到 `Available / No Attached`。
参数:必填 `volume`;可选 `instance`、`device`。
前置条件:当前会话已登录,目标卷在 `/ebs/volumes` 可见,且当前状态为
`In use`。如果测试已经在 VM 内挂载文件系统,必须先通过 SSH 执行 `sync` 和
`umount <mountpoint>`,不能只在 UI 强制卸载。
成功判定:提交卸载后,目标卷状态为 `Available`,Attachments 显示
`No Attached`。
失败信号:目标卷不存在、卷未挂载、Detach 入口不可见、确认弹窗实例不匹配、
轮询超时。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"volume","action":"detach","name":"<volume-name>","status":"Available","message":"volume detached","url":"<current-url>"}
```

操作规则:

- 只卸载本次用例映射的实际卷名,不按逻辑名或近似名匹配。
- 如果列表行显示设备路径,如 `/dev/vdb`,报告中记录 `device`。
- 顶部 `Detach` 按钮可能在选中行后短暂 disabled;应等待 enabled 后再点击。
- 卸载弹窗必须确认 `Instance to Detach` 是本次映射的实例。
- 提交后轮询 `/ebs/volumes`,直到目标卷 `Available / No Attached`。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { volume: '<volume-name>', instance: '<instance-name>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.volume, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'detach', name: input.volume, status: 'missing', message: 'volume not found', url: location.href };
    } else if (!text(row).includes('In use')) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'detach', name: input.volume, status: 'not_attached', message: 'volume is not In use', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      const device = text(row).match(/\/dev\/vd[b-z]/)?.[0] || null;
      return { ok: null, terminal: false, submitted: false, resource: 'volume', action: 'detach', name: input.volume, status: 'selected', message: 'click Detach, verify instance in dialog, submit, then poll Available / No Attached', device, url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'detach', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

<a id="create_volume_snapshot"></a>

## create_volume_snapshot 创建卷快照

用途:对云硬盘创建快照,并验证快照列表中目标快照达到 `Available`。
参数:必填 `volume`、`snapshot_name`;可选 `forced=false`。
前置条件:当前会话已登录,目标卷在 `/ebs/volumes` 可见;挂载中卷必须
设置 `forced=true`。
成功判定:`/ebs/volume-snapshots` 中出现目标快照,状态为 `Available`。
失败信号:目标卷不存在、More 菜单无 `Create Snapshot`、快照名未被表单接受、
强制创建未选择、轮询超时。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"volume_snapshot","action":"create","name":"<snapshot-name>","status":"Available","message":"volume snapshot created","url":"<current-url>"}
```

操作规则:

- 列表页 refs 会随页面刷新失效;每次打开列表后重新 snapshot 或用可见 DOM 定位。
- 挂载中卷必须选择 `Forced to Create Snapshot = Yes`。
- 挂载中卷的弹窗默认 `No` 时,`Snapshot Name` 和 `Description` 可能是
  disabled;必须先点击 `Yes`,再填写快照名。
- 快照名输入必须触发 `input/change/blur`;否则 `Create` 可能保持 disabled。
- 弹窗提交按钮必须限定在 `Create Snapshot` 弹窗内查找。
- 如果弹窗内存在 form,优先提交该 form;否则点击 modal footer 里的 primary
  按钮,不要点页面底层同名 `Create`。
- 如果 Yes/No 都未选中,重新点击 `Yes` label,并再次触发快照名输入事件。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { volume: '<volume-name>', snapshotName: '<snapshot-name>', forced: true, project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.volume, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume_snapshot', action: 'create', name: input.snapshotName, status: 'missing_volume', message: 'volume not found', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      uniqueButton(document, 'More').click();
      return { ok: null, terminal: false, submitted: false, resource: 'volume_snapshot', action: 'create', name: input.snapshotName, status: 'menu_opened', message: 'click Create Snapshot, set Forced=Yes before filling name for in-use volumes, submit dialog, then poll /ebs/volume-snapshots until Available', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'volume_snapshot', action: 'create', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

<a id="rollback_volume_snapshot"></a>

## rollback_volume_snapshot 回滚卷快照

用途:将源云硬盘回滚到指定快照, 并核实卷稳定状态和快照点数据一致.
参数:必填 `snapshot_name`;可选 `volume` 用于确认弹窗中的源卷。
前置条件:当前会话已登录,目标快照在 `/ebs/volume-snapshots` 可见且状态为
`Available`。如果卷挂载到实例,实例必须先关机;如果 VM 内挂载了文件系统,
回滚前必须先执行 `sync` 和 `umount`。
成功判定:两层确认均已提交,卷列表中目标卷无 `Error`,并在数据校验步骤中
确认 md5 或业务数据与快照点一致。
失败信号:目标快照不可见、非最新快照且其后仍有同卷快照、按钮 disabled、
未处理第二层 `Confirm Snapshot RollBack`、卷进入 Error、数据校验不一致。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"volume_snapshot","action":"rollback","name":"<snapshot-name>","status":"verified","message":"volume rollback state and snapshot data verified","url":"<current-url>"}
```

操作规则:

- 回滚通常只能选择当前快照链中可回滚的快照;若要回滚更早快照,先删除其后的
  同卷快照,并确认删除真正完成。
- 选中行优先使用 `agent-browser snapshot` 中该行的 `LabelText [ref=...]`
  做真实点击;ng-zorro 复选框经常不响应单纯 DOM `.click()`。
- 点击 `Roll Back Volume` 后有两层确认:
  1. `Rolling Back Data From Snapshot` 弹窗中的 `Confirm`
  2. `Confirm Snapshot RollBack` 弹窗中的 `Confirm`
- 两层确认按钮文本相同,必须限定在当前弹窗内,或使用 snapshot 中最后一个
  `Confirm` ref,不能点击底层页面的同名按钮。
- 第一层 `Confirm` 点击后必须重新获取当前 modal,再处理第二层 `Confirm`。
- 提交后轮询 `/ebs/volumes`,并结合 VM 内数据校验判断是否真正生效;只看卷
  仍为 `In use` 不足以证明回滚成功。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { snapshotName: '<snapshot-name>', volume: '<volume-name>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.snapshotName, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume_snapshot', action: 'rollback', name: input.snapshotName, status: 'missing', message: 'snapshot not found', url: location.href };
    } else if (!text(row).includes('Available')) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume_snapshot', action: 'rollback', name: input.snapshotName, status: 'not_ready', message: 'snapshot is not Available', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      const button = uniqueButton(document, 'Roll Back Volume');
      button?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return { ok: null, terminal: false, submitted: false, resource: 'volume_snapshot', action: 'rollback', name: input.snapshotName, status: 'confirm_needed', message: 'confirm Rolling Back Data From Snapshot, then confirm Confirm Snapshot RollBack, then poll and verify data', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'volume_snapshot', action: 'rollback', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

<a id="delete_volume_snapshot"></a>

## delete_volume_snapshot 删除卷快照

用途:删除云硬盘快照,并验证快照列表中不再出现目标快照。
参数:必填 `snapshot_name`。
前置条件:当前会话已登录,目标快照在 `/ebs/volume-snapshots` 可见。
成功判定:完成所有确认后,重新打开快照列表且目标快照不存在。
失败信号:目标快照不可见、按钮 disabled、只点了第一层 Delete、轮询后目标快照
仍存在。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"volume_snapshot","action":"delete","name":"<snapshot-name>","status":"deleted","message":"volume snapshot deleted","url":"<current-url>"}
```

操作规则:

- 删除弹窗可能是两层确认:先点击 `Delete Volume Snapshot` 弹窗中的 `Delete`;
  如果出现 `Unrecoverable after deletion, please confirm again.`,再点击 `Confirm`。
- 页面上有底层 `Delete` 工具栏按钮和弹窗 `Delete` 主按钮,二者同名;解析 ref
  时取弹窗内按钮,不能取第一个同名按钮。
- 第一层删除后重新获取当前 modal,再找第二层 `Confirm`。
- 提交后必须等待表格完整加载再判断;半加载状态下 `body` 不含目标名不能当作删除成功。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { snapshotName: '<snapshot-name>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.snapshotName, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume_snapshot', action: 'delete', name: input.snapshotName, status: 'missing', message: 'snapshot not found', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      const button = uniqueButton(document, 'Delete');
      button?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return { ok: null, terminal: false, submitted: false, resource: 'volume_snapshot', action: 'delete', name: input.snapshotName, status: 'confirm_needed', message: 'click modal Delete, then second Confirm if present, then poll /ebs/volume-snapshots until row disappears', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'volume_snapshot', action: 'delete', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

<a id="upload_image"></a>

## upload_image 上传 VM 镜像

此操作保留 VM 镜像参数契约, 已移至 [image-ops.md](image-ops.md).
VM 镜像与容器仓库不是同一入口; 不使用 `/container-registry/image` 上传 qcow2.
容器包上传使用独立的 `upload_container_image`, 见同一文档.

<a id="create_volume_from_snapshot"></a>

## create_volume_from_snapshot 从快照创建卷

用途:从云硬盘快照创建云硬盘,并验证新卷在卷列表达到 `Available`。
参数:必填 `snapshot_name`、`volume_name`;可选 `copy_full_data=false`。
前置条件:当前会话已登录,目标快照在 `/ebs/volume-snapshots` 可见且状态
为 `Available`。
成功判定:提交创建后,`/ebs/volumes` 中出现 `volume_name`,状态为
`Available`。
失败信号:目标快照不存在、快照未 Available、创建卷入口不可见、卷名未被
表单接受、拷贝全量数据选项设置错误、轮询超时。
返回值约定:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"volume","action":"create_from_snapshot","name":"<volume-name>","status":"Available","message":"volume created from snapshot","url":"<current-url>"}
```

操作规则:

- 路径使用 `/ebs/volume-snapshots`。
- 选中目标快照后点击 `Create Volume`。
- 创建卷弹窗默认继承快照 Size 和 Type;除用例特别说明,不修改继承值。
- `Copy Full Data` 默认保持 `No` 或显式选择 `No`。
- 只有用例明确要求“全量拷贝数据”时,才选择 `Yes`。
- 卷名输入后必须触发 `input/change/blur`,再检查 `Create` 按钮是否 enabled。
- 提交后进入 `/ebs/volumes` 轮询目标卷到 `Available`。

`agent-browser eval --stdin` 示例:

```js
(async () => {
  try {
    const input = { snapshotName: '<snapshot-name>', volumeName: '<volume-name>', copyFullData: false, project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const table = resourceTable();
    const { row, identity } = resolveResource(table, { name: input.snapshotName, project: input.project, domain: input.domain, id: input.id });
    if (!row) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'create_from_snapshot', name: input.volumeName, status: 'missing_snapshot', message: 'snapshot not found', url: location.href };
    } else if (!text(row).includes('Available')) {
      return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'create_from_snapshot', name: input.volumeName, status: 'snapshot_not_ready', message: 'snapshot is not Available', url: location.href };
    } else {
      await selectOnlyResource(table, row, readSelectionCount);
      uniqueButton(document, 'Create Volume', 'a,button').click();
      return { ok: null, terminal: false, submitted: false, resource: 'volume', action: 'create_from_snapshot', name: input.volumeName, status: 'dialog_opened', message: 'fill volume name, keep Copy Full Data No unless explicitly required, then submit dialog', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'volume', action: 'create_from_snapshot', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```

<a id="待迁移操作"></a>

## Planned Operations 待迁移操作

以下名称当前仅保留为待迁移操作清单(`planned`),不作为当前可执行入口:

- `extend_volume`
- `edit_volume`
- `create_image_from_volume`
- `delete_image`
