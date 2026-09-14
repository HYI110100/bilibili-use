---
name: bilibili-use
description: "B站（bilibili/哔哩哔哩）全功能使用技能。用户发来B站链接/BV号/b23.tv短链时总结视频（闲聊/速览/文章/思维导图）；下载视频、字幕、音频、关键帧；逛B站（热门/排行/搜索/动态/收藏/历史/稍后再看）；点赞、投币、三连、关注、发评论、发私信、发动态；直播操作、视频投稿、创作中心数据；账号与UP主分析。凡提及 B站、bilibili、哔哩哔哩、BV号、b23.tv、UP主 的任务都使用本技能。"
version: 0.2.0
author: hyi, Hermes Agent
license: MIT
platforms: [linux, windows]
metadata:
  hermes:
    tags: [bilibili, b站, video, content, social-media]
---

# Bilibili Use

在 B站上完成任何任务的完整操作体系：内容消费（看、总结、下载）、社交（互动、私信、评论）、创作（投稿、动态）、运营（数据分析）。

## 任务路由

| 任务 | 加载 |
|---|---|
| 总结视频——发来链接/BV号，闲聊、速览、写文章、画思维导图 | `references/summarizing.md`（内部先调 watching） |
| 下载视频文件、字幕、音频、关键帧 | `references/downloading.md` |
| 逛B站——热门、排行、搜索、动态流、收藏、历史、稍后再看、UP主主页 | `references/browsing.md` |
| 点赞、投币、三连、关注/取关、发/删动态 | `references/publishing.md` |
| 发评论/回复、发私信、直播操作、视频投稿、创作中心数据 | `references/library.md` |
| 账号数据、消费画像、对标UP主分析 | `references/account.md` |

> `watching.md` 是内部步骤，由 summarizing 或 downloading 调用，不直接响应用户请求。

## 脚本

| 脚本 | 功能 |
|---|---|
| `scripts/resolve_video_id.py` | 解析链接/ID → 统一ID + 缓存目录（识别单视频/多P/合集） |
| `scripts/get_video_info.py` | 元数据 + 多P检测 |
| `scripts/get_subtitle.py` | 字幕（超长自动拆分） |
| `scripts/get_ai_summary.py` | B站 AI 总结 |
| `scripts/get_comments.py` | 评论（热门/最新） |
| `scripts/extract_audio.py` | 音频 → ASR-ready WAV 分段 |
| `scripts/extract_stt.py` | 语音转写留白——按你的用户偏好自行补充（通常调 STT 服务） |
| `scripts/compute_timestamps.py` | 时长 → 最佳抽帧时间点 |
| `scripts/extract_frames.py` | 流式抽帧（不下载完整视频） |
| `scripts/download_video.py` | 下载完整视频 |
| `scripts/html_to_png.py` | HTML → PNG（思维导图输出） |
| `scripts/cleanup_cache.py` | 缓存清理 |
| `scripts/config.py` | 共享配置，被其他脚本 import |

## 全局规则

- **Step 0**：任何操作前，先执行 `python3 scripts/cleanup_cache.py`（无脑执行。Windows 上命令是 `python`）
- 平台差异：`python3` 在 Windows 上用 `python`；`~/` 在 Windows 上是 `%USERPROFILE%`
- 所有 `scripts/*.py` 先查缓存 → 未命中才调 CLI/yt-dlp → 结果写缓存（缓存结构见 AGENTS.md）
- `bili` 命令始终加 `--yaml`
- 抽帧走流式（`yt-dlp -g` + `ffmpeg -ss`），不下载完整视频
- 字幕超长 → `get_subtitle.py` 自动拆分 → 并行压缩各段 → 只看压缩结果
- 多步骤操作时保持进度跟踪（按平台的 task/todo 机制）
- 帧的用途：①自己分析——用平台图片/视觉能力看；②展示给用户——有视觉亮点时用平台媒体语法附上（见 summarizing.md）。视觉工具不可用则跳过
- markmap 思维导图生成前需加载其 skill 文档
