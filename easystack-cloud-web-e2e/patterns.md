# Patterns

本文件定义 EasyStack Cloud Web 的原子操作、观察结果及等待规则。通过 `agent-browser`
复用 `patterns/` 中的操作, 按实际页面和异步边界短段执行。

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
  "id": "<resource-uuid-or-null>",
  "status": "Available",
  "message": "volume created",
  "url": "https://example.local/ebs/volumes"
}
```

`id` 必须是资源的真实 ID（页面详情或后台查询获得）；未取得时返回 `null` 并说明原因，不能用名称代替。

失败时保持同一结构:

- `ok: false`
- `terminal: true`
- `status` 写入失败类别或最终观察状态
- `message` 写入关键失败原因
- `url` 写入最后可见页面地址

中间态使用 `ok: null`、`terminal: false`; `submitted` 只说明是否已经提交后台操作。
菜单打开、行选中、dialog 打开和 wizard 推进均不是成功结果。

## Wait And Retry 等待与重试

- 优先等待 URL、目标表格行、状态文本或弹窗消失。
- 固定时长等待(如 `agent-browser wait 1000`)只能作为动画或轮询间隔兜底。
- 轮询必须设置最大次数,并在失败返回结构化错误。
- 不通过固定截图序列判断成功。

## Resource Identity 资源身份

- 使用调用方给出的名称或 ID 精确匹配。核对项目、身份和当前状态后执行。
- 已有逻辑名映射时直接用确认过的实际名。无法确认对象时返回实际观察与缺失项。
- 遇到未确认创建或提交, 按 [执行规则](execution.md#core-rules-关键规则) 回读并记录。

## Historical Content 历史内容处理

资源知识库中保留页面字段和旧测试步骤说明,但当前执行时应以 `patterns/`
原子操作库为准。需要迁移历史步骤时,应新建或更新对应原子操作,而不是在
用例中复制页面交互逻辑。
