# bilibili-use

B站视频消费的行为指导层。基于成熟的开源工具，编排出一套完整的「看→下载→总结」工作流。

## 做什么

- 发 B站链接，自动获取字幕、评论、关键帧，默认闲聊模式
- 速览总结 / 深度文章 / 思维导图（markmap 渲染）
- 下载视频、音频、字幕文件
- 流式抽帧、热力图时间点算法

## 依赖

本技能本身是纯 Python 脚本 + Markdown 策略文档。实际能力来自以下开源项目：

| 项目 | 用途 | 仓库 |
|---|---|---|
| bilibili-cli | B站 API 客户端 | https://github.com/public-clis/bilibili-cli |
| yt-dlp | 视频下载 / 流媒体直链 | https://github.com/yt-dlp/yt-dlp |
| markmap | Markdown → 交互式思维导图 | https://github.com/markmap/markmap |
| ffmpeg | 音视频处理 / 抽帧 | https://ffmpeg.org |

## 安装

```bash
# 安装本技能（替换 <username> 为你的 GitHub 用户名）
npx skills add <username>/bilibili-use --global

# 依赖的 CLI 工具
uv tool install bilibili-cli
uv tool install yt-dlp
npm install -g markmap-cli

# Python 包
pip install pyyaml playwright
python -m playwright install chromium   # html_to_png.py 需要

# B站登录（下载高清需要）
bili login
```

系统需 `python3` 和 `ffmpeg`。

## 使用

把 B站链接发给 AI agent，什么都不用说：

```
https://www.bilibili.com/video/BV1DAgS6SEqa
```

→ 默认闲聊模式。也可以指定："总结一下"、"写篇文章"、"画个导图"、"下载这个"。

## 设计

本技能是一组 **策略文档**（`references/`）+ **自动化脚本**（`scripts/`）。不绑定特定 AI 平台——描述意图而非工具名，适用于 Hermes、Claude Code、Codex、OpenCode 等。

缓存目录：`~/.cache/bilibili-use/`

## 许可证

MIT
