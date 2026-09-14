# bilibili-api-python 17.4.2 能力清单

- **库全名**：bilibili-api-python（import 名 `bilibili_api`）
- **版本**：17.4.2（PyPI 末版，绝版）
- **生成日期**：2026-09-14
- **来源**：从 17.4.2 wheel 源码逐一枚举（`vendor/bilibili_api_python-17.4.2-py3-none-any.whl` 解包），所有条目均以源码实际代码为准
- **License**：GPL-3.0-or-later
- **维护状态**：GitHub 仓库 2026-07 被 B站侵权告知函关停，不再有上游更新；B站接口变更后相关能力可能静默失效

本文覆盖 17.4.2 全部 41 个功能模块（不含 `__init__.py`）。另有三个支撑子包在相应章节顺带说明：`utils/`（网络层、Credential、parse_link 等）、`exceptions/`（异常类）、`tools/ivitools`（互动视频播放器）。

## 能力总览

### 视频

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| video | 视频信息/下载直链/弹幕/点赞投币收藏/字幕/播放数据上报 | `Video`, `VideoOnlineMonitor`, `VideoDownloadURLDataDetecter` |
| interactive_video | 互动视频剧情树解析、编辑、整部下载打包 | `InteractiveVideo`, `InteractiveVideoDownloader` |
| video_tag | 视频标签查询、关注/取关标签 | `Tag` |
| video_zone | 视频分区查询（本地 JSON）、分区排行 | （纯函数 + `VideoZoneTypes` 枚举） |

### 用户与社交

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| user | 用户空间/投稿/关系链/个人数据/关注分组/历史记录 | `User` |
| black_room | 小黑屋封禁公示、风纪委员案件仲裁 | `BlackRoom`, `JuryCase` |

### 动态与内容发布

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| dynamic | 动态读取/发布/删除/置顶/转发、定时动态、抽奖信息 | `Dynamic`, `BuildDynamic` |
| opus | 图文（专栏式动态）读取与转 Markdown | `Opus` |
| vote | 投票创建/更新/查询 | `Vote`, `VoteChoices` |
| topic | 话题搜索/内容列表/点赞收藏 | `Topic` |
| emoji | 表情包列表/详情/添加 | （纯函数） |

### 评论与弹幕

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| comment | 通用评论发送/点赞/点踩/置顶/删除/举报/子评论 | `Comment` |
| ass | 字幕获取转 ass/srt/lrc、弹幕转 ass 文件 | `AssSubtitleObject` |

### 直播

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| live | 直播间信息/开播下播/禁言/送礼/弹幕收发/实时弹幕监听 | `LiveRoom`, `LiveDanmaku` |
| live_area | 直播分区查询、按分区列直播间 | （纯函数） |
| watchroom | 一起看放映室创建/加入/播放控制/踢人 | `WatchRoom` |

### 音频

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| audio | 音频/歌单信息、下载直链、投币 | `Audio`, `AudioList` |
| music | 视频关联 BGM 元数据、音乐索引 | `Music` |
| audio_uploader | 音频投稿上传（含歌词/封面） | `AudioUploader`, `SongMeta` |

### 专栏文章与笔记

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| article | 专栏读取/转 Markdown/点赞/收藏/投币 | `Article`, `ArticleList` |
| article_category | 专栏分类查询、分区推荐文章 | （纯函数 + `ArticleOrder`） |
| note | 视频笔记（公开/私有）读取与转 Markdown | `Note` |

### 收藏与历史

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| favorite_list | 收藏夹增删改/内容复制移动/多类型收藏列表 | `FavoriteList` |

### 漫画·番剧·课程

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| manga | 追漫列表/追漫设置/更新推荐 | `Manga` |
| bangumi | 番剧/影视元数据、索引筛选、追番、剧集弹幕字幕 | `Bangumi`, `Episode` |
| cheese | 课程（知识区付费）列表与视频、下载直链 | `CheeseList`, `CheeseVideo` |

### 搜索与发现

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| search | 全类型搜索、热搜、搜索联想 | （纯函数 + 多个枚举） |
| hot | 热门视频、每周必看、入站必刷、热词图鉴 | （纯函数） |
| rank | 全站/分区/音乐/大会员/漫画/直播/短剧各类榜单 | （纯函数 + 多个枚举） |
| homepage | 首页推荐视频、顶部图、链接、收藏夹+稍后再看入口 | （纯函数） |

### 登录与凭证

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| login_v2 | 密码/短信/二维码（Web+TV）登录与安全验证 | `QrCodeLogin`, `LoginCheck`, `PhoneNumber` |

### 私信与会话

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| session | 私信收发、回复/赞/@通知、会话轮询监听 | `Session`, `Event` |

### 创作工具

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| video_uploader | 视频分 P 上传、稿件编辑、封面/话题/活动 | `VideoUploader`, `VideoEditor`, `VideoMeta` |
| creative_center | 创作中心数据看板、评论管理、弹幕管理 | （纯函数 + 多个枚举） |

### 其他

