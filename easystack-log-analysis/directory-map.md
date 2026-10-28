# Log Directory Structure Map

Use this file to map an extracted `ecs.*` directory to service domains before searching. It does not define root-cause logic; use [cross-domain-analysis.md](cross-domain-analysis.md) and [search-patterns.md](search-patterns.md) after choosing the relevant domains.

解压脚本同时生成 `components/` 跨平台普通文件视图。它沿用下述组件相对路径, 但去掉
`ecs.node-*` 中间层。例如原始 `ecs.node-1.../openstack/cinder/cinder-volume...log`
复制为 `components/openstack/cinder/cinder-volume...log`。同名文件保留较大者; 调查
报告仍引用原始 `ecs.*` 路径, 以便审计具体来源。

## Directory Layout 目录布局

```
ecs.<host>.<date>.<N>/
├── alcubierre/              # Alcubierre distributed storage
│   ├── alcubierre-node.*.log          # Node agent (iSCSI connection management)
│   ├── alcubierre-manager.*.log       # Manager service
│   ├── alcubierre-target.*.log        # iSCSI target
│   ├── alcubierre-target-init.*.log   # Target init
│   ├── alcubierre-exporter.*.log      # Metrics exporter
│   └── quorum-adjust.*.log           # Quorum adjustments
│
├── ceph/                    # Ceph storage cluster
│   ├── host.ceph-mon.*.log           # Monitor
│   ├── host.ceph-mgr.*.log           # Manager
│   ├── host.ceph-osd.*.log           # OSDs
│   ├── host.ceph-volume.*.log        # Volume management
│   ├── host.ceph.*.log               # Combined ceph log
│   ├── host.post_start.*.log         # Post-start scripts
│   └── kube.*.log                    # Kubernetes-managed ceph pods
│
├── ceph-k8s/                # Ceph OSD disk operations
│   ├── osd_disk_prepare_*.log        # OSD disk preparation
│   └── pci-*.log                     # PCI device logs
│
├── cloud-products/          # ** EasyStack 云产品类服务(非核心 OpenStack)**
│   ├── apisix/apisix.*.log           # API 网关(南北向公网入口、路由、限流)
│   ├── iam/                          # EasyStack IAM(账号 / 子用户 / 鉴权)
│   │   ├── iam-dashboard.*.log
│   │   └── init.*.log
│   ├── ironic/                       # ** 裸金属管理(启用时才存在) **
│   │   ├── ironic-api.*.log              # Ironic API(节点 CRUD、部署触发)
│   │   ├── ironic-conductor.*.log        # ** Conductor:部署/清理/电源管理主流程 **
│   │   ├── ironic-inspector.*.log        # 硬件 introspection / 自动注册
│   │   ├── ironic-dashboard.*.log        # Ironic 控制台
│   │   ├── dnsmasq*.log                  # PXE DHCP
│   │   └── tftp*.log                     # PXE TFTP
│   └── ... (其他云产品按集群版本而定,例如 esecf / esks / esdb / dts / esobs / esbackup
│            等数据库/对象存储/容器/灾备等产品,启用后会出现在此目录)
│
│
├── ecas/                    # Automation services
│   ├── ess-automation.*.log          # Automation engine
│   ├── automation-operators.*.log    # K8s operators
│   ├── coaster-agent/*.log           # Coaster agent
│   └── celery/*.log                  # Celery workers
│
├── ecms/                    # Monitoring & logging
│   ├── prometheus.*.log              # Prometheus
│   ├── alertmanager.*.log            # Alertmanager
│   ├── grafana.*.log                 # Grafana
│   ├── fluentbit.*.log               # Fluent Bit
│   ├── fluentd.*.log                 # Fluentd
│   ├── thanos-*.log                  # Thanos components
│   ├── node-exporter.*.log           # Node exporter
│   ├── blackbox-exporter.*.log       # Blackbox exporter
│   ├── kube-state-metrics.*.log      # KSM
│   └── openstack-metrics.*.log       # OpenStack metrics
│
├── ems/                     # Dashboard services
│   ├── ecp-dashboard-api.*.log       # ECP dashboard API
│   ├── ecp-dashboard.*.log           # ECP dashboard
│   ├── ems-dashboard-api.*.log       # EMS dashboard API
│   └── opa.*.log                     # OPA policy engine
│
├── kubernetes/              # Kubernetes system
│   ├── kube-apiserver.*.log          # API server
│   ├── kube-scheduler.*.log          # Scheduler
│   ├── kube-controller-manager.*.log # Controller manager
│   ├── kube-proxy.*.log              # Kube-proxy
│   ├── kube-flannel.*.log            # Flannel CNI
│   ├── kube-monitor.*.log            # Kube monitor
│   ├── coredns.*.log                 # CoreDNS
│   ├── csi-rbdplugin.*.log           # Ceph CSI RBD plugin (PV mount path)
│   ├── driver-registrar.*.log        # CSI driver registrar
│   ├── docker-registry.*.log         # Container image registry
│   ├── chartmuseum.*.log             # Helm chart museum
│   ├── image-manager.*.log           # Image manager
│   ├── clearer.*.log                 # Cluster cleanup/clearer
│   └── k8s-keystone-auth.*.log       # Keystone auth webhook for K8s
│
├── libvirt/                 # Hypervisor
│   ├── libvirt.*.log                 # libvirtd daemon
│   ├── libvirt-sync.*.log            # Libvirt sync service
│   ├── qemu.instance-*.log           # ** Per-instance QEMU logs (one file per domain) **
│   ├── ceph-conf-placement.*.log     # Ceph config placement
│   ├── ceph-keyring-placement.*.log  # Ceph keyring placement
│   ├── etcd-client.*.log             # etcd client (libvirt → etcd)
│   ├── etcdlock-manager.*.log        # etcd lock manager (lock arbitration)
│   └── reservation-key-gen.*.log     # PR-key generator for shared volumes
│
├── openstack/               # Main OpenStack services
│   ├── nova/                         # Compute service
│   │   ├── nova-compute.*.log             # ** Primary: VM lifecycle, volume attach/detach **
│   │   ├── nova-api.*.log                 # Nova API
│   │   ├── nova-conductor.*.log           # Conductor
│   │   ├── nova-scheduler.*.log           # Scheduler
│   │   ├── nova-operator.*.log            # K8s operator
│   │   ├── nova-maintenance.*.log         # Maintenance (evacuation, cell management)
│   │   ├── nova-novncproxy.*.log          # VNC proxy
│   │   ├── nova-placement-api.*.log       # Placement API
│   │   └── ceph-keyring-placement.*.log   # Ceph keyring for nova
│   │
│   ├── cinder/                       # Block storage service
│   │   ├── cinder-volume.*.log             # ** Primary: volume operations **
│   │   ├── cinder-api.*.log                # Volume API
│   │   ├── cinder-scheduler.*.log          # Volume scheduler
│   │   ├── cinder-dashboard.*.log          # Dashboard
│   │   ├── golem.*.log                     # Golem (volume proxy)
│   │   └── ceph-keyring-placement.*.log    # Ceph keyring for cinder
│   │
│   ├── neutron/                      # Networking service
│   │   ├── proton-server.*.log             # Neutron server
│   │   ├── proton-ovn-controller.*.log     # OVN controller
│   │   ├── proton-ovn-metadata-agent.*.log # Metadata agent
│   │   ├── proton-ovn-l2gw-agent.*.log     # L2 gateway agent
│   │   ├── proton-insight-agent.*.log      # Insight agent
│   │   └── proton-maintenance.*.log        # Maintenance
│   │
│   ├── glance/                       # Image service
│   │   ├── glance-api.*.log
│   │   └── ceph-keyring-placement.*.log
│   │
│   ├── keystone/                     # Identity service
│   │   └── keystone-api.*.log
│   │
│   ├── horizon/                      # Dashboard
│   │   ├── horizon.*.log
│   │   └── nginx.*.log
│   │
│   └── ... (other services see below)
│   │
│   ├── aodh/                        # Alarming service
│   ├── ceilometer/                  # Telemetry collector
│   ├── gnocchi/                     # Time-series metrics storage
│   ├── mariadb/                     # ** Galera DB (WSREP) — control-plane DB **
│   │   ├── mariadb.*.log
│   │   └── mariadb-N-readiness.*.log
│   ├── rabbitmq/                    # ** AMQP message bus (all OS services depend on it) **
│   │   ├── rabbitmq.*.log
│   │   └── rabbit-init-check.*.log
│   ├── memcached/                   # Memcached (Keystone token cache, etc.)
│   ├── mongodb/                     # MongoDB
│   ├── redis/                       # Redis
│   ├── escache/                     # EasyStack cache
│   ├── keepalived/                  # VIP failover for control-plane endpoints
│   ├── esvmm/                       # EasyStack VM manager
│   ├── esdm/                        # EasyStack disaster-recovery manager
│   ├── esguides/                    # EasyStack onboarding guides
│   ├── ota/                         # OTA upgrade service
│   ├── dozer/
│   │   └── bash-history.*.log       # ** Operator shell history (audit trail) **
│   └── busybox-openstack/           # Auxiliary busybox helper logs
│
├── os/                       # Operating system
│   ├── messages.*.log                # ** System messages (dmesg, syslog) **
│   ├── chrony.*.log                  # ** NTP — clock drift kills Galera/Ceph quorum **
│   ├── sa/                           # sysstat binary (sar) data — node-level perf
│   └── openvswitch/                  # OVS/OVN
│       ├── ovs-vswitchd.*.log
│       ├── ovsdb-server.*.log
│       ├── ovn-controller.*.log
│       ├── ovn-northd.*.log
│       ├── ovn-ovsdb-nb.*.log               # NB DB
│       ├── ovn-ovsdb-nb-relay.*.log
│       ├── ovn-ovsdb-sb.*.log               # SB DB
│       ├── ovn-ovsdb-sb-relay.*.log
│       ├── ovn-ovsdb-sb-leader-relay.*.log
│       └── ovn-tool.*.log
│
└── ecms/                    # Monitoring & logging (expanded)
    ├── prometheus.*.log
    ├── alertmanager.*.log
    ├── grafana.*.log
    ├── fluentbit.*.log / fluentbit-init.*.log
    ├── fluentd.*.log / fluentd-api.*.log
    ├── thanos-*.log
    ├── node-exporter.*.log
    ├── blackbox-exporter.*.log
    ├── kube-state-metrics.*.log
    ├── openstack-metrics.*.log
    ├── ipmi-collector.*.log              # IPMI metric collector
    ├── emla-apiserver.*.log              # Log analytics API server
    ├── emla-controller-manager.*.log     # Log analytics controller
    ├── emla-dashboard.*.log              # Log analytics dashboard
    ├── config-reloader.*.log
    ├── init-config-reloader.*.log
    └── httpd.*.log
│
└── others/                   # Other services
    ├── kube.gpu-api.*.log            # GPU API
    ├── kube.topology-operators.*.log  # Topology operators
    ├── kube.event-monitor.*.log       # Event monitor
    └── kube.craftman.*.log           # Craftman node image manager
```

