# IAM Provisioning 部门/项目/用户与配额

本文件记录 EasyStack 控制台后台开通**部门（domain）、项目、用户、member 角色和资源配额**的操作方法。适用于需要批量准备测试租户、又不想逐页点击控制台的场景。

## 1. 适用范围与前提

- 部门 = Keystone **domain**；项目 = 该 domain 下的 project；用户 = 该 domain 下的 user。
- 接口是控制台 IAM API（`/apis/iam/v1/*` 和 `/ecs/api/*`），不是 `/openrc` 的 v2 Keystone。
- 必须使用**云管理员控制台会话**（浏览器 cookie）：
  - 同源 `fetch` 会自动带 cookie；
  - 用 curl 时需带 `sessionid` cookie 和 `X-Requested-With: XMLHttpRequest`；POST/PUT 若返回 403，补 `X-CSRFToken`（值取 cookie `csrftoken`）。
- 不同环境的管理员账号不同。172.34/43/44 的 `admin@example.org` 与 100.100.4.11 不通用，执行前先确认各环境管理员会话。

### 1.1 测试账号配对（必须）

每个测试环境至少准备两个账号，缺一不可：

| 账号 | 角色 | 用途 |
|---|---|---|
| 普通用户 | 项目 member | 默认执行用例、创建/查询/删除测试资源 |
| 管理员 | 云管理员/部门管理员 | 分配配额、类型管理、存储迁移、权限前置 |

- 默认用普通用户执行；普通用户配额不足时，先由管理员分配配额并回读，再回到普通用户继续。
- 管理员不替代普通用户的用例步骤，也不改变用例语义。
- 结果中记录管理员操作的对象、原因和修改前后配额值；密码不落盘。

## 2. 查询接口（已验证）

| 用途 | 方法 | 路径 |
|---|---|---|
| 部门列表 | GET | `/apis/iam/v1/domains` |
| 项目列表 | GET | `/apis/iam/v1/projects` |
| 用户列表 | GET | `/apis/iam/v1/users` |
| 项目配额 | GET | `/ecs/api/usage/projectquota/{project_id}/` |
| 部门配额 | GET | `/ecs/api/usage/domainquota/{domain_id}/` |
| 项目用户/角色 | GET | `/apis/iam/v1/project_user_role/{project_id}` |

请求头：

```text
X-Requested-With: XMLHttpRequest
Content-Type: application/json
```

## 3. 创建顺序

### 3.1 创建部门（domain）

```http
POST /apis/iam/v1/domains
{"name":"pgc","description":"pgc department","enabled":true}
```

返回 `data.id` 即 `domain_id`。

### 3.2 创建项目

```http
POST /apis/iam/v1/projects
{"name":"pgc","description":"pgc project","parent_id":"<domain_id>","enabled":true}
```

`parent_id` 必须是部门 domain ID，不是部门名称。

返回 `data.id` 即 `project_id`。

### 3.3 创建用户

```http
POST /apis/iam/v1/users
{"domain_id":"<domain_id>","name":"pgc","email":"pgc@qq.com","password":"<password>","enabled":true}
```

返回 `data.id` 即 `user_id`。邮箱需唯一；密码按环境密码策略。

### 3.4 授予部门角色（登录与加入项目的前置）

只创建用户不够。没有部门角色时：
- 控制台登录会报“用户名或密码错误”；
- 项目访问控制里的用户复选框是禁用的，并提示“用户必须有角色信息才能添加到项目中”。

```http
PATCH /apis/iam/v1/users/{user_id}/roles?domain_id={domain_id}
{"new":[{"id":"<role_id>","name":"member","type":"","description":""}],"original":[]}
```

- 普通用户 = `member`；部门管理员 = `domain_admin`；项目管理员 = `project_admin`。
- 用例要求项目 member 时，部门角色选 `member`（普通用户），不要选管理员角色。
- 角色 ID 从 `GET /apis/iam/v1/roles` 获取；`member` 的 `display=true`。

### 3.5 分配项目

```http
PATCH /apis/iam/v1/users/{user_id}/projects?domain_id={domain_id}
{"new":[{"id":"<project_id>","name":"pgc"}],"original":[]}
```

回读 `GET /apis/iam/v1/users/{user_id}/projects`，或登录后看 `/apis/iam/v1/accountInfo` 的 `projects`。

### 3.6 项目内 member 角色

```http
GET   /apis/iam/v1/project_user_role/{project_id}?domain_id={domain_id}&page=1&page_size=100
PATCH /apis/iam/v1/project_user_role/{project_id}
{"new":[{"user_id":"<user_id>","user_name":"pgc","role":[{"name":"member","id":"<member_role_id>","type":"","description":""}]}],"original":[]}
```