| 模块 | 一句话用途 | 关键类 |
|---|---|---|
| activity | 活动列表/详情、活动评论区 aid | （纯函数） |
| app | 手机 App 开屏图 | （纯函数） |
| client | IP 归属地查询（主站/直播接口） | （纯函数） |
| festival | 节日专门页（拜年祭等）信息 | `Festival` |
| game | 游戏中心游戏详情/排行榜/公测时间线 | `Game` |
| garb | 装扮/收藏集搜索与详情 | `DLC`, `Garb` |
| show | 会员购展出/票务信息、创建购票订单 | `OrderTicket` |

## 分模块详解

### video —— 视频核心

模块 docstring：视频相关操作（同时存在 page_index 和 cid 的参数时，两者至少提供一个）。

**Video**（bvid/aid 构造）关键 async 方法：

- `get_info` / `get_detail` —— 基本信息 / 详细信息（含 tag、staff）
- `is_episode` / `turn_to_episode` —— 判断并转为番剧 Episode
- `get_tags` —— 标签列表（按分 P）
- `get_chargers` —— 充电用户列表
- `get_pages` / `get_cid` —— 分 P 列表 / 指定分 P 的 cid
- `get_video_snapshot` —— 视频 storyboard 截图拼图（预览图）
- `get_download_url` —— 播放流直链（DASH/FLV/MP4，可 html5 免鉴权），配合 `VideoDownloadURLDataDetecter`
- `get_related` —— 相关视频推荐
- `get_relation` / `has_liked` / `get_pay_coins` / `has_favoured` —— 自己与该视频的交互状态
- `get_ai_conclusion` —— B站官方 AI 视频总结（本 skill 在用的能力）
- `get_pbp` —— 高能进度条（heatmap 原始数据）
- `get_online` —— 实时在线人数
- `get_danmaku_view` / `get_danmakus` / `get_special_dms` / `get_history_danmaku_index` / `get_danmaku_xml` / `get_danmaku_snapshot` —— 弹幕视图/全量弹幕（protobuf 解析）/特殊弹幕/历史弹幕索引/XML 源
- `send_danmaku` / `like_danmaku` / `recall_danmaku` / `operate_danmaku` —— 发送/点赞/撤回/删除保护弹幕
- `has_liked_danmakus` —— 查询弹幕是否已点赞
- `like` / `pay_coin` / `triple` / `share` —— 点赞 / 投币 / 一键三连 / 分享
- `set_favorite` —— 设置收藏（指定收藏夹增删）
- `add_tag` / `delete_tag` —— 管理标签（UP 主）
- `appeal` —— 投诉稿件（`VideoAppealReasonType` 枚举）
- `get_player_info` / `get_subtitle` / `submit_subtitle` —— 播放器信息 / 字幕列表 / **上传字幕**
- `is_forbid_note` / `get_private_notes_list` / `get_public_notes_list` —— 笔记开关与列表
- `add_to_toview` / `delete_from_toview` —— 稍后再看增删
- `report_watch_history` / `report_start_watching` —— 上报观看进度 / 开始观看（计播放量）

**VideoOnlineMonitor**：WebSocket 实时在线人数与弹幕监听，`connect`/`disconnect`，事件 `ONLINE`/`DANMAKU`。

**VideoDownloadURLDataDetecter**：`check_video_and_audio_stream`、`check_flv_mp4_stream`、`detect`（按清晰度/编码/音质过滤）、`detect_best_streams`（选最优流）。配套 dataclass：`VideoStreamDownloadURL`/`AudioStreamDownloadURL`/`FLVStreamDownloadURL`/`MP4StreamDownloadURL`。

模块级：`get_cid_info(cid)` —— 用 cid 反查视频（走 biliplus 第三方 API）。

注：`get_stat` 已被源码注释（接口 403/404）。

### interactive_video —— 互动视频

模块 docstring：互动视频相关操作。

**InteractiveVideo**（继承 Video）新增：

- `up_get_ivideo_pages` —— 获取互动视频分 P（需 UP 主身份）
- `up_submit_story_tree` —— **上传/编辑剧情树**（需 UP 主身份）
- `get_graph_version` / `get_edge_info` —— 剧情图版本 / 节点信息（含选择按钮）
- `get_graph` —— 获取完整情节树 `InteractiveGraph`
- `mark_score` —— 为互动视频打分

剧情树模型类：`InteractiveVariable`（变量，含随机变量）、`InteractiveButton`、`InteractiveJumpingCondition`（条件表达式求值）、`InteractiveJumpingCommand`（变量赋值命令）、`InteractiveNode`（`get_children` 遍历子节点）、`InteractiveGraph`（`get_root_node` 从根遍历）。

**InteractiveVideoDownloader**：`start`/`abort` 下载全部节点视频；模式枚举 `InteractiveVideoDownloaderMode`（打包 `.ivi` / 仅节点视频 / dot 图）；事件枚举 `InteractiveVideoDownloaderEvents`。模块级 `get_ivi_file_meta` 解析 ivi 包。

另附 `tools/ivitools`：命令行工具（`__main__.py`），含 `player.py` —— 基于 **PyQt6** 的互动视频桌面播放器（依赖较重）。

### video_tag —— 视频标签

模块 docstring：视频标签相关，部分标签 id 与同名频道 id 一致。

**Tag**（tag_name/tag_id 任一构造）：`get_tag_id`、`get_tag_name`、`get_tag_info`、`get_similar_tags`、`subscribe_tag`（关注标签）、`unsubscribe_tag`（取关标签）。

### video_zone —— 视频分区

