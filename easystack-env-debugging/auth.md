# OpenStack Authentication

Use this file after environment access is established and the task requires OpenStack CLI authentication, busybox pod usage, or credential checks. Do not use it as the first access path.
For failure root-cause requests, read service logs first; use OpenStack CLI only
after logs require extra resource context or the user asks for resource status.

## 重要:执行 OpenStack 命令前必须先 source 认证

**busybox pod 没有预设的 OS_ 环境变量,所有 openstack 命令必须在 source 之后执行。**

```bash
# 推荐:一次性只读命令
kubectl exec -n openstack services/busybox -- bash -c 'source /openrc && openstack volume list --all'
kubectl exec -n openstack services/busybox -- bash -c 'source /openrc && openstack server list --all'

# 错误方式(会报错:missing auth-url / missing OS_USERNAME)
kubectl exec -n openstack services/busybox -- openstack volume list
kubectl exec -n openstack services/busybox -- cinder show <volume-id>
```

`/openrc` 下查询资源列表时默认可能只看到当前项目。调查用户资源异常时,
list 类命令优先带跨项目参数, 例如 `cinder list --all`; 其他资源列表命令也按
对应 CLI 的跨项目参数处理。

避免默认进入交互式 busybox shell。交互式 shell 容易执行到有影响操作,
只有在用户明确要求时再进入。

## User Identities 用户身份

busybox 内可以通过不同认证方式切换身份:

| 用户 | 认证方式 | 用途 |
|------|---------|------|
| `drone` (service 项目用户) | `source /openrc` | 日常只读 openstack 查询 |
| `admin` | 手动 export 环境变量 | 需要管理员权限的只读查询 |

```bash
# 切到 drone 用户
source /openrc

# 切到 admin 用户(手动 export)
export OS_IDENTITY_API_VERSION=3
export OS_USERNAME=admin
export OS_PASSWORD='<PASSWORD>'
export OS_AUTH_URL='http://keystone-api.openstack.svc.cluster.local/v3'
...
```

## Drone User (/openrc) 日常认证

日常排障用 `source /openrc` 就够,admin 权限更大但很少需要。
默认只执行 `list`、`show`、`get` 等查询命令。

`/openrc` 包含 `drone` 用户凭据(keystone v2.0 auth):

```bash
source /openrc
# Now you can run:
openstack volume list --all
openstack server list --all
cinder list --all
nova list --all
```

`openstack endpoint list` may fail with `Could not find requested endpoint in
Service Catalog` under `/openrc`. Do not use it as the default busybox
authentication check; prefer `server list` or `volume list`.

## Admin Credentials 管理员认证

Admin credentials have broader permissions. Use them only for explicit read-only
queries that cannot be completed with `/openrc`. Any create/update/delete action
still requires explicit user authorization.
