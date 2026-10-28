# Execution

本文件承接 EasyStack Cloud Web E2E的执行细节。顶层 `SKILL.md` 只保留入口
路由和硬规则;执行测试或资源操作时再读取本文件。

## Execution Flow 执行流程

1. 检查 `agent-browser` 是否可用; 不可用时报告建议安装命令并等待用户确认。
2. 执行 `agent-browser skills get core`,加载与当前版本匹配的浏览器操作说明。
3. 读取 `/tmp/easystack-env.json` 获取静态环境配置与默认参数。
4. 按 `connection.md` / `patterns/login.md` 准备登录态,并校验左上角项目上下文。
5. 根据任务选择 `patterns/` 原子操作或资源知识库。
6. 将同一用例内的同类页面动作合并到少量 `agent-browser eval --stdin` 或
   `agent-browser batch` 调用。
7. 将新建资源、执行结果和截图路径写入测试报告;不得写回
   `/tmp/easystack-env.json`。
8. 长流程用例之间主动压缩上下文;如果当前客户端支持 `/compact`,优先执行。
9. 如果执行中形成了新的可复用页面操作,按“操作库维护规则”沉淀。

## Core Rules 关键规则

1. 同一稳定页面上的相关动作优先批量完成, 按实际页面/异步边界短段执行并回读.
2. 所有当前执行入口统一使用 `agent-browser`,其他浏览器自动化框架和历史脚本不得作为默认执行路径。
3. 如果本机缺少 `agent-browser`, 未获得安装确认前返回阻塞; 安装或启动失败时不继续
   执行 UI 测试。
4. 截图只用于关键状态确认、失败诊断或用户明确要求。
5. `/tmp/easystack-env.json` 只保存平台连接、SSH、镜像、网络、规格、卷类型等静态默认值。
6. 环境 JSON 不保存任何历史测试创建的实例、云硬盘、快照、浮动 IP 等运行产物。
7. 用例参数优先级:显式参数 > `/tmp/easystack-env.json` > 页面默认值。
8. 每个用例必须创建新的资源,不复用之前用例创建的测试资源。
9. 每个用例创建的资源名称必须唯一,推荐格式为 `<case-id>-<resource-type>-<timestamp-or-runid>`。
10. 用例前置条件写“已存在云主机 vm1”“已创建云硬盘 volume”等资源时,
    默认解释为“本用例执行过程中需要先新建这些资源”,不得从环境历史资源、
    报告、`test_resources` 或列表中挑选已有资源替代。
11. 只有用户在当前对话中明确允许复用某个资源名时,才可复用;否则必须
    使用新的 run id 通过 UI 创建。
12. 用户提供的逻辑名如 `vm1`、`volume1` 应映射为本次唯一资源名,例如
    `<case-id>-vm1-<runid>`,报告中同时记录逻辑名和实际资源名。
13. 资源创建提交后如果轮询未出现或状态未确认,必须记录为
    `creation_unconfirmed`, 先回读页面和已知后台观察信号; 最多换新 run id 重试 1 次,
    第二次仍未确认就停止, 不继续创建或使用该未确认名称.
14. 用户提供的资源名称必须原样使用,不替换为平台上的近似名称。
15. 如果页面中找不到精确匹配项,应返回失败结果并提示确认。
16. 独立 E2E 用例默认创建新资源; 用户明确要求操作现有资源并提供精确名称时,
    可以复用该资源, 但必须先验证项目、名称、当前状态和操作影响。
17. 测试中所有可原子化的操作必须从 `patterns/` 调用,不在用例中重复编写页面交互逻辑。
18. 列表页操作按钮可能在首屏渲染后由权限、配额或数据加载异步放开;创建、
    挂载、删除等动作前必须等待目标按钮 enabled,超时后才判定为环境阻塞。
19. 按钮持续 disabled 时,先检查 `.projects-switch-wrapper` 项目是否与用例
    或 `resources.project_name` 一致;项目错误不能直接判定为权限或配额问题。
20. 需要探索新模块时,优先记录当前 URL、页面标题、列表字段、顶部按钮、行内动作、
    更多操作、勾选前后按钮状态,再决定是否执行真实提交。