模块 docstring：分区相关操作，与频道不互通。

纯函数：`get_zone_info_by_tid`、`get_zone_info_by_name`、`get_zone_list`、`get_zone_list_sub`（读本地 `video_zone.json`，无需请求）；`get_zone_top10(tid, day)` async —— 分区 3/7 日前十排行。`VideoZoneTypes` 枚举列全部分区。

### user —— 用户与社交

模块 docstring：用户相关。

**User** 关键 async 方法：

- `get_user_info` —— 空间详情（含 w_webid 风控参数自动获取 `get_access_id`）
- `get_space_notice` / `set_space_notice` —— 空间公告读/写
- `get_relation_info` / `get_relation` —— 关注粉丝统计 / 与某用户的关系
- `modify_relation` —— **关注/取关/拉黑/解除拉黑/移除粉丝**（`RelationType`）
- `get_up_stat` —— UP 主总播放/阅读/点赞（需登录）
- `get_top_videos` / `get_masterpiece` —— 代表作
- `get_user_medal` —— 粉丝牌列表
- `get_live_info` —— 用户直播间信息
- `get_videos` / `get_media_list` —— 投稿视频（支持分区/关键词/排序）
- `get_audios` / `get_album` / `get_articles` / `get_article_list` —— 音频/相簿/专栏/文集
- `get_dynamics` / `get_dynamics_new` —— 用户动态（旧/新接口）
- `get_upower_qa_list` / `get_upower_qa_detail` —— 充电专属问答
- `get_subscribed_bangumi` —— 追番/追剧列表（`BangumiFollowStatus`）
- `get_followings` / `get_all_followings` / `get_followers` / `top_followers` / `get_self_same_followers` —— 关注/粉丝/共同关注/粉丝排行
- `get_overview_stat` —— 订阅投稿概览
- `get_channel_videos_series` / `get_channel_videos_season` / `get_channel_list` / `get_channels` —— 合集与列表
- `get_cheese` —— 用户课程
- `get_reservation` —— 空间预约（直播/投稿预约）
- `get_elec_user_monthly` —— 充电公示
- `get_uplikeimg` —— 三连特效图
- `get_opus` —— 用户图文列表
- `get_user_fav_tag` —— 关注的标签

模块级 async 函数：

