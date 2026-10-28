# Patterns

本文件只定义 EasyStack Cloud Web E2E 测试的编排规则和结果约定。
实际浏览器操作必须复用 `patterns/` 下的 `agent-browser` 原子操作,
不得在本文件中维护独立的其他浏览器自动化框架模板。

## Execution Constraints 执行硬约束

- 所有 UI 操作统一通过 `agent-browser` 执行。
- 缺少 `agent-browser` 时先报告安装命令和影响, 等待用户确认; 未确认或安装失败时
  停止真实 UI 测试。
- 执行前加载 `agent-browser skills get core`。
- 同一稳定页面内的相关动作优先合并为 `agent-browser batch` 或短 `eval --stdin`;
  页面切换、DOM 重建和长等待使用新的短段并回读, 不强制一次 eval 跨完整向导.
- 不逐步依赖 snapshot 驱动操作;snapshot 只用于必要诊断。
- 不新增其他浏览器自动化模板或非 `agent-browser` 示例。
- 历史测试片段不作为当前执行入口。
- 长耗时用例需要后台任务执行时:
  - 不在 skill 中固定模型名称或推理等级。
  - 按当前会话 `AGENTS.md`、用户要求和平台可用能力选择。

这些约束的目标是减少跨步骤上下文、截图和 snapshot 消耗,避免长用例执行时
token 膨胀。

## Orchestration Flow 推荐编排流程

1. 检查并加载 `agent-browser`。
2. 读取 `/tmp/easystack-env.json`,只校验 `platform.*` 和静态默认资源字段。
3. 执行 `patterns/login.md`,准备可复用会话。
4. 按资源域选择原子操作文档:
   - 实例:`patterns/instance-ops.md`
   - 云硬盘:`patterns/volume-ops.md`
   - VM/容器镜像:`patterns/image-ops.md`
   - 网络:`patterns/network-ops.md`
5. 将一个测试用例内的同类页面操作尽量组合为少量批量调用。
6. 每个原子操作返回结构化对象后,再决定是否继续下一步。
7. 将新建资源、执行结果和截图路径写入测试报告;不得写回环境 JSON。
8. 长流程用例之间主动压缩上下文;如果当前客户端支持 `/compact`,优先执行。
9. 后台任务只执行指定用例并返回报告;发现可复用操作时记录
   `skill_improvements`,由主会话统一沉淀到操作库。

## Case Structure 用例结构

每个测试用例建议包含:

- 用例编号和名称
- 前置条件
- 输入参数来源
- 使用的原子操作
- 成功判定
- 失败处理
- 资源清理策略
- 结果报告字段

示例:

```md
### TC-VOL001: 创建空白云硬盘

- 前置条件:平台可登录,目标卷类型存在
- 输入参数:`name`、`size`、`resources.volume_type`
- 原子操作:`create_volume`
- 成功判定:返回 `ok=true` 且 `status=Available`
- 清理策略:用例结束后按需要调用 `delete_volume`
- 报告字段:`resources_created[].name`
```

## Operation Contract 原子操作调用约定

所有原子操作必须遵循统一返回结构:

```json
{
  "ok": true,
  "terminal": true,
  "submitted": true,
  "resource": "volume",
  "action": "create",
  "name": "vol-01",
  "status": "Available",
  "message": "volume created",
  "url": "https://example.local/ebs/volumes"
}
```

失败时保持同一结构:

- `ok: false`
- `terminal: true`
- `status` 写入失败类别或最终观察状态
- `message` 写入关键失败原因
- `url` 写入最后可见页面地址

中间态使用 `ok: null`、`terminal: false`; `submitted` 只说明是否已经提交后台操作。
菜单打开、行选中、dialog 打开和 wizard 推进均不是成功结果。

## Screenshots And Reports 截图与报告

- 截图只在关键状态确认、失败诊断或用户明确要求时保存。
- 截图目录:`/tmp/easystack-screenshots/<用例名>/`
- 全局报告:`/tmp/easystack-screenshots/test_report.json`
- 报告至少记录:用例名、开始时间、结束时间、状态、错误信息、截图路径。

## Wait And Retry 等待与重试

- 优先等待 URL、目标表格行、状态文本或弹窗消失。
- 固定时长等待(如 `agent-browser wait 1000`)只能作为动画或轮询间隔兜底。
- 轮询必须设置最大次数,并在失败返回结构化错误。
- 不通过固定截图序列判断成功。

## Resource Naming 资源命名

- 每个用例创建的资源名称必须唯一。
- 每个用例必须创建新的测试资源,不复用之前用例创建的实例、云硬盘、快照或浮动 IP。
- 推荐格式:`<case-id>-<resource-type>-<timestamp-or-runid>`。
- `/tmp/easystack-env.json` 不保存历史测试资源;只保存静态环境和默认参数。
- 新建资源只写入本次测试报告,例如 `resources_created[]`。
- 用户提供的名称必须原样使用,不替换为平台上的近似名称。
- 如果页面中找不到精确匹配项,应返回失败结果并提示确认。
- 用例前置条件中的逻辑资源名,例如 `vm1`、`volume1`、`volume-snap`,
  不表示可以复用环境已有资源;默认必须在本用例内新建并映射为唯一实际名。
- 报告中同时记录逻辑名和实际名,后续步骤只能引用本次映射,不能从页面列表
  选择同名、近似名或历史测试资源。
- 创建提交后未在列表中确认成功的资源,先回读页面和后台资源状态。仍未确认时记为
  `creation_unconfirmed`; 最多使用新的 run id 重试 1 次,不能沿用未确认资源名。第二次
  仍未确认时停止创建并报告可能已创建的资源,不自动清理。

## Historical Content 历史内容处理

资源知识库中保留页面字段和旧测试步骤说明,但当前执行时应以 `patterns/`
原子操作库为准。需要迁移历史步骤时,应新建或更新对应原子操作,而不是在
用例中复制页面交互逻辑。
