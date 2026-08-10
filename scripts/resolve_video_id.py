#!/usr/bin/env python3
"""Resolve any B站 link/ID to canonical ID, cache path, and video type.

Usage:
  resolve_video_id.py <input>            # BV ID, URL, or short link
  resolve_video_id.py <input> --yaml     # YAML output (default)

Detects:
  - single:   普通单视频
  - multi_p:  多P视频（同一 BV 下有多个分P）
  - collection: 合集（未来支持）

Cache structure:
  single:        ~/.cache/bilibili-use/<bv_id>/
  multi_p:       ~/.cache/bilibili-use/<bv_id>/p<N>/
  collection:    ~/.cache/bilibili-use/<col_id>/<bv_id>/

Output (YAML):
  type: single|multi_p
  bv_id: BV1xxx
  page: 1
  cache_dir: /home/hyi/.cache/bilibili-use/...
  index_path: /home/hyi/.cache/bilibili-use/.../index.yaml  (multi_p only)
"""

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
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.geturl()
    except Exception as e:
        print(f"[ERROR] Failed to resolve short link: {e}", file=sys.stderr)
        sys.exit(1)


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
    """Parse raw input into {bv_id, page, timestamp}."""
    raw = raw.strip()

    if "b23.tv" in raw:
        raw = follow_redirect(raw)

    page = 1
    timestamp = 0
    if "?" in raw:
        qs = parse_qs(urlparse(raw).query)
        page = int(qs.get("p", [1])[0])
        timestamp = int(qs.get("t", [0])[0])

    bv_id = resolve_id(raw)
    return {"bv_id": bv_id, "page": page, "timestamp": timestamp}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw = sys.argv[1]
    parsed = parse_input(raw)
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
