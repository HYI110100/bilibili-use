# 发布内容 / 互动

代用户执行写操作：发动态、删动态、点赞、投币、三连、取消关注。

> **所有写操作都作用于用户的真实B站账号。执行前必须确认（见安全规则）。**
> 需要可写凭证（`bili_jct`）——`bili login` 扫码登录后自动具备。
> 命令集已在 bilibili-cli 0.6.2 源码中逐一核验（含底层库 API，见文末注记）。

## 能力边界

| 操作 | 支持 | 方式 |
|---|---|---|
| 发文字动态 | ✅ | `bili dynamic-post`（支持 `--from-file`） |
| 删动态 | ✅ | `bili dynamic-delete` |
| 点赞 / 取消点赞 | ✅ | `bili like [--undo]` |
| 投币 | ✅ | `bili coin [--num 1\|2]`（默认 1 枚） |
| 一键三连 | ✅ | `bili triple`（赞 + 币 + 收藏） |
| 取消关注 | ✅ | `bili unfollow --yes` |
| **关注** | ❌ | CLI 未暴露命令（底层库支持 SUBSCRIBE 关系，但无 `follow` 命令）。用B站APP/网页 |
| **上传视频** | ❌ | 不支持。指引用B站创作中心：member.bilibili.com（网页/APP） |
| 图文/转发动态 | ❌ | 仅纯文字 |

## 安全规则（写操作铁律）

1. **执行前复述确认**：把「动作 + 对象 + 内容」完整复述给用户，得到明确同意才执行。
   - 发动态：展示要发布的完整文字
   - 点赞/投币：展示视频标题 + BV号
   - 删动态：展示动态内容摘要 + ID
2. **检查凭证**：先 `bili status --yaml`。未登录 → 指引 `bili login`；报 `当前登录凭证不支持写操作` → 需重新扫码登录获取 `bili_jct`。
3. **不自动追加操作**：用户只说点赞就不投币。三连（`triple`）是点赞+投币+收藏的合体，用户明说"三连"才用。
4. **发布内容**：用户口述大意时，拟好文案给用户过目，确认后发布。不要替用户编造没说过的内容。
5. **跳过交互确认**：`unfollow` / `dynamic-delete` 默认有交互确认（click.confirm），agent 执行**必须加 `--yes`**，否则命令会挂起等待输入。确认职责由 agent 与用户完成，不依赖 CLI 交互提示。

## 发动态

```bash
bili dynamic-post "要发布的文字" --yaml
bili dynamic-post --from-file draft.txt --yaml   # 长文从文件读
# → 返回动态 ID，记下来供删除用
```

## 删动态

```bash
bili my-dynamics --yaml                      # 先列出我发的动态，找到 ID
bili dynamic-delete <动态ID> --yes --yaml    # --yes 跳过交互确认
```

## 互动

```bash
bili like <bv_id> --yaml                # 点赞
bili like <bv_id> --undo --yaml         # 取消点赞
bili coin <bv_id> --num 2 --yaml        # 投 2 枚（--num 1 或 2，默认 1）
bili triple <bv_id> --yaml              # 一键三连
bili unfollow <mid> --yes --yaml        # 取关（必须 --yes）
```

## 结果处理

| 情况 | 行为 |
|---|---|
| 写操作成功 | 向用户报告结果（含B站返回的动态ID/状态） |
| `not_authenticated` | 指引 `bili login` |
| `permission_denied`（凭证只读） | 指引重新扫码登录 |
| `rate_limited` / HTTP 412 | 稍等重试 |
| `invalid_input`（BV号格式错） | 检查ID，回到 resolve_video_id.py 解析 |

## 常见组合

- **看完视频想支持UP主**："给这个视频点个赞" → 确认 → `bili like`。
- **发总结到动态**：用户看完视频（summarizing.md 流程）后想把要点发动态 → 拟文案 → 用户过目 → `dynamic-post`。
- **清理自己的动态**：`my-dynamics` 列表 → 用户选 → 确认 → 逐条 `dynamic-delete --yes`。

## 底层依赖注记（2026-09 源码核验）

写操作链路：bili CLI 0.6.2 → `bilibili-api-python` 17.4.x，对应库 API 均已确认存在：
`Video.like/pay_coin/triple`、`User.modify_relation(RelationType.UNSUBSCRIBE)`、
`dynamic.BuildDynamic/send_dynamic`、`Dynamic.delete`。

⚠️ 生态风险：bilibili-api-python 的 GitHub 仓库已于 2026-07 被B站侵权告知函关停，
PyPI 末版 17.4.2（2026-06-19）仍可安装但不再维护。若B站接口变更，写操作可能失效，
届时本文档命令需重新验证。
