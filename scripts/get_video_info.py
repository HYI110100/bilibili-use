#!/usr/bin/env python3
"""Get B站 video metadata with cache support.

Usage:
  get_video_info.py <bv_id_or_url>  [--force]  [--json]

Output: YAML metadata with [CACHE: HIT/MISS] header.
Cache: ~/.cache/bilibili-use/<bv_id>/metadata.yaml (TTL: 24h)
"""

import subprocess
import sys
import json
import yaml
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR, resolve_id
CACHE_TTL = 24 * 3600  # 24 hours


def detect_multipage(bv_id: str) -> dict:
    """Check if video has multiple pages via yt-dlp flat playlist."""
    url = f"https://www.bilibili.com/video/{bv_id}"
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--dump-json", url],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return {"multi_p": False, "reason": "yt-dlp unavailable"}
    try:
        data = json.loads(result.stdout.strip().split("\n")[0])
        if data.get("_type") in ("playlist", "url") and data.get("playlist_count"):
            return {"multi_p": True, "count": data["playlist_count"],
                    "title": data.get("title", "")}
    except (json.JSONDecodeError, KeyError):
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
    as_json = "--json" in sys.argv

    bv_id = resolve_id(raw_input)
    cache_dir = CACHE_DIR / bv_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "metadata.yaml"

    data = None
    if not force and cache_fresh(cache_file):
        data = yaml.safe_load(cache_file.read_text())
        cache_status = "HIT"
    else:
        data = fetch_metadata(bv_id)
        cache_file.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        cache_status = "MISS"

    # Multi-P detection (always run, fast via yt-dlp flat playlist)
    multi = detect_multipage(bv_id)

    status_line = f"[CACHE: {cache_status}]"
    if multi["multi_p"]:
        status_line += f" [MULTI-P: {multi.get('count', '?')} pages]"

    if as_json:
        print(status_line)
        output = {"metadata": data, "multi_p": multi}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(status_line)
        if multi["multi_p"]:
            print(f"[WARN] Multi-page video ({multi['count']} pages). Processing P1 only.")
        print(yaml.dump(data, allow_unicode=True, default_flow_style=False))
    print(f"[CACHED: {cache_file}]")


if __name__ == "__main__":
    main()
