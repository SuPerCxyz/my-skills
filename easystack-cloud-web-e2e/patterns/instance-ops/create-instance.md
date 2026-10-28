# create_instance

> 来源:`patterns/instance-ops.md`,按原子操作拆分。

示例依赖 [interactions.md](../../interactions.md) 的资源身份和按钮 helper; 将 helper 与
调用片段放在同一次 eval 中. 实例子文件的相对路径为 `../../interactions.md`.
从当前 UI 定义可验证的全局 `readSelectionCount` 探针, 无法核实跨页选择时停止批量动作.
先核实 domain/project 或项目 UUID、名称和可用资源 UUID; 有其他已选资源或身份不唯一时停止.

## create_instance 创建云主机

### Purpose 用途

创建一台实例,并在实例列表中验证其出现且达到目标状态。

### Parameters 参数

- 必填参数: `name`
- 环境默认参数: `image` -> `resources.image_name`
- 环境默认参数: `flavor` -> `resources.flavor`
- 环境默认参数: `network` -> `resources.network_name`
- 可选环境参数: `subnet` -> `resources.subnet_name`,仅在页面要求显式选择子网时使用
- 环境默认参数: `key_name` -> `ssh.key_name`
- 环境默认参数: `password` -> `vm_defaults.password`
- 自动生成参数: 未提供 `password` 且未提供 `key_name` 时,运行时生成密码
- 显式可选参数: `system_disk_size`,必须在基础配置页的 `*Root Disk` 区域设置
- 显式可选参数: `target_status`,默认 `Active`

### Prerequisites 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标镜像、规格、网络在当前项目中可见
- 若页面要求显式选择子网,则目标子网在当前项目中可见
- 已按 `connection.md` 校验左上角项目上下文
- 如果环境存在多个项目,优先显式使用 `resources.project_name`;未配置时,如
  创建页出现 `Quota exceeded`,先切换到有目标镜像/网络/配额的项目再重试,不要
  直接判定创建能力不可用。

### Success Criteria 成功判定

- 创建提交后返回实例列表
- 列表中出现目标实例
- 实例状态达到 `target_status`

### Operation Steps 执行步骤概览

- 打开实例创建页并确认当前会话仍处于已登录状态
- 若直接打开创建 URL 被 SPA 重定向回实例列表,应从实例列表点击
  `Create Instance` 按钮进入向导。
- 连续完成基础配置、网络配置、系统配置和最终确认; 同页动作批量执行,
  页面或异步边界短段回读, 不在每步向用户确认
- 选择镜像、规格、网络、子网,并按登录凭证优先级设置凭证
- 如用例要求系统盘大小,必须在基础配置页进入下一步前设置 `*Root Disk`
  区域的 `Size GiB`,并在最终确认页核对系统盘大小
- 提交创建请求并回到实例列表页
- 轮询实例列表,直到目标实例出现且状态达到 `target_status`

### Root Disk Size 系统盘大小设置规则

- `system_disk_size` 属于基础配置页,不属于系统配置页;进入网络配置页后再设置
  已经无效。
- 定位范围必须限定在 `*Root Disk` / `.system-disk` 区域,避免误改实例数量、
  数据盘数量或镜像最小盘字段。
- 设置 `Size GiB` 时不能只改 DOM `value`;必须通过页面输入事件触发表单:
  聚焦输入框 -> 全选/清空 -> 输入目标值 -> 触发 `input`、`change`、`blur`。
- 设置后立即读取 `*Root Disk` 区域展示值;最终确认页必须再次核对系统盘大小。
- 如果最终确认页或实例列表显示仍为镜像最小盘,判定为系统盘大小未被页面接受,
  不得在需要严格前置的用例中继续。

### Credential Priority 登录凭证优先级

系统配置页必须按以下顺序选择登录凭证:

1. 同时存在 `vm_defaults.password` 和 `ssh.key_name`:选择 `Both`
2. 仅存在 `vm_defaults.password`:选择 `Password`
3. 仅存在 `ssh.key_name`:选择 `SSH Key Pair`
4. 都不存在:运行时生成密码,选择 `Password`

自动生成的密码不得写入运行报告或 `/tmp/easystack-env.json`。优先只保存在当前进程
内存; 必须落盘时写入权限为 `0600` 的本次运行临时文件, 报告只记录临时引用和生成
方式, 验证结束后删除临时文件。

### Failure Signals 失败信号

- 缺少名称、镜像、规格、网络或平台地址等必填输入
- 页面跳转到登录页,说明当前会话失效
- 镜像、规格、网络、子网或密钥对在页面中不可见或无法选中
- 当前项目配额不足;这时应记录项目名并尝试按 `resources.project_name` 或项目
  切换器选择正确项目。
- 轮询超时后,实例仍未出现或未达到目标状态

### Control Selection 控件选择注意事项

- 镜像和规格表格行点击可能不会选中 radio;优先点击目标行内的
  `label.ant-radio-wrapper`。
- 环境中的 `resources.flavor` 可能带系统盘后缀,例如 `4C-8G-100G`,而页面
  flavor 只显示 `4C-8G`。匹配时先尝试完整值,再尝试去掉末尾磁盘大小后的规格名,
  但最终确认页必须记录页面实际 flavor 和 root disk。
- 网络步骤如默认选中共享网络,应优先按 `resources.network_name` 和
  `resources.subnet_name` 显式选择目标网络/子网,避免后续 SSH 路由不可达。

### Result Contract 返回值约定

```json
{
  "ok": true,
  "terminal": true,
  "submitted": true,
  "resource": "instance",
  "action": "create",
  "name": "<instance-name>",
  "status": "Active",
  "message": "instance created",
  "url": "<current-url>"
}
```

### Browser Example `agent-browser eval --stdin` 示例

```js
(async () => {
  try {
    const input = { name: '<instance-name>', image: '<image>', flavor: '<flavor>', network: '<network>', project: '<project-name>', domain: '<domain-name>', id: null };
    const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
    const setValue = (node, value) => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      setter.call(node, String(value));
      node.dispatchEvent(new Event('input', { bubbles: true }));
      node.dispatchEvent(new Event('change', { bubbles: true }));
      node.dispatchEvent(new Event('blur', { bubbles: true }));
    };
    const nextButton = uniqueButton(document, 'Next: Network Configuration');
    if (!nextButton) {
      return { ok: false, terminal: true, submitted: false, resource: 'instance', action: 'create', name: input.name, status: 'button_unavailable', message: 'Next button unavailable', url: location.href };
    } else {
      nextButton.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return { ok: null, terminal: false, submitted: false, resource: 'instance', action: 'create', name: input.name, status: 'wizard_progressing', message: 'continue the authorized wizard in bounded batches, verify Root Disk before network step and final summary, then submit and poll instance list', url: location.href };
    }
  } catch (error) {
    return { ok: false, terminal: true, submitted: false, resource: 'instance', action: 'create', status: 'interaction_failed', message: error.message, url: location.href };
  }
})()
```
