# Current Console Discovery

Use this file only as observed console context for the recorded environment and date. Treat it as a page-behavior hint that must be revalidated during a fresh UI run.

本文件记录 2026-06-18 对当前 EasyStack Cloud 控制台的真实页面探索结果。
用于补充 `patterns/` 的通用规则,避免后续大模型再次因页面覆盖、ref 失效、
权限提示或按钮启用条件判断错误而误操作。

## Login And Overview 登录与首页

- 登录页:`/auth_login/?next=%2F`
- 默认成功首页:`/overview`
- 顶部入口:
  - `Overview`
  - `Service Catalog`
  - `English`
  - `Help`
  - 当前用户入口 `<CURRENT_USER>`
- 当前账号登录后首页会展示 Overview 卡片区、Quick Access、User Guides、
  Recent Operations、Platform Information 等模块。
- 首页右上方用户菜单在探索时没有稳定展开,但页面明确存在当前用户入口。

## Service Catalog 服务目录

`Service Catalog` 不是独立业务页,而是覆盖在当前页上的大型导航面板。

### Catalog Groups 已识别一级分组

- Computing
- Product Service Management
- Block Storage
- Observability
- Configurations
- Network
- Operation
- Identity & Access Management
- Monitor & Management

### Catalog Items 已识别二级菜单

- Computing:
  `Instance`、`Instance Snapshot`、`Instance Recycle Bin`、`Instance Group`、
  `Instance Image`、`SSH Key Pair`、`Instance Flavor`、
  `AZ & Host Aggregates`、`Compute Node`
- Block Storage:
  `Volume`、`Volume Snapshot`、`Volume Type`
- Network:
  `Network`、`vNIC`、`Access Control`、`Router`、`NAT Gateway`、
  `Floating IP`、`Layer 2 Bridging`、`Network Topology`、`Network Node`、
  `Network O&M`
- Identity & Access Management:
  `Domain Management`、`Project Management`、`User Management`、`User Group`、
  `Role`、`Policy`、`Application Identity Management`、
  `OAuth Authorization Management`

### Catalog Constraints 服务目录操作限制

- 打开服务目录后,目录面板会覆盖当前业务页。
- 后续点击必须使用“目录面板里的 ref”,不能继续点页面本体里同名元素。
- 服务目录打开时,如果再尝试点击被覆盖的页面元素,`agent-browser` 会正确报
  `covered by <ul/div#products-menu>`;此时应改点目录面板内元素,而不是 force click。

## Observed Modules 已探索模块

### Overview 概览

- 路由:`/overview`
- 用途:平台总览与快捷入口
- 主要内容:
  `Recently Visited Service Catalog`、`Common Resource Tags`、`IAM`、
  `Solutions`、`Platform Information`、`Learn to Build`、`Quick Access`、
  `User Guides`、`Recent Operations`
- 特殊点:
  - 首页存在 `edit` 入口
  - 探索期间页面上方出现过 `View Name` 相关输入与 `Cancel/Save` 区块
  - 该区块会覆盖顶部用户菜单点击区域

### Instance 云主机

- 路由:`/eec/instances`
- 用途:实例列表与批量运维入口
- 列表字段:
  `Name`、`Availability Zone / Node`、`Status / Monitor`、
  `Flavor / Boot Source`、`IP Address`、`Domain / Project`、`Created Time`、`VNC`
- 顶部按钮:
  `Create Instance`、`Start`、`Shutoff`、`Reboot`、`More`、`Export`、`Setup`
- 前置条件:
  - `Start/Shutoff/Reboot/More` 默认需要先勾选行
  - 按钮是否 enabled 还受实例状态影响
- 实测状态变化:
  - 未选中时:`Start/Shutoff/Reboot/More` disabled
  - 单选 `Active` 实例时:`Shutoff/Reboot/More` enabled,`Start` disabled
  - 单选 `Shutoff` 实例时:重新勾选后 `Start` 才 enabled
- `More` 菜单实测文案包括:
  `Pause/Unpause`、`Suspend/Unsuspend`、`Edit Name`、`Resize`、
  `Modify Boot Order`、`Reset Password`、`Enable Agent`、`Clone`、
  `Create Snapshot`、`Snapshot Rollback`、`Edit Tags`、
  `Associate/Disassociate Floating IP`、`Associate/Disassociate Network`、
  `Edit Security Group`、`Manage Virtual IP`、`Attach/Detach Volume`、
  `Mount/Unmount ISO`、`Mount/Unmount USB Device`、
  `Storage Cold Migration`、`Storage Live Migration`、
  `Cold Migrate`、`Live Migrate`、`Evacuate`、`Reset State`、
  `Lock/Unlock`、`Rebuild`、`Delete`
- 自动化重点:
  - 勾选后要重新 snapshot,再读顶部按钮状态
  - `More` 菜单展开后会覆盖表格,若要继续点复选框或别的行,先收起菜单或重载
  - `More` 文案完整集在 `body` 文本中比 interactive snapshot 更全

### Compute Node 计算节点

- 路由:`/eec/hosts`
- 用途:物理计算节点管理
- 列表字段:
  `Name`、`Availability Zone`、`CPU Architecture/Model`、`Status`、
  `vCPU (Used/Total)`、`Memory (Used/Total)`、`Root Disk (Used/Total)`、
  `Number of Instances`、`Number of Devices`、`Enabled`、`Action`
