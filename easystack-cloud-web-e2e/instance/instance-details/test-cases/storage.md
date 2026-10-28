# Storage

## Scenario Status 场景状态

以下是基于现有页面知识的场景规范, 不是已运行的自动化结果. 使用 agent-browser,
先核实项目与精确资源身份, 复用对应 patterns 操作及 interactions helper.
`planned` 表示缺少已确认的可调用操作或字段, 先现场只读发现, 不编造入口/参数.
场景执行不要求先修改 skill; 缺少必要控件或权限时报告未验证及恢复点.
清理只针对本用例记录的实际资源, 按已有准确授权执行; 未授权时只列清单和依赖顺序.
任何提交未确认都先回读, 不因超时重复提交或自动删除.

> 来源:`easystack-cloud-web-e2e/instance/instance-details/test-cases.md`,按测试用例边界拆分。

### TC-I004: 从云主机页面卸载云硬盘

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例 In use 数据盘及附件 UUID 明确, 文件系统已 sync/umount |
| 操作 | 按 detach_volume 选择确切卷和实例, 提交并轮询 |
| 可观察断言与恢复 | 卷 Available/No Attached, VM 内设备解绑符合用例; 超时保留绑定状态, 不强制再次卸载或误删系统盘 |
