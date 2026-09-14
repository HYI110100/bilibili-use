# 逛 B站 / 发现内容

用户没给具体链接，而是想「找点看的」「看看B站」时的策略。
发现具体视频后，把 bv_id 交给 `watching.md` 流程处理。

> **需要获取视频资源（字幕、帧等）时看 `downloading.md`。**
> `bili` 命令始终加 `--yaml`，并用 `--max` 控制返回量，避免撑爆上下文。
> 命令集已在 bilibili-cli 0.6.2 源码中逐一核验（2026-09）。

## 场景路由

| 用户说 | 走 |
|---|---|
| "看看热门"、"有什么好看的" | 热门流 |
| "B站最近流行什么"、"排行榜" | 排行榜 |
| "关注的人有什么更新"、"刷刷动态" | 动态流（需登录） |
| "搜一下XX"、"找XX的视频" | 搜索 |
| "XX UP主最近发了什么" | UP主主页 |
| "我收藏了什么"、"稍后再看"、"观看历史" | 个人内容库（需登录） |

## 发现流

### 热门视频

```bash
bili hot --max 10 --yaml
bili hot --page 2 --max 10 --yaml   # 翻页
```

### 全站排行榜

```bash
bili rank --day 3 --max 20 --yaml   # 3日榜（默认）
bili rank --day 7 --max 30 --yaml   # 7日榜
```

### 动态流（关注的人）

```bash
bili feed --yaml
bili feed --offset <上页返回的游标> --yaml   # 翻页
```

需登录（`bili status` 检查）。未登录时建议用户先 `bili login`，或降级到热门流。

## 搜索

```bash
bili search "关键词" --type video --max 5 --yaml
bili search "关键词" --type user --max 5 --yaml    # 搜UP主
bili search "关键词" --page 2 --yaml               # 翻页
```

## UP主深挖

```bash
bili user "影视飓风" --yaml              # 按名字找（返回 mid + 资料）
bili user 946974 --yaml                 # 按 mid 查
bili user-videos 946974 --max 10 --yaml # 最近视频列表
```

看中某个视频 → 走 watching.md 流程（`python3 scripts/resolve_video_id.py <bv_id>` 起）。

## 相关推荐

已经在看某个视频，用户想找类似的：

```bash
bili video <bv_id> --related --yaml
```

## 个人内容库（需登录）

```bash
bili favorites --yaml                  # 收藏夹列表
bili favorites <ID> --yaml             # 某个收藏夹里的视频
bili watch-later --yaml                # 稍后再看
bili history --yaml                    # 观看历史
bili following --yaml                  # 关注列表
```

## 行为准则

- **先列表后深入**：先给用户摘要列表（标题 + UP主 + 数据），让用户挑。不要自作主张替用户分析每个视频。
- **列表呈现**：每条一行——标题、UP主、播放/点赞数、时长。别超过 10 条，问用户要不要翻页。
- **选中即交接**：用户挑中后，bv_id 交给 `watching.md` 四阶段流程，不要在 browsing 里重复造流程。
- **浏览结果不缓存**：发现流/搜索是实时的，不走 `~/.cache/`（缓存在 watching 阶段按视频维度建立）。
- **限流**：B站反爬触发（HTTP 412）时，等一会重试或减小 `--max`，别刷太快。