- `name2uid` —— 用户名转 uid
- `get_self_info` / `edit_self_info` —— 自己的信息读/**写**（昵称/签名/生日/性别）
- `create_subscribe_group` / `delete_subscribe_group` / `rename_subscribe_group` / `set_subscribe_group` —— **关注分组管理**
- `get_self_history` / `get_self_history_new` —— 浏览历史（旧/新，新接口支持类型过滤）
- `get_self_coins` —— 硬币余额
- `get_self_special_followings` / `get_self_whisper_followings` / `get_self_friends` / `get_self_black_list` —— 特殊关注/悄悄关注/互粉/黑名单
- `get_toview_list` / `clear_toview_list` / `delete_viewed_videos_from_toview` —— 稍后再看列表读/清空/删已看
- `check_nickname` —— 昵称可用性校验
- `get_self_notes_info` / `get_self_public_notes_info` —— 自己的笔记列表
- `get_self_jury_info` —— 风纪委员信息
- `get_self_login_log` / `get_self_moral_log` / `get_self_experience_log` —— 登录/节操/经验记录

### black_room —— 小黑屋与仲裁

模块 docstring：小黑屋。

- `get_blocked_list` —— 封禁公示列表（按类型/来源过滤）
- **BlackRoom**：`get_details`、`get_reason`（封禁原因枚举）
- **JuryCase**（风纪委员）：`get_details` 案件详情、`get_opinions` 观点列表、`vote` **提交仲裁投票**（`JuryVoteOpinion`）
- `get_next_jury_case` —— 领取下一个待审案件
- `get_jury_case_raw` / `get_jury_case_list` —— 案件列表

### dynamic —— 动态

模块 docstring：动态相关。

- `upload_image` —— 上传动态图片
- **BuildDynamic** —— 动态内容构建器（链式 + 参数两种）：`empty`/`create_by_args`、`add_plain_text`、`add_text`（自动解析 @ 和 [表情]）、`add_at`、`add_emoji`、`add_vote`、`add_image`、`set_topic`（话题）、`set_attach_card`（直播预约卡片）、`set_options`（精选评论/关闭评论）、`set_send_time`（**定时发布**）
- `send_dynamic` —— 发布动态（图片自动上传）
- `get_schedules_list` / `send_schedule_now` / `delete_schedule` —— 定时动态列表/立即发布/删除
- **Dynamic**：`get_info`、`is_article`/`turn_to_article`、`is_opus`/`turn_to_opus`、`markdown`（转 Markdown 含 YAML 元数据）、`get_reaction`（点赞转发列表）、`get_reposts`、`get_likes`、`get_rid`（评论 oid）、`set_like`、`set_favorite`、`delete`、`repost`（**转发动态**）、`get_lottery_info`（动态抽奖详情）、`set_top`/`remove_top`（置顶）
- `get_new_dynamic_users` / `get_live_users` —— 关注的 UP 谁更新了动态 / 谁在直播
- `get_dynamic_page_UPs_info` / `get_dynamic_page_info` / `get_dynamic_page_list` —— 动态页信息与列表（全类型或指定 UP）

### opus —— 图文

模块 docstring：图文相关。

**Opus**：`get_info`、`is_article`/`turn_to_article`（图文与专栏/动态数据共享）、`turn_to_dynamic`、`markdown`（含代码块/居中/表情图片）、`get_images_raw_info`/`get_images`（提取全部图片为 `Picture`）、`set_like`、`set_favorite`、`add_coins`、`get_reaction`、`get_rid`。

### vote —— 投票

模块 docstring：投票相关操作。

- **VoteChoices** —— 投票选项构建（`add_choice` 支持图片选项）
- `create_vote` —— **创建投票**（文字/图片、多选数、持续秒数）
- **Vote**：`get_info`、`get_title`、`update_vote`（更新投票内容）

### topic —— 话题

模块 docstring：话题相关。

- `get_hot_topics` —— 动态页火热话题
- `search_topic` —— 搜索话题
- **Topic**：`get_info`、`get_cards`（话题下内容，最新/最热/推荐排序）、`like`（点赞话题）、`set_favorite`（收藏话题）

### emoji —— 表情包

模块 docstring：表情包相关。

`get_emoji_list`（按 reply/dynamic 场景）、`get_emoji_detail`、`get_all_emoji`、`add_emoji`（**添加表情包**）。

### comment —— 评论

模块 docstring：评论相关（oid 适配视频/专栏/动态图文/课程/音频/歌单/小黑屋/漫画/活动，`CommentResourceType` 枚举）。

- **Comment**（单条评论操作）：`like`、`hate`（点踩）、`pin`（**置顶**，UP 主）、`delete`（删除自己的）、`get_sub_comments`（子评论翻页）、`report`（**举报**，`ReportReason` 枚举 17 类）
- `send_comment` —— **通用发送评论**：支持回复楼中楼（root/parent），支持携带图片（自动走动态图床上传）
- `get_comments` / `get_comments_lazy` —— 评论列表（旧版翻页 / 新版 offset 链表）

### ass —— 字幕与弹幕转 ass

模块 docstring：有关 ASS 文件的操作。

- **AssSubtitleObject**：`get_lan_list`（可选语言）、`request_ass_data_json`/`request_ass_data_str`（拉取字幕 JSON）、`to_srt` 等
- `request_subtitle_languages` / `request_subtitle` —— 对 Video/Episode/CheeseVideo 拉取字幕
- `make_ass_file_subtitle` / `make_srt_file_subtitle` / `make_lrc_file_subtitle` / `make_simple_json_file_subtitle` —— 字幕落盘为 ass/srt/lrc/简化 JSON
- `make_ass_file_danmakus_protobuf` / `make_ass_file_danmakus_xml` —— **弹幕转 ass 字幕文件**（protobuf 或 XML 源，内部用 `utils/danmaku2ass.py`）

### live —— 直播

模块 docstring：直播相关。

**LiveRoom** 关键 async 方法：

- `start(area_id)` / `stop` —— **开播 / 下播**
- `get_room_play_info` / `get_room_info` / `get_room_play_info_v2` —— 房间信息、真实房间号、可用清晰度与流地址
- `get_room_play_url` —— 直播流直链（清晰度枚举到 4K）
- `get_danmu_info` —— 弹幕服务器配置
- `get_emoticons` —— 房间可用表情
- `get_fan_model` / `get_user_info_in_room` / `get_general_info` —— 粉丝牌 / 自己在房间的信息 / 大航海状态
- `get_popular_ticket_num` / `send_popular_ticket` —— 人气票查询 / **赠送免费人气票**
- `get_dahanghai` / `get_gaonengbang` / `get_seven_rank` / `get_fans_medal_rank` —— 大航海/高能榜/七日榜/粉丝牌榜
- `get_black_list` —— 房间黑名单
- `ban_user` / `unban_user` —— **房管禁言 / 解禁**
- `send_danmaku` / `send_emoticon` —— 直播间发弹幕 / 发表情
- `sign_up_dahanghai` —— 大航海签到
- `send_gift_from_bag` / `send_gift_gold` / `send_gift_silver` —— **送背包礼物 / 金瓜子 / 银瓜子礼物**
- `receive_reward` —— 领取航海日志奖励
- `update_news` —— **修改直播间公告**

**LiveDanmaku**：WebSocket 实时弹幕/事件监听，`connect`/`disconnect`；事件覆盖 60+ cmd（DANMU_MSG、SEND_GIFT、SUPER_CHAT_MESSAGE、GUARD_BUY、天选时刻 ANCHOR_LOT_*、禁言、红包、进场特效等，见类 docstring）；自动解析 protobuf（INTERACT_WORD_V2、ONLINE_RANK_V3）。

模块级 async 函数：`get_self_info`、`get_self_live_info`、`get_self_dahanghai_info`、`get_self_bag`（礼物背包）、`get_gift_config`（全量礼物配置）、`get_area_info`、`get_live_followers_info` / `get_unlive_followers_info`（关注的主播开播/未开播）、`create_live_reserve`（**创建直播预约**）、`get_self_live_watching_history`（直播观看记录）。

注：`get_gift_special` 已失效（docstring 注明，改用 `get_gift_config`）。

### live_area —— 直播分区

模块 docstring：直播间分区相关操作。

`fetch_live_area_data`（抓取并缓存分区数据）、`get_area_info_by_id`/`get_area_info_by_name`、`get_area_list`/`get_area_list_sub`、`get_list_by_area`（按分区列直播间，含 w_webid 风控）。

### watchroom —— 放映室（一起看）

模块 docstring：放映室相关 API（需 Credential 且带 buvid3）。

- `create(season_id, episode_id)` —— **创建放映室**
- `match` —— 匹配公开放映室
- **WatchRoom**：`get_info`、`open`/`close`（公开/关闭）、`progress`（**设置播放进度与暂停**）、`join`（凭 token 加入）、`send`（房间聊天，`Message`/`MessageSegment` 支持表情）、`kickout`（踢人）、`share`（获取邀请 token）

### audio —— 音频

模块 docstring：音频相关。

- **Audio**（auid）：`get_info`、`get_tags`、`get_download_url`、`add_coins`（音频投币）
- **AudioList**（amid，歌单）：`get_info`、`get_tags`、`get_song_list`
- `get_user_stat` —— 用户音乐页数据；`get_hot_song_list` —— 热门歌单

### music —— 音乐（BGM）

模块 docstring：B站音频与音乐不互通；此处数据来自视频 bgm 标签和全站音乐榜。

- `get_homepage_recommend` —— 音频首页推荐
- `get_music_index_info` —— 音乐索引（语言/风格/排序筛选）
- **Music**（music_id，如 MA436...）：`get_info`、`get_music_videos`（该 BGM 的视频列表）

### audio_uploader —— 音频投稿

模块 docstring：音频上传。

- **AudioUploader**：`start`/`abort` —— 上传音频文件（事件 `AudioUploaderEvents`）
- **SongMeta** —— 歌曲元数据 dataclass（类型/语言/风格/作词作曲编曲混音等 30+ 字段）
- `SongCategories` / `CompilationCategories` —— 官方分类枚举全集
- `upload_lrc` —— 上传歌词；`get_upinfo` —— 创作者信息搜索；`upload_cover` —— 上传封面

### article —— 专栏

模块 docstring：专栏相关。

- `get_article_rank` —— 专栏排行榜（日/周/月榜）
- **ArticleList**（rlid 文集）：`get_content`
- **Article**（cvid）：`get_info`、`get_detail`、`get_all`（含 dyn_id 映射）、`fetch_content`（解析 HTML 正文为节点树）、`markdown`、`json`、`set_like`、`set_favorite`、`add_coins`（专栏投币）、`turn_to_dynamic`/`turn_to_opus`/`is_note`/`turn_to_note`
- Node 体系（`ParagraphNode`/`ImageNode`/`CodeNode`/`LatexNode`/各卡片 Node 等）—— 专栏正文解析树

注：源码注释 `# TODO: 专栏上传/编辑/删除` —— **专栏写操作未实现**，只有读取与互动。

### article_category —— 专栏分类

模块 docstring：专栏分类相关。

纯数据函数：`get_category_info_by_id`/`get_category_info_by_name`/`get_categories_list`/`get_categories_list_sub`（本地 JSON）；async `get_category_recommend_articles` —— 分区推荐文章（`ArticleOrder` 排序）。

### note —— 笔记

模块 docstring：笔记相关。

- `upload_image` —— 上传笔记图片
- **Note**（公开=cvid / 私有=aid+note_id）：`get_info`（`get_private_note_info`/`get_public_note_info`）、`get_images_raw_info`/`get_images`、`get_all`、`set_like`、`set_favorite`、`add_coins`、`fetch_content`/`markdown`/`json`

注：源码注释 `# TODO: 笔记上传/编辑/删除` —— 笔记写操作未实现。

### favorite_list —— 收藏夹

模块 docstring：收藏夹操作。

- **FavoriteList**（视频/专栏/课程三种类型）：`get_info`、`get_content_video`（支持关键词搜索/排序/跨收藏夹搜索）、`get_content`、`get_content_ids_info`
- `get_video_favorite_list` —— 某用户的收藏夹列表（可检测某视频是否已在其中）
- `get_video_favorite_list_content` —— 收藏夹内容
- `get_topic_favorite_list` / `get_article_favorite_list` / `get_course_favorite_list` / `get_note_favorite_list` —— 话题/专栏/课程/笔记收藏
- `create_video_favorite_list` / `modify_video_favorite_list` / `delete_video_favorite_list` —— **新建 / 修改 / 删除收藏夹**
- `copy_video_favorite_list_content` / `move_video_favorite_list_content` / `delete_video_favorite_list_content` / `clean_video_favorite_list_content` —— **内容复制 / 移动 / 删除 / 清除失效稿件**
- `get_favorite_collected` —— 收藏的合集列表

### manga —— 漫画

模块 docstring：漫画相关操作。

- `set_follow_manga` —— **追漫 / 取消追漫**
- `get_followed_manga` —— 追漫列表（`MangaOrderType` 排序）
- `get_manga_update` —— 每日更新推荐
- `get_manga_home_recommend` —— 首页推荐漫画

注：`Manga.get_info`、`get_episode_info`、`get_images`、漫画索引 `get_manga_index` 等均已失效（源码注释「此函数已失效 2025-01-04」「失效 2025-01-27」），漫画正文图片获取不可用。

### bangumi —— 番剧与影视

模块 docstring：番剧相关（media_id/season_id/episode_id 三级概念）。

- `get_timeline` —— 番剧时间线（`BangumiType`：番剧/影视/国创）
- `get_index_info` —— 番剧索引筛选查询（`IndexFilterMeta` 提供地区/季度/付费/字幕等全量筛选枚举）
- **Bangumi**（md/ss/ep 任一构造，支持港澳台 oversea 兼容）：`get_media_id`/`get_season_id`、`get_up_info`、`get_meta`（评分/封面）、`get_short_comment_list`/`get_long_comment_list`（短评/长评）、`get_episode_list`/`get_episodes`（分集列表并生成 Episode 对象）、`get_stat`（播放/追番数据）、`get_overview`
- `set_follow` / `update_follow_status` —— **追番开关 / 追番状态**（想看/在看/已看）
- **Episode**（继承 Video，epid 构造）：`get_bvid`/`get_aid`/`get_cid`、`turn_to_video`、`get_episode_info`、`get_bangumi_from_episode`、`get_download_url`（番剧播放直链）、`set_favorite`（type=42 收藏）、弹幕全套（`get_danmakus`/`get_danmaku_view`/`get_danmaku_xml`/`get_history_danmaku_index`/`send_danmaku`/`recall_danmaku`）、字幕全套（`get_player_info`/`get_subtitle`/`submit_subtitle`）、`get_pbp`、`get_ai_conclusion`

### cheese —— 课程

模块 docstring：bilibili 课程 API；课程视频与其他视频几乎不互通，season_id/ep_id 不与番剧相通。

- **CheeseList**（season_id/ep_id）：`get_meta`、`get_list_raw`、`get_list`（生成 `CheeseVideo` 列表）
- **CheeseVideo**（epid）：`get_aid`/`get_cid`/`get_meta`/`get_cheese`、`get_download_url`（课程播放直链）、`get_stat`、`get_pages`、`get_danmaku_view`/`get_danmakus`/`get_danmaku_xml`/`send_danmaku`、`has_liked`/`get_pay_coins`/`has_favoured`/`like`/`pay_coin`/`set_favorite`、`get_pbp`

### search —— 搜索

模块 docstring：搜索。

- `search` —— 仅关键词的 Web 搜索
- `search_by_type` —— 按类型搜索（视频/番剧/影视/直播/专栏/话题/用户/直播用户/相簿），支持排序、时长区间、分区 tid、发布时间区间
- `get_default_search_keyword` / `get_hot_search_keywords` / `get_suggest_keywords` —— 默认词 / 热搜 / 联想词
- `search_games` / `search_manga` / `search_cheese` —— 游戏 / 漫画 / 课程专用搜索

### hot —— 热门

模块 docstring：热门相关 API。

`get_hot_videos`、`get_weekly_hot_videos_list`/`get_weekly_hot_videos`（每周必看）、`get_history_popular_videos`（入站必刷 85 个）、`get_hot_buzzwords`（热词图鉴）。

### rank —— 排行榜

模块 docstring：和哔哩哔哩视频排行榜相关的 API。

`get_rank`（全站及 20+ 分区，`RankType`）、`get_music_rank_list`/`get_music_rank_weekly_detail`/`get_music_rank_weekly_musics`（全站音乐榜）、`get_vip_rank`（大会员热播榜）、`get_manga_rank`（漫画榜）、`get_live_hot_rank`/`get_live_sailing_rank`/`get_live_energy_user_rank`/`get_live_rank`/`get_live_user_medal_rank`（直播各榜）、`subscribe_music_rank`（**关注音乐榜**）、`get_playlet_rank_phases`/`get_playlet_rank_info`（短剧榜）。

### homepage —— 首页

模块 docstring：主页相关操作。

`get_top_photo`（首页顶部图）、`get_links`、`get_popularize`（推广位）、`get_videos`（**首页推荐视频**）、`get_favorite_list_and_toview`/`get_favorite_list_content`（右上角收藏夹+稍后再看入口）。

### login_v2 —— 登录

模块 docstring：登录。

- `login_with_password` —— **密码登录**（RSA 加密，需 `Geetest` 极验；返回 Credential 或 `LoginCheck`）
- `send_sms` / `login_with_sms` —— **短信验证码登录**（`PhoneNumber` 支持国际区号）
- **QrCodeLogin** —— **二维码登录**（Web / TV 双渠道）：`generate_qrcode`（生成 Picture 与终端字符串）、`check_state`（SCAN/CONF/TIMEOUT/DONE）
- **LoginCheck** —— 密码登录二次验证：`fetch_info`、`send_sms`、`complete_check`
- 国家区号工具：`get_countries_list`/`search_countries`/`have_code` 等

配套 `utils/network.py` 的 **Credential**：`check_valid`（cookie 是否有效）、`check_refresh`（是否需要刷新）、`refresh`（**刷新 cookies**）、`from_cookies`；`utils/geetest.py` 提供极验验证码流程。

### session —— 私信与会话

模块 docstring：消息相关。

- `send_msg` —— **发送私聊消息**（文本/图片，图片自动上传）
- `fetch_session_msgs` —— 拉取某人最近 30 条消息
- `new_sessions` / `get_sessions` / `get_session_detail` —— 新消息 / 会话列表 / 会话详情（私聊/通知/应援团）
- `get_replies` / `get_likes` / `get_at` —— **收到的回复 / 赞 / @**
- `get_unread_messages` / `get_system_messages` / `get_session_settings` —— 未读 / 系统消息 / 消息设置
- **Session**（AsyncEvent）：`start`/`run`（6 秒轮询的**消息监听**，`on(EventType)` 注册回调）、`reply`（对事件快速回复）、`close`

### video_uploader —— 视频投稿

模块 docstring：视频上传。

- **VideoUploader**：`start`/`abort` —— 分 P 上传（线路选择 bda2/qn/ws/bldsa + 自动测速、分块续传、事件 `VideoUploaderEvents` 全程回调）
- **VideoMeta** —— 投稿元数据：分区/标题/简介/封面/标签/话题/活动/原创/充电/评论精选/弹幕开关/杜比/Hi-Res/字幕设置/**定时发布 delay_time**/**商单 porder**（`VideoPorderMeta` 花火/其他，行业/品牌/展示类型枚举）
- **VideoUploaderPage** —— 分 P 文件
- **VideoEditor**：`start`/`abort` —— **编辑已发布稿件**（改标题/简介/封面等）
- `upload_cover` —— 上传封面；`get_available_topics` —— 可用话题；`get_missions` —— 投稿活动列表

