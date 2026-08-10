# 观看 B站 视频

当用户让你「看看」或「总结」一个 B站 视频时的策略。
多步骤操作时保持进度跟踪。

> **需要获取资源？** 看 `downloading.md`——它管怎么拿。本文只决定拿什么。

## 流程

```
创建进度计划，按以下步骤执行：

第1步: 元数据
  python3 scripts/get_video_info.py <bv_id>
  → 标题、时长、作者、数据、多P 警告
        │
第2步: 字幕（平台）
  python3 scripts/get_subtitle.py <bv_id>
        │
   ┌────┼──────────┐
   ▼    ▼          ▼
  ≤3K   >3K     无字幕
   │    │          │
   │  [SPLIT]     │
   │  并行压缩各段  │
   │  → 合并      │
   │    │         │
   └────┴─────────┘
        │
第3步: 质量检查
  模型读字幕（直接或压缩版）。
  判断：内容是干货，还是歌词/废话/广告？
        │
   ┌────┼────────────┐
   ▼    ▼            ▼
  好   差/无字幕     歌词/废话
   │    │            │
   │  第3b步:        │
   │  本地STT         │
   │  python3 scripts/ │
   │  extract_stt.py   │
   │  (未实现→降级    │
   │   为视觉分析)     │
   │    │            │
   └────┴────────────┘
        │
第4步: 评论
  python3 scripts/get_comments.py <bv_id> --mode hot
  python3 scripts/get_comments.py <bv_id> --mode latest
        │
第5步: 视觉
  帧是给自己做视觉分析的，不是给用户展示的全部素材。
  展示给用户哪些帧、几张，是 summarizing 阶段根据模式决定的。

  无字幕/差 → 强制抽帧：
    python3 scripts/compute_timestamps.py --duration <seconds>
    python3 scripts/extract_frames.py <bv_id> --at <timestamps>
    然后用平台的图片查看能力逐帧分析画面内容，
    将观察结果融入理解。这和最终给用户看什么不是一回事。

  字幕好 → 模型判断是否需要抽单个帧辅助理解：
    "3:15 提了图表" → 抽 195s 那帧，自己看
```

## 第3步详解：质量检查

拿到字幕后，读前 500 字判断：

| 信号 | 判断 | 是否需要视觉 |
|---|---|---|
| 术语、步骤、讲解 | ✅ 干货 | 可选——模型判断某个时间点要不要看画面 |
| "点赞/关注/投币"反复、歌词、表情刷屏 | ❌ 废话 | **强制**——需要抽帧 |
| 乱码、语言不对 | ❌ 差 | **强制**——同时试 `get_ai_summary.py` |
| 空 / `[NO SUBTITLE]` | ❌ 无 | **强制**——同时试 `get_ai_summary.py` |

**字幕好时**：模型思考每个关键时间点——画面有没有字幕传达不了的东西？
图表、UI、表情、场景切换？有就抽帧，没有就跳过。

**字幕差或无字幕时**：画面是主要信息源。用 `compute_timestamps.py` + `extract_frames.py` 抽帧。

## 并行压缩（字幕拆分）

当 `get_subtitle.py` 返回 `[SPLIT] N chunks` 时，将每段字幕交给独立任务并行压缩：

```
每个任务:
  "压缩这段B站字幕 [00:00-02:15]。保留关键信息和时间戳 [MM:SS]。
   去掉广告、废话、重复。输出不超过原文50%。"

→ 合并所有压缩结果
→ 保存到 subtitle.compressed.md
→ 读压缩版
```

## 多P 视频

如果元数据显示 `[MULTI-P: N pages]`：
- 警告用户，只处理第1P
- 其他P：用 yt-dlp `-I <N>`（超出 bili CLI 范围）
