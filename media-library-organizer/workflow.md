# 工作流程

Use this file as the ordered execution flow for media organization. Read the specialized files only when a step needs naming, NFO, artwork, TMDB, technical parsing, configuration, or safety details.

## 流程概览

```
用户提供路径
  → 步骤1: 扫描路径，识别所有待处理的资源
  → 步骤2: 对每个资源分析文件结构 + 判断媒体类型
  → 步骤3: 从 TMDB 获取元数据
  → 步骤4: 生成完整预览(不改文件)
  → 步骤5: 用户明确确认后执行
  → 步骤6: 生成 mapping / rollback 后执行重命名
  → 步骤7: 生成 NFO 文件
  → 步骤8: 下载图片(含别名 hardlink)
  → 步骤9: 完成 mapping + 校验回滚能力
```

## 步骤1: 扫描路径

- 如果路径下只有 **1 个主视频文件** → 单资源
- 如果路径下有 **多个视频文件**，需要继续判断:
  - 如果文件名包含同一剧集的 `SxxExx` / `EPxx` / `第X集` / `第X期` / 日期期号 → 按单个剧集资源处理
  - 如果多个视频文件分别像不同电影，且没有共同剧集特征 → 按多个电影资源处理
  - 如果无法判断，必须在预览中列出候选分组，让用户确认
- 字幕、NFO、图片、txt、url 不参与资源数量判断，只作为附属文件处理
- 如果路径下包含多个子文件夹 → 多资源，逐个处理
- 每个子文件夹独立判断类型
- 只扫描用户指定的 source root; 发现嵌套媒体库或多个候选 root 时, 不自动扩大到父目录
- root 为空或没有主视频文件时, 停止并报告空结果, 不生成真实执行计划
- 对所有路径执行 `realpath` 校验，避免 `../` 路径逃逸
- 禁止处理系统根目录 `/`
- 禁止处理用户 home 根目录
- 禁止处理 `/bin`、`/etc`、`/usr`、`/var`、`/boot`、`/dev`、`/proc`、`/sys`
- 禁止跟随符号链接到输入路径之外
- 所有目标路径必须位于用户指定的媒体库根目录或 staging 目录内

## 步骤2: 媒体类型判断

**判断优先级:**

1. 用户显式指定 `media_type=movie / tv / variety / documentary / anime`
2. 文件名是否包含 `SxxExx`、`E01`、`EP01`、`第01集`、`第1期`、`20240601` 等剧集特征
3. 目录名是否包含 `Season`、`S01`、`第1季`、`第一季`
4. TMDB 搜索结果 `movie / tv` 的匹配度
5. 单文件默认电影，但如果命中「第X集 / 第X期 / EPxx / SxxExx」，仍按剧集处理
6. 多文件不一定是剧集;如果只有一个主视频 + 花絮 / 预告 / 字幕 / 样片，应按电影处理

**需要考虑的特殊情况:**
- 电影 + 花絮 → 电影主文件进电影目录，花絮进 Extra 子目录
- 电影 + 字幕 → 字幕文件跟随主视频重命名，保持 basename 一致，保留语言后缀
- 电影 CD1/CD2 → 合并为一个条目，文件名加 `-CD1` / `-CD2`
- 综艺一期一个文件 → 按剧集处理，Season-01
- 纪录片单集 → 按剧集处理
- 电视剧只有一集 → 按剧集处理，Season-01
- 动画剧场版 → 按电影处理

## 步骤3: 获取 TMDB 数据

详见 `tmdb-api.md`。

**TMDB API Key:**
- 优先读取环境变量 `TMDB_API_KEY`
- 其次读取 Skill 配置中的 `tmdb_api_key`
- 如果没有 API Key，则禁止直接调用 TMDB API
- API Key 不得写入日志、预览、NFO、映射文件或回滚脚本

**TMDB 获取优先级:**

1. 用户显式提供 `tmdb_id` → 直接使用
2. 文件夹名 / 文件名搜索 → 返回候选列表
3. 置信度高于阈值(≥80%)才自动选择
4. 多个候选相似时必须生成候选预览，让用户确认
5. 禁止在低置信度下直接改名
6. API 返回空结果、鉴权失败或明确不可用时, 才允许按 `tmdb-api.md` 查询网页 fallback;
   网页结果标记 `source=web` 和 `confidence`
7. API 与网页候选冲突时停止自动选择并让用户确认; 两者均失败时标记 `guessed` /
   `unknown`, 仅保留 dry-run

