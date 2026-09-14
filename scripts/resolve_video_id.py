#!/usr/bin/env python3
"""Resolve any B站 link/ID to canonical ID, cache path, and video type.

Usage:
  resolve_video_id.py <input>            # BV ID, URL, or short link
  resolve_video_id.py <input> --yaml     # YAML output (default)

Detects:
  - single:     普通单视频
  - multi_p:    多P视频（同一 BV 下有多个分P）
  - collection:  合集（space.bilibili.com/<mid>/lists/<sid> 或 channel/collectiondetail）

Cache structure:
  single:        ~/.cache/bilibili-use/<bv_id>/
  multi_p:       ~/.cache/bilibili-use/<bv_id>/p<N>/
  collection:    ~/.cache/bilibili-use/<sid>/<bv_id>/

Output (YAML):
  type: single|multi_p|collection
  bv_id: BV1xxx
  page: 1
  cache_dir: /home/hyi/.cache/bilibili-use/...
  index_path: .../index.yaml          (multi_p / collection)
  total_pages: N                      (multi_p only)
  collection_id: <sid>                (collection only)
  title: <合集标题>                    (collection only)
  total_videos: N                     (collection only)
"""

from __future__ import annotations

import subprocess
import sys
import json
import yaml
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR, resolve_id


def follow_redirect(url: str, timeout: int = 10) -> str:
    """Follow b23.tv redirect. On failure, return original URL (degrade gracefully)."""
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.geturl()
    except Exception:
        return url


