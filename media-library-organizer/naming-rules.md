# 命名规则

Use this file when generating target folder and file names after media type and metadata have already been identified. For rollback and conflict handling, read [safety.md](safety.md).

## 电影

```
文件夹: {title}-{originalTitle}({year})-{videoFormat}-{videoCodec}-{hdrformat}-{3Dformat}-{mediaSource}-{audioChannelsDot}
文件:   同文件夹名(不含扩展名)
```

示例:
```
阿凡达-Avatar(2009)-2160p-HEVC-HDR10--BluRay-7.1.mkv
泰坦尼克号-Titanic(1997)-1080p-AVC-SDR--WEB-DL-5.1.mkv
```

## 多集内容(电视剧/综艺/动漫/纪录片)

```
根目录: {showTitle}-{showOriginalTitle}-{showYear}/
结构:   Season-{seasonNr2}/
文件:   {showTitle}-S{seasonNr2}E{episodeNr2}-{title}-{videoFormat}-{videoCodec}-{hdr}-{mediaSource}-{audioChannelsDot}.mp4
特殊:   {showTitle}-S00E{episodeNr2}-S{realSeason}E{episodeInSeasonNr2}-{specialType}-{videoFormat}-{videoCodec}-{hdr}-{mediaSource}-{audioChannelsDot}.mp4
```

示例:
```
├── 狂飙-The-Knockout-2023/
│   ├── Season-01/
│   │   ├── 狂飙-S01E01-高启强-2160p-HEVC-SDR-WEB-DL-2.0.mp4
│   │   ├── 狂飙-S01E01-高启强-2160p-HEVC-SDR-WEB-DL-2.0.nfo
│   │   └── 狂飙-S01E01-高启强-2160p-HEVC-SDR-WEB-DL-2.0-thumb.jpg
│   ├── Season-00/     ← 特殊内容/番外
│   │   ├── 狂飙-S00E01-S01E01-加更-2160p-HEVC-SDR-WEB-DL-2.0.mp4
│   │   ├── 狂飙-S00E02-S01E02-加更-2160p-HEVC-SDR-WEB-DL-2.0.mp4
│   │   ├── 狂飙-S00E03-S01E03-特辑-2160p-HEVC-SDR-WEB-DL-2.0.mp4
│   │   ├── 狂飙-S00E04-S01E04-花絮-2160p-HEVC-SDR-WEB-DL-2.0.mp4
│   │   └── 狂飙-S00E05-S01E05-花絮-2160p-HEVC-SDR-WEB-DL-2.0.mp4
│   ├── tvshow.nfo
│   ├── poster.jpg / fanart.jpg
│   ├── banner.jpg / clearlogo.png
│   └── season01-poster.jpg / season00-poster.jpg
```

## 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `{title}` | 中文标题 | 狂飙、阿凡达 |
| `{originalTitle}` | 原标题 | The Knockout、Avatar |
| `{year}` | 年份 | 2023、2009 |
| `{videoFormat}` | 分辨率 | 2160p、1080p、720p |
| `{videoCodec}` | 视频编码 | HEVC、AVC、AV1、VP9 |
| `{hdr}` / `{hdrformat}` | HDR 类型 | SDR、HDR10、DV、HLG |
| `{3Dformat}` | 3D 格式 | 空、Half-SBS、Half-OU |
| `{mediaSource}` | 来源 | WEB-DL、BluRay、HDTV、DVD |
| `{audioChannelsDot}` | 声道 | 2.0、5.1、7.1 |
| `{seasonNr2}` | 季号(2位) | 01、02 |
| `{episodeNr2}` | 集号(2位) | 01、02 |
| `{realSeason}` | 特殊内容所属真实季 | 01、02 |
| `{episodeInSeasonNr2}` | 特殊内容在所属季内的全局序号, 跨所有特殊类型统一从 1 递增(不是按类型分组重新编号) | 01、67 |