21. 发生操作失败时,不要只记一句“click failed”;至少补齐:
    页面、路径、使用的定位方式、错误现象、截图路径、console、errors、
    network requests、原因分析、修复后的正确做法。
22. 如果菜单、dropdown、service catalog、modal 覆盖了目标元素,优先处理覆盖层,
    不要直接 force click。
23. interactive snapshot 可能漏掉禁用菜单项或纯文本提示;探索更多操作时,必要时
    同时读取 `agent-browser get text body`。
24. 创建云主机连续完成基础配置、网络配置、系统配置和最终确认. 优先使用
    `agent-browser batch`; 页面变更或异步加载需要时使用有界的短 `eval`, 每段内
    Observe -> Act -> Wait -> Verify, 不在每步向用户确认, 不以长 eval 强行跨页.
25. 创建云主机登录凭证优先级:同时设置密码和密钥 > 密码 > 密钥 > 自动生成
    密码并使用密码登录。自动生成密码不得写入报告或环境文件; 仅保存在当前进程
    内存, 必须落盘时使用权限为 `0600` 的本次运行临时文件并在验证后删除。
26. 创建云主机系统盘大小必须在基础配置页的 `*Root Disk` 区域设置,并在进入
    网络配置页前确认页面接受;不要在系统配置页或最终确认页才尝试设置。
27. 长耗时用例需要后台执行时:
    - 不在 skill 中固定模型名称或推理等级。
    - 按当前会话 `AGENTS.md`、用户要求和平台可用能力选择。
28. 子任务无法满足当前平台的模型或推理配置时, 返回主会话串行执行, 不自行改用
    某个固定模型。
29. 长耗时用例被取消、中断或切回主任务后,不得假设最后一个异步动作成功;
    必须重新通过页面列表确认资源状态后再继续、清理或下结论。
30. 用户取消测试时只整理已验证事实、已创建资源、最后确认点和可沉淀规则;
    未经用户明确要求,不继续执行后续步骤,也不主动清理测试资源。
31. 清理资源前必须先向用户说明待清理资源清单、清理顺序和影响范围;未得到
    用户明确确认时,不主动删除实例、浮动 IP、云硬盘、快照等资源,只在报告
    标记 `cleanup: recommended`。

## Background Task Policy 后台任务策略

- 适用场景:fio 大数据写入、快照链创建、长时间轮询、性能耗时统计等。
- 不在 skill 中固定模型名称或推理等级。
- 按当前会话 `AGENTS.md`、用户要求和平台可用能力选择。
- 后台任务只负责执行指定用例、写报告和返回结果;不要修改 skill 文档。
- 发现可沉淀操作时,在最终结果中列出 `skill_improvements`,由主会话统一更新
  操作库,避免后台任务与主会话写冲突。

## Operation Maintenance 操作库维护规则

执行过程中发现以下情况时, 在报告中记录 `skill_improvements`。只有当前任务明确包含
skill 维护, 或用户随后确认更新时, 才修改 skill 文档:

- 同一页面动作可能被多个用例复用。
- 操作包含 3 步以上稳定页面交互。
- 操作会创建、修改、删除或绑定平台资源。
- 操作已经通过一次真实 UI 执行或静态逻辑确认,具备沉淀价值。

更新步骤:

1. 选择资源域文档:实例写入 `patterns/instance-ops.md`, 云硬盘写入
   `patterns/volume-ops.md`, 镜像写入 `patterns/image-ops.md`, 网络写入 `patterns/network-ops.md`.
2. 按 `patterns/operation-template.md` 补齐:用途、参数、前置条件、成功判定、
   执行步骤概览、失败信号、返回值约定、`agent-browser eval --stdin` 示例。
3. 如果只是识别出操作但尚未完成模板,先加入该文档的 `待迁移操作` 清单。
4. 同步 `patterns/quick-reference.md`,把状态标成 `ready-template`、
   `ready-validated` 或 `planned`。
5. 重新检查不含非 `agent-browser` 示例;测试环境凭据只允许存在于运行时
   环境文件或调用参数中,不写入 skill 文档、操作库模板或测试报告。

## Configuration 环境配置

基础登录字段以 `connection.md` 为准:

