# bilibili-use

**让 AI 真正会用 B站。**

把 B站链接丢给 AI，它自动抓字幕、评论、关键帧，替你"看完"视频——默认陪你闲聊，也能一键出速览、深度文章、思维导图。

## 为什么做这个

装了 [bilibili-cli](https://github.com/public-clis/bilibili-cli) 之后，我以为 AI 就会用 B站了。结果发现根本不是那么回事——CLI 只是**命令手册**，告诉 AI "有哪些命令"，但没告诉它"拿到一个 B站链接后该怎么处理"。

于是 AI 拿到链接后的表现是：

- 字幕一次全量糊进上下文，长的直接炸
- 从没想过抽帧——画面内容（美食、测评、游戏）全靠猜
- 多P合集分不清，80 集的视频当一集看
- 同一个视频每次重新抓，浪费 token 又慢
- 输出时好时坏，不知道闲聊和深度文章是两回事

**这就是我要解决的痛点**：给 AI 一套标准的 B站内容消费流程，让它拿到链接就知道该干什么、每一步怎么判断。

## 有哪些功能

| 功能 | 说明 |
|---|---|
| 🗣️ 闲聊总结（默认） | 发链接 → 视频讲了什么 + 有意思的点 + 评论区风向 |
| ⚡ 速览 | "总结一下" → 3-5 个要点 + 值不值得看 |
| 📝 深度文章 / 思维导图 | "写篇文章" / "画个导图" → 结构化输出 |
| 🎞️ 关键帧 | 自动抽关键时间点的画面，展示视觉亮点 |
| ⬇️ 下载 | 完整视频 / 音频 / 字幕文件 |
| 📚 多P / 合集 | 识别类型，默认处理当前集，想看全集逐个分析 |
| 🧠 缓存 | 重复看同一视频秒回，不重复请求 |
| 🔗 链接解析 | BV / AV / ep / b23.tv 短链 / 带时间戳参数，全支持 |

## 你能得到什么

- **装一个技能，AI 就会用 B站**：不用再手把手教 AI 敲命令
- **看视频省时间**：长的不用全看，AI 帮你提炼核心
- **评论风向一键掌握**：不用翻几百条评论
- **画面信息不丢**：关键帧自动抽，视觉内容也进总结
- **跨平台通用**：Hermes、Claude Code、Codex、OpenCode 都行，同一份技能

## 怎么使用

**方式一：直接丢给 AI（推荐）**

把整个仓库给 AI 看，它读 `AGENTS.md` 就知道环境怎么配、流程怎么走。之后你只需要发 B站链接。

```bash
# AI 读 AGENTS.md 后，按里面引导安装依赖即可
npx skills add HYI110100/bilibili-use --global
```

**方式二：手动装**

```bash
# 1. 安装本技能
npx skills add HYI110100/bilibili-use --global

# 2. 装依赖
uv tool install bilibili-cli   # B站 API
uv tool install yt-dlp         # 视频下载 / 流媒体直链
npm install -g markmap-cli     # 思维导图渲染
apt install ffmpeg             # 音视频处理 / 抽帧
pip install pyyaml playwright  # playwright 仅思维导图转 PNG 需要
pip install bilibili-api       # 可选：多P真实标题，不装自动降级

# 3. 可选：登录解锁高清
bili login
```

装完把 B站链接发给 AI，什么都不用说，它自己会处理。

## 关联的开源项目

本技能是纯 Python 脚本 + Markdown 策略文档，实际能力来自这些成熟项目：

| 项目 | 用途 |
|---|---|
| [bilibili-cli](https://github.com/public-clis/bilibili-cli) | B站 API 客户端（命令层） |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | 视频下载 / 流媒体直链 |
| [markmap](https://github.com/markmap/markmap) | Markdown → 交互式思维导图 |
| [ffmpeg](https://ffmpeg.org) | 音视频处理 / 抽帧 |

## 许可证

[MIT](./LICENSE)
