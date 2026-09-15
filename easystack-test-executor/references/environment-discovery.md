# Environment Discovery

## Goal 目标

本文件只负责访问门禁、当前用例上下文和动态服务发现, 不扩展成全面健康检查。
Runtime profile 的字段、缓存和刷新规则以
[environment-profile-cache.md](environment-profile-cache.md) 为唯一来源。

进入环境前先检查
`/tmp/easystack-test-executor-profiles/<environment-key>.yaml`。存在 profile 时读取
[environment-profile-cache.md](environment-profile-cache.md), 只对本次引用的资源 ID
执行 freshness check, 不重复 list 全部 Image、Flavor、Network 或 Volume Type。

## Access Gate 访问门禁

进入 EasyStack 环境前读取:

- 可按需复用现有环境访问文档或统一访问脚本。缺少这些辅助文件时, 使用用户提供且已授权
  的等价入口, 不猜测 SSH 或跳板参数。

当前环境提供统一 `env-access.sh` 时优先使用 `bash <path>/env-access.sh`, 不手写 SSH 或跳板链路。脚本不可用时使用
用户提供的授权入口; 未提供 `172.18.*` 的 jump host 参数时停止并请求该入口信息, 不猜测
控制节点链路。

先做最小只读验证:

```text
whoami
id -u
hostname
pwd
kubectl get nodes -o name
```

## Required Profile 必需 Profile

执行任何用例前至少确认:

1. 环境标识、目标 IP 或环境别名、IANA timezone 和当前 UTC offset。
2. OpenStack CLI 执行位置和认证加载方式。
3. Project、Region、Interface 和用例要求的 API microversion。
4. Kubernetes namespace、用例所需 Pod、Container 和相关节点。
5. Pod 发现使用的稳定 label, 以及 label 缺失时的名称模式。
6. 日志访问方式和权限。
7. 用例输入资源、配额和可用区。
8. `cleanup_policy`、允许的破坏性操作和结果目录。
9. 用例超时、轮询间隔和允许的重试次数。

密码、Token、应用凭据 secret 和私钥只记录为 `<REDACTED>`。

首次环境发现按 [environment-profile-cache.md](environment-profile-cache.md) 固化稳定
字段; 资源操作直接使用 [common-operations.md](common-operations.md)。

## Domain-Specific Discovery 领域发现

Nova 用例按需确认:

- Image、Flavor、Network、Security Group、Keypair 和 guest 登录方式。
- Availability Zone、compute host、aggregate、trait 和 Floating IP 容量。
- `nova-api`、`nova-scheduler`、`nova-conductor`、相关 `nova-compute`。

Cinder 用例按需确认:

- Volume Type、`volume_backend_name`、Availability Zone 和协议。
- Source Volume、Snapshot、Image、加密配置和 Barbican 可用性。
- Image-Volume Cache、multipath 或 NVMe native multipath 要求。
- `cinder-api`、`cinder-scheduler` 和全部相关 `cinder-volume`。

跨服务用例只添加实际参与的 Neutron、Glance、Barbican、libvirt、multipathd、
iscsid、NVMe 或后端服务。

## EasyStack Discovery Hints EasyStack 发现提示

常见 EasyStack 约定:

- OpenStack 服务位于 `openstack` namespace。
- OpenStack CLI 位于 `busybox-openstack` pod。
- 稳定标签通常为 `application=<service>` 和 `component=<role>`。
- API、scheduler、conductor 和 volume 服务可能有多个副本。
- `nova-compute` 通常按计算节点部署, 必须覆盖实际源和目标节点。

这些只是发现提示。必须以目标环境实时查询结果为准, 不硬编码 pod 名称或副本数。

## Output 输出

执行前生成:

```text
environment.yaml
environment-summary.md
service-inventory.json
```

首次采集或 profile 刷新时同时更新:

```text
/tmp/easystack-test-executor-profiles/<environment-key>.yaml
```

`environment-summary.md` 必须区分已确认事实、假设、非阻塞缺项和阻塞缺项。存在阻塞
缺项时标记 `RUN_BLOCKED`, 不进入资源操作。
