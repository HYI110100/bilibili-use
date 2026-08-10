# AGENTS.md

AI agent 使用本技能前需准备的环境。

## 概述

`bilibili-use` 是一个跨平台的 B站 视频内容消费技能。包含观看、下载、总结三大能力，12 个 Python 脚本 + markmap 思维导图生成。

## 必备依赖

### 安装本技能

```bash
npx skills add <your-username>/bilibili-use --global
```

### CLI 工具

| 工具 | 安装 | 用途 |
|---|---|---|
| `bili` | `uv tool install bilibili-cli` | B站 API（需扫码登录） |
| `yt-dlp` | `uv tool install yt-dlp` | 视频下载/流媒体直链 |
| `ffmpeg` | `apt install ffmpeg` | 抽帧/音视频处理 |
| `markmap` | `npm install -g markmap-cli` | 思维导图 HTML 生成 |
| `python3` | 系统自带 | 所有脚本运行环境 |

### 官方 Skill

本技能依赖 `bilibili-cli` 的官方 skill 来使用底层命令：

- 仓库：https://github.com/public-clis/bilibili-cli
- 安装：`npx skills add jackwener/bilibili-cli --global`

### Python 包

```
pip install pyyaml playwright
python -m playwright install chromium
```

> `playwright` 仅 `html_to_png.py` 需要。不需要 PNG 输出可不装。

### 登录

```bash
bili login    # 扫码登录 B站
```

未登录不影响基本搜索和热门，但画质受限、无法获取个性化内容。

## 目录结构

```
bilibili-use/
├── AGENTS.md                  ← 本文件
├── SKILL.md                   ← 入口：触发描述、工具链、缓存约定、任务路由
├── references/
│   ├── watching.md            ← 观看策略（内部步骤）
│   ├── downloading.md         ← 下载执行（12个脚本调用）
│   └── summarizing.md         ← 总结输出（闲聊/速览/文章/思维导图）
└── scripts/
    ├── config.py              ← 共享配置（缓存路径、ID解析）
    ├── resolve_video_id.py    ← 链接解析：BV/AV/ep/b23.tv → 统一 ID
    ├── get_video_info.py      ← 元数据 + 多P 检测
    ├── get_subtitle.py        ← 字幕获取 + 超长自动拆分
    ├── get_ai_summary.py      ← B站 AI 段落摘要
    ├── get_comments.py        ← 评论（热门/最新）
    ├── compute_timestamps.py  ← 热力图算法：时长 → 抽帧时间点
    ├── extract_frames.py      ← 流式抽帧（不下载完整视频）
    ├── extract_audio.py       ← 音频提取（ASR-ready WAV）
    ├── extract_stt.py         ← 本地 STT（未实现，返回降级指引）
    ├── download_video.py      ← 完整视频下载
    ├── html_to_png.py         ← HTML 转 PNG（思维导图输出）
    └── cleanup_cache.py       ← 缓存清理（Step 0 自动执行）
```

## 缓存

所有内容缓存于 `~/.cache/bilibili-use/`：

```
~/.cache/bilibili-use/
└── <bv_id>/
    ├── resolve.json            # 链接解析结果
    ├── metadata.yaml           # 24h TTL
    ├── subtitle.platform.srt   # 永久
    ├── subtitle.compressed.md  # 永久
    ├── chunks/                 # 超长字幕拆分片段
    ├── ai_summary.md           # 永久
    ├── comments.yaml           # 6h/1h TTL
    ├── audio/                  # WAV 分段
    ├── frames/                 # JPG 帧
    ├── video_*.mp4             # 完整视频（7天自动清理）
    └── p<N>/                   # 多P视频第2P起，结构同上
```

## 工作流

```
用户发 B站链接
  → SKILL.md 路由到 summarizing.md（默认闲聊模式）
    → 内部先调 watching.md（三阶段分析流程）
      → 需要资源时调 downloading.md（12个脚本）
    → 最终输出：闲聊 / 速览 / 文章 / 思维导图
```

## 设计原则

- **平台无关**：不依赖 Hermes/Claude Code/Codex 等特定平台工具
- **脚本自给**：所有数据获取脚本独立运行，先查缓存再获取
- **意图驱动**：文档描述「做什么」而非「用什么工具」，各平台自行选择实现
- **按需视觉**：帧用于模型内部分析，不是默认展示给用户的素材