- `platform.url`
- `platform.username`
- `platform.password`

推荐结构。该文件不得包含 `test_resources` 或任何历史测试资源名:

```json
{
  "platform": {
    "url": "https://example.local",
    "username": "<USERNAME>",
    "password": "<PASSWORD>"
  },
  "ssh": {
    "user": "root",
    "fallback_users": ["centos", "ubuntu"],
    "password": "<PASSWORD>",
    "key_name": "<KEY_NAME>",
    "key_file": null
  },
  "screenshot_dir": "/tmp/easystack-screenshots",
  "resources": {
    "project_name": "<PROJECT_NAME>",
    "image_name": "<IMAGE_NAME>",
    "network_name": "<NETWORK_NAME>",
    "subnet_name": "<SUBNET_NAME>",
    "flavor": "4C-8G-100G",
    "volume_type": "<VOLUME_TYPE>"
  },
  "vm_defaults": {
    "password": "<PASSWORD>",
    "setup_key": true
  }
}
```

## Run Artifacts 运行产物记录

- 新建资源、执行状态、截图路径和清理建议只写入测试报告。
- 报告必须区分 `logical_name` 与 `actual_name`,例如逻辑 `vm1` 对应
  实际 `<case-id>-vm1-<runid>`。
- 未确认创建成功的资源也要记录到 `unconfirmed_resources[]`,并写明需要
  通过 UI 列表重新确认或清理。
- 长耗时用例取消或中断时,也必须记录当前已创建资源、已完成阶段、最后一个
  可恢复检查点和用户允许继续/清理的建议。
- 中断发生在提交弹窗、异步创建、后台轮询或 SSH 长命令期间时,报告必须标明
  “未确认最终状态”,并列出需要通过 UI 重新确认的资源名和页面路径。
- 截图根目录优先使用 `/tmp/easystack-env.json` 中的 `screenshot_dir`。
- 未配置 `screenshot_dir` 时,默认使用 `/tmp/easystack-screenshots`。
- 推荐报告路径:`<screenshot_dir>/test_report.json`。
- 报告中记录的资源只服务本次运行,不作为后续用例默认输入。
- 后续用例如需同类资源,应重新创建,而不是读取历史报告或环境 JSON 复用。
- 对未清理资源,报告必须写明 `cleanup: recommended`、资源类型、资源名、
  是否仍绑定,以及建议清理顺序。

## Required Fields 必填字段提示

| 必填字段 | 缺失时提示 |
|----------|-----------|
| `platform.url` | 请提供平台地址 |
| `platform.username` | 请提供登录用户名 |
| `platform.password` | 请提供登录密码 |
| `resources.image_name` | 请提供镜像名称 |
| `resources.network_name` | 请提供网络名称 |
| `resources.flavor` | 请提供实例规格 |
| `ssh.user` | 请提供 VM SSH 用户名 |

## SSH 连接策略

1. 优先使用密钥连接:`ssh -i <key_file>`。
2. 密钥连接失败时使用密码连接。
3. 首选用户失败后尝试 `fallback_users`。

用户未提供 `key_file` 时,不指定密钥路径,仅用密码连接。

## VM Defaults 创建 VM 默认行为

| 项目 | 默认值 | 说明 |
|------|--------|------|
| 登录凭证 | 同时设置 > 密码 > 密钥 > 自动生成密码 | 同时存在 `vm_defaults.password` 和 `ssh.key_name` 时选择 Both |
| 密码 | `vm_defaults.password` | 未提供密码但需要密码登录时自动生成运行时密码 |
| 密钥 | `ssh.key_name` | 仅无密码但存在密钥时使用 SSH Key Pair |
| 规格 | `resources.flavor` | 如 `4C-8G-100G` |

## Screenshots And Reports 截图与报告

- 截图目录:`<screenshot_dir>/<用例名>/`
- 全局报告:`<screenshot_dir>/test_report.json`
- 报告至少记录:用例名、开始时间、结束时间、状态、错误信息、截图路径。

## Page Paths 页面路径

页面路径以 `navigation.md` 的“当前主路径 + 历史/别名路径”表为准。

执行层默认使用当前主路径;历史路径只作为旧文档或历史实现的对照信息。