### creative_center —— 创作中心

模块 docstring：创作中心相关（务必携带 Credential）。

数据看板：`get_compare`（对比）、`get_graph`/`get_overview`（播放/访问/粉丝/点赞/收藏/分享/评论/弹幕/投币/充电图表与概览，时间段到历史累计）、`get_video_survey`（分区占比）、`get_video_playanalysis`（完播率）、`get_video_source`（播放来源分布）、`get_fan_overview`/`get_fan_graph`（粉丝概览/新增/取关）、`get_article_overview`/`get_article_graph`/`get_article_rank`/`get_article_source`（文章数据）。

内容管理：`get_video_draft_upload_manager_info`（草稿）、`get_video_upload_manager_info`（稿件列表，按状态/分区/排序）、`get_article_upload_manager_info`/`get_article_list_upload_manager_info`（文章/文集管理）。

评论管理：`get_comments`（**全账号评论搜索**，按稿件类型/关键词）、`del_comments`（**批量删除评论**）。

弹幕管理：`get_recently_danmakus`、`get_danmakus`（**弹幕高级搜索**：按稿件/用户/关键词/进度/时间/模式/弹幕池）、`del_danmaku`、`edit_danmaku_state`（删除/保护/取消保护）、`edit_danmaku_pool`（移入字幕池）。

