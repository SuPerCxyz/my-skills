# Quick Reference

本文件只索引 `patterns/` 当前能力。
`ready-validated` 必须附当前修订、平台版本、日期、用例和脱敏结果引用;
`ready-template` 表示已按 `patterns/operation-template.md` 补齐统一模板但尚未
完成真实用例闭环验证;
`planned` 仅保留待迁移名称清单,不作为当前可执行入口。

## Usage Flow 使用流程

1. 先读 `patterns/login.md`
2. 再读对应资源域文档
3. 优先使用 `ready-validated`;`ready-template` 可作为模板执行但必须现场确认;
   `planned` 只代表后续迁移目标

## Click Decisions 点击决策

1. 页面普通按钮:优先 `agent-browser click <ref/selector>`,点击前确认按钮已
   visible 且 enabled。
2. modal 按钮:只在当前最上层可见 modal 内定位按钮;点完第一层确认后重新
   获取 modal。
3. form 提交:如果操作依赖 `ngSubmit` 或 modal 内存在 form,优先
   `form.requestSubmit()`,不要全局搜索同名 `Create/Confirm`。
4. checkbox / 行选择:优先点击 `label.ant-checkbox-wrapper` 或可见包装元素,
   不要默认只点隐藏 input。
5. 页面发生 modal 开关、切页、筛选、表格刷新后,旧 ref 一律视为失效。
6. 顶部工具栏按钮和 `More` 菜单动作默认要求先选中目标行;行名称、详情链接、
   行内链接通常不要求先选中。
7. 选中成功必须是可观测的:checkbox 已 checked,或目标动作按钮由 disabled
   变 enabled;只“点过这一行”不算成功。
8. 也有页面采用纯行内动作模式,例如计算节点、浮动 IP;这类页面很多操作在
   Action 列,而不在顶部批量工具栏。

## Required Inputs 必填项

1. 主操作按钮如果是 disabled,先不要点击;优先检查当前页面或弹窗中的必填项。
2. 必填输入填值后,要补齐页面所需事件,例如 `input`、`change`、`blur`。
3. 必填下拉或联动字段必须真正选中并刷新完成,再检查主按钮是否 enabled。
4. 只有必填项满足、主操作按钮变 enabled 后,才执行点击或提交。
5. 下拉、联动字段或资源选择框点击后,必须回读当前展示值;值没变就视为未选中。
6. 如果点击后没有任何跳转、提示或网络请求,先检查隐藏字段、登录类型、权限提示
   和覆盖层,不要立刻判定为元素无效。

## State Waiting 状态等待

1. 创建或操作资源后,先看到资源名出现,只能说明“资源记录已出现”,不能直接
   说明操作成功。
2. 必须继续等待资源从中间态进入目标稳定态,例如:
   `Creating -> Available`、`Creating -> Active`、`In use -> Available`。
3. 如果资源停留在 `Creating`、`Binding`、`Associating`、`Detaching`、
   `Deleting` 等中间态,继续轮询并记录当前状态,不要提前判成功。
4. 不要用长时间 `for` 循环直接等待“资源出现 + 状态完成”两个目标;应拆成
   “短窗口等出现”与“出现后等稳定态”。
5. 短窗口内如果资源未出现,先刷新页面、重建定位、检查筛选条件或项目上下文,
   再决定是否继续等待。
6. 按钮启用、modal 提交、列表刷新这类普通 UI 等待,默认只给短预算;超过短预算
   仍无变化时,不再傻等,转检查必填项、项目、配额、筛选条件或替代入口。
7. 只有云硬盘迁移数据、云主机迁移、`fio` 等明确长耗时任务,才允许放宽等待上限;
   放宽前必须在结果里说明这是长耗时等待,不得把常规创建/编辑/绑定操作也当成长任务。
8. 结果判定优先级默认是:资源列表稳定态 > 详情页状态 > toast/notification。
9. 列表实时刷新、高频新增、切换筛选/排序后,不再依赖旧行号、旧分页位置或旧 ref;
   必须重新按资源名和状态重新定位。
10. interactive snapshot 可能漏掉禁用菜单项;探索 `More` 或下拉菜单时,必要时同时
    查看 `get text body`。

## Observed Notes 现场补充

1. 登录页密码输入后,不要立刻提交;先确认 `Sign In` 已变为真正的可点击
   `button`。
2. 登录成功后,先检查左上角 `.projects-switch-wrapper`;如果当前项目没有目标
   操作所需的配额或资源,执行前切到正确项目。
3. 非破坏性验证优先选择“打开弹窗 -> 检查主按钮状态 -> 关闭弹窗”,不要触发
   创建、删除、解绑等真实提交。
4. `Click here for filters.` 一类控件不要默认当成即时名称搜索框;如果输入后列表
   不收窄,立即改查该控件是否需要额外确认动作,或改用真正的筛选入口/分页定位。
5. 表格列筛选会影响整张表当前展示的数据集合;启用后,后续分页、状态判断、资源定位
   都必须基于筛选后的结果重新判断。
6. 服务目录是覆盖层而不是普通跳转页;打开后所有点击都必须限定在目录面板内。
7. 部分资源动作权限不足时不会弹 modal,而是直接在页面正文给出提示文案;这属于
   产品权限反馈,不是自动化 click 失败。

