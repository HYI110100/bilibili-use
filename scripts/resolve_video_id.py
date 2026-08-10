#!/usr/bin/env python3
"""Resolve any B站 link/ID to canonical ID + cache path.

Usage:
  resolve_video_id.py <input>            # BV ID, URL, or short link
  resolve_video_id.py BV1xxx --json      # JSON output

Supported formats:
  - BV ID:      BV1ABcsztEcY
  - AV ID:      av21877586
  - Episode:    ep198381
  - Full URL:   https://www.bilibili.com/video/BV1ABcsztEcY?p=2
  - Short link: https://b23.tv/xxxxx

Output (default text):
  BV_ID [pN] [TIMESTAMP]

Output (--json):
  {"bv_id": "BV1xxx", "page": 1, "timestamp": 0,
   "cache_dir": "~/.cache/bilibili-use/BV1xxx/",
   "multi_p": false, "collection": null}
"""

import subprocess
import sys
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Import shared cache config
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR


def follow_redirect(url: str, timeout: int = 10) -> str:
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.geturl()
    except Exception as e:
        print(f"[ERROR] Failed to resolve short link: {e}", file=sys.stderr)
        sys.exit(1)


def detect_playlist(bv_id: str) -> dict:
    """Check if video is multi-P or collection via yt-dlp."""
    url = f"https://www.bilibili.com/video/{bv_id}"
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--dump-json", url],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return {}
    try:
        data = json.loads(result.stdout.strip().split("\n")[0])
        if data.get("playlist_count", 0) > 1:
            return {
                "playlist_id": data.get("playlist_id", bv_id),
                "playlist_count": data["playlist_count"],
                "playlist_title": data.get("playlist_title", ""),
            }
    except (json.JSONDecodeError, KeyError):
        pass
    return {}


def parse_bv_id(raw: str) -> dict:
    raw = raw.strip()

    if "b23.tv" in raw:
        raw = follow_redirect(raw)

    page = 1
    timestamp = 0
    if "?" in raw:
        qs = parse_qs(urlparse(raw).query)
        page = int(qs.get("p", [1])[0])
        timestamp = int(qs.get("t", [0])[0])

    clean = raw.split("?")[0].split("#")[0]

    bv_id = None
    m = re.search(r"(BV[0-9A-Za-z]{10})", clean)
    if m:
        bv_id = m.group(1)

    if not bv_id:
        m = re.search(r"av(\d+)", clean, re.IGNORECASE)
        if m:
            bv_id = f"av{m.group(1)}"

    if not bv_id:
        m = re.search(r"ep(\d+)", clean, re.IGNORECASE)
        if m:
            bv_id = f"ep{m.group(1)}"

    if not bv_id:
        print(f"[ERROR] Cannot extract Bilibili video ID from: {raw}", file=sys.stderr)
        sys.exit(1)

    return {"bv_id": bv_id, "page": page, "timestamp": timestamp}


def build_cache_path(bv_id: str, page: int, playlist_info: dict) -> Path:
    """Build cache directory path based on video structure.

    Single video:       ~/.cache/bilibili-use/<bv_id>/
    Multi-P video p1:   ~/.cache/bilibili-use/<bv_id>/      (same as single)
    Multi-P video p2+:  ~/.cache/bilibili-use/<bv_id>/p<N>/
    """
    base = CACHE_DIR / bv_id

    if playlist_info and playlist_info.get("playlist_count", 1) > 1 and page > 1:
        base = base / f"p{page}"

    base.mkdir(parents=True, exist_ok=True)
    return base


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw = sys.argv[1]
    as_json = "--json" in sys.argv

    result = parse_bv_id(raw)
    bv_id = result["bv_id"]
    page = result["page"]
    timestamp = result["timestamp"]

    # Detect multi-P / collection
    playlist = detect_playlist(bv_id)

    # Build cache path
    cache_path = build_cache_path(bv_id, page, playlist)

    # Save resolution result
    resolve_cache = cache_path / "resolve.json"
    resolve_data = {
        "bv_id": bv_id,
        "page": page,
        "timestamp": timestamp,
        "original": raw,
        "multi_p": playlist.get("playlist_count", 0) > 1,
        "playlist": playlist if playlist else None,
        "cache_dir": str(cache_path),
    }
    resolve_cache.write_text(json.dumps(resolve_data, ensure_ascii=False, indent=2))

    if as_json:
        print(json.dumps(resolve_data, ensure_ascii=False, indent=2))
    else:
        parts = [bv_id]
        multi = playlist.get("playlist_count", 1)
        if multi > 1:
            parts.append(f"[{multi}P]")
        if page > 1:
            parts.append(f"p{page}")
        if timestamp > 0:
            parts.append(f"t{timestamp}s")
        print(" ".join(parts))
    print(f"[CACHED: {resolve_cache}]")


if __name__ == "__main__":
    main()
