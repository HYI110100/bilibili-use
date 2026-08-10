#!/usr/bin/env python3
"""Download full B站 video to local cache.

Usage:
  download_video.py <bv_id_or_url>  [--quality 1080p]  [--force]  [--cache-dir <path>]

Downloads complete video file via yt-dlp with cookies for best quality.
Use this when you need the full video (not just frames).
Cache: ~/.cache/bilibili-use/<bv_id>/video_<quality>.mp4

Requires: yt-dlp
"""

import subprocess
import sys

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import resolve_cache_dir, resolve_bv_id, COOKIE_SOURCES


def parse_quality(arg: str) -> str:
    """Parse quality flag: '4k'→'2160', '2k'→'1440', '1080p'→'1080'"""
    raw = arg.lower().replace("p", "").replace("k", "000")
    if raw == "4000":
        return "2160"
    if raw == "2000":
        return "1440"
    return raw


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw_input = sys.argv[1]
    force = "--force" in sys.argv
    max_quality = "1080"

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--quality" and i + 1 < len(args):
            max_quality = parse_quality(args[i + 1])
            i += 2
        else:
            i += 1

    cache_dir = resolve_cache_dir(raw_input, sys.argv)
    cache_dir.mkdir(parents=True, exist_ok=True)
    video_path = cache_dir / f"video_{max_quality}p.mp4"

    if not force and video_path.exists():
        print(f"[CACHE: HIT] {video_path}")
        return

    # Resolve bv_id for URL
    bv_id = resolve_bv_id(raw_input, cache_dir)

    url = f"https://www.bilibili.com/video/{bv_id}"
    fmt = "bestvideo+bestaudio/best"
    sort = f"res:{max_quality},codec:avc1:m4a"

    for cookie_args in COOKIE_SOURCES:
        cmd = [
            "yt-dlp", "-f", fmt, "-S", sort,
            "-o", str(video_path),
            "--merge-output-format", "mp4",
            "--no-playlist",
            *cookie_args, url
        ]
        print(f"[DOWNLOAD] Trying with cookies: {cookie_args[1]}...", file=sys.stderr)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"[CACHED: {video_path}]")
            return

    # Fallback no cookies
    cmd = [
        "yt-dlp", "-f", fmt, "-S", sort,
        "-o", str(video_path),
        "--merge-output-format", "mp4",
        "--no-playlist", url
    ]
    print("[DOWNLOAD] Trying without cookies...", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"[ERROR] Download failed: {result.stderr[-500:]}", file=sys.stderr)
        sys.exit(1)

    print(f"[CACHED: {video_path}]")


if __name__ == "__main__":
    main()
