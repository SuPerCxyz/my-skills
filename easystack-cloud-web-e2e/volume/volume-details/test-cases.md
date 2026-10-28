# Test Cases

## Scenario Status 场景状态

以下是基于现有页面知识的场景规范, 不是已运行的自动化结果. 使用 agent-browser,
先核实项目与精确资源身份, 复用对应 patterns 操作及 interactions helper.
`planned` 表示缺少已确认的可调用操作或字段, 先现场只读发现, 不编造入口/参数.
场景执行不要求先修改 skill; 缺少必要控件或权限时报告未验证及恢复点.
清理只针对本用例记录的实际资源, 按已有准确授权执行; 未授权时只列清单和依赖顺序.
任何提交未确认都先回读, 不因超时重复提交或自动删除.

> 来源:`easystack-cloud-web-e2e/volume/volume.md`,按原文标题边界拆分。

> 说明:本文件保留页面步骤和断言知识作为页面知识库。
> 新的可复用原子操作请优先参考 `../../patterns/volume-ops.md`。

## Test Cases 测试用例

### TC-001: 创建空白云硬盘

**前置条件:** 已登录 EasyStack Cloud 平台

**步骤:**
1. 导航到云硬盘页面
2. 点击 "Create Volume" 按钮
3. 填写 Volume Name
4. 选择 Volume Source 为 "Empty Volume"
5. 选择 Type 为 "hdd"
6. 设置 Size
7. 点击 "Create" 按钮
8. 验证创建成功

**代码:**

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 目标项目、卷类型/容量、唯一卷名明确 |
| 操作 | 调用 create_volume, 回读 Empty Volume/Type/Size 后提交一次 |
| 可观察断言与恢复 | 同项目/UUID 卷 Available且容量/类型/来源正确; 未确认时遵守有限重试并记录可能已创建对象 |


### TC-002: 创建从镜像来源的云硬盘

**步骤:**
1. 导航到云硬盘页面
2. 点击 "Create Volume" 按钮
3. 填写 Volume Name
4. 选择 Volume Source 为 "Image"
5. 选择具体的镜像
6. 设置 Size
7. 点击 "Create" 按钮

**代码:**

| 项目 | 场景要求 |
|---|---|
| 状态 | `planned`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例可信可用 VM 镜像 UUID、目标卷大小/类型明确 |
| 操作 | 核实当前 Create Volume 支持 Image 来源, 选择准确镜像后提交 |
| 可观察断言与恢复 | 目标卷 Available, 来源为该镜像 UUID且容量不小于镜像要求; 不进入容器仓库选择镜像 |


### TC-003: 创建从快照来源的云硬盘

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 本用例 Available 快照 UUID和唯一新卷名明确 |
| 操作 | 调用 create_volume_from_snapshot, 回读继承大小/类型和 Copy Full Data 选项 |
| 可观察断言与恢复 | 新卷 Available且快照来源/属性正确; 用例要求时挂载验证基线数据, 清理不删除源快照 |


### TC-004: 创建云硬盘 - 验证表单校验

| 项目 | 场景要求 |
|---|---|
| 状态 | `ready-template`, 当前未执行真实 UI 验证 |
| 前置条件 | 仅验证表单, 无有效提交授权 |
| 操作 | 打开创建表单, 分别检查缺名称/缺类型及当前页面标明的容量边界, 每次恢复输入 |
| 可观察断言与恢复 | 必填/边界错误有明确提示且 Create不可提交, 恢复合法值后校验消失; 结束Cancel并确认未生成资源 |