## Scenario Log Map 场景日志映射

| Scenario | Primary Log (search first) | Secondary Logs (cross-reference) |
|----------|---------------------------|----------------------------------|
| **VM hard reboot failure** | `openstack/nova/nova-compute.*.log` | `libvirt/libvirt.*.log`, `openstack/cinder/cinder-volume.*.log` |
| **Volume not found** | `openstack/nova/nova-compute.*.log` | `alcubierre/alcubierre-node.*.log`, `openstack/cinder/cinder-volume.*.log` |
| **iSCSI connection failure** | `alcubierre/alcubierre-node.*.log` | `openstack/nova/nova-compute.*.log`, `os/messages.*.log` |
| **Ceph OSD down** | `ceph/host.ceph-osd.*.log` | `ceph/host.ceph.*.log`, `os/messages.*.log` |
| **Node reboot/crash** | `os/messages.*.log` | `openstack/nova/nova-compute.*.log`, `kubernetes/kube-*.log` |
| **Network connectivity** | `os/openvswitch/ovs-vswitchd.*.log` | `openstack/neutron/proton-server.*.log` |
| **Database issues** | `openstack/mariadb/mariadb.*.log` | `openstack/nova/nova-compute.*.log`, `openstack/cinder/cinder-volume.*.log` |
| **VM live migration** | `openstack/nova/nova-compute.*.log` | `openstack/nova/nova-conductor.*.log` |
| **AMQP / RPC timeout** | `openstack/rabbitmq/rabbitmq.*.log` | any service log with `oslo_messaging` errors |
| **Galera split-brain / readiness** | `openstack/mariadb/mariadb.*.log` | `openstack/mariadb/mariadb-*-readiness.*.log` |
| **K8s PV mount failure** | `kubernetes/csi-rbdplugin.*.log` | `os/messages.*.log`, `kubernetes/driver-registrar.*.log` |
| **Clock drift / NTP** | `os/chrony.*.log` | `openstack/mariadb/mariadb.*.log` (Galera), `ceph/host.ceph.*.log` |
| **Operator action audit** | `openstack/dozer/bash-history.*.log` | n/a (single source) |
| **VIP failover** | `openstack/keepalived/keepalived.*.log` | `os/messages.*.log` |
| **裸金属部署失败** | `cloud-products/ironic/ironic-conductor.*.log` | `cloud-products/ironic/ironic-inspector.*.log`、`os/messages.*.log`(IPMI/链路)、`openstack/neutron/proton-server.*.log`(部署网切换)|
| **裸金属 PXE 不起** | `cloud-products/ironic/dnsmasq*.log`、`tftp*.log` | `os/openvswitch/ovs-vswitchd.*.log`、`os/messages.*.log` |
| **公网/南北向访问异常** | `cloud-products/apisix/apisix.*.log` | `openstack/keepalived/keepalived.*.log`、`os/openvswitch/*.log` |