单稿件：`get_archive_edits`（**稿件编辑记录**）、`get_archive_parts`（分 P 信息）。

### 其他模块（简述）

- **activity**：`get_activity_list`（活动列表）、`get_activity_info`（详情）、`get_activity_aid`（活动评论区 aid，可配合 comment 读活动评论）。
- **app**：`get_loading_images` / `get_loading_images_special` —— App 开屏图（含生日彩蛋参数）。
- **client**：`get_zone` / `get_zone_live` —— IP 归属地。
- **festival**：`Festival.get_info` —— 节日专门页（festival id 如拜年祭）信息。
- **game**：**Game**（`get_info`/`get_up_info`/`get_detail`/`get_wiki`/`get_videos`）；`get_game_rank`（热度/预约/新游/口碑/B指/端游榜）、`get_start_test_list`（公测时间线）、`game_name2id`（游戏名转编码，走 biligame wiki）。
- **garb**：`search_garb_dlc_raw`/`search_garb_dlc_obj`/`search_garb_dlc`（搜索装扮/收藏集）、`get_garb_dlc_items_raw`/`_obj`/`get_garb_dlc_items`（列表）；**DLC**（收藏集：`get_info`/`get_lottery_id`/`get_detail`）、**Garb**（装扮：`get_detail`）。
- **show**：`get_project_info`（演出项目信息）、`get_available_sessions`（场次票档）、`get_all_buyer_info`/`get_all_buyer_info_obj`（购票人信息）；**OrderTicket**：`get_token`、`create_order` —— **创建购票订单**（自动处理一人一证载荷与点击坐标伪装）。

