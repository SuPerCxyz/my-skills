# Execution

## Execution Flow 执行流程

1. 确认 `agent-browser` 可用, 加载 `agent-browser skills get core`。
2. 按 [连接](connection.md) 登录或复用会话, 核对目标项目和本次操作需要的权限与资源。
3. 通过 [原子操作索引](patterns/quick-reference.md) 和 [页面导航](navigation.md) 选择入口。
   根据目标状态和调用方断言执行观察、操作、等待和回读。
4. 按 [结果约定](patterns.md#operation-contract-原子操作调用约定) 返回是否已提交、资源 ID、
   当前状态、最后观察与证据路径。中断后先回读已发生的动作和资源状态, 再决定是否继续。

发布测试调用本执行层时, 使用所传的角色、操作、资源身份、预期和取证要求完成当前动作。

## Core Rules 关键规则

1. 同一稳定页面上的相关动作优先批量完成, 按实际页面/异步边界短段执行并回读.
2. 所有当前执行入口统一使用 `agent-browser`,其他浏览器自动化框架和历史脚本不得作为默认执行路径。
3. 如果本机缺少 `agent-browser`, 未获得安装确认前返回阻塞; 安装或启动失败时不继续
   执行 UI 测试。
4. `/tmp/easystack-env.json` 只保存平台连接、SSH、镜像、网络、规格、卷类型等静态默认值。
5. 环境 JSON 不保存任何历史测试创建的实例、云硬盘、快照、浮动 IP 等运行产物。
6. 资源创建提交后如果轮询未出现或状态未确认,必须记录为
    `creation_unconfirmed`, 先回读页面和已知后台观察信号; 最多换新 run id 重试 1 次,
    第二次仍未确认就停止, 不继续创建或使用该未确认名称.
7. 用户提供的资源名称必须原样使用,不替换为平台上的近似名称。
8. 列表页操作按钮可能在首屏渲染后由权限、配额或数据加载异步放开;创建、
    挂载、删除等动作前必须等待目标按钮 enabled,超时后返回当前项目、按钮状态及相关反馈。
9. 按钮持续 disabled 时,先检查 `.projects-switch-wrapper` 项目是否与请求指定
    的项目或 `resources.project_name` 一致;项目错误不能直接判定为权限或配额问题。
10. 需要探索新模块时,优先记录当前 URL、页面标题、列表字段、顶部按钮、行内动作、
    更多操作、勾选前后按钮状态,再决定是否执行真实提交。
11. 发生操作失败时,不要只记一句“click failed”;至少补齐:
    页面、路径、使用的定位方式、错误现象、截图路径、console、errors、
    network requests、原因分析、修复后的正确做法。
12. 如果菜单、dropdown、service catalog、modal 覆盖了目标元素,优先处理覆盖层,
    不要直接 force click。
13. interactive snapshot 可能漏掉禁用菜单项或纯文本提示;探索更多操作时,必要时
    同时读取 `agent-browser get text body`。
14. 创建云主机连续完成基础配置、网络配置、系统配置和最终确认. 优先使用
    `agent-browser batch`; 页面变更或异步加载需要时使用有界的短 `eval`, 每段内
    Observe -> Act -> Wait -> Verify, 不在每步向用户确认, 不以长 eval 强行跨页.
15. 创建云主机登录凭证优先级:同时设置密码和密钥 > 密码 > 密钥 > 自动生成
    密码并使用密码登录。自动生成密码不得写入报告或环境文件; 仅保存在当前进程
    内存, 必须落盘时使用权限为 `0600` 的本次运行临时文件并在验证后删除。
16. 创建云主机系统盘大小必须在基础配置页的 `*Root Disk` 区域设置,并在进入
    网络配置页前确认页面接受;不要在系统配置页或最终确认页才尝试设置。

## Screenshots And Video 截图与录像

- 默认截图和录像的实际像素均为 **1920×1080**。首次取证前在同一浏览器会话设置
  `agent-browser set viewport 1920 1080 1`, 回读目标标签页后使用视口截图。步骤执行和
  回读后立即保存截图, 页面已变化时可用当时的录像抽帧。
- 录制前检查当前版本的 `record` 支持和 `ffmpeg` 的 WebM 编码能力。准备好页面后用
  `agent-browser record start "$raw_video" --cursor` 开始, 首个有效操作前留出至少 3 秒
  画面。取得最终 UI 结果后立刻 `agent-browser record stop`, 中断也保存已录内容。
- 成片起点为首个有效操作前 **3 秒**, 原录像不足 3 秒时从首帧开始。终点为最后一次
  有效结果回读结束。保留操作、验证和必要等待, 裁去首尾的登录准备、空等和汇报时间。
  用例本身验证登录时, 首次登录动作属于用例证据。
- 原录像已有正确首尾时直接交付。需要裁剪时在实际录像中确定起点和终点, 用两点的
  时间差作为 `clip_duration`, 输出到调用方指定的成片路径。

```bash
ffmpeg -nostdin -n -ss "$clip_start" -i "$raw_video" -t "$clip_duration" \
  -c:v libvpx -crf 12 -b:v 4M "$case_video"
```

- 用 `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x <文件>`
  复核截图和成片的实际像素。核对视频可播放且包含首个操作和最后观察, 并在操作结果记录取证失败
  或实际像素偏差。

- 预览器无法播放 WebM 时, 可用支持 `libx264` 的 FFmpeg 输出 H.264 MP4, 使用
  `-pix_fmt yuv420p -movflags +faststart`。核对成片在目标入口可播放, 返回相对证据路径。

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

最小连接字段和项目选择规则见 [连接说明](connection.md)。运行时沿用
`/tmp/easystack-env.json` 及 `resources.project_name`, 仅使用已核实的静态参数。
操作产物记录在本次操作结果。默认截图路径读取 `screenshot_dir`, 缺省为
`/tmp/easystack-screenshots`。凭据和临时运行数据按实际授权与范围处理。

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

## Page Paths 页面路径

页面路径以 `navigation.md` 的“当前主路径 + 历史/别名路径”表为准。

执行层默认使用当前主路径;历史路径只作为旧文档或历史实现的对照信息。
