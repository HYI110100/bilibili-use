#!/usr/bin/env python3
"""Extract frames from B站 videos at given timestamps via stream (no full download).

Usage:
  extract_frames.py <bv_id_or_url> --at 10,45,120  [--quality 4k]  [--force]
  extract_frames.py <bv_id_or_url> --at 30  [--json]

Uses yt-dlp -g to get direct stream URL, then ffmpeg seeks to each timestamp.
No full video download — single frames extracted in ~0.5s each.
Quality: defaults to max 1080p. Pass --quality 4k / 2160p / 2k / 720p.
Cache: ~/.cache/bilibili-use/<bv_id>/frames/<timestamp>s.jpg

Requires: yt-dlp, ffmpeg
"""

import subprocess
import sys
import json
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR, resolve_id


def get_stream_url(bv_id: str) -> str:
    """Get direct video stream URL via yt-dlp with cookies."""
    url = f"https://www.bilibili.com/video/{bv_id}"

    cookie_sources = [
        ["--cookies-from-browser", "firefox"],
        ["--cookies-from-browser", "chrome"],
    ]
    for cookie_args in cookie_sources:
        result = subprocess.run(
            ["yt-dlp", "-g", *cookie_args, url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]

    # Fallback: no cookies
    result = subprocess.run(
        ["yt-dlp", "-g", url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0 or not result.stdout.strip():
        print(f"[ERROR] Cannot get stream URL: {result.stderr[-300:]}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip().split("\n")[0]


def extract_frame(stream_url: str, timestamp: float, output_path: Path) -> bool:
    """Extract single frame from stream URL using ffmpeg seek."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", stream_url,
        "-vframes", "1",
        "-q:v", "2",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0 and output_path.exists()


def main():
    if len(sys.argv) < 3 or "--at" not in sys.argv:
        print(__doc__)
        sys.exit(1)

    raw_input = sys.argv[1]
    force = "--force" in sys.argv
    as_json = "--json" in sys.argv

    timestamps_str = ""
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--at" and i + 1 < len(args):
            timestamps_str = args[i + 1]
            i += 2
        else:
            i += 1

    if not timestamps_str:
        print("[ERROR] --at required (comma-separated seconds)", file=sys.stderr)
        sys.exit(1)


    bv_id = resolve_id(raw_input)
    frames_dir = CACHE_DIR / bv_id / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    try:
        timestamps = [float(t.strip()) for t in timestamps_str.split(",") if t.strip()]
    except ValueError:
        print("[ERROR] Invalid timestamps. Use: --at 10,45.5,120", file=sys.stderr)
        sys.exit(1)

    # Check cache
    results = []
    missing_ts = []
    for ts in timestamps:
        fp = frames_dir / f"{ts:06.1f}s.jpg"
        if not force and fp.exists():
            results.append({"timestamp": ts, "path": str(fp), "cached": True})
        else:
            missing_ts.append(ts)
            results.append({"timestamp": ts, "path": str(fp), "cached": False})

    # Stream-extract missing frames
    if missing_ts:
        print(f"[STREAM] Extracting {len(missing_ts)} frames via stream (no download)...",
              file=sys.stderr)
        stream_url = get_stream_url(bv_id)
        for ts in missing_ts:
            fp = frames_dir / f"{ts:06.1f}s.jpg"
            ok = extract_frame(stream_url, ts, fp)
            for r in results:
                if r["timestamp"] == ts:
                    r["cached"] = ok
                    r["path"] = str(fp) if ok else None

    # Output
    if as_json:
        print(json.dumps({"bv_id": bv_id, "frames": results}, ensure_ascii=False, indent=2))
    else:
        hit = sum(1 for r in results if r["cached"])
        miss = len(missing_ts)
        print(f"[FRAMES] {hit} cached, {miss} stream-extracted")
        for r in results:
            status = "HIT" if r["cached"] else ("OK" if r["path"] else "FAIL")
            print(f"  {r['timestamp']:8.1f}s  [{status}]  {r['path']}")

    print(f"[CACHED: {frames_dir}/]")


if __name__ == "__main__":
    main()
