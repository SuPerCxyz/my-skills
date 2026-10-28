# Snapshot Bootable Volume

## Scenario Status 场景状态

以下是基于现有页面知识的场景规范, 不是已运行的自动化结果. 使用 agent-browser,
先核实项目与精确资源身份, 复用对应 patterns 操作及 interactions helper.
`planned` 表示缺少已确认的可调用操作或字段, 先现场只读发现, 不编造入口/参数.
场景执行不要求先修改 skill; 缺少必要控件或权限时报告未验证及恢复点.
清理只针对本用例记录的实际资源, 按已有准确授权执行; 未授权时只列清单和依赖顺序.
任何提交未确认都先回读, 不因超时重复提交或自动删除.

> 来源:`easystack-cloud-web-e2e/instance/instance-details/test-cases.md`,按测试用例边界拆分。

### TC-I005: 从云主机页面创建快照

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例实例与数据基线明确, I/O已静止或语义已确认 |
| 操作 | 调用 create_instance_snapshot, 记录实例/快照身份并等待 |
| 可观察断言与恢复 | 快照 Available 且 Snapshot Source 指向该实例; 未稳定不进入后续恢复步骤 |


### TC-I006: 从可启动卷创建云主机

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例可启动卷 UUID、大小/类型/启动属性明确 |
| 操作 | 现场核实 Bootable Volume 入口, 按 create_instance 向导选择该卷和所需网络/凭据 |
| 可观察断言与恢复 | 实例 Active 且实际根盘引用该卷 UUID, 业务可启动; 入口不支持时不改用近似镜像, 清理遵守保留卷策略 |
