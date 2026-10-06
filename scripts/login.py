#!/usr/bin/env python3
"""扫码登录 B站（修复版，替代 bili login）。

为什么需要这个脚本（2026-08 起）：
- B站改版了 WEB 扫码登录：成功后 data.url 不再是带 cookie 参数的链接，
  而是 crossDomain ticket 链接，真正的 SESSDATA/bili_jct/DedeUserID 通过
  跟随该链接的 Set-Cookie 响应头下发。
- bili CLI 0.6.2 依赖的 bilibili-api-python 17.4.2（绝版，无法修复）只会
  从 URL query 解析 cookie → `bili login` 显示"登录成功"但存下空凭证，
  后续命令全部 not_authenticated。
- 终端字符二维码在 GUI/agent 场景经常变形无法扫描。本脚本输出 PNG 图片，
  agent 直接把图片展示给用户。

用法：
    python3 scripts/login.py            # 生成二维码 PNG，轮询，成功后写凭证
    python3 scripts/login.py --check    # 只检查当前登录状态

二维码约 2 分钟有效；过期会打印 QR_TIMEOUT，重跑即可。
凭证写入 ~/.bilibili-cli/credential.json（与 bili CLI 完全兼容）。

依赖：bilibili-api-python（bili CLI 环境自带；也可 pip install 或装 vendor/ 里的 wheel）。
"""

import argparse
import asyncio
import json
import sys
import time
import urllib.parse
import urllib.request
import http.cookiejar
from pathlib import Path

CRED = Path.home() / ".bilibili-cli" / "credential.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def find_python_env():
    """Locate a Python that has bilibili_api: current interpreter → bili CLI tool env."""
    try:
        import bilibili_api  # noqa: F401
        return
    except ImportError:
        pass
    import subprocess
    bili = Path.home() / ".local" / "bin" / "bili"
    if bili.exists():
        try:
            real = subprocess.run(["readlink", "-f", str(bili)], capture_output=True, text=True).stdout.strip()
            # bili shim → .../bilibili-cli/bin/bili ; site-packages is two levels up
            tool_bin = Path(real).parent
            site = next(tool_bin.parent.glob("lib/python*/site-packages"), None)
            if site:
                sys.path.insert(0, str(site))
                return
        except Exception:
            pass
    print("ERROR: 需要 bilibili-api-python。安装：pip install bilibili-api-python "
          "或 pip install <skill>/vendor/bilibili_api_python-17.4.2-py3-none-any.whl",
          file=sys.stderr)
    sys.exit(2)


def check_status():
    if not CRED.exists():
        print("NOT_LOGGED_IN")
        return 1
    try:
        d = json.loads(CRED.read_text())
        if d.get("sessdata"):
            age_days = (time.time() - d.get("saved_at", 0)) / 86000
            print(f"LOGGED_IN user={d.get('dedeuserid','?')} saved {age_days:.1f} 天前")
            return 0
        print("NOT_LOGGED_IN (凭证文件存在但 sessdata 为空——旧版 bili login 假成功留下的)")
        return 1
    except Exception as e:
        print(f"NOT_LOGGED_IN ({e})")
        return 1


def exchange_ticket(url: str) -> dict:
    """跟随 crossDomain ticket 链接（浏览器 UA），从 Set-Cookie 收集 cookie。"""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [("User-Agent", UA), ("Referer", "https://www.bilibili.com/")]
    opener.open(url, timeout=15)
    return {c.name: c.value for c in jar if c.value}


async def qr_login(png_path: Path):
    import qrcode
    from bilibili_api import Api
    from bilibili_api.login_v2 import QrCodeLogin, API
    from bilibili_api.utils.network import Credential

    login = QrCodeLogin()
    await login.generate_qrcode()
    link = login._QrCodeLogin__qr_link
    key = login._QrCodeLogin__qr_key
    qrcode.make(link).save(png_path)
    print(f"QR_IMAGE: {png_path}", flush=True)
    print("请用 B站 App 扫描该图片二维码，并在手机上确认（二维码约 2 分钟有效）", flush=True)

    events = None
    while True:
        api = API["qrcode"]["web"]["get_events"]
        events = await Api(credential=Credential(), **api).update_params(qrcode_key=key).result
        code = events.get("code")
        if code in (86101, 86090):   # 未扫码 / 已扫码待确认
            await asyncio.sleep(2)
        elif code == 86038:
            print("QR_TIMEOUT", flush=True)
            return 1
        else:
            break

    # 成功：兼容两种格式
    url = events["url"]
    refresh_token = events.get("refresh_token", "")
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    cookies = {}
    # 旧格式：cookie 直接在 query 里
    for name, key_q in (("SESSDATA", "SESSDATA"), ("bili_jct", "bili_jct"),
                        ("DedeUserID", "DedeUserID")):
        if key_q in q:
            cookies[name] = q[key_q][0]
    # 新格式（2026-08 起）：crossDomain ticket → 跟随链接收 Set-Cookie
    if not cookies.get("SESSDATA") and "ticket" in q:
        cookies.update(exchange_ticket(url))

    sessdata = cookies.get("SESSDATA", "")
    if not sessdata:
        print("FAILED: 登录确认成功但没拿到 SESSDATA，url=", url[:160], flush=True)
        return 1

    data = {
        "sessdata": sessdata if "%" in sessdata else urllib.parse.quote(sessdata),
        "bili_jct": cookies.get("bili_jct", ""),
        "ac_time_value": refresh_token,
        "buvid3": cookies.get("buvid3", ""),
        "buvid4": cookies.get("buvid4", ""),
        "dedeuserid": cookies.get("DedeUserID", ""),
        "saved_at": time.time(),
    }
    CRED.parent.mkdir(parents=True, exist_ok=True)
    CRED.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    CRED.chmod(0o600)
    print("LOGIN_OK", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(description="B站扫码登录（修复版，输出二维码 PNG）")
    ap.add_argument("--check", action="store_true", help="只检查登录状态")
    ap.add_argument("--png", default=str(Path.home() / ".cache" / "bilibili-use" / "login_qr.png"),
                    help="二维码 PNG 输出路径")
    args = ap.parse_args()

    if args.check:
        sys.exit(check_status())

    find_python_env()
    png = Path(args.png).expanduser()
    png.parent.mkdir(parents=True, exist_ok=True)
    sys.exit(asyncio.run(qr_login(png)))


if __name__ == "__main__":
    main()
