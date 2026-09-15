# Media Library Organizer

媒体库整理:TMDB 刮削 + 重命名 + NFO 生成 + 图片下载,支持电影 / 电视剧 / 综艺 / 纪录片 / 动漫,含完整安全机制与回滚。它面向影视媒体元数据整理, 不用于普通文件清理、日志分析、自动化测试或 UI 自动化。

## 核心特性

- 自动扫描并逐个处理资源文件夹
- 能从 TMDB API 拿就从 API 拿,不能拿再 fallback 网页抓取
- 能用 ffprobe 就不用猜,猜出来的字段标记 `guessed`
- 默认永远 dry-run, 真实修改需用户确认当前预览的 `plan_id`
- 真实修改前生成 `_rename_mapping.json` 和 `_rollback.sh`, 回滚覆盖移动、本次新建
  文件、替换备份和空目录删除

## 快速开始

```
1. 提供一个文件夹路径(单个资源 或 多个资源的父目录)
2. Skill 自动扫描、匹配 TMDB、生成预览(dry-run)
3. 预览确认后回复 `确认执行 <plan_id>` 或 `apply <plan_id>` 才执行真实整理

本 skill 的本地 Python 脚本统一通过 `python3 <path> ...` 调用, 不依赖脚本执行位。
```

## 文件说明

| 文件 | 内容 | 何时查阅 |
|------|------|---------|
| [SKILL.md](SKILL.md) | 核心原则、安全门禁、执行路由、文件索引 | 执行前必读 |
| [workflow.md](workflow.md) | 步骤 1~9 完整工作流程 | 执行时按步骤查阅 |
| [configuration.md](configuration.md) | 配置参数、媒体库边界、dry-run 行为、文件类型识别 | 判断参数、路径边界或文件类型时查阅 |
| [naming-rules.md](naming-rules.md) | 电影/剧集/特殊内容命名规则 + 字段说明 | 生成文件名时查阅 |
| [nfo-templates.md](nfo-templates.md) | movie / tvshow / episodedetails / season NFO 模板 | 生成 NFO 时查阅 |
| [artwork.md](artwork.md) | 图片下载列表、别名策略、图片来源 | 下载图片时查阅 |
| [tmdb-api.md](tmdb-api.md) | API Key、URL、append_to_response、置信度评分 | 查询 TMDB 时查阅 |
| [technical-reference.md](technical-reference.md) | parse_filename、ffprobe 检测代码、技术信息优先级 | 写脚本时查阅 |
| [safety.md](safety.md) | 回滚要求、mapping 格式、校验、冲突处理、路径安全 | 回滚与冲突处理时查阅 |
| [scripts/plan-gate.py](scripts/plan-gate.py) | 生成和复核 deterministic `plan_id` | Dry-run 和执行前运行 |
| [tests/test_plan_gate.py](tests/test_plan_gate.py) | Plan gate 回归测试 | 修改脚本后运行 |