### 支撑设施（utils，简述）

- `utils/network.py`：`Api` 链式请求（自动 csrf/wbi/buvid/bili_ticket）、`Credential`（见 login_v2 节）、`request_settings`（代理/超时/SSL/事件开关）、WBI 签名、buvid 指纹生成。
- `utils/parse_link.py`：`parse_link(url)` —— **任意 B站链接解析为对应资源对象**（视频/番剧/课程/音频/歌单/专栏/用户/直播/合集/收藏夹/动态/图文/小黑屋/游戏/话题/漫画/节日/笔记），是通用入口能力。
- `utils/picture.py`：`Picture`（本地/URL/bytes 图片，格式转换与上传）。
- `utils/danmaku.py`：`Danmaku`/`SpecialDanmaku` 弹幕对象。

## bili CLI 0.6.2 未暴露的能力

对照 bili CLI 0.6.2 全部命令：`login/logout/status/whoami/video/user/user-videos/search/hot/rank/feed/my-dynamics/dynamic-post/dynamic-delete/favorites/following/history/watch-later/like/coin/triple/unfollow/audio`。

这些命令在库中均有对应实现（login→`login_v2.QrCodeLogin`；whoami/status→`user.get_self_info`/`Credential`；video→`Video`；user/user-videos→`User.get_user_info`/`get_videos`；search→`search.search_by_type`；hot→`hot`；rank→`rank`；feed→`homepage.get_videos`；my-dynamics→`user.get_dynamics_new`；dynamic-post→`dynamic.send_dynamic`；dynamic-delete→`Dynamic.delete`；favorites→`favorite_list`；following/unfollow→`User.get_followings`/`modify_relation`；history→`user.get_self_history_new`；watch-later→`user.get_toview_list`；like/coin/triple→`Video.like`/`pay_coin`/`triple`；audio→`audio`）。

