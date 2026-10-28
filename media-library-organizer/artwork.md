# 图片下载

Use this file when the dry-run plan includes artwork download or artwork alias generation. It does not replace the main workflow in [workflow.md](workflow.md) or the safety checks in [safety.md](safety.md).

## 并发下载策略

- 独立资源可按当前会话的委派规则分工, 不固定子 Agent 数量, 不让多个任务写入同一路径
- 实际图片下载可使用 Python asyncio / ThreadPoolExecutor
- `max_workers` 默认 4, 仅限制下载线程/协程; Agent 并发和会话上限服从当前会话
- 所有下载失败必须记录, 不能阻断重命名主流程

## 图片别名策略

- 同一张图片需要生成多个兼容命名时, 优先使用 hardlink
- hardlink 失败时复制
- 跨文件系统 hardlink 失败时自动 fallback copy
- 如果用户设置 `artwork_alias=false`, 则只生成主命名, 不生成别名

## 电影图片

```
poster.jpg
fanart.jpg
clearlogo.png
banner.jpg
{movieFileName}-poster.jpg
{movieFileName}-fanart.jpg
{movieFileName}-clearlogo.png
{movieFileName}-thumb.jpg
```

## 剧集图片

```
poster.jpg
fanart.jpg
clearlogo.png
banner.jpg
season01-poster.jpg
season02-poster.jpg
season00-poster.jpg
season-specials-poster.jpg(额外生成, 提高兼容性)
episode同名-thumb.jpg
```

## 图片来源

- 海报 `poster.jpg`:TMDB posters, `original` 尺寸
- 背景图 `fanart.jpg`:TMDB backdrops, `original` 尺寸
- 横幅图 `banner.jpg`:TMDB backdrops, 选取与 fanart 不同的图
- 透明 Logo `clearlogo.png`:TMDB logos, 最大尺寸 PNG
- 各季海报 `season{nn}-poster.jpg`:TMDB 各季页面独立海报
- 特别篇海报 `season00-poster.jpg` + `season-specials-poster.jpg`
- 每集剧照 `*-thumb.jpg`:TMDB stills, `w500` 尺寸
