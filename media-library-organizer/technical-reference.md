# 技术实现参考

Use this file when implementing or reviewing parsing and media-info extraction logic. It is not an execution checklist; use [workflow.md](workflow.md) for the ordered flow.

## 从文件名提取技术信息

```python
import re
from pathlib import Path

def parse_filename(filename):
    base = Path(filename).stem
    info = {
        "resolution": None,
        "video_codec": None,
        "hdr": None,
        "source": None,
        "audio": None,
    }
    m = re.search(r'\.(\d+p)\.', base)
    if m: info["resolution"] = m.group(1)
    m = re.search(r'\.(HEVC|AVC|H\.264|H\.265|AV1|VP9)', base)
    if m: info["video_codec"] = m.group(1)
    if "HDR10" in base: info["hdr"] = "HDR10"
    elif "DV" in base or "DoVi" in base: info["hdr"] = "DV"
    elif "HLG" in base: info["hdr"] = "HLG"
    elif "SDR" in base: info["hdr"] = "SDR"
    if "BluRay" in base: info["source"] = "BluRay"
    elif "WEB-DL" in base: info["source"] = "WEB-DL"
    elif "HDTV" in base: info["source"] = "HDTV"
    m = re.search(r'\.(\d+\.\d)', base)
    if m: info["audio"] = m.group(1)
    return info
```

## 从文件检测技术信息(ffprobe 优先)

**ffprobe 优化规则:**
- 每个媒体文件只执行一次 ffprobe
- ffprobe JSON 结果必须缓存
- 分辨率、编码、HDR、声道、音频编码都从同一份 ffprobe 结果中读取
- ffprobe 失败时才允许从文件名猜测
- 从文件名猜测的字段必须标记为 guessed
- helper 缺少可信结果时返回 `None`, 不补造 SDR、2.0 或默认分辨率。汇总时记录字段来源, 预览将 `None` 显示为 `unknown`

```python
import subprocess, json

# 缓存 ffprobe 结果, 避免重复执行
_ffprobe_cache = {}

def get_ffprobe_data(filepath):
    """获取并缓存 ffprobe JSON 结果"""
    if filepath in _ffprobe_cache:
        return _ffprobe_cache[filepath]
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", filepath],
            capture_output=True, text=True, timeout=30, check=True
        )
        data = json.loads(result.stdout)
        if not isinstance(data, dict) or not isinstance(data.get("streams"), list):
            data = None
        _ffprobe_cache[filepath] = data
        return data
    except (OSError, subprocess.SubprocessError, ValueError):
        _ffprobe_cache[filepath] = None
        return None

def get_hdr(filepath):
    """ffprobe 检测 HDR, 优先于文件名猜测"""
    d = get_ffprobe_data(filepath)
    if not d:
        return None  # 未取得证据, 不冒充 SDR
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            ct = s.get("color_transfer", "")
            pix = s.get("pix_fmt", "")
            # Dolby Vision 检测(优先级最高)
            if "dovi" in pix.lower() or "dolby" in str(s.get("side_data_list", [])).lower():
                return "DV"
            # HDR10+ 检测
            if ct == "smpte2094-40":
                return "HDR10+"
            # HDR10
            if ct == "smpte2084":
                return "HDR10"
            # HLG
            if ct == "arib-std-b67":
                return "HLG"
            if ct in {"bt709", "smpte170m", "bt470m", "bt470bg", "iec61966-2-1"}:
                return "SDR"
            return None
    return None

def get_audio_channels(filepath):
    """ffprobe 检测声道数"""
    d = get_ffprobe_data(filepath)
    if not d:
        return None
    for s in d.get("streams", []):
        if s.get("codec_type") == "audio":
            ch = s.get("channels")
            if type(ch) is not int or ch <= 0:
                return None
            channel_map = {1: "1.0", 2: "2.0", 6: "5.1", 8: "7.1"}
            return channel_map.get(ch, f"{ch}.0")
    return None

def get_video_codec(filepath):
    """ffprobe 检测视频编码"""
    d = get_ffprobe_data(filepath)
    if not d:
        return None
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            codec = s.get("codec_name", "").lower()
            codec_map = {"h264": "AVC", "hevc": "HEVC", "av1": "AV1", "vp9": "VP9"}
            return codec_map.get(codec, codec.upper())
    return None

def get_resolution(filepath):
    """ffprobe 检测分辨率"""
    d = get_ffprobe_data(filepath)
    if not d:
        return None
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            h = s.get("height")
            if type(h) is not int or h <= 0:
                return None
            if h >= 2160: return "2160p"
            if h >= 1440: return "1440p"
            if h >= 1080: return "1080p"
            if h >= 720: return "720p"
            if h >= 480: return "480p"
            return f"{h}p"
    return None
```

## 技术信息优先级

```
技术信息优先级:
1. ffprobe 实际检测结果(prefer_ffprobe=true 时)
2. 文件名标签
3. `None` / `unknown`, 不自动猜默认值

如果字段来自文件名猜测而非 ffprobe 检测, 必须在预览中标记为 [guessed]。
```

字段汇总示例保持原有 helper 的标量接口, 在调用方记录来源; 没有可信值时不执行字符串拼接或伪造 NFO 测量字段:

```python
def collect_technical_info(filepath):
    guessed = parse_filename(filepath)
    measured = {
        "resolution": get_resolution(filepath),
        "video_codec": get_video_codec(filepath),
        "hdr": get_hdr(filepath),
        "audio": get_audio_channels(filepath),
    }
    fields = {}
    for name in ("resolution", "video_codec", "hdr", "audio", "source"):
        value = measured.get(name)
        source = "ffprobe"
        if value is None or value == "":
            value = guessed.get(name)
            source = "filename" if value is not None else "unknown"
        fields[name] = {"value": value, "source": source}
    return fields

# 预览: source=filename 的值标记 guessed, source=unknown 显示 unknown。
# 本例的 source 字段表示证据来源; fields["source"] 的 value 仍表示媒体来源 (如 BluRay)。
```

## 下载文件

```python
import urllib.request

def download(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except:
        return False
```
