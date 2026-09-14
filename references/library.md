# bilibili-api-python 库——发评论、私信、直播、投稿等

B站全功能 Python 库。以下功能只能通过本库完成（`bili` CLI 无对应命令）：**发评论/回复、关注、私信、消息通知、直播操作、视频投稿、创作中心数据**。

全部 41 个模块的能力索引见 `vendor/bilibili-api-python-capabilities.md`——做上面没列的事之前先查它。

## 环境准备（每次使用前完成）

**解释器**：库要求 Python >= 3.10。
- `bili` CLI 已装则其 uv 环境自带本库：定位方式同 `resolve_video_id.py` 的 `_find_bili_cli_python()`（`shutil.which("bili")` → 同目录找 python）
- 或本机 Python >= 3.10：`pip install bilibili-api-python`
- PyPI 不可用时：`pip install ./vendor/bilibili_api_python-17.4.2-py3-none-any.whl`

**凭证**：读 `bili login` 存下的登录态（先 `bili login` 扫码登录一次）：

```python
import json
from pathlib import Path
from bilibili_api import Credential

cfg = json.loads((Path.home() / ".bilibili-cli" / "credential.json").read_text())
cred = Credential(
    sessdata=cfg["sessdata"],
    bili_jct=cfg["bili_jct"],   # 写操作必须；为空 = 凭证只读，需重新 bili login
    buvid3=cfg["buvid3"],
    buvid4=cfg["buvid4"],
    dedeuserid=cfg["dedeuserid"],
    ac_time_value=cfg["ac_time_value"],
)
```

**调用形式**：所有 API 是 async，用 `sync()` 同步执行：

```python
from bilibili_api import sync
result = sync(some_api(..., credential=cred))
```

**写操作确认**：以下所有写操作作用于用户真实账号——执行前向用户复述「动作 + 对象 + 内容」，确认后才执行（同 publishing.md 安全铁律）。

## 发评论 / 回复

```python
from bilibili_api import comment, sync, bvid2aid
from bilibili_api.comment import CommentResourceType

oid = bvid2aid("BV1xxxxxxxx")   # ⚠️ oid 是 av 号，不是 BV 号
sync(comment.send_comment(
    "好活当赏",
    oid=oid,
    type_=CommentResourceType.VIDEO,
    credential=cred,
))
# 回复评论：root=<评论ID>
# 楼中楼：  root=<所在评论ID>, parent=<被回复评论ID>
# 资源类型：VIDEO / ARTICLE / DYNAMIC / DYNAMIC_DRAW / AUDIO / AUDIO_LIST / CHEESE / MANGA 等
```

## 关注 / 拉黑 / 移除粉丝

```python
from bilibili_api import user, sync

sync(user.User(uid=946974, credential=cred).modify_relation(user.RelationType.SUBSCRIBE))
# SUBSCRIBE / UNSUBSCRIBE / BLOCK / UNBLOCK / REMOVE_FANS
# （SUBSCRIBE_SECRETLY 悄悄关注已失效）
```

## 私信

```python
from bilibili_api import session, sync
from bilibili_api.session import EventType

sync(session.send_msg(
    credential=cred,
    receiver_id=946974,
    msg_type=EventType.TEXT,
    content="你好",
))
```

## 消息通知（谁回复/赞/@ 了我）

```python
from bilibili_api import session, sync

sync(session.get_replies(credential=cred))   # 收到的回复
sync(session.get_likes(credential=cred))     # 收到的赞
sync(session.get_at(credential=cred))        # 收到的 @
sync(session.fetch_session_msgs(credential=cred, talker_id=946974))  # 与某人的最近消息
```

## 直播

```python
from bilibili_api import live, sync

room = live.LiveRoom(room_display_id=21452505, credential=cred)
sync(room.start(area_id=21))     # 开播（分区ID用 live_area 模块查）
sync(room.stop())                # 下播
sync(room.ban_user(uid=946974))  # 禁言
```

监听实时弹幕/礼物/SC（60+ 事件，长驻任务）：

```python
from bilibili_api import live

dm = live.LiveDanmaku(room_display_id=21452505, credential=cred)

@dm.on("DANMU_MSG")
async def on_danmu(event):
    print(event)

sync(dm.connect())   # 断开：dm.disconnect()；事件清单见 capabilities 文档 live 节
```

## 视频投稿

```python
from bilibili_api import Picture, sync
from bilibili_api.video_uploader import VideoUploader, VideoUploaderPage, VideoMeta

meta = VideoMeta(
    tid=17,                          # 分区ID，用 video_zone 模块查
    title="标题",
    desc="简介",
    cover=Picture.from_file("cover.jpg"),
    tags="标签1,标签2",
    delay_time=3600,                 # 可选：定时发布（秒）；立即发布删掉此行
)
pages = [VideoUploaderPage(path="video.mp4", title="第一P")]
uploader = VideoUploader(pages, meta, credential=cred)
sync(uploader.start())
# 改已发布稿件：VideoEditor(bvid, meta_dict, credential=cred).start()
```

## 创作中心数据（数据看板、评论/稿件管理）

```python
from bilibili_api import creative_center, sync

sync(creative_center.get_overview(credential=cred))                    # 数据概览
sync(creative_center.get_fan_graph(credential=cred))                    # 粉丝增长
sync(creative_center.get_video_upload_manager_info(credential=cred))    # 稿件列表
sync(creative_center.get_comments(credential=cred, keyword="关键词"))    # 全账号评论搜索
sync(creative_center.del_comments(credential=cred, oid=[<视频ID>], rpid=[<评论ID>]))  # 批量删评论
```

## 更多能力

以上只是高频入口。完整索引（41 模块 × 每个类的方法清单）：`vendor/bilibili-api-python-capabilities.md`，按域速查：

| 想做什么 | 看该节 |
|---|---|
| 番剧/课程/漫画/音频/歌单 | bangumi / cheese / manga / audio |
| 收藏夹管理、观看历史写入 | favorite_list / user |
| 弹幕发送、ass 字幕转换 | video / ass |
| 互动视频（剧情树、打包下载） | interactive_video |
| 专栏文章读取、图文动态 | article / opus |
| 投票、话题、表情 | vote / topic / emoji |
| 小黑屋、风纪委员 | black_room |

## 排错

- `not_authenticated` 类错误 → 凭证失效，重跑 `bili login`
- 报错但代码正确 → 先怀疑B站接口变更（库已停更，见 AGENTS.md 生态风险）
- 已知失效：manga 正文图片、专栏/笔记上传、`video.get_stat`、悄悄关注——完整清单见 capabilities 文档末节
