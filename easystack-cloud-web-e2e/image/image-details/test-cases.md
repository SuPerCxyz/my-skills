# Test Cases

## Scenario Status 场景状态

以下是基于现有页面知识的场景规范, 不是已运行的自动化结果. 使用 agent-browser,
先核实项目与精确资源身份, 复用对应 patterns 操作及 interactions helper.
`planned` 表示缺少已确认的可调用操作或字段, 先现场只读发现, 不编造入口/参数.
场景执行不要求先修改 skill; 缺少必要控件或权限时报告未验证及恢复点.
清理只针对本用例记录的实际资源, 按已有准确授权执行; 未授权时只列清单和依赖顺序.
任何提交未确认都先回读, 不因超时重复提交或自动删除.

> 来源:`easystack-cloud-web-e2e/image/image.md`,按原文标题边界拆分。

## Test Cases 测试用例

### TC-IMG001: 验证镜像管理页面加载

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 目标项目明确, 请求为容器镜像页面 |
| 操作 | 打开 /container-registry/image, 等待工作空间/列表加载 |
| 可观察断言与恢复 | URL与页面域正确且项目/工作空间可核实; VM意图转 patterns/image-ops.md, 不互换路由 |


### TC-IMG002: Upload Image 弹窗验证

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 已登录目标项目, 只验证弹窗 |
| 操作 | 打开Upload Image, 检查Workspace/本地tar上传/大小限制与覆盖提示, Cancel |
| 可观察断言与恢复 | 字段属于容器镜像, 弹窗关闭且未上传; 不期望source_url/qcow2/OS分类字段 |


### TC-IMG003: 按名称过滤镜像

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 当前工作空间与可精确核实的镜像名明确 |
| 操作 | 按真实名称筛选入口提交条件并等待结果, 结束清除筛选 |
| 可观察断言与恢复 | 结果名称精确且工作空间未变; 同名不同空间不能合并, 空列表不等于镜像不存在于其他空间 |


### TC-IMG004: 导航到镜像详情页

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例容器镜像workspace/name/tag已记录 |
| 操作 | 点击精确名称进入详情, 核对workspace参数及Image Tags |
| 可观察断言与恢复 | 名称/空间/tag/镜像地址一致; 旧tag或错误空间不成功, 缺产物保持未确认 |


### TC-IMG005: 编辑镜像描述

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例镜像身份与新描述明确, 编辑已授权 |
| 操作 | 在同一工作空间打开Edit, 仅修改Description并Confirm |
| 可观察断言与恢复 | 详情描述更新, 原name/workspace/tag不变; 错误不重复提交, 无需求不改Access Level |
