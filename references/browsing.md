# 逛B站——热门、排行、搜索、动态、收藏、历史

用户没给具体链接、想找内容看时用本模块。选中视频后把 bv_id 交给 `watching.md` 流程。

> `bili` 命令始终加 `--yaml`，用 `--max` 控制返回量。需登录的命令先 `bili status` 检查。

## 热门 / 排行

```bash
bili hot --max 10 --yaml                  # 热门视频
bili hot --page 2 --max 10 --yaml         # 翻页
bili rank --day 3 --max 20 --yaml         # 全站排行（3日榜，默认）
bili rank --day 7 --max 30 --yaml         # 7日榜
```

## 搜索

```bash
bili search "关键词" --type video --max 5 --yaml
bili search "关键词" --type user --max 5 --yaml      # 搜UP主
bili search "关键词" --page 2 --yaml                 # 翻页
```

## 动态流（关注的人，需登录）

```bash
bili feed --yaml
bili feed --offset <上页返回的游标> --yaml    # 翻页
```

## UP主主页

```bash
bili user "影视飓风" --yaml                # 按名字找（返回 mid + 资料）
bili user 946974 --yaml                   # 按 mid 查
bili user-videos 946974 --max 10 --yaml   # 最近投稿
```

## 相关推荐

```bash
bili video <bv_id> --related --yaml        # 正在看的视频的同类
```

## 个人内容库（需登录）

```bash
bili favorites --yaml                      # 收藏夹列表
bili favorites <ID> --yaml                 # 收藏夹内视频
bili watch-later --yaml                    # 稍后再看
bili history --yaml                        # 观看历史
bili following --yaml                      # 关注列表
```

## 策略

- **先列表后深入**：给摘要列表（标题 + UP主 + 数据，每条一行，≤10 条），让用户挑，选中后走 `watching.md`。不要替用户逐个分析
- 浏览/搜索结果是实时的，不进缓存（缓存按视频维度，在 watching 阶段建立）
- HTTP 412 = 反爬触发：等一会重试或减小 `--max`
