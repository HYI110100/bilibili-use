#!/usr/bin/env python3
"""Get B站 video metadata with cache support.

Usage:
  get_video_info.py <bv_id_or_url>  [--force]
  get_video_info.py <bv_id_or_url>  --cache-dir <path>  [--force]

Output: YAML metadata with [CACHE: HIT/MISS] header.
Cache: <cache_dir>/metadata.yaml (TTL: 24h)
"""

import subprocess
import sys
import yaml
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import resolve_cache_dir, resolve_bv_id, CACHE_DIR

CACHE_TTL = 24 * 3600


def detect_multipage(bv_id: str) -> dict:
    """Check if video has multiple pages via yt-dlp flat playlist."""
    url = f"https://www.bilibili.com/video/{bv_id}"
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--dump-json", url],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return {"multi_p": False}
    try:
        import json as _json
        data = _json.loads(result.stdout.strip().split("\n")[0])
        count = data.get("playlist_count", 0) or data.get("n_entries", 0)
        if count > 1:
            return {"multi_p": True, "count": count, "title": data.get("playlist_title", "")}
    except Exception:
        pass
    return {"multi_p": False}


def cache_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < CACHE_TTL


def fetch_metadata(bv_id: str) -> dict:
    result = subprocess.run(
        ["bili", "video", bv_id, "--yaml"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"[ERROR] bili CLI failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(result.stdout)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw_input = sys.argv[1]
    force = "--force" in sys.argv

    cache_dir = resolve_cache_dir(raw_input, sys.argv)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "metadata.yaml"

    # Resolve bv_id for API call
    bv_id = resolve_bv_id(raw_input, cache_dir)

    # Cache check
    data = None
    if not force and cache_fresh(cache_file):
        data = yaml.safe_load(cache_file.read_text())
        cache_status = "HIT"
    else:
        data = fetch_metadata(bv_id)
        cache_file.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        cache_status = "MISS"

    # Multi-P check only on cache MISS (resolve step handles this primarily)
    if cache_status == "MISS":
        multi = detect_multipage(bv_id)
    else:
        multi = {"multi_p": False}
    vinfo = data.get("data", {}).get("video", {})
    total_s = vinfo.get("duration_seconds", 0)

    status_line = f"[CACHE: {cache_status}]"
    if multi["multi_p"]:
        page_count = multi["count"]
        per_s = total_s // page_count if page_count > 0 else 0
        total_h, total_m = total_s // 3600, (total_s % 3600) // 60
        per_h, per_m = per_s // 3600, (per_s % 3600) // 60
        status_line += f" [MULTI-P: {page_count}P]"
        print(status_line)
        print(f"[DURATION] Total: {total_h}h{total_m}m | Per-P: ~{per_h}h{per_m}m")
    else:
        print(status_line)

    print(yaml.dump(data, allow_unicode=True, default_flow_style=False))
    print(f"[CACHED: {cache_file}]")


if __name__ == "__main__":
    main()
