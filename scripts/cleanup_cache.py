#!/usr/bin/env python3
"""Clean up B站 video cache to free disk space.

Usage:
  cleanup_cache.py                    # Default: remove video files older than 7 days
  cleanup_cache.py --older-than 3d    # Custom age threshold
  cleanup_cache.py --bv BVxxx         # Remove specific video cache
  cleanup_cache.py --dry-run          # Preview only, no deletion
  cleanup_cache.py --stats            # Show cache size breakdown

Default policy: only removes video .mp4 files (largest). 
Keeps subtitles, frames, metadata, audio.
"""

import sys
import time
import shutil
import argparse

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR


def parse_age(age_str: str) -> int:
    """Parse '7d', '24h', '30d' → seconds."""
    age_str = age_str.strip().lower()
    if age_str.endswith("d"):
        return int(age_str[:-1]) * 86400
    elif age_str.endswith("h"):
        return int(age_str[:-1]) * 3600
    return int(age_str)  # raw seconds


def get_size_mb(path: Path) -> float:
    """Get directory/file size in MB."""
    if path.is_file():
        return path.stat().st_size / (1024 * 1024)
    total = 0
    for f in path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total / (1024 * 1024)


def main():
    parser = argparse.ArgumentParser(description="Bilibili cache cleaner")
    parser.add_argument("--older-than", default="7d", help="Remove files older than (default: 7d)")
    parser.add_argument("--bv", help="Remove specific video ID")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--stats", action="store_true", help="Show cache stats")
    args = parser.parse_args()

    if not CACHE_DIR.exists():
        print("[CLEANUP] No cache directory. Nothing to do.")
        return

    # Stats mode
    if args.stats:
        total = get_size_mb(CACHE_DIR)
        videos = sum(get_size_mb(CACHE_DIR / d) for d in CACHE_DIR.iterdir()
                     if d.is_dir())
        count = sum(1 for d in CACHE_DIR.iterdir() if d.is_dir())
        print(f"[STATS] {count} videos, {total:.1f}MB total cache")
        # Breakdown by file type
        mp4_size = sum(f.stat().st_size for f in CACHE_DIR.rglob("video_*.mp4")) / 1024 / 1024
        frames_size = sum(f.stat().st_size for f in CACHE_DIR.rglob("frames/*.jpg")) / 1024 / 1024
        audio_size = sum(f.stat().st_size for f in CACHE_DIR.rglob("audio/*.wav")) / 1024 / 1024
        print(f"  video .mp4: {mp4_size:.1f}MB")
        print(f"  frames .jpg: {frames_size:.1f}MB")
        print(f"  audio .wav: {audio_size:.1f}MB")
        return

    # Single video cleanup
    if args.bv:
        target = CACHE_DIR / args.bv
        if target.exists():
            size_before = get_size_mb(target)
            if args.dry_run:
                print(f"[DRY-RUN] Would remove: {target} ({size_before:.1f}MB)")
            else:
                shutil.rmtree(target)
                print(f"[CLEANUP] Removed: {args.bv} ({size_before:.1f}MB)")
        else:
            print(f"[CLEANUP] Not found: {args.bv}")
        return

    # Age-based cleanup: remove old video .mp4 files only
    cutoff = time.time() - parse_age(args.older_than)
    removed = 0
    freed = 0.0

    for video_dir in CACHE_DIR.iterdir():
        if not video_dir.is_dir():
            continue
        for mp4 in video_dir.glob("video_*.mp4"):
            if mp4.stat().st_mtime < cutoff:
                size_mb = mp4.stat().st_size / (1024 * 1024)
                if args.dry_run:
                    print(f"[DRY-RUN] Would remove: {mp4} ({size_mb:.1f}MB)")
                else:
                    mp4.unlink()
                    print(f"[CLEANUP] Removed: {mp4.name} ({size_mb:.1f}MB)")
                removed += 1
                freed += size_mb

    if removed == 0:
        print(f"[CLEANUP] Nothing to clean (threshold: >{args.older_than})")
    else:
        action = "Would free" if args.dry_run else "Freed"
        print(f"[CLEANUP] {action} {freed:.1f}MB from {removed} files")


if __name__ == "__main__":
    main()
