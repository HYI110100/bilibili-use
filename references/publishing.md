# 互动——点赞、投币、三连、关注/取关、发/删动态

代用户执行写操作。全部作用于真实B站账号。

## 能力

| 操作 | 命令 |
|---|---|
| 点赞 / 取消点赞 | `bili like <bv_id> [--undo]` |
| 投币 1-2 枚 | `bili coin <bv_id> [--num 2]` |
| 一键三连（赞+币+收藏） | `bili triple <bv_id>` |
| 取关 | `bili unfollow <mid> --yes` |
| 发文字动态 | `bili dynamic-post "文字"` |
| 从文件发长文动态 | `bili dynamic-post --from-file draft.txt` |
| 删动态 | `bili dynamic-delete <动态ID> --yes` |
| 我的动态列表 | `bili my-dynamics` |
| **关注** | 无 CLI 命令 → `library.md` 用户关系节 |
| **上传视频** | 不支持 → 指引用B站创作中心 member.bilibili.com（或 `library.md` 投稿节） |

## 安全铁律

1. **执行前复述确认**：把「动作 + 对象 + 内容」完整复述给用户，同意才执行
   - 发动态：展示完整文字
   - 点赞/投币：展示视频标题 + BV号
   - 删动态：展示内容摘要 + ID
2. 用户口述大意时：拟文案 → 用户过目 → 发布。不替用户编造内容
3. 不自动追加：用户说点赞就不投币；明说"三连"才用 triple
4. **必须加 `--yes`**：`unfollow` / `dynamic-delete` 默认交互确认，不加会挂起等待输入

## 命令

```bash
bili like BV1ABcsztEcY --yaml                    # 点赞
bili like BV1ABcsztEcY --undo --yaml             # 取消点赞
bili coin BV1ABcsztEcY --num 2 --yaml            # 投 2 枚（默认 1）
bili triple BV1ABcsztEcY --yaml                  # 三连
bili unfollow 946974 --yes --yaml                # 取关
bili dynamic-post "要发布的文字" --yaml            # 发动态（返回动态ID供删除）
bili my-dynamics --yaml                          # 列出我的动态找 ID
bili dynamic-delete <动态ID> --yes --yaml         # 删动态
```

## 前置与排错

```bash
bili status --yaml    # 写操作前检查；未登录 → bili login 扫码
```

| 错误 | 处理 |
|---|---|
| `not_authenticated` | `bili login` |
| `permission_denied` / 凭证不支持写操作 | 重新扫码登录（获取 bili_jct） |
| `rate_limited` / HTTP 412 | 稍等重试 |
| `invalid_input`（BV号格式错） | 用 `resolve_video_id.py` 重新解析 |