以下是**库里有、CLI 没有对应命令**的能力（均经源码确认存在）：

### 高价值（建议优先评估）

1. **评论全链路** —— `comment.send_comment`（发评论/回复/楼中楼/带图）、`Comment.like/hate/pin/delete/report`、`get_comments_lazy`。CLI 无任何评论命令。
2. **私信与消息通知** —— `session.send_msg`（发私信）、`Session` 消息轮询监听（可做自动回复机器人）、`get_replies/get_likes/get_at`（谁回复/赞/@了我）。CLI 无。
3. **视频投稿与稿件编辑** —— `video_uploader.VideoUploader`（分 P 上传、断点续传、定时发布、商单标记）、`VideoEditor`（改稿件）、`Video.submit_subtitle`（上传字幕）。CLI 无。注意：专栏/笔记的**上传**在库里也是 TODO 未实现，只有视频/音频/字幕可传。
4. **直播操作** —— `LiveRoom.start/stop`（开播下播）、`ban_user/unban_user`（禁言）、`send_gift_gold/silver/from_bag`（送礼）、`send_danmaku`（直播弹幕）、`LiveDanmaku`（60+ 事件实时监听，含 SC/天选/礼物）、`create_live_reserve`（直播预约）、`watchroom`（放映室）。CLI 无。
5. **创作中心数据** —— `creative_center` 全模块：播放/粉丝/文章图表、评论管理（全账号评论搜索+批量删除）、弹幕管理（高级搜索+删除/保护）、稿件编辑记录。CLI 无。

### 中等价值

6. **弹幕（视频侧）** —— `Video.send_danmaku/like_danmaku/recall_danmaku/operate_danmaku`、历史弹幕按日期拉取、`ass` 模块弹幕/字幕转 ass-srt-lrc 文件。CLI 无。
7. **收藏夹管理写操作** —— 新建/修改/删除收藏夹、内容复制/移动/批量删除/清除失效（CLI 的 favorites 仅为查询类）。
8. **互动视频** —— 剧情树读取/遍历（`InteractiveVideo.get_graph`）、UP 主编辑剧情树、整部打包下载（`InteractiveVideoDownloader`）。CLI 无。
9. **番剧/课程/漫画深度** —— `bangumi.set_follow`/`update_follow_status`（追番管理）、`Episode` 全套（下载直链/弹幕/字幕/AI 总结）、`cheese`（课程下载直链，课程投币收藏）、`manga.set_follow_manga`（追漫）。CLI 无。
10. **图文/投票/话题创作** —— `BuildDynamic` 支持图片+@+表情+投票+话题+定时发布+直播预约卡片的富动态；`vote.create_vote`（新建投票）；`topic.like/set_favorite`。CLI 的 dynamic-post 能力范围未知，但库的构建能力显著更全。
11. **账号与社交管理** —— `edit_self_info`（改昵称签名）、`set_space_notice`（空间公告）、关注分组增删改、拉黑/移除粉丝（CLI 仅 unfollow）、`check_nickname`。
12. **历史/稍后再看写操作** —— `Video.add_to_toview/delete_from_toview`、`clear_toview_list`、`report_watch_history`（上报进度）、`report_start_watching`。
13. **多方式登录与 cookie 保活** —— 密码登录、短信登录、TV 端二维码、`Credential.refresh`（cookie 刷新）。CLI login 仅扫码。
14. **风纪委员仲裁** —— `get_next_jury_case` + `JuryCase.vote`（自动众裁）。CLI 无。
15. **充电问答/代表作等空间扩展** —— `get_upower_qa_list/detail`、`get_masterpiece`、`get_reservation`。

### 低价值/场景有限

16. 会员购购票（`show.OrderTicket.create_order`，含购票人信息读取）
17. 装扮/收藏集（`garb`）、游戏中心（`game`）、音乐榜订阅、活动页、开屏图、IP 归属地、节日页
18. 用户图文（`opus`）与专栏（`article`）的**读取**及转 Markdown（CLI 无，但对本 skill 的总结场景有直接用处）

### 已知失效/未实现（评估时注意）

- `manga`：漫画详情/分话图片/索引（2025-01 起失效，仅剩追漫列表和推荐）
- `video.get_stat`（接口 403/404，已注释）
- `live.get_gift_special`（已失效，改用 `get_gift_config`）
- 专栏上传/编辑/删除、笔记上传/编辑/删除：源码 TODO 未实现
- `user.RelationType.SUBSCRIBE_SECRETLY`（悄悄关注）已失效
