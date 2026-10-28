# Cleanup Resources

本文件定义测试结束后的清理建议生成规则。清理动作会删除资源,必须先向用户
说明并获得明确确认;未确认时只写报告,不执行 UI 删除。

## Scope 适用范围

- 测试用例新建的云主机、云硬盘、云硬盘快照、浮动 IP、网络等资源
- 报告中标记为 `cleanup: recommended` 的资源
- 用户明确要求清理某个 run id 或用例资源

## Hard Rules 硬规则

- 不从 `/tmp/easystack-env.json` 的 `test_resources` 读取历史资源作为清理目标。
- 只清理本次报告中 `logical_name -> actual_name` 映射到的实际资源。
- 清理前必须输出资源清单、影响范围和建议顺序,并等待用户明确确认。
- 用户未确认时,不执行删除、解绑、释放、关机等动作。
- 所有清理操作仍必须通过 EasyStack Web UI 和 `agent-browser` 执行。

## Cleanup Order 建议清理顺序

1. VM 内停止 I/O 并卸载文件系统:例如 `sync; umount <mountpoint>`。
2. UI 卸载数据盘:调用 `detach_volume`。
3. UI 删除数据盘:调用 `delete_volume`。
4. UI 解绑浮动 IP:调用 `disassociate_floating_ip`。
5. UI 释放浮动 IP:调用 `release_floating_ip`。
6. UI 删除云主机:调用 `delete_instance`。
7. 按依赖顺序删除快照、镜像、网络等其他资源。

## Result Contract 返回值约定

未确认清理时:

```json
{
  "ok": null,
  "terminal": false,
  "submitted": false,
  "action": "cleanup_plan",
  "status": "confirmation_required",
  "resources": [
    {"type": "instance", "name": "<instance-name>", "impact": "will delete VM and root disk according to policy"}
  ],
  "message": "cleanup requires user confirmation"
}
```

确认并执行后,每个原子清理操作必须返回自己的结构化结果,并写入报告:

```json
{
  "ok": true,
  "terminal": true,
  "submitted": true,
  "resource": "floating_ip",
  "action": "release",
  "name": "<floating-ip>",
  "status": "released",
  "message": "floating ip released",
  "url": "<current-url>"
}
```

## Report Fields 报告字段

- `cleanup_plan[]`: 建议清理的资源和顺序
- `cleanup_confirmed`: 用户是否确认
- `cleanup_results[]`: 已执行清理操作的结构化结果
- `cleanup_remaining[]`: 未清理资源及原因
