# Environment Profile Cache

## Goal 目标

环境首次用于测试时采集一次 Compute、Storage、Network 创建资源所需的稳定信息,
保存到 `/tmp/easystack-test-executor-profiles/<environment-key>.yaml`。后续测试
优先复用 profile, 不重复执行完整 resource list 和 CLI help 查询。
本文件是 profile schema、freshness check 和刷新策略的唯一来源。

固定使用 `/tmp/easystack-test-executor-profiles` 避免依赖某个用户的 home 目录。
不得在 skill 目录、源码仓库、`/home/<user>/tmp` 或可分发压缩包内创建环境 profile。
目录权限必须为 `0700` 或更严格, 文件权限必须为 `0600` 或更严格。保存后运行:

```bash
python3 scripts/compile-profile.py --input <CAPTURED_PROFILE>
python3 scripts/validate-profile.py \
  --profile /tmp/easystack-test-executor-profiles/<environment-key>.yaml
```

`python3 scripts/compile-profile.py` 校验必需字段、明文 Secret、fingerprint 和 timestamp, 再根据稳定
environment key 原子写入固定 `/tmp` store。不要手工选择文件名。

## First Capture 首次采集

至少记录:

### Access And Auth 访问和认证

- Environment name、target、control node、namespace 和 CLI location。
- Auth URL、Project ID、User ID、Region 和 API version。
- 只记录认证方式, Password、Token 和 Secret 一律写为 `<REDACTED>`。

### Compute 计算

- 可用 AZ、Hypervisor hostname。
- 常用 Image ID、name、status 和 format。
- 常用 Flavor ID、name、vCPU、RAM 和 disk。
- Project Security Group ID。
- Keypair name 或明确记录不存在。

### Storage 存储

- Volume AZ、Volume Type ID/name 和 `volume_backend_name`。
- Cinder backend service、protocol 和 encryption capability。
- 常用 Source Volume、Image 或 Snapshot 只在它们是固定 fixture 时记录。

### Network 网络

- Tenant Network ID/name、Subnet ID/CIDR。
- External Network ID/name、Floating IP pool。
- Router、Port 或固定 Network fixture 只在测试长期复用时记录。

### Command Compatibility 命令兼容

- 记录 `openstack`、兼容 client 的 version 和 command help 验证结果。
- 记录 Image、Security Group、Floating IP 和 boot-from-volume capability。
- Server 只记录 force delete strategy 和 capability, 普通 delete 不能作为 fallback。
- 通用命令只维护在 [common-operations.md](common-operations.md), 不复制到 profile。
- 只有环境特有的参数差异或不支持项才进入 profile。

### Fingerprint 环境指纹

profile version 2 必须记录 Kubernetes cluster UID、OpenStack release、
openstackclient version 和 storage/network backend fingerprint。environment key 由
target、Region、Project、namespace 和 cluster UID 派生, 不使用 IP 或 home path 作为
唯一身份。指纹变化时定向重建受影响部分。

## Reuse Flow 复用流程

后续测试按以下顺序:

1. 读取对应 profile。
2. 先运行 `python3 scripts/validate-profile.py`, 再使用精确 `show <ID>` 对本次会引用的 Image、Flavor、Network、Subnet、
   Security Group 和 Volume Type 做 freshness check。
3. 全部引用仍有效时直接执行, 不重新 list 全部资源。
4. 单个引用失效时只更新该类别。
5. Auth、endpoint、CLI location 或多个核心引用同时失效时重建 profile。

freshness check 只验证存在性、可见性和本次需要的关键状态, 不做全面健康检查。

## Dynamic Information 动态信息

以下内容不得依赖缓存, 每个相关用例前后实时发现:

- Pod name、Pod UID、container ID、restart count 和 node。
- `cinder-volume`、`nova-compute` 等 worker 实例集合。
- 当前 source/destination host、backend 和 Request ID。
- 临时资源状态、quota 余量和故障注入状态。

## Refresh Triggers 刷新触发

出现以下任一情况时刷新相关 profile:

- 用户明确要求刷新。
- 目标 OpenStack release、部署或 backend 已升级。
- 目标环境本地时区或 UTC offset 已变化。
- 直接 `show` 返回 not found、forbidden 或字段不兼容。
- Image、Flavor、Network、Volume Type 或 Security Group 被替换。
- 连续两个测试因相同缓存信息失败。

不得因为一次业务用例失败就重建全部 profile。先区分资源引用失效和产品行为失败。

## Profile Maintenance Profile 维护

- 更新 `captured_at_local`、`last_verified_at_local`、IANA timezone、当前 UTC offset
  和 `source_environment`。时间值使用带 offset 的 RFC3339。
- 变更资源 ID 时保留简短原因, 不保存旧 Token 或凭据。
- Profile 仅属于本地 runtime data, 不得进入 skill、源码仓库或分发包。
- Profile store 目录权限建议为 `0700`, profile 文件权限建议为 `0600`。
- 环境特定 profile 不能当作其它环境的默认事实。
