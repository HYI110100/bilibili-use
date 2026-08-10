# bilibili-use

**把 B站链接丢给 AI，它替你"看完"这个视频。**

自动抓字幕、评论、关键帧，默认陪你闲聊，也能一键出速览、深度文章、思维导图。下载视频、抽帧、提取音频也是顺手的事。

```text
你：https://www.bilibili.com/video/BV1DAgS6SEqa
AI：帮你总结这个视频讲了什么，配关键帧，聊评论区在吵什么 👇
```

## 解决什么痛点

| 痛点 | 它怎么解决 |
|---|---|
| 视频太长不想全看 | AI 自动抓字幕/评论/关键帧，总结核心内容 |
| 评论区吵翻天，懒得翻 | 自动提炼高赞风向、争议点 |
| 想看某个画面但懒得拖进度条 | 自动抽关键时间点帧图 |
| 多P/合集几十集，不知从哪看 | 列全部分P标题，默认处理当前集，想看全集逐个分析 |
| 命令行下视频太麻烦 | 一句"下载这个"拿完整视频/音频/字幕 |

## 能做什么

| 场景 | 你只要说 | 得到 |
|---|---|---|
| 🗣️ 闲聊（默认） | 发个链接 | 视频讲了什么 + 有意思的点 + 评论区风向 |
| ⚡ 速览 | "总结一下" | 3-5 个要点 + 值不值得看 |
| 📝 深度 | "写篇文章" / "画个导图" | 结构化文章 / 交互式思维导图 |
| ⬇️ 下载 | "下载这个" | 完整视频 / 音频 / 字幕文件 |
| 🎞️ 抽帧 | "看看画面" | 关键时间点的画面截图 |

多P视频和合集也支持：默认处理第一个，想看全集就让它逐个分析。

## 快速开始

```bash
# 1. 安装本技能
npx skills add HYI110100/bilibili-use --global

# 2. 装依赖（CLI 工具）
uv tool install bilibili-cli   # B站 API
uv tool install yt-dlp         # 视频下载 / 流媒体直链
npm install -g markmap-cli     # 思维导图渲染
apt install ffmpeg             # 音视频处理 / 抽帧

# 3. Python 包
pip install pyyaml playwright  # playwright 仅思维导图转 PNG 需要

# 4.（可选）多P视频真实标题，不装自动降级
pip install bilibili-api

# 5.（可选）登录解锁高清画质
bili login
```

装完把 B站链接发给你的 AI agent，什么都不用说，它自己会处理。

## 它是什么

一组**策略文档**（教 AI 怎么分析视频）+ **自动化脚本**（拿字幕、评论、帧的活都封装好了）。不绑定任何 AI 平台——Hermes、Claude Code、Codex、OpenCode 都能用，同一份技能，各平台自己实现。

所有抓取内容缓存到 `~/.cache/bilibili-use/`，重复看同一视频秒回，不重复请求。

## 依赖的开源项目

| 项目 | 用途 |
|---|---|
| [bilibili-cli](https://github.com/public-clis/bilibili-cli) | B站 API 客户端 |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | 视频下载 / 流媒体直链 |
| [markmap](https://github.com/markmap/markmap) | Markdown → 交互式思维导图 |
| [ffmpeg](https://ffmpeg.org) | 音视频处理 / 抽帧 |

## 许可证

MIT
