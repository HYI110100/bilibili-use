# 直接使用 bilibili-api-python 库

CLI（bilibili-cli）只包装了库的一小部分能力（约 24 个函数 vs 库 41 个模块）。
**CLI 没有命令的功能**——发评论、关注、私信、直播、投稿上传、创作中心数据——直接调库完成。

> 完整能力菜单：`vendor/bilibili-api-python-capabilities.md`（41 模块，从 17.4.2 源码逐一枚举）。
> 库已停更（生态风险见 AGENTS.md），绝版 wheel 兜底在 `vendor/`。

## 何时用库，何时用 CLI

| 场景 | 用 |
|---|---|
| CLI 已有的命令（视频信息/字幕/评论**读取**/热门/收藏/点赞/发动态...） | CLI（输出规范、省事） |
| 发评论 / 回复 / 楼中楼 | 库 |
| **关注**（CLI 只有 unfollow） | 库 |
| 私信、回复/赞/@ 通知 | 库 |
| 直播：开播/禁言/送礼/弹幕监听 | 库 |
| 视频投稿 / 改稿 / 传字幕 | 库 |
| 创作中心数据（播放/粉丝图表、评论批量管理） | 库 |
| 互动视频下载、番剧/课程/漫画 | 库 |

## 运行环境

库要求 **Python >= 3.10**。本技能脚本本身兼容 3.8+，互不影响——库调用单独跑，可用：

1. **bili CLI 的解释器（推荐，零配置）**：`bili` 已装则其 uv 环境自带本库。定位方式同 `resolve_video_id.py` 的 `_find_bili_cli_python()`（`shutil.which("bili")` → 同目录找 python）
2. 本机 Python >= 3.10：`pip install bilibili-api-python`
3. PyPI 下架时离线装：`pip install ./vendor/bilibili_api_python-17.4.2-py3-none-any.whl`

## 凭证（关键：复用 CLI 的登录态，不二次扫码）

库的每个 API 都接受 `Credential` 对象（本质是 Cookie 容器）。`bili login` 之后，
CLI 把凭证存在 `~/.bilibili-cli/credential.json`，字段与库的构造参数**一一对齐**，直接读：

```python
import json
from pathlib import Path
from bilibili_api import Credential

cfg = json.loads((Path.home() / ".bilibili-cli" / "credential.json").read_text())
cred = Credential(
    sessdata=cfg["sessdata"],
    bili_jct=cfg["bili_jct"],        # 写操作必须；为空 = 凭证只读
    buvid3=cfg["buvid3"],
    buvid4=cfg["buvid4"],
    dedeuserid=cfg["dedeuserid"],
    ac_time_value=cfg["ac_time_value"],
)
```

> 前提：先 `bili login` 扫码登录过一次。
> 凭证失效的表现：`not_authenticated` 类错误 → 重跑 `bili login`。
> 完全没有 CLI 时，库自带扫码原语：`login_v2.QrCodeLogin`（`generate_qrcode()` →
> 轮询 `check_state()` → `get_credential()`），但凭证持久化要自己写。

## 同步调用（免 async 样板）

```python
from bilibili_api import sync
result = sync(some_async_api(...))
```

## 已验证示例

### 关注 UP（CLI 未暴露此能力）

```python
from bilibili_api import user, sync

sync(user.User(uid=946974).modify_relation(user.RelationType.SUBSCRIBE))
# RelationType: SUBSCRIBE / UNSUBSCRIBE / BLOCK / UNBLOCK / REMOVE_FANS
# （SUBSCRIBE_SECRETLY 悄悄关注在 17.4.2 已标注失效）
```

### 发评论 / 回复

```python
from bilibili_api import comment, sync, bvid2aid
from bilibili_api.comment import CommentResourceType

oid = bvid2aid("BV1xxxxxxxx")   # ⚠️ 视频评论的 oid 是 av 号，不是 BV 号
sync(comment.send_comment(
    "好活当赏",
    oid=oid,
    type_=CommentResourceType.VIDEO,
    credential=cred,
))
# 回复评论：root=<评论ID>
# 楼中楼：root=<所在评论ID>, parent=<被回复评论ID>
# 资源类型：VIDEO / ARTICLE / DYNAMIC / DYNAMIC_DRAW / AUDIO / AUDIO_LIST / CHEESE / MANGA 等
```

## 安全铁律（同 publishing.md）

所有写操作（发评论/关注/私信/送礼/开播/删稿...）作用于用户真实账号：
**先向用户复述「动作 + 对象 + 内容」，确认后才执行。**

## 风险与已知失效

- 库 17.4.2 为绝版（2026-07 关停），B站接口变更后对应能力可能**静默失效**——调用报错时先怀疑接口变动
- 已知失效：manga 正文图片（2025-01 起）、专栏/笔记上传（源码 TODO 未实现）、`video.get_stat`
- 详细失效清单见 `vendor/bilibili-api-python-capabilities.md` 末节
