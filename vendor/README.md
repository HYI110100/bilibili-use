# vendor/ — 内置依赖包（离线兜底）

本目录收录两个已停止维护的 PyPI 包的最终版 wheel，防止 PyPI 下架后无法安装。

## 收录清单

| 文件 | 版本 | PyPI 上传 | License | Python |
|---|---|---|---|---|
| `bilibili_api_python-17.4.2-py3-none-any.whl` | 17.4.2（绝版） | 2026-06-19 | GPL-3.0-or-later | >=3.10 |
| `bilibili_cli-0.6.2-py3-none-any.whl` | 0.6.2 | 2026-03-11 | Apache-2.0 | >=3.10 |

### sha256 校验值

```
91e002b2e0bcd3eb50239e35ceb849133b574f407a92a06636e1de1031b6d09d  bilibili_api_python-17.4.2-py3-none-any.whl
185b5df16262415c830a74216ca9c4a74df0e63cf542537444fb295a236a9f5d  bilibili_cli-0.6.2-py3-none-any.whl
```

> 两个 wheel 均从 PyPI 原样收录、未做任何修改（可用上面的 sha256 验证）。

### 为什么要收录

- `bilibili-api-python`：GitHub 仓库 2026-07 被 B站侵权告知函关停（仓库只剩声明），PyPI 17.4.2 为绝版。bili CLI 的全部写操作（点赞/投币/发动态/取关等）和字幕、多P数据都依赖此库。
- `bilibili-cli`：同样停更（末次提交 2026-03-14），且强依赖上面的绝版库——一旦 PyPI 下架该库，`uv tool install bilibili-cli` 会因依赖解析失败而装不上。

## 离线安装（PyPI 不可用时的兜底）

```bash
# bili CLI（--find-links 让依赖解析优先使用本目录的 wheel）
uv tool install ./vendor/bilibili_cli-0.6.2-py3-none-any.whl --find-links ./vendor/

# 或 pipx
pipx install ./vendor/bilibili_cli-0.6.2-py3-none-any.whl --pip-args "--find-links ./vendor"

# 只要 bilibili-api-python（脚本的多P真实标题等功能用）
pip install ./vendor/bilibili_api_python-17.4.2-py3-none-any.whl
```

其余依赖（aiohttp、click、rich、pyyaml 等）均为活跃维护包，仍从 PyPI 正常拉取，不在收录范围。

## 能力清单

[`bilibili-api-python-capabilities.md`](bilibili-api-python-capabilities.md) 是从 17.4.2 wheel 源码逐一枚举的完整能力清单，含「bili CLI 未暴露的能力」对照——评估本技能后续能做什么时先看它。

## 版权说明

本目录下的 wheel 是第三方产物，版权与许可归属各自原作者（GPL-3.0-or-later / Apache-2.0），不属于本项目 MIT 许可的覆盖范围。
