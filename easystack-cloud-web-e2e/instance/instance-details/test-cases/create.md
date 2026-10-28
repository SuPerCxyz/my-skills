# Create

## Scenario Status 场景状态

以下是基于现有页面知识的场景规范, 不是已运行的自动化结果. 使用 agent-browser,
先核实项目与精确资源身份, 复用对应 patterns 操作及 interactions helper.
`planned` 表示缺少已确认的可调用操作或字段, 先现场只读发现, 不编造入口/参数.
场景执行不要求先修改 skill; 缺少必要控件或权限时报告未验证及恢复点.
清理只针对本用例记录的实际资源, 按已有准确授权执行; 未授权时只列清单和依赖顺序.
任何提交未确认都先回读, 不因超时重复提交或自动删除.

> 来源:`easystack-cloud-web-e2e/instance/instance-details/test-cases.md`,按测试用例边界拆分。

## Instance Test Cases 实例测试用例

> 来源:`easystack-cloud-web-e2e/instance/instance.md`,按原文标题边界拆分。

## Test Cases 测试用例

### TC-I001: 创建云主机(当前为未验证模板)

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 当前项目配额、镜像/规格/网络明确, 名称唯一 |
| 操作 | 调用 create_instance, 连续完成向导并逐段回读 Root Disk/网络/凭据和最终摘要 |
| 可观察断言与恢复 | 实例 UUID/项目一致且 Active, 规格/根盘/网络与输入一致; 错误或未确认时保留检查点 |


### TC-I002: 创建带数据盘的云主机

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 同上, 数据盘类型/大小/删除策略明确 |
| 操作 | 在基础配置 Data Disk 添加所需盘, 回读最终摘要后提交 |
| 可观察断言与恢复 | 实例 Active, Storage 中数据盘数量/大小/类型/删除策略一致; 不猜测自动生成盘名, 记录实际 UUID 供清理 |


### TC-I003: 挂载云硬盘到云主机

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例实例和 Available 卷, 项目/UUID 均已确认 |
| 操作 | 调用 attach_volume, 回读弹窗实例选择并提交一次 |
| 可观察断言与恢复 | 卷 In use 且 attachment 指向本次实例 UUID; 用例需要时在 VM 内验证设备出现, 清理先 sync/umount 后卸载 |
