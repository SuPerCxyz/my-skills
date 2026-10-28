# Image Ops

VM 镜像用于启动实例; 容器镜像用于容器仓库. 两者的资源身份、入口和上传格式不同.
只说“上传镜像”且上下文不能区分时, 先确认镜像类型, 不用文件后缀替代用户目标.
两个操作当前均为 `ready-template`, 未进行真实 UI 验证.

## VM Image VM 镜像

### upload_image 上传 VM 镜像

保留原操作名和 `name`、`source_url`、`os_category`、`disk_format='qcow2'`、
`container_format='bare'` 的 VM 镜像语义. 前置条件为已登录、目标项目明确、来源可信、
具有上传权限及配额. `os_category` 可来自 `resources.image_os_category`.

1. 通过 Service Catalog -> Computing -> Instance Image 查找实例镜像入口,
   回读当前 URL、页面标题和表单字段. 当前资料没有可靠的 VM 镜像固定 URL;
   `/glance/images` 仅为历史线索, `/container-registry/image` 是容器仓库.
2. 核实当前表单是否支持 URL 来源和指定格式. 字段不存在时报告
   `unsupported_upload_contract`, 不将 URL 填入容器包上传框, 不自行改变镜像类型.
3. 以现场观察到的标签定位并填写目标名称、来源、格式和操作系统分类;
   对联动字段回读展示值, 核实项目、访问范围和主按钮 enabled.
4. 只提交一次并记录实际镜像身份. 先有限等待记录出现, 再等待镜像状态达到
   当前版本实际提供的可用终态; Queued/Saving/Creating 是中间态, Error 为失败.
5. 最终核实同一项目/UUID 的名称、格式和可用状态, 才返回
   `ok:true, terminal:true, submitted:true, status:'available'`.

缺入口、权限、必填参数或不支持字段时不提交. 提交后超时保留 `ok:null` 和观察
检查点, 不重复上传. 删除本次镜像仍须遵循已获清理授权及精确身份规则.
以上是待现场适配的流程契约, 不冒充已实现并验证的固定 selector 脚本.

## Container Image 容器镜像

### upload_container_image 上传容器镜像

必填 `workspace`、`local_file`、预期 `image_name` 和 `tag`; 项目及实际页面 URL
来自当前已确认会话. `local_file` 应为可信的 `.tar`/`.tar.gz` 容器镜像包,
当前页面基线限制不超过 2 GiB. 名称与 tag 来自包的元数据, 不在上传时任意改名.

1. 打开 `/container-registry/image`, 核实当前项目和工作空间, 定位 Upload Image.
   当前页面字段见 [page-and-dialogs.md](../image/image-details/page-and-dialogs.md).
2. 核实目标 workspace/name/tag 是否已存在. 当前 UI 声明同版本会覆盖;
   若已存在, 先说明准确目标与覆盖影响并获得明确覆盖授权, 否则不提交.
3. 选择并回读 Workspace, 使用当前 agent-browser 版本支持的文件上传动作选择
   本地包. 不把 VM 的 source_url/qcow2/os_category 参数填入这个表单.
4. 仅在上传文件被表单接受且 Upload enabled 后提交一次. 先等待上传结束,
   再进入同一工作空间的镜像详情, 核实预期名称和 tag、镜像地址及可取得的摘要/大小.
5. 名称刚出现、上传 toast 或旧 tag 仍存在均不能证明成功. 新版本必须可见且上传
   结束; 覆盖版本还需包摘要或可确认的版本更新时间证明本次变更生效.

最终成功才返回 `ok:true, terminal:true, submitted:true, status:'available'`;
上传中或身份未确认返回 `ok:null, terminal:false`. 错误需区分尚未提交与已提交失败.
超时先回读同一目标, 不重复覆盖; 恢复和清理均记录准确 workspace/name/tag.

## Result Examples 结果示例

等待上传或核实结果:

```json
{"ok":null,"terminal":false,"submitted":true,"resource":"container_image","action":"upload","name":"<workspace>/<name>:<tag>","status":"uploading","message":"wait for upload completion and verify the expected tag"}
```

核实实际产物后:

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"container_image","action":"upload","name":"<workspace>/<name>:<tag>","status":"available","message":"expected workspace, image and tag verified"}
```
