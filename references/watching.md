# 观看 B站 视频

当用户让你「看看」或「总结」一个 B站 视频时的策略。
多步骤操作时保持进度跟踪。

> **脚本详细参数和边界情况** 看 `downloading.md`。

## 流程

四阶段：解析 → 收集 → 分析 → 补充。

### 阶段零：解析（识别视频类型、建立缓存目录）

```
第0步: 解析链接
  python3 scripts/resolve_video_id.py <url>
  → 输出 YAML：type, bv_id, page, cache_dir, index_path
  → type=single: 普通视频，cache_dir=.../BV1xx/
  → type=multi_p: 多P视频，cache_dir=.../BV1xx/pN/
  → type=collection: 合集，cache_dir=.../<sid>/<bv_id>/
  → 同时生成 index.yaml（多P列表）和 resolve.yaml（元信息）
```

后续所有脚本都加 `--cache-dir <cache_dir>` 指向 resolve 返回的目录。

### 阶段一：收集（并行获取所有可用内容）

```
第1步: 元数据
  python3 scripts/get_video_info.py <bv_id> --cache-dir <cache_dir>
  → 标题、时长、作者、数据、多P 警告

第2步: 并行拉取字幕、AI总结、评论（三者互不依赖，同时进行）
  python3 scripts/get_subtitle.py <bv_id> --cache-dir <cache_dir>
  python3 scripts/get_ai_summary.py <bv_id> --cache-dir <cache_dir>
  python3 scripts/get_comments.py <bv_id> --cache-dir <cache_dir> --mode hot
  python3 scripts/get_comments.py <bv_id> --cache-dir <cache_dir> --mode latest

  → 字幕可能无、AI总结可能空、评论可能少——都先拿到手再说
```

### 阶段二：分析（读内容，评估信息量）

逐一阅读阶段一的结果，判断信息是否足够理解视频：
- 字幕好（有术语、步骤、讲解）→ 基本够了，但可以思考从内容推理出是否需要再看看画面
- 字幕差（歌词、广告、废话、乱码）或无 → 缺口，需要补充
- AI总结和评论始终作为辅助信息源

信息够 → 进入总结；不够 → 进入阶段三。

### 阶段三：补充（按需获取视觉信息）

```
根据阶段二的缺口，动态决定：

需要视觉（字幕差/无/废话）：
  python3 scripts/compute_timestamps.py --duration <seconds>
  python3 scripts/extract_frames.py <bv_id> --cache-dir <cache_dir> --at <timestamps>
  用平台的图片分析能力逐帧分析（见下方「看图方式」），融入理解

需要 STT（字幕无但需要理解口播内容）：
  python3 scripts/extract_stt.py <bv_id>
  → 留白项：本技能不提供实现，由你按用户偏好自行补充（通常是调用语音识别服务）
  → 输入音频用 extract_audio.py 备好；确实无实现时降级为视觉分析

不需要补充（字幕够好）：
  模型自己决定要不要在关键时间点抽个别帧辅助理解
  "3:15 提了图表" → 可选抽那帧看一下
```

### 看图方式

帧有两个用途：**自己分析**（主要）和**展示给用户**（有视觉亮点时，见 summarizing.md「展示帧给用户」）。这里讲自己分析：
- 用平台的图片/视觉分析能力查看帧文件，自己看画面内容。不要用浏览器打开图片给用户看。
- 视觉工具不可用时，基于字幕、评论、AI总结完成理解，不强制抽帧。

## 字幕超长处理

当 `get_subtitle.py` 返回 `[SPLIT] N chunks` 时，用平台的并行任务机制将各段分发给独立任务同时压缩：

```
每个并行任务:
  "压缩这段B站字幕 [00:00-02:15]。保留关键信息和时间戳 [MM:SS]。
   去掉广告、废话、重复。输出不超过原文50%。"

→ 合并所有压缩结果 → 保存到 subtitle.compressed.md → 读压缩版
```

不要在主流程里逐段串行处理——N 段就开 N 个并行任务。

## 多P 视频

如果 resolve 返回 `type: multi_p`：
- 默认只处理当前页（page=1），cache_dir 指向 `p1/`
- 警告用户有 N 个分P，只处理第1P
- index.yaml 包含全部 P 的列表（标题、时长）
- 列出全部分P标题：
  `cat <cache_dir>/../index.yaml`
- 用户要求处理全部时：读 index.yaml → 拆子代理，每个子代理处理一P
- 下载其他P：`yt-dlp -I <N> https://www.bilibili.com/video/<bv_id>`

## 合集视频

如果 resolve 返回 `type: collection`：
- 默认处理第一个视频，cache_dir 指向 `.../<sid>/<bv_id>/`
- index.yaml 包含合集全部视频（bv_id、标题、时长）
- 警告用户合集有 N 个视频，只处理第一个
- 用户要求处理全部时：读 index.yaml → 拆子代理，每个子代理处理一个 bv_id
  （每个视频的 cache_dir = `.../<sid>/<bv_id>/`）
