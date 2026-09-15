# Alcubierre Volume Unmap

## Trigger And Scope 触发与边界

用户给出明确环境、一个或多个 Cinder volume UUID, 并要求“解挂高性能盘”、
“解挂 Alcubierre 盘”或“解除 mapping”时使用本流程。UUID 数量不设固定上限,
但必须先去重并完整预检。

仅要求查看、分析状态或表示“可能需要解挂”时只执行预检。用户已表达执行意图时,
预检后仍要展示对象、协议、客户端标识、影响和回滚限制, 获得一次批量确认后才能
调用 disconnection API。确认仅覆盖当次展示的 UUID 集合。

本流程只解除 Alcubierre mapping。不要修改 Cinder 状态, 不要删除云硬盘, 不要自动
修改 Alcubierre `volume` 或 `volctrl`。

## Access Routing 访问路由

默认通过 `bash scripts/env-access.sh` 进入环境。用户指定普通跳板机时增加
`--via <SSH_TARGET>`。批量操作统一通过 `bash scripts/run-alcubierre-unmap.sh` 发送固定脚本:

```bash
bash scripts/run-alcubierre-unmap.sh \
  --via eswork \
  --target 192.168.3.3 \
  -- preflight \
  <VOLUME_UUID_1> <VOLUME_UUID_2>
```

普通跳板机后的 direct、jump18 和 JumpServer 组合见 [access.md](access.md)。
runner 内部仍调用统一访问脚本, 不在远端落盘。不要手写多层 SSH 或把完整批量逻辑
拼进 `--cmd`。

## Phase 1: Read-Only Preflight 只读预检

先校验 UUID。接受大小写十六进制, 输出和查询时保留用户输入:

```text
^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[1-5][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$
```

使用 runner 一次预检完整 UUID 集合。脚本自动校验并去重:

```bash
bash scripts/run-alcubierre-unmap.sh \
  <ENV_ACCESS_ARGS> \
  -- preflight <VOLUME_UUID...>
```

选择 `Running`、全部容器 Ready 且不是 Terminating 的 Manul pod。不要使用
`.items[0]`, 因为 Kubernetes 中 Terminating pod 的底层 phase 仍可能是 Running:

```bash
MANUL_POD=$(kubectl -n alcubierre get pod \
  -l 'application=alcubierre,component=manul' \
  --no-headers |
  awk '$3 == "Running" {
    split($2, ready, "/")
    if (ready[1] == ready[2]) {
      print $1
      exit
    }
  }')

test -n "$MANUL_POD"
kubectl -n alcubierre get pod "$MANUL_POD" -o wide
```

每个批次只读取一次完整 volume 清单, 脚本在内存中按已校验 UUID 过滤, 不把无关
volume 输出到报告:

```bash
VOLUME_SNAPSHOT=$(kubectl exec -n alcubierre "$MANUL_POD" -c manul -- \
  kvctl list volume --format object)
```

必须完成全部只读预检后再进行一次批量确认, 不要边查询边解挂。

记录 `id='alcub_...'`、`state`、`task_state`、`error_message` 和 `protocol`。

iSCSI 查询:

```bash
kubectl exec -n alcubierre "$MANUL_POD" -c manul -- \
  kvctl list volumemapping --where "name=$DISK_ID"
```

NVMe-oF 查询:

```bash
kubectl exec -n alcubierre "$MANUL_POD" -c manul -- \
  kvctl list nvmemapping --where "volume_id=$DISK_ID"
```

按客户端标识去重。iSCSI 使用 `initiator`, NVMe-oF 使用 `hostnqn`。同一客户端标识
在 node-2、node-3 等多个存储节点出现属于一个待解挂连接, disconnection API 只调用
一次。多个不同客户端标识可能代表 multiattach, 阻止自动操作并单独向用户确认。
固定脚本在一次 Manul pod `kubectl exec` 中循环全部目标 `DISK_ID`, 用边界标记归组
每盘结果; 不为每个 UUID 重复建立 pod exec, 也不扫描无关 mapping。

## Preflight Classification 预检分类

每个 UUID 只能进入以下一种结果:

1. `READY`: 找到唯一 volume, 协议受支持, volume 为 `linked`, 且存在一个
   唯一客户端标识。
2. `NOOP`: mapping 为空, 不论 volume 当前显示 `linked` 还是 `unlinked`。
3. `BLOCKED_NOT_FOUND`: 找不到 UUID 或匹配到多个 volume。
4. `BLOCKED_PROTOCOL`: 协议不是 `ISCSI` 或 `NVMEOF`。
5. `BLOCKED_MULTI_CLIENT`: 存在多个不同 initiator 或 hostnqn。
6. `BLOCKED_STATE`: mapping 存在, 但 volume 不是 `linked` 或状态无法解释。

任一 UUID 为 `BLOCKED_*` 时不要开始批量写操作。先报告全部预检结果并让用户处理
阻塞对象或缩小本次 UUID 集合。

## Confirmation Gate 确认门禁

确认信息必须包含:

