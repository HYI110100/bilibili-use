# 下载 B站 资源

> **需要从B站获取任何资源（字幕、音频、帧、视频文件、AI摘要、评论、元数据）
> ——本文档管怎么拿。其他 reference（watching、browsing、publishing）只管决定拿什么。**

## 可用脚本

| 脚本 | 获取 | 缓存 | 输出 |
|---|---|---|---|
| `get_video_info.py` | 元数据 YAML | 24h TTL | YAML 文本或 `[CACHE: HIT]` |
| `get_subtitle.py` | 平台字幕 | 永久 | 短：内容。长：`[SPLIT]` 分段路径 |
| `get_ai_summary.py` | B站 AI 摘要 | 永久 | ~100-300 字文本 |
| `get_comments.py` | 热门/最新评论 | 6h/1h TTL | YAML 文本 |
| `extract_audio.py` | 音频 → WAV 分段 | 永久 | WAV 文件路径 |
| `extract_frames.py` | 流式抽帧 | 永久 | JPG 文件路径 |
| `compute_timestamps.py` | 最佳抽帧时间点 | N/A | 逗号分隔的秒数 |
| `download_video.py` | 完整视频 .mp4 | 永久 | 文件路径 |
| `html_to_png.py` | HTML → PNG 截图 | N/A | PNG 文件路径 |
| `cleanup_cache.py` | 清理旧视频文件 | N/A | 释放的 MB 数 |

## 第0步：始终先清理

```bash
python3 scripts/cleanup_cache.py
```

不要思考，不要判断是否需要。在任何内容获取前无脑执行。
脚本自动删除超过 7 天的视频 .mp4 文件，保留字幕、帧和元数据。

## 脚本调用

### 元数据（始终最先）
```bash
python3 scripts/get_video_info.py <bv_id>
```

### 字幕
```bash
python3 scripts/get_subtitle.py <bv_id>
# 短字幕 → 直接返回内容，读完
# [SPLIT] → 返回分段 → 并行压缩（见 watching.md）
# [NO SUBTITLE] → 降级到 --ai 或抽帧
```

### AI 摘要（无字幕时）
```bash
python3 scripts/get_ai_summary.py <bv_id>
```

### 评论
```bash
python3 scripts/get_comments.py <bv_id> --mode hot
python3 scripts/get_comments.py <bv_id> --mode latest
```

### 抽帧时间点
```bash
python3 scripts/compute_timestamps.py --duration <seconds>
# → "3,15,30,52,80,120,200,350"
```

### 流式抽帧
```bash
python3 scripts/extract_frames.py <bv_id> --at 10,45,120
# ~0.5s/帧，走 yt-dlp -g + ffmpeg -ss
```

### 提取音频（用于 ASR）
```bash
python3 scripts/extract_audio.py <bv_id> --segment 25
# → WAV 分段，ASR 就绪
```

### 下载完整视频
```bash
python3 scripts/download_video.py <bv_id> --quality 1080p
# 用户明确要求保存文件时才用
```

### HTML 转 PNG（思维导图输出）
```bash
python3 scripts/html_to_png.py <html文件>
# 需要 playwright（pip install playwright && python -m playwright install chromium）
```

## 缓存结构

```
~/.cache/bilibili-use/
│
├── <bv_id>/                  # 单视频 / 多P的根
│   ├── resolve.yaml          # 类型: single/multi_p
│   ├── metadata.yaml         # 24h TTL
│   ├── subtitle.platform.srt # 永久（B站原始字幕）
│   ├── subtitle.compressed.md# 压缩版
│   ├── chunks/               # 超长字幕拆分片段
│   ├── ai_summary.md         # 永久
│   ├── comments_hot.yaml     # 6h TTL
│   ├── comments_latest.yaml  # 1h TTL
│   ├── audio/seg_*.wav       # 永久
│   ├── frames/*.jpg          # 永久
│   ├── video_*.mp4           # 7天自动清理（cleanup_cache.py）
│   │
│   ├── p1/                   # 多P视频第1P（结构同上）
│   ├── p2/                   # 第2P
│   └── index.yaml            # 多P列表（page, title, duration_s）
│
└── <collection_id>/          # 合集（sid）
    ├── index.yaml            # 合集视频列表（bv_id, title, duration_s）
    └── <bv_id>/              # 每个视频一个目录（结构同上）
```

## 画质与 Cookies

- 默认：res:1080，优先 H.264，cookies Firefox→Chrome→无
- `--quality 4k` → 2160p（需要大会员）
- 无 cookies → 降级到 ~480p，不报错

## 边界情况

| 情况 | 行为 |
|---|---|
| Cookies 过期 | 降级到无 cookie 模式，画质降低 |
| 流地址过期（抽帧） | 重新从 yt-dlp -g 获取 |
| 视频已删除/私密 | yt-dlp 非零退出，脚本报错 |
| 无字幕 | `[NO SUBTITLE]`，调用者决定降级 |
| bili audio 未安装 | `extract_audio.py` 降级到 yt-dlp bestaudio |
| 多P 视频 | 默认只处理第1P |