**从 TMDB 获取以下信息:**

**通用信息:**
- 中文标题 / 原标题
- 年份 / 首播日期
- 类型(类型)
- 国家 / 地区
- 语言
- 简介(plot)
- 评分(vote_average)
- 演员列表
- 导演 / 主创
- 标签(keywords)
- 海报 URL(poster)
- 背景图 URL(fanart/backdrop)

**剧集额外信息:**
- 每集中文标题
- 每集播出日期
- 每集剧情简介
- 每集剧照 URL(still)

## 步骤4: 生成预览

预览必须包含以下内容:

```
1. 资源识别结果
   - 类型:movie / tv / variety / documentary / anime
   - TMDB ID
   - 匹配置信度
   - 标题 / 原标题 / 年份

2. 文件变更映射
   old_path -> new_path

3. NFO 生成列表
   - tvshow.nfo
   - episode同名.nfo
   - movie同名.nfo
   - season.nfo(如果启用)

4. 图片下载列表
   - poster
   - fanart
   - banner
   - clearlogo
   - season poster
   - episode still

5. 风险提示
   - 无法匹配 TMDB 的文件
   - TMDB 匹配置信度不足
   - 目标路径冲突
   - 缺失剧集标题
   - 缺失剧照
   - 技术信息无法检测
   - 字段来自猜测(标记为 guessed)

6. 执行绑定
   - source root
   - execution options
   - source inventory(size + mtime)
   - `plan_id`:由 `python3 scripts/plan-gate.py build` 对 normalized roots、options、
     inventory 和 mappings 计算 canonical JSON SHA-256
```

**预览不改任何文件。**

Plan input 使用 JSON object, 至少包含 `source_root`、`media_root`、`target_root`、
`options` 和 `mappings`。Plan artifact 必须保存在 `source_root` 外:

```bash
python3 scripts/plan-gate.py build --input <PLAN_INPUT_JSON> --output <PLAN_JSON>
```

## 步骤5: 用户确认

- 用户看到当前预览后明确回复 `确认执行 <plan_id>` 或 `apply <plan_id>` 后才执行
- 如有问题可调整参数后重新预览
- 参数、source inventory 或目标映射变化后原确认失效, 必须生成新预览
- 禁止接受未携带当前 `plan_id` 的回复
- 真实修改前运行 `python3 scripts/plan-gate.py validate --plan <PLAN_JSON>`; 返回的
  `plan_id` 必须与用户确认完全一致

## 步骤6: 准备回滚并执行重命名

**执行模式:**

支持两种执行模式:

**direct(默认):**
- 原地移动 / 重命名
- 适合普通整理
- 必须依赖 `_rename_mapping.json` 和 `_rollback.sh`

**staging:**
- 先整理到临时 staging 目录
- NFO 和图片都在 staging 中生成
- 校验完成后再切换到目标目录
- 跨文件系统时不能依赖原子 rename，必须明确记录 copy / move 行为

用户设置 `execution_mode=staging` 时使用 staging。

**执行顺序:**

1. 重新计算预览绑定内容, 确认 hash 等于用户确认的 `plan_id`
2. 创建包含全部计划操作和 `plan_id` 的 `_rename_mapping.json`
3. 根据 mapping 生成 `_rollback.sh`, 并通过 `bash _rollback.sh` 先执行 rollback dry-run 校验
4. 按映射执行移动 / 重命名, 成功后原子更新 operation 状态
5. 生成 NFO 前记录 `create` operation, 成功后记录 hash 和 `completed`
6. 下载图片前记录 `create` operation, 成功后记录 hash 和 `completed`
7. 删除空目录前记录 `rmdir` operation, 并再次确认目录为空
8. 校验结果和 mapping 状态
9. 再次通过 `bash _rollback.sh` 执行 rollback dry-run, 确认所有已完成操作均可回滚

**文件名安全清洗:**

生成任何目录名或文件名前，必须清洗非法字符:

- `/ \ : * ? " < > |` 替换为 `-`
- 中文冒号 `:` 替换为 `-`
- 多个空格压缩为一个空格
- 连续多个 `-` 压缩为一个 `-`
- 删除首尾空格、点号和横杠
- 单个文件名长度不超过 240 字符
- 路径总长度过长时，优先缩短 episode title，不缩短 SxxExx
- 不允许生成空文件名;清洗后为空时使用 `unknown`