- 页面特点:
  - 无创建按钮
  - 行内动作型页面,主要操作不依赖顶部 checkbox
- 行内动作实测:
  `Instance Batch Live Migration`、`Instance Batch Cold Migration`、`Enable`、`More`

### Volume 云硬盘

- 路由:`/ebs/volumes`
- 用途:云硬盘列表与批量管理
- 列表字段:
  `Name`、`Status`、`Migrate Status`、`Size / Type`、`Shared Volume`、
  `Volume Source`、`Attachments`、`Domain / Project`、`Creation Time`
- 顶部按钮:
  `Create Volume`、`Attach`、`Detach`、`Update Status`、`More`、`Export`、`Setup`
- 前置条件:
  - 未选中时:`Attach/Detach/Update Status/More` disabled
  - 单选 `Available + No Attached` 卷时:`Update Status/More` enabled,
    `Attach/Detach` 仍可能 disabled,不能想当然认为 `Available` 就一定可挂载
- `More` 菜单实测文案:
  `Reset Attach Status`、`Edit`、`Create Snapshot`、`Create Image`、
  `Extend Size`、`Modify Property`、`Migrate`、`Delete`、`Edit Tags`
- 弹窗实测:
  - `Edit Volume` 弹窗字段:
    `Volume Name`、`Description`,按钮 `Save`
  - `Create Volume` 弹窗字段:
    `Volume Name`、`Description`、`Volume Source`、`Type`、`Size`
- 当前环境特殊限制:
  - `Create Volume` 弹窗里 `Type` 出现 `No type available`
  - 即使填了 `Volume Name`,`Create` 仍 disabled
  - 这是页面/环境能力限制,不是填表动作遗漏
- 自动化重点:
  - 列表数据高频刷新,新卷会不断顶掉旧卷位置
  - 不能依赖“当前第 1 行就是刚才那条”

### Floating IP 浮动 IP

- 路由:`/ens/floatingIPs`
- 用途:公网 IP 绑定、解绑、释放和带宽管理
- 列表字段:
  `IP Address`、`Tags`、`Related router`、`Attach Resource`、
  `Bandwidth(Mbps)`、`Floating IP Pool`、`Domain/Project`、
  `Creation Time`、`Action`
- 顶部按钮:
  `Apply For IP To Project`、`Release Floating IPs`、`Export`、`Setup`
- 页面特点:
  - 同时存在顶部批量按钮和行内动作
  - 行内动作会根据是否已绑定显示 `Bind to resource` 或 `Disassociate`
- 勾选规则:
  - 未勾选时顶部 `Release Floating IPs` disabled
  - 勾选后顶部 `Release Floating IPs` enabled
- 行内动作实测:
  - 已绑定行:`Release Floating IPs`、`Disassociate`、`Update Bandwidth`、`More`
  - 未绑定行:`Release Floating IPs`、`Bind to resource`、`Update Bandwidth`、`More`
- 权限限制:
  - 以当前观察账号点击未绑定浮动 IP 的 `Bind to resource` 时,
    页面直接提示:
    `Please do this by re-logging into the console as the project administrator/user to which the resource belongs`
  - 这是产品权限限制,不是自动化点击失败

### User Management 用户管理

- 路由:`/iam/users`
- 用途:用户管理、授权、项目分配、用户组分配
- 列表字段:
  `Name`、`Email`、`ID`、`Domain Belonging`、`Role`、
  `Bind UKey`、`Status`、`AD/LDAP User`
- 顶部按钮:
  `Create User`、`User Invitation`、`Authorize`、`Assign Projects`、
  `Add to User Group`、`More`、`Export`、`Setup`
- 勾选规则实测:
  - 未选中时:`Authorize/Assign Projects/Add to User Group/More` disabled
  - 单选普通用户后:`Authorize`、`Add to User Group`、`More` enabled,
    `Assign Projects` 仍可能 disabled
- `More` 菜单实测:
  `Edit`、`Change Password`、`Delete`
- `Create User` 向导实测:
  - 3 步:
    1. `User Info`
    2. `Authorize`
    3. `Assign Projects`
  - 第一步字段:
    `User Name`、`Email`、`Password`、`Confirm Password`、`Domain`
  - 默认按钮:`Next`

## Historical Observations 已验证的自动化坑点

1. 登录页可见密码框不等于真实提交字段
   必须同时确认隐藏 `#pwd[name="password"]` 被同步。

2. 当前环境登录页存在登录类型切换异常
   可见的是邮箱密码表单,但隐藏 `login_type` 可能仍是 `ukey`,导致直接提交后
   留在登录页。

3. 服务目录是覆盖层,不是普通跳转页
   打开后所有后续点击必须限定在目录面板内。

4. `@eN` ref 不能跨页面、跨 reload、跨 overlay 复用
   本次探索里就发生过原本要点 `Volume`,却因为复用旧 ref 进入了
   `Compute Node`。

5. `More` 菜单展开后会挡住表格
   后续如果想继续点复选框、别的行、顶部按钮,先收起菜单或 reload。

6. interactive snapshot 可能漏掉禁用菜单项
   完整菜单文案常要结合 `get text body` 一起看。

7. `agent-browser` 不是 Playwright
   不支持 `button:has-text(...)` 这类选择器,仍应优先 snapshot/ref、
   `find text`、`find label` 或明确 CSS。
