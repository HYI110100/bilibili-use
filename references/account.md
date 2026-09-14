# 账号分析——账号概况、消费画像、对标UP主

分析B站账号：用户自己的、或任意UP主。涉及"我"的数据需登录（`bili status` 检查）。

> `bili` 命令始终加 `--yaml`，用 `--max` 控制返回量。

## 账号概况

```bash
bili whoami --yaml     # 等级、硬币、粉丝数、关注数、大会员
bili status --yaml     # 登录状态
```

## 消费画像（需登录）

```bash
bili history --yaml           # 观看历史
bili watch-later --yaml       # 稍后再看
bili favorites --yaml         # 收藏夹列表（逐个 bili favorites <ID> --yaml 深入）
bili following --yaml         # 关注列表
```

分析流程：并行拉数据源 → 按主题/UP主聚类 → 对比收藏 vs 看过 vs 稍后再看 → 输出画像（兴趣分布、活跃度、关注结构）+ 1-2 条可执行观察（如"收藏很多教程但稍后再看堆了 30 条"）。结论带数字，不凭印象。

## 自有内容表现

```bash
bili my-dynamics --yaml                       # 我发的动态
bili user-videos <自己的mid> --max 20 --yaml   # 我的投稿（mid 从 whoami 拿）
bili video <bv_id> --yaml                     # 单个投稿数据
bili video <bv_id> --comments --yaml          # 该视频评论反馈
```

更深的数据（播放/粉丝图表、评论批量管理）→ `library.md` 创作中心节。

## 对标UP主分析

```bash
bili user "UP主名字" --yaml                  # 定位 mid + 基础数据
bili user-videos <mid> --max 20 --yaml       # 最近投稿（标题+时长+数据）
```

分析维度：
- **更新节奏**：投稿频率、时长分布
- **爆款共性**：哪些视频播放/点赞显著高于均值 → 标题风格、题材、时长
- **内容结构**：系列化（多P/合集）还是单发
- **评论区**：挑 2-3 个高表现视频 `bili video <bv_id> --comments --yaml`，看观众在夸什么、要什么

输出：对标报告——账号定位一句话、数据亮点（表格）、可借鉴的 3 个点。

## 策略

- 用户只说"看看我账号"时：先给概况 + 问想深入哪个方向，不直接拉全量数据
- 批量拉取克制：投稿列表默认 `--max 20`，逐个拿数据走缓存；HTTP 412 → 减量/等待
- 对标给的是结构和选题参考，提醒用户结合自己定位
