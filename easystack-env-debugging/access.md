# Environment Access

当任务需要先进入运行中的环境时阅读本文件。本文件只覆盖访问路径选择;
访问成功后, 再切换到 [pods.md](pods.md)、[logs.md](logs.md)、
[auth.md](auth.md) 或 [network.md](network.md) 等对应领域文档。

## 访问环境后台

默认只做查看操作。连接成功后，优先执行 `whoami`、`id -u`、`hostname`、`pwd`、
`kubectl get`、`kubectl describe`、`kubectl logs --tail=<N>` 等无影响命令。
不要在未获得明确授权时执行 `edit/delete/apply/patch/rollout restart/helm rollback` 等变更命令。

外部进入目标环境时, MUST 使用 `bash <path>/scripts/env-access.sh`。
不要手写 `ssh`、`ssh js`、多层跳板命令或临时 expect 脚本来登录环境。
也不要直接修改 [scripts/env-access.sh](scripts/env-access.sh) 或
[scripts/jumpserver-env.sh](scripts/jumpserver-env.sh)。如果脚本执行确实有问题,
先向用户抛出目标、命令、错误输出和建议改动点; 获得明确允许后再修改脚本。
调用这些脚本时 MUST 通过 `bash` 启动, 不要依赖执行位; 这样同步后的安装副本
即使暂时缺少 `+x` 也能正常运行。

标准 `BJ-<N>` 请求通过 `bash <path>/env-access.sh --env BJ-<N>` 执行。首次调用前不要
`grep`/`cat ~/.ssh/config`、列出 SSH key 或读取脚本源码; `env-access.sh` 会通过
`ssh -G` 自行解析配置并选择连接路径。只有脚本明确报告配置或连接问题时, 才进入
本文件后续配置排查。

## 推荐入口: 统一访问脚本

所有外部环境登录链路统一放在脚本里。调用时只追加业务命令, 避免手写多层
SSH、expect 和 shell 引号导致命令执行失败。

```bash
# 打开交互 shell
bash easystack-env-debugging/scripts/env-access.sh --env BJ-<ENV_ID>

# BJ-xx / 172.<N>.0.2: 脚本先走本机 SSH config 跳板直达, 失败后按脚本逻辑回退
bash easystack-env-debugging/scripts/env-access.sh --env BJ-<ENV_ID> -- whoami
bash easystack-env-debugging/scripts/env-access.sh --target 172.<N>.0.2 -- kubectl get nodes -o name

# 172.18.*: 脚本封装外层跳板机和内层控制节点登录
bash easystack-env-debugging/scripts/env-access.sh --target <JUMP_IP> --control-node <CONTROL_NODE_IP> -- hostname

# 先经过一层普通 SSH 跳板机, 再直连目标环境
bash easystack-env-debugging/scripts/env-access.sh \
  --via <ORDINARY_JUMP> \
  --target <TARGET_IP> \
  -- hostname

# JumpServer 菜单 fallback
bash easystack-env-debugging/scripts/env-access.sh --asset <ASSET_NAME> --mode jumpserver -- whoami

# 本地 SSH config 不完整时，显式传入 JumpServer 认证信息
bash easystack-env-debugging/scripts/env-access.sh \
  --env BJ-<ENV_ID> \
  --jumpserver-host <JUMPSERVER_HOST> \
  --jumpserver-user <JUMPSERVER_USER> \
  --jumpserver-port <JUMPSERVER_PORT> \
  --jumpserver-identity-file <IDENTITY_FILE> \
  -- whoami
```

带管道、循环、变量展开等复杂 shell 语法时, 用 `--cmd` 传一段命令字符串, 仍然只保留
一层本地引号:

```bash
bash easystack-env-debugging/scripts/env-access.sh --env BJ-<ENV_ID> --cmd 'kubectl get namespaces | grep openstack'
```

## Ordinary SSH Jump Host 普通 SSH 跳板机

用户说明必须先登录 `eswork` 等普通 SSH 主机时, 使用 `--via <SSH_TARGET>`。
`--via` 使用 OpenSSH ProxyJump, 与现有 mode 正交组合; 不把 skill 脚本复制到
普通跳板机。

普通跳板后直连目标:

```bash
bash easystack-env-debugging/scripts/env-access.sh \
  --via eswork \
  --target 192.168.3.3 \
  --mode ssh \
  --cmd 'hostname'
```

普通跳板后再经过环境跳板机:

```bash
bash easystack-env-debugging/scripts/env-access.sh \
  --via eswork \
  --target 172.18.0.118 \
  --mode jump18 \
  --control-node 10.20.0.3 \
  --cmd 'hostname'
```

普通跳板后进入 JumpServer:

