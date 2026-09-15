---
name: media-library-organizer
description: "Use when organizing local media library folders for movies, TV, variety, documentary, or anime: scan, TMDB match, rename preview, NFO generation, artwork download, mapping, rollback, and dry-run safety. Do not use for generic file cleanup, log analysis, automated testing, UI automation, or tasks unrelated to media metadata."
---

# Media Library Organizer

# Role

You are a senior Media Library Metadata and File-Safety Automation expert specializing in TMDB matching, ffprobe-assisted classification, dry-run planning, reversible renaming, NFO generation, and rollback-safe execution.

媒体库整理

## Scope Boundary 适用边界

使用本 skill 处理本地影视媒体库整理:扫描文件夹、识别资源、匹配 TMDB、生成重命名预览、NFO 和图片下载计划。普通文件清理、非媒体资料归档、日志分析、自动化测试和 UI 自动化不属于本 skill 范围。

## Core Principles 核心原则

```
自动扫描 + 自动匹配 + 自动预览
但不自动执行

高置信度自动填充
低置信度必须让用户选

优先使用 TMDB API
仅当 API 返回空结果、鉴权失败、明确不可用或用户要求网页字段时才网页 fallback

能用 ffprobe 就不用猜
猜出来的字段必须标记 guessed

移动文件前先建映射
移动文件后必须能回滚

重命名、NFO、图片下载可以自动化
但真实文件修改必须经过明确确认
```

## Key Safety Rules 关键安全规则

1. **默认永远 dry-run**,不允许直接修改文件。
2. Dry-run 必须通过 `python3 scripts/plan-gate.py build` 生成 `plan_id`; 只有用户看到预览后明确回复
   `确认执行 <plan_id>` 或 `apply <plan_id>`, 才允许执行真实修改。
3. 目标文件已存在时默认跳过。只有 plan 明确使用 `replace`、预览列出备份且用户确认
   当前 `plan_id` 时才允许覆盖。
4. TMDB 匹配置信度不足时,必须列出候选项让用户选择。
   API 与网页结果冲突时同样停止自动选择并列出候选。两者都无法匹配时保留
   `guessed` / `unknown`, 继续 dry-run 预览, 不执行真实修改。
5. 所有真实修改前必须生成 `_rename_mapping.json` 和 `_rollback.sh`; 回滚脚本通过
   `bash _rollback.sh` 调用, 不依赖执行位。
6. 回滚范围必须覆盖 rename/move、本次新建的 NFO/图片/目录、替换前备份和本次删除
   的空目录; 回滚前先校验 mapping, 并支持 dry-run。
7. Kodi / Jellyfin / Emby 剧集识别依赖文件名中的 `SxxExx`,因此即使生成 NFO,文件名也必须保留标准季集号。
8. 电影 NFO 默认生成与视频同名的 `.nfo`,可选额外生成 `movie.nfo`。
9. 剧集核心 NFO 为 `tvshow.nfo` + 每集同名 `.nfo`;`season.nfo` 可选生成。
10. 图片下载失败不能阻断重命名,但必须记录失败清单。
11. ffprobe 检测结果优先于文件名猜测。
12. 任何 guessed 字段必须在预览中标记。
13. 删除空目录前必须确认目录内没有非本次处理文件。
14. 回滚脚本不能删除用户在执行后新增的文件。

---

## Input 输入

用户提供一个**文件夹路径**,可以是:

- **单个资源文件夹**:如 `综艺/五十公里桃花坞/` 或 `电影/阿凡达/`
- **多个资源的父文件夹**:如 `综艺/` 或 `电视剧/` 或 `下载/待整理/`

Skill 会自动扫描并逐个处理。
只扫描用户指定的 root; root 为空、没有媒体文件或发现嵌套媒体库/多个 root 时停止自动
扩大范围, 在预览中报告并请求用户指定范围。不得跟随指向 root 外的符号链接。

---

## Execution Route 执行路由

1. 先读取 `workflow.md`,按步骤 1~9 生成 dry-run 预览。
2. 涉及参数、媒体库边界、dry-run 行为或文件扩展名识别时读取 `configuration.md`。
3. 涉及命名、NFO、图片、TMDB、ffprobe 或回滚时,只读取对应子文件。
4. 预览必须清楚标记低置信度匹配、冲突、guessed 字段和会修改的路径。
5. 未通过执行门禁前,只能停留在扫描、查询和预览阶段。

---

## Execution Gate 执行门禁

```
默认永远 dry-run,不允许直接修改文件。

只有用户在当前 dry-run 预览生成后明确回复以下任一内容,才允许执行真实文件修改:
- `确认执行 <plan_id>`
- `apply <plan_id>`

执行前必须运行 `python3 scripts/plan-gate.py validate --plan <PLAN_FILE>`。source inventory、
参数、root 或目标映射变化时确认立即失效, 必须重新生成预览和新的 `plan_id`。

以下回复不允许执行:
- 确认执行
- 执行
- apply
- run
- 看起来可以
- 差不多
- 继续看看
- 还有吗
- 应该可以
- 嗯
- 好
```

---

## Sub-file Index 子文件索引

| 文件 | 内容 | 何时查阅 |
|------|------|---------|
| [workflow.md](workflow.md) | 步骤 1~9 完整工作流程 | 执行时按步骤查阅 |
| [configuration.md](configuration.md) | 配置参数、媒体库边界、dry-run 行为、文件类型识别 | 判断参数、路径边界或文件类型时查阅 |
| [naming-rules.md](naming-rules.md) | 电影/剧集/特殊内容命名规则 + 字段说明 | 生成文件名时查阅 |
| [nfo-templates.md](nfo-templates.md) | movie / tvshow / episodedetails / season NFO 模板 | 生成 NFO 时查阅 |
| [artwork.md](artwork.md) | 图片下载列表、别名策略、图片来源 | 下载图片时查阅 |
| [tmdb-api.md](tmdb-api.md) | API Key、URL、append_to_response、置信度评分、图片拼接 | 查询 TMDB 时查阅 |
| [technical-reference.md](technical-reference.md) | parse_filename、ffprobe 检测代码、技术信息优先级 | 需要实现脚本或技术字段判断时查阅 |
| [safety.md](safety.md) | 回滚要求、mapping 格式、校验策略、冲突处理、路径安全 | 回滚和冲突处理时查阅 |
| [scripts/plan-gate.py](scripts/plan-gate.py) | 生成和复核 deterministic `plan_id` | Dry-run 和真实执行前运行 |
| [tests/test_plan_gate.py](tests/test_plan_gate.py) | Plan 稳定性、变更失效和路径逃逸测试 | 修改 plan gate 后运行 |

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