**目标路径冲突处理:**
- 目标路径已存在时禁止覆盖
- 自动生成冲突报告
- 可选策略:
  1. `skip`:跳过(默认)
  2. `suffix`:追加 `-dup1` / `-dup2`
  3. `replace`:只有用户明确确认后才允许覆盖

**已存在附属文件处理规则:**
- 已存在的 NFO 不允许直接覆盖
- 已存在的 `poster.jpg` / `fanart.jpg` / `banner.jpg` / `clearlogo.png` 不允许直接覆盖
- 如果需要生成同名文件，默认跳过
- 如果用户明确允许 `replace`，则覆盖前必须先备份
- 备份目录为 `_backup_before_rename_{timestamp}`
- 备份文件路径必须写入 `_rename_mapping.json`
- 回滚时只恢复本次备份的文件，不删除用户后来新增的文件

**综艺识别规则:**
- 优先从文件名提取「期号 / 日期 / 上中下 / 加更 / 纯享 / 会员版 / 花絮 / 预告」
- 正片进入真实 Season
- 加更、特辑、花絮、预告、重逢篇、聚会、集结进入 Season-00
- Season-00 文件名必须保留来源季号和特殊类型
- 如果 TMDB 没有对应 episode title，使用本地解析标题，不强行覆盖

**外挂字幕处理:**

- 字幕文件不单独作为媒体资源
- 字幕文件必须绑定到对应主视频
- 字幕文件必须跟随主视频重命名
- 保持与主视频相同 basename
- 保留语言后缀，例如 `zh-CN` / `zh` / `en` / `ja` / `chs` / `cht`
- 如果无法识别字幕语言，保留原语言标签或原后缀
- 禁止丢弃字幕文件
- 禁止把字幕文件移动到与主视频不同的目录

示例:
```
Movie.mkv
Movie.zh-CN.srt
Movie.en.srt

Show-S01E01.mkv
Show-S01E01.zh-CN.srt
Show-S01E01.en.ass
```

## 步骤7: 生成 NFO

详见 `nfo-templates.md`。

**电影 NFO:**
- 默认生成与视频同名的 `.nfo`(如 `阿凡达-Avatar(2009)-2160p-HEVC-HDR10--BluRay-7.1.nfo`)
- 可选额外生成 `movie.nfo`
- 默认以 Kodi / tmm 兼容格式为主

**剧集 NFO:**
- 根目录生成 `tvshow.nfo`
- 每集生成与视频同名的 `.nfo`
- `season.nfo` 可选生成，不作为刮削成功的必要条件

**重要:** Kodi / Jellyfin / Emby 对剧集识别仍然依赖文件名中的 `SxxExx`。即使生成 NFO，剧集文件名也必须保留标准季集号。

## 步骤8: 下载图片

详见 `artwork.md`。

**并发下载策略:**
- 如果当前环境支持子代理 / Task / Workflow，则每个资源分配一个子任务
- 如果不支持，则使用 Python asyncio / ThreadPoolExecutor 并发下载
- 最大并发数默认 4，可通过 `max_workers` 参数调整
- 所有下载失败必须记录，不能阻断重命名主流程

## 步骤9: 完成 mapping + 校验回滚能力

详见 `safety.md`。

**校验策略:**
- 默认记录 `size` + `mtime`
- mapping 中使用 `hash_type` + `hash` 字段，不固定使用 sha256
- `hash_type` 取值:`none` / `quick_hash` / `sha256`
- 小于 1GB 的文件可计算完整 sha256(`hash_type=sha256`)
- 大于 1GB 的文件默认使用 quick_hash，读取文件头尾各 64MB(`hash_type=quick_hash`)
- 用户设置 `full_hash=true` 时统一使用 sha256
- 如果只记录 size + mtime:`hash_type=none`, `hash=null`

**回滚要求:**
- 所有计划操作必须在真实修改前写入 `_rename_mapping.json`
- JSON 记录 `old_path`、`new_path`、`hash_type`、`hash`、`size`、`mtime`、
  `operation`、`status`、`timestamp`
- operation 至少支持 `rename`、`move`、`create`、`replace_backup`、`rmdir`
- 回滚只删除 mapping 中状态为 `completed` 且 hash 匹配的本次新建文件
- 替换已有文件时从本次备份恢复; 删除的空目录按 mapping 重建
- 如果目标路径被其他文件占用或校验不匹配, 回滚中止并提示人工处理
- `_rollback.sh` 必须在真实修改前生成并支持 dry-run