```bash
bash easystack-env-debugging/scripts/env-access.sh \
  --via eswork \
  --asset BJ-123 \
  --mode jumpserver \
  --cmd 'hostname'
```

`--via` 接受 SSH alias、IP 或 `user@host`。值不能以 `-` 开头。所有 SSH 路径
显式读取用户 SSH config; 如果文件不存在则使用 `/dev/null`, 避免损坏的系统
SSH config 阻断链路。`--via` 只负责追加 ProxyJump。

## BJ-xx SSH config 跳板直达模式

当用户说 `xx 环境` / `BJ-xx 环境` 时, 默认认为需要通过跳板/堡垒机访问。
如果本机 `~/.ssh/config` 已配置 `Host 172.*.0.2`, BJ-xx 测试环境必须通过
统一访问脚本访问。脚本内部会按 SSH config 进入目标资产, 该方式仍经过
JumpServer, 但不需要进入 TUI 菜单, 也不需要临时生成 expect 脚本。

一次性准备控制连接目录:

```bash
mkdir -p ~/.ssh/control
chmod 700 ~/.ssh/control
```

SSH config 示例:

```sshconfig
Host 172.*.0.2
    HostName js.easystack.io
    Port 2222
    User "<JUMPSERVER_USER>#dev#%n"
    IdentityFile ~/.ssh/es-rsa
    IdentitiesOnly yes
    RequestTTY force

    ServerAliveInterval 30
    ServerAliveCountMax 3

    ControlMaster auto
    ControlPersist 8h
    ControlPath ~/.ssh/control/%C
```

