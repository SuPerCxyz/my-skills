# EasyStack Project Relationships

## Inventory And Sources 清单与来源

以下基于用户说明及 2026-10-16 对 `~/EScode` 的只读调查: 26 个 Git 目录对应
25 个不同 origin, 其中 24 个 Gerrit 项目、1 个 GitLab 项目. 本地目录和远端项目
不是同一个计数; 两个 os-brick 目录是同一项目的不同分支 checkout.
具体路径、分支、提交、已有修改及部署版本每次重新核对, 不将本次工作区当线上版本.

用户确认 EasyStack 公司项目的默认 [Gerrit 评审站点](https://review.easystack.cn/).
该网页地址不代替实际 Git remote; 交付时仍核对仓库 remote、项目和目标分支,
按 `git-delivery` 规则处理, 不自动改写 remote. 公司默认值不扩展到个人 `my-skills`
的交付与身份; `rainbow-doc` 保留现有 GitLab 入口和实际交付方式.

除 `rainbow-doc` 的 origin 是 `gitlab.easystack.io/es-cms/rainbow-doc` 外,
已检查 origin 均指向 `review.easystack.cn/easystack/` 下的项目.
这是已定位的本地清单, 不是完整 Gerrit 目录. 用户提供的仓库浏览入口是
[Gerrit Repositories](https://review.easystack.cn/admin/repos); 可见项目以实际取回的数据为准.
该页面是前端入口; [项目列表 API](https://review.easystack.cn/Documentation/rest-api-projects.html#list-projects)
只返回当前调用者可见的项目. 必须记录查询身份和可见范围,
不将匿名空列表解释成站点没有项目, 也不以页面返回 200 证明已取得仓库清单.

| 本地目录 | 角色 | 关系定位入口 |
|----------|------|--------------|
| `nova` | 计算核心 API、scheduler、conductor、compute、virt | `nova/volume/cinder.py`, `nova/virt/`, `nova/network/`, `nova/image/` |
| `nova-dashboard-api` | Django/SDK 计算网关 | `nova_dashboard_api/api/rest/nova.py`, `nova_dashboard_api/api/nova.py` |
| `nova-dashboard` | 计算 UI, 业务根 `projects/ecs` | `projects/ecs/services/instance-api.service.ts` |
| `nova-operator` | Go/Kubernetes controller, 同时调用 Nova/Cinder | `controllers/nova/volumecreate_controller.go`, `go.mod` |
| `cinder` | 卷、快照、备份及 scheduler/manager/driver | `cinder/volume/`, `cinder/backup/`, `cinder/api/` |
| `golem` | 存储与备份 API/SDK 适配层 | `golem/api/v3/`, `golem/api/v1/`, `golem/api/contrib/` |
| `ebs-dashboard` | 云硬盘 UI, 业务根 `projects/ebs` | `projects/ebs/services/api.service.ts` |
| `ark-cinder` | Cinder、golem、UI 的 Helm 配置和部署 | `chart/cinder/` |
| `os-brick` | 主机侧连接、断开、多路径、加密公共库 | `os_brick/initiator/connector.py`, `os_brick/initiator/connectors/` |
| `os-brick-nvmeof-clean` | 同一 os-brick origin 的专项分支副本 | 先核对该 checkout 的分支、目标 Patch 和 connector 实现 |
| `yak` | 备份 UI, 业务根 `projects/yak` | `projects/yak/services/api.service.ts` |
| `ark-thor` | Thor 备份部署, 包含 yak/golem/backup workers | `chart/thor/` |
| `ironic` | 裸金属 API、conductor 和硬件驱动 | `ironic/api/`, `ironic/conductor/`, `ironic/drivers/` |
| `ironic-dashboard-api` | Django/SDK 裸金属网关 | `ironic_dashboard_api/api/rest/ironic.py`, `ironic_dashboard_api/api/ironic.py` |
| `ironic-dashboard` | 裸金属 UI, 业务根 `projects/ironic` | `projects/ironic/services/requests/` |
| `ark-ironic` | 裸金属服务、UI、网关的 Helm 部署 | `chart/ironic/` |
| `glance` | 镜像 API、存储与导入任务 | `glance/api/`, `glance/db/`, `glance/async_/` |
| `ark-glance` | Glance 及相关 dashboard/API 部署配置 | `chart/glance/` |
| `neutron` | 网络 API、插件与 agent | `neutron/`, `tox.ini` |
| `proton` | Neutron 派生网络产品, Python 分发包仍名 neutron | `setup.cfg`, `neutron/`, governance 的 proton 分组 |
| `keystone` | 身份、认证、项目与授权 | `keystone/`, `tox.ini` |
| `cube` | Kolla 容器镜像构建体系 | `README.rst`, `docker/`, `deliverables.yaml` |
| `etcdlock-manager` | C 锁守护进程、Go/HTTP 代理、etcd lease 与 fencing | `src/`, `pkg/etcd_client/`, `doc/ARCHITECTURE.md` |
| `tempest` | 真实 OpenStack 的 API/场景验证与自身测试框架 | `tempest/api/`, `tempest/scenario/`, `tox.ini` |
| `governance` | 技术治理和产品发版仓库分组, 不是运行时服务 | `cloud-product/project-list.yaml` |
| `rainbow-doc` | Hexo 产品文档及版本/语言导航 | `package.json`, `README.md` |

`ark-nova` 的配置/启动职责由用户确认, governance 也列出该项目,
但本次未发现其本地 checkout. 分组里另有 placement、客户端和 `ark-resource-*`
等仓库, 仅在当前任务实际涉及时定位, 不补造本地目录或遍历全部项目.

## Release Groups 发版分组

以本次检查的 `governance@ee92b99` 为来源:

| 业务域 | 已列出的相关项目 | 源码位置 |
|--------|------------------|----------|
| 计算 | nova、ark-nova、nova-dashboard、nova-dashboard-api、nova-operator 等 | `cloud-product/project-list.yaml:20-31` |
| 云硬盘 | cinder、ebs-dashboard、golem、ark-cinder 等 | `cloud-product/project-list.yaml:357-363` |
| 备份 Thor | cinder、golem、yak、ark-thor | `cloud-product/project-list.yaml:629-634` |
| 裸金属 | ironic、ironic-dashboard-api、ironic-dashboard、ark-ironic 等 | `cloud-product/project-list.yaml:225-231` |
| 网络 Proton | proton 作为单独产品分组 | `cloud-product/project-list.yaml:78-86` |

分组证明维护/发版归属, 不证明运行时直接调用或每次必须同步修改.
代码仓库名、镜像名、Deployment 名也需分开: 例如 ebs-dashboard 源码对应的部署
仍可能名为 cinder-dashboard; 不将它误记成另一个已确认源码仓库.

以下业务域入口按角色定位候选调查范围, 不表示每次全部必改.
进入后结合代码关系证据, 再给出必改、需查证或不需改的结论.

<a id="nova"></a>

### Nova 计算

`nova-dashboard` UI -> `nova-dashboard-api` 网关 -> `nova` 核心服务.
`ark-nova` 负责配置/部署, 本次未发现本地 checkout; `nova-operator` 是 controller
调用入口, 涉及其行为或消费契约变化时纳入, 它也实际调用 Cinder. 卷挂载等变化再核查 Cinder/os-brick;
端口、镜像或裸金属变化按实际契约扩展到对应项目.

<a id="cinder"></a>

### Cinder 云硬盘

`ebs-dashboard` 是 UI, `golem` 是 API/SDK 适配层, `cinder` 是核心服务,
`ark-cinder` 负责配置/部署. UI 外部 prefix 到 golem v3 的 gateway rewrite 尚未证明,
需按本次功能核查实际路由, 不把角色排列当成完整调用链.

<a id="backup"></a>

### Backup 备份

`yak` UI -> `golem` 备份 API -> `cinder` 仓库的 backup 模块;
`ark-thor` 负责相关 UI、API 和 backup workers 的配置/部署.
backup 模块与部署进程属于已有仓库关系, 不据此补造独立的 cinder-backup 仓库.

<a id="ironic"></a>

### Ironic 裸金属

`ironic-dashboard` UI -> `ironic-dashboard-api` 网关 -> `ironic` 核心服务;
`ark-ironic` 负责配置/部署. 按具体功能核查接口、SDK 与服务端状态的实际连接.

<a id="glance"></a>

### Glance 镜像

`glance` 是镜像核心服务, `ark-glance` 负责配置/部署.
本次未核实前端源码仓库, 涉及 UI 或网关时再定位, 不补造仓库名称.

<a id="network"></a>

### Network 网络

分别定位 `neutron` 网络服务与 `proton` 派生网络产品的目标仓库和版本.
两者 Python 模块同名不证明互相调用; 按实际网络功能和服务契约选择调查范围.

## Code Evidence 代码关系证据

路径均以调查根为基准, 行号是本次定位入口而非永久接口保证.
复用证据前核对目标版本; 含已有修改的工作区需区分目标 Patch、基线与其他修改.

| 连接 | 已检查证据 | 修改时重点 |
|------|------------|------------|
| Nova UI -> 计算网关 -> Nova | `nova-dashboard/projects/ecs/services/instance-api.service.ts:38`; `nova-dashboard-api/nova_dashboard_api/api/rest/nova.py:1294,1312` 与 `nova-dashboard-api/nova_dashboard_api/api/nova.py:510,522` | 参数、租户、SDK 调用、错误与异步状态 |
| EBS UI / golem / Cinder | `ebs-dashboard/projects/ebs/services/api.service.ts:14,116` 用 `/cinder_dashboard_api/api/cinder/volumes/`; `golem/golem/api/v3/router.py:88` 与 `golem/golem/api/v3/volume.py:119` | 消费与适配层均存在, 外部前缀到 v3 的 gateway rewrite 本轮尚未证明, 不能直接拼成完整路由 |
| yak -> golem -> Cinder Backup | `yak/projects/yak/services/api.service.ts:19,36`; `golem/golem/api/v1/router.py:37`; `golem/golem/api/contrib/backups.py:44-45,79` | `/golem/v1/volumebackups`, CinderClient 与 backup API 的字段、能力及终态 |
| Cinder 内部备份链 | `cinder/setup.cfg:66`; `cinder/cinder/backup/api.py:33,67`, `cinder/cinder/backup/manager.py:48,58`, `cinder/cinder/backup/rpcapi.py:52` | API -> RPC -> manager/driver, 恢复、取消、状态与清理 |
| 裸金属 UI -> 网关 -> Ironic | `ironic-dashboard/projects/ironic/services/requests/register-node-api.service.ts:21`; `ironic-dashboard-api/ironic_dashboard_api/api/rest/ironic.py:519` 与 `ironic-dashboard-api/ironic_dashboard_api/api/ironic.py:118-123` | 注册接口、catalog baremetal endpoint、SDK 与核心状态 |
| Nova -> Cinder | `nova/nova/volume/cinder.py:28-29,603,638,787-813` | attachment、connector、connection_info、调用时序; attachment_complete 所需最低 microversion |
| Nova/Cinder -> os-brick | `nova/requirements.txt:54`, `cinder/requirements.txt:61`; `nova/nova/virt/libvirt/volume/alcubierre_v2.py:38,55`; `os-brick/os_brick/initiator/connector.py:68-70`; `cinder/cinder/volume/volume_utils.py:47-48` | 包约束与实际 connector 类型、设备路径、多路径、加密、断开和扩容 |
| Nova -> Ironic/Neutron/Glance | `nova/nova/virt/ironic/client_wrapper.py:134`, `nova/nova/network/neutron.py:28-29`, `nova/nova/image/glance.py:33-34` | 具体功能下的客户端参数、最低能力、状态与异常约定 |
| nova-operator -> Cinder | `nova-operator/controllers/nova/volumecreate_controller.go:31,669` | gophercloud blockstorage v3、重入去重、状态/finalizer 与实际卷结果 |
| ark/cube -> 镜像与服务 | `ark-cinder/chart/cinder/templates/deployment-cinder-golem.yaml:49`; `ark-thor/chart/thor/templates/deployment-yak.yaml:25,49`, `ark-thor/chart/thor/templates/deployment-golem.yaml:26,50`, `ark-thor/chart/thor/templates/deployment-backup-rbd.yaml:26`; `cube/docker/cinder/cinder-base/Dockerfile.j2:31-35` | chart 消费镜像与配置, cube 构建服务源码; 代码改动不当然要求改配方或 chart |
| etcdlock-manager 场景协作 | `etcdlock-manager/src/client.c:513,607`, `etcdlock-manager/src/etcdlock_manager_sock.h:23-25`, `etcdlock-manager/pkg/etcd_client/etcd_client.go:175-193`, `etcdlock-manager/doc/ARCHITECTURE.md:35-49` | 锁/lease/事务和 fencing; 本轮未证明 Nova/Cinder/os-brick 直接调用, 不编造强依赖 |

Proton 与 Neutron 的模块同名不证明两者相互调用. 文档站与 governance 也不作为
每个业务修改的必改项; 只有可观察行为、发布约定或有效需求触发时才进入范围.

## Impact Analysis 联动判断

从本次要改变的可观察行为出发, 追踪实际生产和消费位置:

| 触发变化 | 必要调查边界 |
|----------|--------------|
| UI 字段、搜索、排序、分页 | UI service、网关字段映射、核心 API、响应总数与权限 |
| API、SDK、RPC 或 object 变化 | 请求/返回/错误契约、最低版本、序列化、cap 与兼容转换 |
| 连接、迁移、扩容、备份或设备操作 | manager/driver/connector、异步状态、真实数据或设备效果及失败恢复 |
| DB、配置、权限、持久化格式 | 实际迁移机制、读写双方、租户、旧版本和滚动升级 |
| operator 或锁服务 | CRD/状态/finalizer、重入、协议、lease、fencing 与实际消费方 |
| 镜像、启动和发布 | cube 配方、实际 ark 配置生产/消费、镜像标签与部署衔接 |

对每个真正相关仓库给出一种结论:

- **必改**: 当前代码无法满足已确认行为, 给出路径、修改点和验证方式.
- **需查证**: 版本、调用、权限、配置或部署事实不足, 说明影响的决策与补证方法.
- **不需改**: 现有契约已满足目标, 给出实际代码/接口依据.

例如 API 已正确返回字段而 UI 未展示, 可仅修改 UI; 只有中间层裁剪或语义不兼容
才扩展到网关/服务. 这只是判定方法, 不冒充真实 Gerrit 联动案例.
同 EAS、类似标题、同 topic 或发版分组只用于寻找候选;
`Depends-On` 支持当时的显式依赖, 当前任务仍需核对目标版本和代码.

## Working Record 记录与对账

将结果写入当前 Requirement Review、有效 OpenSpec 或报告, 不创建平行计划.

| 仓库与分支 | 判定 | 原因与改动点 | 证据 | 验证 |
|------------|------|--------------|------|------|
| `<repo>@<branch>` | 必改 / 需查证 / 不需改 | `<具体行为或缺口>` | `<path:line 或已核对 Change URL>` | `<确认行为与验证入口>` |

先消除影响方向的缺口, 再实现必改仓库. 新的公共 contract、迁移、依赖或共享配置
超出原授权时重新 Review. 保护已有修改, 两个 os-brick 副本先确认目标, 不合并或清理.
完成前核对字段、状态、权限、错误语义、版本、部署与验证一致,
不把一个仓库 CI 通过当成跨项目闭环. Git 交付分别按
[git-delivery](../git-delivery/SKILL.md) 核对分支、Change、依赖 footer 和实际授权.

EasyStack 新提交的 Author Email 和 Committer Email 均使用
`guangchao.pan@easystack.cn`. 实际提交前核对最终生效身份, 姓名使用已核实信息,
不虚构姓名. amend 时当前 Committer 使用此邮箱; 原 Author 邮箱不同时,
先明确具体提交、作者归属和处理方式, 不自动改署历史作者、使用 `--reset-author`
或批量改写历史. 保留正确的 Change-Id; 此约定不授权修改 Git 配置或执行提交.

仅在用户要求多仓交付时, 逐仓汇总实际 remote、目标分支、真实 Change 链接、
依赖和验证结果; 链接未取得或尚未上传时明确标记. 分别记录实际操作的
未执行/成功/失败等状态及整体剩余项, 不将单仓上传成功表述为整项交付完成.
单仓提交规范和操作授权继续使用 `git-delivery`, 不另建模板或复制 footer 规则.