def get_total_duration(bv_id: str) -> int:
    """Get total video duration in seconds via bili CLI."""
    result = subprocess.run(
        ["bili", "video", bv_id, "--yaml"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        return 0
    try:
        data = yaml.safe_load(result.stdout)
        return data.get("data", {}).get("video", {}).get("duration_seconds", 0)
    except Exception:
        return 0


def _find_bili_cli_python() -> str | None:
    """Locate python interpreter inside bili CLI's uv environment (if any)."""
    import shutil
    bili_path = shutil.which("bili")
    if not bili_path:
        return None
    # Resolve symlinks (uv shim → real env dir), then look for python next to it
    real = Path(bili_path).resolve()
    bin_dir = real.parent
    for candidate in ("python", "python3"):
        p = bin_dir / candidate
        if p.exists():
            return str(p)
    return None


def _pages_via_import(bv_id: str) -> list | None:
    """Get real pages via bilibili_api imported in the current interpreter."""
    try:
        import asyncio
        from bilibili_api import video

        async def _fetch():
            v = video.Video(bvid=bv_id)
            return await v.get_pages()

        return asyncio.run(_fetch())
    except Exception:
        return None


def _pages_via_bili_cli(bv_id: str) -> list | None:
    """Get real pages by running bilibili_api inside bili CLI's interpreter."""
    bili_py = _find_bili_cli_python()
    if not bili_py:
        return None
    code = (
        "import asyncio, json, sys\n"
        "from bilibili_api import video\n"
        "async def main():\n"
        "    v = video.Video(bvid=sys.argv[1])\n"
        "    print(json.dumps(await v.get_pages(), ensure_ascii=False))\n"
        "asyncio.run(main())\n"
    )
    result = subprocess.run([bili_py, "-c", code, bv_id],
                            capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def get_pages_rich(bv_id: str) -> list | None:
    """Get real per-P titles/durations via bilibili_api with fallback chain.

    Chain: current interpreter → bili CLI interpreter → None (degrade).
    Returns [{page, part, duration, cid}, ...] or None if unavailable.
    """
    pages = _pages_via_import(bv_id)
    if pages is None:
        pages = _pages_via_bili_cli(bv_id)
    return pages


def detect_playlist(bv_id: str) -> dict:
    """Check if video is multi-P via yt-dlp flat playlist.

    Page count from yt-dlp; real titles/durations via bilibili_api
    (degraded to P1/P2 placeholders + average duration if unavailable).
    """
    url = f"https://www.bilibili.com/video/{bv_id}"
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--dump-json", url],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return {}

    lines = result.stdout.strip().split("\n")
    entries = []
    for line in lines:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    if not entries:
        return {}

    first = entries[0]
    count = first.get("playlist_count", 0) or first.get("n_entries", 0) or len(entries)

    if count <= 1 and len(entries) <= 1:
        return {}

    # Try real titles/durations via bilibili_api (best effort)
    rich_pages = get_pages_rich(bv_id)
    if rich_pages and len(rich_pages) == count:
        items = [{
            "page": p.get("page", i + 1),
            "title": p.get("part", f"P{i + 1}"),
            "duration_s": p.get("duration") or 0,
            "cid": p.get("cid"),
        } for i, p in enumerate(rich_pages)]
        total_duration = sum(p.get("duration") or 0 for p in rich_pages)
    else:
        # Degrade: placeholders + average duration
        total_duration = get_total_duration(bv_id)
        per_page = total_duration // count if count > 0 else 0
        items = [{
            "page": i + 1,
            "title": f"P{i + 1}",
            "duration_s": per_page,
        } for i in range(count)]

    return {
        "multi_p": True,
        "count": count,
        "title": first.get("playlist_title", ""),
        "total_duration_s": total_duration,
        "items": items,
    }


def build_index(bv_id: str, playlist: dict) -> Path:
    """Generate index.yaml for multi-P video. Returns path."""
    index_dir = CACHE_DIR / bv_id
    index_dir.mkdir(parents=True, exist_ok=True)
    index_path = index_dir / "index.yaml"

    index_data = {
        "type": "multi_p",
        "id": bv_id,
        "title": playlist.get("title", ""),
        "total": playlist["count"],
        "items": playlist["items"],
    }
    index_path.write_text(yaml.dump(index_data, allow_unicode=True, default_flow_style=False))
    return index_path


def build_cache_dir(bv_id: str, page: int, playlist: dict) -> Path:
    """Build cache directory based on video type.

    single:   ~/.cache/bilibili-use/<bv_id>/
    multi_p:  ~/.cache/bilibili-use/<bv_id>/p<N>/
    """
    base = CACHE_DIR / bv_id
    if playlist and playlist.get("multi_p"):
        base = base / f"p{page}"
    base.mkdir(parents=True, exist_ok=True)
    return base


def write_resolve(cache_dir: Path, bv_id: str, page: int, vtype: str, original: str):
    """Write resolve.yaml into cache directory."""
    resolve_data = {
        "bv_id": bv_id,
        "page": page,
        "type": vtype,
        "resolved_from": original,
    }
    (cache_dir / "resolve.yaml").write_text(
        yaml.dump(resolve_data, allow_unicode=True, default_flow_style=False))


def parse_input(raw: str) -> dict:
    """Parse raw input into video or collection descriptor.

    Returns video:  {type: 'video', bv_id, page, timestamp}
    Returns collection: {type: 'collection', mid, sid}
    """
    raw = raw.strip()

    if "b23.tv" in raw:
        raw = follow_redirect(raw)

    # Collection URLs:
    #   space.bilibili.com/<mid>/channel/collectiondetail?sid=<sid>
    #   space.bilibili.com/<mid>/lists/<sid>
    col = re.search(r"space\.bilibili\.com/(\d+)/(?:channel/collectiondetail\?sid=|lists/)(\d+)", raw)
    if col:
        return {"type": "collection", "mid": int(col.group(1)), "sid": int(col.group(2))}

    page = 1
    timestamp = 0
    if "?" in raw:
        qs = parse_qs(urlparse(raw).query)
        page = int(qs.get("p", [1])[0])
        timestamp = int(qs.get("t", [0])[0])

    bv_id = resolve_id(raw)
    return {"type": "video", "bv_id": bv_id, "page": page, "timestamp": timestamp}


# ---------- Collection support ----------

def get_collection_rich(sid: int) -> dict | None:
    """Get collection info via bilibili_api with fallback chain.

    Returns {title, total, items: [{bv_id, title, duration_s}]} or None.
    """
    try:
        import asyncio
        from bilibili_api import user

        async def _fetch():
            u = user.User(0)  # mid not needed for season query
            data = await u.get_channel_videos_season(sid=sid, ps=100)
            return data

        data = asyncio.run(_fetch())
    except Exception:
        # Fallback: bili CLI interpreter
        bili_py = _find_bili_cli_python()
        if not bili_py:
            return None
        code = (
            "import asyncio, json, sys\n"
            "from bilibili_api import user\n"
            "async def main():\n"
            "    u = user.User(0)\n"
            "    data = await u.get_channel_videos_season(sid=sys.argv[1], ps=100)\n"
            "    print(json.dumps(data, ensure_ascii=False))\n"
            "asyncio.run(main())\n"
        )
        result = subprocess.run([bili_py, "-c", code, str(sid)],
                                capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return None

    meta = data.get("meta", {})
    archives = data.get("archives", [])
    if not archives:
        return None

    items = [{
        "bv_id": v.get("bvid", ""),
        "title": v.get("title", f"V{i + 1}"),
        "duration_s": v.get("duration") or 0,
    } for i, v in enumerate(archives)]

    return {
        "title": meta.get("name", meta.get("title", "")),
        "total": len(items),
        "items": items,
    }


def get_collection_degraded(sid: int) -> dict | None:
    """Fallback: collection items via yt-dlp flat-playlist (bvid only)."""
    url = f"https://space.bilibili.com/0/channel/collectiondetail?sid={sid}"
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--dump-json", url],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return None
    items = []
    for line in result.stdout.strip().split("\n"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        bv = d.get("id", "")
        if bv:
            items.append({"bv_id": bv, "title": f"V{len(items) + 1}", "duration_s": 0})
    if not items:
        return None
    return {"title": f"合集{sid}", "total": len(items), "items": items}


def build_collection_index(sid: int, col: dict) -> Path:
    """Generate index.yaml for collection. Returns path."""
    index_dir = CACHE_DIR / str(sid)
    index_dir.mkdir(parents=True, exist_ok=True)
    index_path = index_dir / "index.yaml"

    index_data = {
        "type": "collection",
        "id": sid,
        "title": col.get("title", ""),
        "total": col["total"],
        "items": col["items"],
    }
    index_path.write_text(yaml.dump(index_data, allow_unicode=True, default_flow_style=False))
    return index_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw = sys.argv[1]
    parsed = parse_input(raw)

    # ---------- Collection branch ----------
    if parsed["type"] == "collection":
        sid = parsed["sid"]
        # Try real titles via bilibili_api, degrade to yt-dlp bvid list
        col = get_collection_rich(sid) or get_collection_degraded(sid)
        if not col or not col["items"]:
            print(f"[ERROR] Cannot fetch collection {sid}", file=sys.stderr)
            sys.exit(1)

        index_path = build_collection_index(sid, col)

        # Default: process first video in collection
        first = col["items"][0]
        bv_id = first["bv_id"]
        cache_dir = CACHE_DIR / str(sid) / bv_id
        cache_dir.mkdir(parents=True, exist_ok=True)
        write_resolve(cache_dir, bv_id, 1, "collection", raw)

        output = {
            "type": "collection",
            "collection_id": sid,
            "title": col.get("title", ""),
            "bv_id": bv_id,
            "page": 1,
            "cache_dir": str(cache_dir),
            "index_path": str(index_path),
            "total_videos": col["total"],
        }
        print(yaml.dump(output, allow_unicode=True, default_flow_style=False))
        print(f"[COLLECTION] {col.get('title', '')} → {col['total']} videos")
        return

    # ---------- Video branch ----------
    bv_id = parsed["bv_id"]
    page = parsed["page"]

    # Detect multi-P
    playlist = detect_playlist(bv_id)
    is_multi = bool(playlist and playlist.get("multi_p"))

    # Build index for multi-P
    index_path = None
    if is_multi:
        index_path = build_index(bv_id, playlist)

    # Build cache directory
    cache_dir = build_cache_dir(bv_id, page, playlist)

    # Write resolve.yaml
    vtype = "multi_p" if is_multi else "single"
    write_resolve(cache_dir, bv_id, page, vtype, raw)

    # Output
    output = {
        "type": vtype,
        "bv_id": bv_id,
        "page": page,
        "cache_dir": str(cache_dir),
    }
    if is_multi:
        output["index_path"] = str(index_path)
        output["total_pages"] = playlist["count"]

    print(yaml.dump(output, allow_unicode=True, default_flow_style=False))

    # Status line for human readability
    if is_multi:
        print(f"[MULTI-P] {bv_id} → {playlist['count']} pages")
    else:
        print(f"[SINGLE] {bv_id}")


if __name__ == "__main__":
    main()