用户提供可直接 SSH 的环境别名时, 也通过统一访问脚本的 `--target <SSH_TARGET>`
入口尝试。进入后按 [进入后台后](#进入后台后) 做只读验证。复杂排查先进入
交互 shell, 避免多层引号和 TTY 行为影响结果。

```bash
bash easystack-env-debugging/scripts/env-access.sh --target 172.<ENV_ID>.0.2 -- whoami
bash easystack-env-debugging/scripts/env-access.sh --target 172.<ENV_ID>.0.2 --cmd 'whoami; id -u; hostname; pwd'
```

适用边界:

- 适用: 用户给出 `xx 环境` / `BJ-xx` 环境, 且可确定 SSH 目标或资产 IP 为 `172.<N>.0.2`。
- 适用: 本机已有上述 `Host 172.*.0.2` SSH config 或用户提供等价配置。
- 不适用: 非 `172.*.0.2` 资产、需要通过 JumpServer 菜单搜索的资产、或本机缺少对应 SSH config。
- 统一访问脚本的 SSH 模式失败时, 不要临时改脚本或新写 expect; 改用统一访问脚本的 [JumpServer 堡垒机模式](#jumpserver-堡垒机模式) 参数入口。

## 跳板机模式(IP 以 172.18. 开头)

必须使用 `bash <path>/env-access.sh --target <JUMP_IP> --control-node <CONTROL_NODE_IP> -- <CMD...>`。
不要手写外层跳板机和内层控制节点的多层 SSH 命令。

```bash
# 打开控制节点交互 shell
bash easystack-env-debugging/scripts/env-access.sh --target <JUMP_IP> --control-node <CONTROL_NODE_IP>

# 一步执行只读验证命令
bash easystack-env-debugging/scripts/env-access.sh --target <JUMP_IP> --control-node <CONTROL_NODE_IP> --cmd 'whoami; id -u; hostname; pwd'
```

- `<JUMP_IP>` 由用户指定
- `<CONTROL_NODE_IP>` 通常为 **10.20.0.3**，失败时询问用户
- 跳板机本身没有 kubectl，必须内层 SSH 到控制节点
- 控制节点可执行 `kubectl get/describe/logs`、`helm list/history`、
  `kubectl get cm -o yaml`、busybox 中的
  `openstack server list` 和 `openstack volume list`

## 直连模式(非 172.18. 开头)

直连 IP 也必须通过统一访问脚本进入, 不直接手写 `ssh root@<TARGET_IP>`。

```bash
# 打开交互 shell
bash easystack-env-debugging/scripts/env-access.sh --target <TARGET_IP>

# 只读验证
bash easystack-env-debugging/scripts/env-access.sh --target <TARGET_IP> --cmd 'whoami; id -u; hostname; pwd'
```

- 认证失败时不得猜测或轮换密码。记录脱敏错误信息, 根据脚本返回的缺失配置向用户
  索取认证方式或凭据路径。

## SSH 直连/跳板补充说明

- **复杂命令避免嵌套 SSH 引号传递** — 无论是跳板机双层 SSH 还是直连后跳 node，引号和变量展开都容易丢失。通过 `bash <path>/env-access.sh --cmd '<CMD>'` 执行短命令; 复杂排查先用脚本进入交互式会话
- 直连和 `172.18.*` 跳板模式不要求排障者手写 SSH 命令, 密码或密钥由脚本的对应模式处理
- **不要从本机直连 K8s 节点内网 IP**(如 10.10.1.x)，必须通过控制节点中转
- 默认只允许查看操作；变更操作必须获得用户明确授权

## JumpServer 堡垒机模式

部分环境通过 JumpServer 堡垒机管理，而非直接 SSH 到 K8s 控制节点。
对于 BJ-xx 且本机已配置 `Host 172.*.0.2` 的环境, 仍然通过统一访问脚本的
`--env BJ-<ENV_ID>` 入口进入。只有 SSH config 跳板直达失败、没有直达 Host
配置、需要 TUI 菜单搜索、或用户明确要求 `ssh js` 菜单交互时, 才使用统一访问
脚本的 `--asset <ASSET_NAME> --mode jumpserver` 参数。

### 连接流程

```
确认用户指定的资产名或环境名
调用 bash <path>/env-access.sh --asset <ASSET_NAME> --mode jumpserver
脚本进入 JumpServer 菜单并选择资产
脚本切换到 root 或报告权限/认证/超时问题
```

### JumpServer 前置条件与配置缺失处理

JumpServer 连接信息优先来自用户 SSH 配置。排障者只选择统一访问脚本参数,
不要把 HostName、Port、User、IdentityFile 等字段硬编码到文档或临时命令里。
如果本机 SSH config 没有对应的 JumpServer 入口，统一访问脚本支持通过
`--jumpserver-host`、`--jumpserver-user`、`--jumpserver-port`、
`--jumpserver-identity-file` 或 `--jumpserver-password-file` 显式传入认证信息;
脚本不会回退去用当前本机用户的普通 SSH 认证信息。密码只从文件读取, 不接受明文
密码命令行参数。

读取顺序:

1. 先使用用户已配置的 SSH alias, 包括 `~/.ssh/config` 及其 Include 文件。
2. BJ-xx / `172.<N>.0.2` 优先走 `Host 172.*.0.2` 这类 SSH config 规则。
3. 如果需要 JumpServer 菜单 fallback, 仍然让统一访问脚本读取用户 SSH 配置。
4. 如果脚本或 SSH 配置无法确定 JumpServer 入口, 不要猜测账号、密钥或 host。

无法从 SSH 配置获取时, 向用户说明缺少 JumpServer 访问信息, 并请用户提供:

- 目标资产名或环境名, 例如 `<ASSET_NAME>` 或 `BJ-<ENV_ID>`
- 环境类型, 例如测试环境(`BJ-xx` 类)或 x86 / arm 生产环境
- SSH 配置 alias, 如果用户已有可用 alias
- JumpServer host 和 port, 如果没有 alias
- JumpServer 用户名
- 认证方式, 例如密钥路径、密码、MFA 或交互确认要求

参考 SSH config:

```sshconfig
Host <SSH_ALIAS>
    HostName <JUMPSERVER_HOST>
    Port 2222
    User <JUMPSERVER_USER>
    IdentityFile <IDENTITY_FILE>
    IdentitiesOnly yes
    RequestTTY force
```

用户补齐后, 仍然通过统一访问脚本进入环境; 不要在排障文档中临时拼接一次性
JumpServer SSH 命令。

### Temporary Authentication Profile 临时认证 Profile

用户提供 JumpServer host、user、port、密码或私钥并希望后续复用时, 使用
`--auth-profile <NAME> --save-auth-profile`。profile 名只允许字母、数字、
点、下划线和连字符。建议按普通跳板机和环境命名, 例如
`eswork-BJ-123`。

首次保存:

```bash
umask 077
AUTH_INPUT=$(mktemp /tmp/easystack-auth-input.XXXXXX)

bash easystack-env-debugging/scripts/env-access.sh \
  --via eswork \
  --asset BJ-123 \
  --mode jumpserver \
  --auth-profile eswork-BJ-123 \
  --save-auth-profile \
  --jumpserver-host <JUMPSERVER_HOST> \
  --jumpserver-user <JUMPSERVER_USER> \
  --jumpserver-port <JUMPSERVER_PORT> \
  --jumpserver-identity-file <IDENTITY_FILE> \
  --jumpserver-password-file "$AUTH_INPUT" \
  --cmd 'hostname'
```

后续复用:

```bash
bash easystack-env-debugging/scripts/env-access.sh \
  --asset BJ-123 \
  --mode jumpserver \
  --auth-profile eswork-BJ-123 \
  --cmd 'hostname'
```

默认保存到 `/tmp/easystack-env-access-${UID}/profiles/<NAME>/`。profile 目录权限为
`0700`, host、user、port、via、密码和私钥文件权限为 `0600`。保存时复制密码和
私钥内容, 后续不依赖原始输入文件。不要输出、diff 或读取缓存中的密码和私钥。
`/tmp` 被清理或系统重启后 profile 失效, 再向用户索取认证信息。

JumpServer 是交互式 TUI 菜单, 统一访问脚本内部会调用固化脚本处理菜单、
资产选择、`sudo su -`、退出目标 shell 和超时递增。排障时不要复制 expect
内容新建临时脚本, 也不要直接改固化脚本。脚本执行确实失败时, 先把失败目标、
执行命令、错误输出和建议改动点反馈给用户, 获得明确允许后再改脚本。

### 查询超时选择

`env-access.sh` 对一次性只读命令默认启用超时梯度。简单命令先用短超时,
只有本轮以 timeout 退出时才自动加大超时重试; 非超时错误立即返回。
显式传入 `--timeout` 时只使用用户指定的单一超时时间。

- 快速查询默认使用 `10 15 20 30 45 60` 秒梯度, 例如连接验证、菜单选择、
  `whoami`、`id -u`、`hostname`、`pwd`、`kubectl get namespaces`。
- 中等查询默认使用 `15 20 30 45 60` 秒梯度, 例如 `kubectl get pods`、
  `kubectl logs --tail=<N>`、`grep`、OpenStack / Cinder / Nova list 查询。
- 慢查询默认使用 `30 45 60` 秒梯度, 例如历史日志、`zgrep`、`journalctl`、
  大目录扫描、较大的 `kubectl describe`、`helm history`。
- 不确定是否安全重复执行的命令不要依赖自动重试; 先确认它是只读查询, 或使用
  `--timeout <SECONDS>` 指定单次执行时长。
- `curl -X POST|PUT|PATCH|DELETE` 等写请求只执行一次; 超时后先查询实际状态,
  不自动重复发送。
- 超时只表示本轮查询未完成; 不要因为超时执行重启、删除、回滚等变更操作。

### 资产名使用方式

JumpServer 资产名由用户在任务中指定。用户说 “ssh js 到 `<ASSET_NAME>` 环境”
或 “到 `<ASSET_NAME>` 环境” 时, 先判断能否转换为 `--env BJ-<ENV_ID>`。
不能转换时, 把 `<ASSET_NAME>` 原样传给统一访问脚本的 `--asset` 参数。

### 注意事项

- JumpServer TUI 菜单支持: 输入资产名(唯一时自动登录)、`/ + IP/名称` 搜索、`p` 列出有权限的主机
- 通过 JumpServer 进入环境时, 部分本地文件或敏感路径查询可能被堡垒机审计策略拦截。
  例如查询 `/root/.ssh/` 这类路径时, 可能不是目标环境命令本身失败, 而是 JumpServer
  拦截了操作。遇到这类结果时先记录拦截信息, 不要把它直接判断为目标主机文件不存在或权限配置错误。
- 如果 `sudo su -` 需要密码，说明不是 NOPASSWD 配置，需询问用户密码
- JumpServer 不是单独手写的登录入口, 而是统一访问脚本的一个模式

## 进入后台后

以下步骤适用于通过统一访问脚本进入后的所有模式。默认只做查看操作。

### 连接验证

进入目标主机并切到 root 后，先做最小只读验证:

```bash
whoami       # 应返回 root
id           # uid=0(root)
hostname
pwd
```

如果目标节点具备 kubectl 和 kubeconfig，再执行 Kubernetes 只读验证:

```bash
kubectl get namespaces | grep openstack
kubectl get pods -n openstack | head
```

查询环境节点名称和列表时, 优先使用 Kubernetes 记录的 node 名称, 作为后续节点跳转、
pod 所在节点判断和跨节点检查的基准:

```bash
kubectl get nodes -o name
```

### 节点间跳转

`env-access.sh` 是从本机进入目标环境的唯一入口。进入目标环境后, 可以使用节点主机名
执行节点间 SSH; 禁止从本机直接执行该节点间 SSH。

始终使用主机名而非 IP 地址访问其他节点。节点有多个 IP 分布在管理网、
存储网、VXLAN 等多个网平面；`/etc/hosts` 由部署工具维护，解析到当前
可用的正确网络路径。直接使用 IP 可能会指定到有问题的网络，导致误判或
SSH 不通。

```bash
# 正确: 使用主机名访问其他节点(节点间通常已配免密)
ssh node-3 'hostname; whoami; pwd'

# 不要直接用 IP
ssh 32.168.40.2 'command'  # 可能选了存储网而非管理网
```