当前修订没有可复核的真实 UI 结果, 所有原有已验证操作降为 `ready-template`.
离线行为测试只覆盖文档 helper/示例与结果约定, 不证明真实资源操作成功.

## Capability Index 能力索引

| 操作名 | 资源域 | 文档位置 | 必填参数 | 默认参数来源 | 返回结果 | 当前状态 |
|---|---|---|---|---|---|---|
| `create_instance` | `instance` | `patterns/instance-ops/create-instance.md` | `name` | `resources.image_name`、`resources.flavor`、`resources.network_name`、`resources.subnet_name`、`ssh.key_name`、`vm_defaults.password` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `delete_instance` | `instance` | `patterns/instance-ops/delete-instance.md` | `name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `attach_volume` | `instance` | `patterns/instance-ops/attach-volume.md` | `instance`、`volume` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `rename_instance` | `instance` | `patterns/instance-ops/rename-instance.md` | `instance`、`new_name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `start_stop_reboot_instance` | `instance` | `patterns/instance-ops/start-stop-reboot.md` | `name`、`action` | `target_status` 可由动作推导 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_instance_snapshot` | `instance` | `patterns/instance-ops/create-snapshot.md` | `instance`、`snapshot_name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_volume` | `volume` | `patterns/volume-ops.md` | `name`、`size` | `resources.volume_type`、`screenshot_dir` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `detach_volume` | `volume` | `patterns/volume-ops.md` | `volume` | `instance`、`device` 可选 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `delete_volume` | `volume` | `patterns/volume-ops.md` | `name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `upload_image` (VM) | `image` | `patterns/image-ops.md` | `name`、`source_url` | `resources.image_os_category` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `upload_container_image` | `container_image` | `patterns/image-ops.md` | `workspace`、`local_file`、`image_name`、`tag` | 当前项目 | 核实 workspace/name/tag 与上传完成 | `ready-template` |
| `create_volume_snapshot` | `volume` | `patterns/volume-ops.md` | `volume`、`snapshot_name` | `forced=false` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `rollback_volume_snapshot` | `volume` | `patterns/volume-ops.md` | `snapshot_name` | `volume` 可选 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `delete_volume_snapshot` | `volume` | `patterns/volume-ops.md` | `snapshot_name` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_volume_from_snapshot` | `volume` | `patterns/volume-ops.md` | `snapshot_name`、`volume_name` | `copy_full_data=false`、快照继承 `size/type` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `allocate_floating_ip` | `network` | `patterns/network-ops.md` | 无 | `resources.project_name`、`resources.external_network` | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `associate_floating_ip` | `network` | `patterns/network-ops.md` | `instance`、`private_ip` | `floating_ip` 可选 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `disassociate_floating_ip` | `network` | `patterns/network-ops.md` | `floating_ip` | `instance` 可选 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `release_floating_ip` | `network` | `patterns/network-ops.md` | `floating_ip` | 无 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_network` | `network` | `patterns/network-ops.md` | `name` | 显式可选参数 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `create_router` | `network` | `patterns/network-ops.md` | `name` | 显式可选参数 | 结构化对象 `{ok,resource,action,status,message,url}` | `ready-template` |
| `probe_resource_list_pages` | `page` | `patterns/page-probes.md` | 无 | `platform.url` | 结构化对象 `{ok,resource,action,pages}` | `ready-template` |
| `probe_create_instance_page` | `page` | `patterns/page-probes.md` | 无 | `platform.url` | 结构化对象 `{ok,resource,action,fields}` | `ready-template` |
| `probe_create_volume_modal` | `page` | `patterns/page-probes.md` | 无 | `platform.url` | 结构化对象 `{ok,resource,action,labels,defaults}` | `ready-template` |
| `cleanup_resources_plan` | `cleanup` | `patterns/cleanup-resources.md` | `resources[]` | 报告中的 `cleanup: recommended` | 结构化对象 `{ok,action,status,resources,message}` | `ready-template` |
| `resize_instance` | `instance` | `patterns/instance-ops.md(待迁移操作)` | `instance`、`flavor` | `resources.flavor` | 待迁移 | `planned` |
| `reset_instance_password` | `instance` | `patterns/instance-ops.md(待迁移操作)` | `instance`、`password` | `vm_defaults.password` | 待迁移 | `planned` |
| `clone_instance` | `instance` | `patterns/instance-ops.md(待迁移操作)` | `instance`、`new_name` | 调用方入参 | 待迁移 | `planned` |
| `lock_instance` | `instance` | `patterns/instance-ops.md(待迁移操作)` | `instance` | 无 | 待迁移 | `planned` |
| `unlock_instance` | `instance` | `patterns/instance-ops.md(待迁移操作)` | `instance` | 无 | 待迁移 | `planned` |
| `rollback_instance_snapshot` | `instance` | `patterns/instance-ops.md(待迁移操作)` | `instance`、`snapshot_name` | 无 | 待迁移 | `planned` |
| `delete_instance_snapshot` | `instance` | `patterns/instance-ops.md(待迁移操作)` | `snapshot_name` | 无 | 待迁移 | `planned` |
| `delete_image` | `volume` | `patterns/volume-ops.md(待迁移操作)` | `image_name` | 无 | 待迁移 | `planned` |
