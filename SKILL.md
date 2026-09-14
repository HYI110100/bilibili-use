---
name: bilibili-use
description: "Use when the user 发来B站链接或视频ID — 默认闲聊总结，支持速览、文章、思维导图。可下载视频、提取字幕和关键帧。"
version: 0.1.0
author: hyi, Hermes Agent
license: MIT
platforms: [linux, windows]
metadata:
  hermes:
    tags: [bilibili, b站, video, content, social-media]
---

# Bilibili Use

B站平台使用技能。**不是 CLI 命令手册**（那在 `bilibili-cli` skill 里），而是教你如何在 B站上完成具体任务：看视频、逛内容、管账号。

## 工具链

| 工具 | 用途 |
|---|---|
| `bili` CLI | 底层命令行（官方 skill `bilibili-cli` 教用法） |
| `scripts/resolve_video_id.py` | 解析链接/ID，识别单视频/多P/合集，建缓存目录 |
| `scripts/get_video_info.py` | 获取视频元数据 + 检测多P |
| `scripts/get_subtitle.py` | 获取字幕，超长自动拆分（返回路径，不返回内容） |
| `scripts/get_ai_summary.py` | 获取 B站 AI 总结（段落摘要） |
| `scripts/extract_audio.py` | 提取音频（ASR-ready WAV 分段） |
| `scripts/extract_stt.py` | 语音转写留白——agent 按用户偏好自行补充（通常调 STT 服务） |
| `scripts/get_comments.py` | 获取评论（热门/最新） |
| `scripts/compute_timestamps.py` | 热力图算法：时长 → 最佳抽帧时间点 |
| `scripts/extract_frames.py` | 流式抽帧（不下载完整视频） |
| `scripts/html_to_png.py` | HTML 转 PNG（思维导图输出用） |
| `scripts/download_video.py` | 下载完整视频文件 |
| `scripts/cleanup_cache.py` | 缓存清理（每次操作前自动执行） |
| `scripts/config.py` | 共享配置（缓存路径、ID 解析）——所有脚本的基础设施 |
| `yt-dlp` | 下载/流媒体直链/多P检测（兜底） |

## 缓存约定

缓存目录：`~/.cache/bilibili-use/`，单视频 / 多P / 合集三层结构。

完整目录结构见 `AGENTS.md` 的「缓存」章节。

所有 `scripts/*.py` 自动遵循：先查缓存 → 未命中才调 CLI/yt-dlp → 结果写缓存。

## 任务路由

| 用户要做什么 | 加载 |
|---|---|
| 发来B站链接（默认） | `references/summarizing.md`（内部先调 watching） |
| 下载视频文件 | `references/downloading.md` |
| 逛B站/发现内容 | `references/browsing.md`（规划中） |
| 发视频/动态 | `references/publishing.md`（规划中） |
| 账号分析/运营 | `references/account.md`（规划中） |

> `watching.md` 是内部步骤，由 summarizing 或 downloading 调用，不直接响应用户请求。

## 全局规则

- **Step 0**: 任何操作前，先执行 `python3 scripts/cleanup_cache.py`（无脑执行。Windows 上命令是 `python`）
- 平台差异：文档中 `python3` 在 Windows 上用 `python`；`~/` 在 Windows 上是 `%USERPROFILE%`；缓存目录由 `config.py` 自动处理，无需关心
- 所有 `scripts/*.py` 先查缓存 → 未命中才调 CLI/yt-dlp → 结果写缓存
- `bili` 命令始终加 `--yaml`
- 抽帧走流式（`yt-dlp -g` + `ffmpeg -ss`），不下载完整视频
- 字幕超长 → `get_subtitle.py` 自动拆分 → 并行压缩各段 → 只看压缩结果
- 多步骤操作时保持进度跟踪（按平台的 task/todo 机制）
- 帧的两种用途：①自己分析——用平台图片/视觉能力看（模型无原生视觉走辅助视觉模型）；②展示给用户——有视觉亮点时用平台媒体语法附上（见 summarizing.md「展示帧给用户」）。视觉工具不可用才跳过分析
- 多P真实标题/时长依赖 `bilibili-api`，未装时自动降级（当前解释器 → bili CLI 环境 → 占位标题），详见 AGENTS.md
- markmap 思维导图生成前需加载其 skill 文档