1. 目标环境和实际访问链路。
2. 去重后的 UUID 数量。
3. 每个 UUID 的 `DISK_ID`、协议、状态、mapping 数量和唯一客户端标识。
4. 解除 mapping 会中断残留存储连接; 若仍有隐藏 I/O, 业务会受影响。
5. 操作没有简单原地回滚; 恢复连接需要重新挂载云硬盘。
6. 执行后只验证存储侧, 不自动删除 Cinder 云硬盘。

用户回复明确的“确认”、“执行”或等价指令后才能执行。新增、删除或替换 UUID 后,
原确认失效, 必须重新预检和确认。

## Phase 2: Execute 执行

确认后使用同一 UUID 集合执行:

```bash
bash scripts/run-alcubierre-unmap.sh \
  <ENV_ACCESS_ARGS> \
  -- execute <VOLUME_UUID...>
```

runner 在一次 SSH 会话内按预检清单顺序逐盘执行。每个盘执行前重新查询 mapping:

1. mapping 为空时输出 `SUCCESS_NOOP` 并跳过, 不发送 POST。
2. mapping 存在时根据批次初始 volume 和 mapping 快照校验唯一客户端和状态。
3. API 保持逐盘串行, API 失败时停止后续 UUID。
4. 批次中断后原样重跑命令; 已完成的盘因 mapping 为空自动跳过, 从未完成盘继续。
5. 全部 API 完成后批量刷新一次 mapping, 再统一刷新 volume 并验证。

iSCSI 每个唯一 initiator 调用一次:

```bash
curl --fail-with-body -sS \
  -X POST \
  "http://alcubierre-manul.alcubierre.svc.cluster.local:8192/v2/volumes/${DISK_ID}/disconnections" \
  -H 'Accept: */*' \
  -H 'Content-Type: application/json' \
  -d "{
    \"disconnection\": {
      \"iqn\": \"${IQN}\"
    }
  }"
```

NVMe-oF 每个唯一 hostnqn 调用一次:

```bash
curl --fail-with-body -sS \
  -X POST \
  "http://alcubierre-manul.alcubierre.svc.cluster.local:8192/v2/volumes/${DISK_ID}/nvme_disconnections" \
  -H 'Accept: */*' \
  -H 'Content-Type: application/json' \
  -d "{
    \"nvme_disconnection\": {
      \"hostnqn\": \"${HOSTNQN}\"
    }
  }"
```

disconnection 是写操作, 不得使用自动 timeout ladder 重试。超时意味着结果未知,
必须先查询 mapping 判断是否已经成功, 不能盲目再次 POST。

## Fail-Fast And Verification 失败与验证

全部 POST 完成后, 在一次 Manul pod exec 中批量重复目标 mapping 查询, 再扫描
一次 volume 清单并执行最终全量验证。批次成功标准:

1. 目标 volume 的 mapping 查询为空。
2. volume `state` 为 `unlinked`。
3. `error_message` 为空。

`task_state=cache_delete_waiting` 可以表示异步缓存清理仍在进行。短时复查并如实报告,
但不要因为等待而修改 `volume` 或 `volctrl`。如果 mapping 已清空且 volume 为
`unlinked`, 存储侧解除 mapping 已完成。

执行前已经没有 mapping 的盘不发送 POST, 即使 volume 仍显示 `linked` 也按
`SUCCESS_NOOP` 跳过。最终全量 `verify` 以 mapping 为空为完成标准, 同时如实报告
volume 和 task state, 不强制修正状态。

任一 API 写操作返回非零或超时时:

1. 停止处理后续 UUID。
2. 当前 UUID 结果视为未知, 原样重跑时先由初始 mapping 快照判断是否已成功。
3. 汇总已经完成、失败和未处理对象。
4. 不回滚已经成功解挂的前序对象, 除非用户另行授权重新挂载。

API 返回成功但 mapping 未清空, 或 volume 状态异常时, 在批次末统一报告失败。
此时其它 API 可能已经执行, 不回滚已经成功的对象。

## Batch Report 批量报告

完成后逐盘报告:

```text
VOLUME_ID=<Cinder UUID>
DISK_ID=<Alcubierre ID>
PROTOCOL=<ISCSI|NVMEOF>
RESULT=<SUCCESS|SUCCESS_NOOP|FAILED|UNKNOWN|NOT_PROCESSED>
MAPPING=<EMPTY|PRESENT|UNKNOWN>
STATE=<unlinked|other>
TASK_STATE=<value>
```

明确说明是否执行了 Cinder 删除。本流程正常结果应为“未执行, 由用户手动删除”。
同时报告 `INITIAL_VOLUME`、`INITIAL_MAPPING`、`API_TOTAL`、`FINAL_MAPPING`、
`FINAL_VOLUME`、`TOTAL` 和每盘 `API` 的秒级耗时。

## Execution Feedback 执行反馈

如果遇到 Terminating pod 被误选、客户端标识解析不稳定、API 超时、mapping 与
volume 状态不一致、访问链路或认证 profile 失效, 最终报告触发位置、实际影响、
临时处理和规则改进建议。凭据必须脱敏。