如果 PATCH 返回 200 但 `selected` 仍为空，优先走控制台 UI：项目 → 勾选项目 → 访问控制 → 选择用户 → 确认。`/ecs/api/keystone/projects/...` 在部分版本不存在（404），不要依赖。

### 3.7 分配配额

优先用后台 CLI（`drone` 对已知 project_id 可操作配额）：

```bash
# 计算：注意 nova quota-update 的 project 是位置参数，不是 --tenant
nova quota-update <project_id> --instances 20 --cores 30 --ram 65536 --key-pairs 10
# 块存储
cinder quota-update --volumes 500 --gigabytes 20000 --snapshots 500 <project_id>
cinder quota-update --volume-type hdd --volumes 500 --gigabytes 20000 --snapshots 500 <project_id>
cinder quota-update --volume-type alcubierre-tcp --volumes 500 --gigabytes 20000 --snapshots 500 <project_id>
# 网络
neutron quota-update --tenant-id <project_id> --floatingip 50 --security-group 20 --network 20
```

也可用控制台配额 API：

```http
# 项目配额更新（路径按 domain 配额模式推导，执行前先 GET 确认字段）
POST /ecs/api/usage/projectquota/{project_id}/updateprojectquota
{"items":[{"cloud_product_name":"nova","name":"instances","quota":20}]}

# 部门配额
POST /ecs/api/usage/domainquota/{domain_id}/updatedomainquota
{"items":[{"cloud_product_name":"nova","name":"instances","quota":20}]}
```

项目配额 GET 返回结构：

```json
{"items":[{"usage":{"available":8,"used":12,"quota":20},"cloud_product_name":"nova","name":"instances"}]}
```

## 4. 使用 agent-browser 执行

登录云管理员后，在同源页面执行：

```js
const h = {'X-Requested-With':'XMLHttpRequest','Content-Type':'application/json'};
const domain = await (await fetch('/apis/iam/v1/domains',{headers:h})).json();
// POST 示例
await fetch('/apis/iam/v1/domains',{
  method:'POST', headers:h,
  body:JSON.stringify({name:'pgc',description:'pgc department',enabled:true})
});
```

执行前先 GET 列表确认名称不冲突；创建后回读 `domains/projects/users` 和 `projectquota`。

## 5. 校验清单

1. `GET /apis/iam/v1/domains` 能看到部门，`enabled=true`。
2. `GET /apis/iam/v1/projects` 中项目的 `domain_id` 正确。
3. `GET /apis/iam/v1/users` 中用户 `domain_id`、`email` 正确，且部门角色已设置。
4. `GET /apis/iam/v1/users/{user_id}/projects` 或登录后的 `accountInfo.projects` 包含目标项目。
5. `GET /apis/iam/v1/project_user_role/{project_id}?domain_id=...` 中用户角色为 `member`（普通用户）。
6. `GET /ecs/api/usage/projectquota/{project_id}/` 配额符合预期。
7. 用新用户邮箱 + 密码登录控制台，确认落在 `/overview`，项目上下文正确，能创建/查看被授权的资源。

## 6. 已知问题与边界

- **只创建用户不够**：必须先给用户授予部门角色（普通用户/member），否则控制台登录报“用户名或密码错误”，项目访问控制里的用户复选框也会禁用，提示“用户必须有角色信息才能添加到项目中”。
- `/openrc` 使用 Keystone **v2.0**，`openstack domain/user/role` 命令不可用；改用 v3 时 `drone` 账号缺少 `identity:list_domains`、`identity:create_domain` 等权限，返回 403。
- 后台 `drone` 的 Keystone token 调 `/apis/iam/v1/domains` 返回 401；IAM API 只接受控制台会话，不接受普通 Keystone token。
- 因此**身份开通必须用控制台管理员会话**；配额可用后台 CLI（已知 project_id）或控制台配额 API。
- `/ecs/api/keystone/projects/{project}/{user}/{role}` 在部分版本返回 404；项目成员关系优先用 `/apis/iam/v1/project_user_role/{project_id}` 或控制台“访问控制”页面。
- `nova quota-update` 的 project 是位置参数；`openstack quota set <project>` 可能因 `identity:list_projects` 403 失败，直接用 `nova/cinder/neutron` 子命令更稳。
- 172.x 环境控制台地址为 `https://172.x.0.2/`，管理员账号需单独确认；不要复用其他环境密码。
- 管理员密码、session cookie、CSRF token 不写入结果 md、汇总或 skill 文档。
