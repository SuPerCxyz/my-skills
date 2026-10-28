# 配置与识别规则

Use this file when selecting execution options, media root boundaries, dry-run behavior, or file type recognition. It defines configuration meaning, not the execution sequence.

本文件保存执行参数、媒体库边界、dry-run 行为和文件类型识别规则。`SKILL.md` 只保留入口门禁, 执行时按需查阅本文件。

## Configuration Parameters 配置参数

```yaml
options:
  dry_run: true                    # 默认永远 dry-run
  language: zh-CN                  # TMDB 语言
  country: CN                      # 国家
  tmdb_id: null                    # 显式 TMDB ID(可选)
  tmdb_api_key: null               # TMDB API Key(优先读环境变量 TMDB_API_KEY)
  media_type: auto                 # auto / movie / tv / variety / documentary / anime
  season_mode: auto                # auto / single / multi
  special_mode: season00           # season00 / inline / skip
  overwrite: false                 # 禁止覆盖
  conflict_policy: skip            # skip / suffix / replace(默认 skip)
  generate_nfo: true               # 生成 NFO
  download_artwork: true           # 下载图片
  artwork_quality: original        # original / w500 / w300
  artwork_alias: true              # 是否生成图片别名(hardlink)
  max_workers: 4                   # 最大并发数
  delete_empty_dirs: true          # 删除空目录
  prefer_ffprobe: true             # ffprobe 优先
  nfo_format: kodi                 # kodi / jellyfin / emby
  jellyfin_compatible: true
  emby_compatible: true
  tmm_compatible: true
  generate_season_nfo: false       # season.nfo 可选生成
  generate_movie_nfo_duplicate: false  # 是否额外生成 movie.nfo
  execution_mode: direct           # direct / staging
  full_hash: false                 # 是否计算完整 sha256(大文件默认 quick_hash)
  media_root: null                 # 媒体库根目录, 目标路径必须在此目录内
  target_root: null                # 可选目标整理目录, 不填则使用 media_root
  staging_root: null               # 可选 staging 根目录, 不填则在 target_root 下创建
```

## Media Root Rules 媒体库根目录规则

- 如果 `media_root` 未设置, 则默认使用用户输入路径的父目录作为安全边界
- `target_root` 必须位于 `media_root` 内
- `staging_root` 必须位于 `media_root` 或 `target_root` 内
- 所有 `old_path` / `new_path` / `staging_path` 都必须经过 `realpath` 校验
- 禁止 `new_path` 跳出 `media_root`
- 扫描只覆盖用户指定的 source root, 不跟随解析后位于 root 外的符号链接
- source root 为空、没有媒体文件、包含多个未指定的媒体 root 或发现嵌套媒体库时, 停止
  自动扩展扫描范围并在 dry-run 中报告

## Dry-Run Behavior Rules Dry-Run 行为规则

dry-run 模式下允许的操作:
- 扫描文件
- 执行 ffprobe
- 查询 TMDB API
- 生成预览
- 输出「将生成的 mapping / rollback 预览」

dry-run 模式下禁止的操作:
- 创建目录
- 移动 / 重命名文件
- 写入 NFO
- 下载图片
- 删除空目录
- 生成真实 rollback 脚本

## File Type Recognition 文件类型识别

### Video File Extensions 视频文件扩展名

```
.mp4 .mkv .avi .mov .wmv .flv .ts .m2ts .mts .webm .rmvb .mpg .mpeg .iso
```

只有视频文件参与 movie / episode 判断。

### Subtitle File Extensions 字幕文件扩展名

```
.srt .ass .ssa .sub .idx .sup .vtt
```

字幕文件必须绑定主视频, 不单独作为资源。跟随主视频重命名, 保留语言后缀。

### Image / NFO / Accessory Extensions 图片 / NFO / 附属文件扩展名

```
.nfo .jpg .jpeg .png .webp .txt .url
```

NFO / 图片 / txt / url 默认作为附属文件处理, 不参与媒体类型判断。

### Unrecognized Extensions 未识别扩展名

默认保留, 不删除、不移动, 除非用户明确要求。
