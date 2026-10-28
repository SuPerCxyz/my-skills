# Pod Patterns

选择 pod、container、label 或 controller 做只读检查时阅读本文件。它用于避免
`exec` 和 `logs` 时选错容器。

## Multi-Container Pods 多容器 Pod

Always check containers before `exec` or `logs`:

```bash
kubectl get pod -n openstack <pod-name> -o jsonpath='{.spec.containers[*].name}'
```

Most service pods follow a pattern of **init container + business container**, some may have multiple business containers. Always specify `-c <container-name>` when exec'ing into non-default containers.

示例:
- `mariadb-0` → `mariadb` (单容器, 不需要 `-c`)
- `fluentd-0` → `httpd` (默认) + `fluentd`
- `cinder-api-*` → `cinder-api` (默认) + `init` (init container)
- `cinder-golem-*` → `golem` (默认) + `init`

不确定时, 显式使用 `-c <container-name>`。

## Exec by Pod Name, Not Service Label 按 Pod 名称执行

服务 pod 避免使用 `kubectl exec -n <ns> -l service=<name>`。带 init container 的
pod 可能打印 `Defaulted container ...`, 且基于 label 的 `exec` 在不同 kubectl
版本和 pod 布局中不够稳定。

优先先确认 label, 再解析具体 pod 名称, 最后用具体 pod 名称执行 `exec`:

```bash
kubectl get pods -n <ns> --show-labels | grep <name>
pod=$(kubectl get pods -n <ns> -l service=<name> -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n <ns> "$pod" -c <container-name> -- <read-only-command>
```

只有确认 pod 确实存在对应 label 后, 才使用 `service=<name>` selector。如果使用
`-l 'service in (a,b,c)'` 这类集合 selector, 先验证目标 kubectl 版本支持;
否则拆成 `-l service=a`、`-l service=b`、`-l service=c` 分别查询。

## Multi-Replica Pods (API Services) 多副本 Pod

API 服务通常运行 3 个副本。修改 configmap 会同时影响所有副本。

```bash
# Quick way: grep the first running pod
kubectl get pods -n openstack | grep <service>-api | head -1

# Or by label selector (component name varies):
# cinder: component=api, nova: component=os-api, glance: component=api
kubectl get pods -n openstack --selector=application=<service>,component=api --field-selector=status.phase=Running
```

重启 deployment 时, 所有 pod 会自动重建。

## StatefulSet vs Deployment vs DaemonSet 控制器差异

| Type | 示例 | Pod 名称 | 重启行为 |
|------|----------|-----------|-----------------|
| **Deployment** | `cinder-api-*`, `nova-conductor-*` | 随机后缀(如 `cinder-api-6b58d8ddd6-jncth`) | 新 pod 使用新名称 |
| **StatefulSet** | `glance-api-0`, `mariadb-0` | 编号后缀(`-0`, `-1`, `-2`) | 名称不变, 有持久卷 |
| **DaemonSet** | `ovn-controller-*`, `nova-compute-*` | 每个匹配节点一个 | Pod 替换可改变名称和 UID, 容器重启可保留 Pod |

区分容器重启、Pod 替换和副本并存。名称相同不证明同一 Pod, 名称改变也不单独证明
节点重启; 结合 Pod UID、restart count、creation timestamp 与事件核对。
