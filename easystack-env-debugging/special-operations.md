# Special Operations

本文件统一收纳会影响运行中 workload 或需要额外授权的组件级特殊操作说明。
普通组件部署、pod 和启动方式仍放在 `openstack/`, `ceph/`, `k8s/` 目录下。

## Scope 使用边界

- 默认排查仍只做查看操作。
- 涉及维护、迁移、疏散、回滚、重启、删除、写数据库、修改 ConfigMap 或进入管理 shell 的动作, 必须先获得用户明确授权。
- 每个组件新增特殊操作时, 在本文件增加对应小节, 不要为每个组件再拆散独立 maintenance 文件。

<a id="nova-maintenance-pod"></a>

## Nova Maintenance Pod 管理入口

Advanced Nova operations (cell management, host maintenance, evacuation, migration debugging)
can affect running workloads. Do not run maintenance commands unless the user explicitly
authorizes the exact operation.

只读查看时, 先定位 maintenance pod:

```bash
kubectl get pods -n openstack | grep nova-maintenance
kubectl describe pod -n openstack nova-maintenance-<HASH>-<ID>
```

该 pod 可以访问 nova 管理命令和 cell 数据库工具。进入交互式 shell 或执行管理命令
不属于默认只读动作。
