#!/usr/bin/env python3
"""Get B站 AI summary with cache.

Usage:
  get_ai_summary.py <bv_id_or_url>  [--force]

Returns B站's AI-generated summary paragraph (~100-300 chars).
Cache: ~/.cache/bilibili-use/<bv_id>/ai_summary.md (permanent)
"""

import subprocess
import sys

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR, resolve_id


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw_input = sys.argv[1]
    force = "--force" in sys.argv

    bv_id = resolve_id(raw_input)
    cache_dir = CACHE_DIR / bv_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "ai_summary.md"

    if not force and cache_file.exists():
        cached = cache_file.read_text().strip()
        if cached and cached != "(empty)":
            print(f"[CACHE: HIT]")
            print(cached)
            print(f"[CACHED: {cache_file}]")
            return

    result = subprocess.run(
        ["bili", "video", bv_id, "--ai", "--yaml"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"[ERROR] bili CLI failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    import yaml
    data = yaml.safe_load(result.stdout)
    summary = data.get("data", {}).get("ai_summary", "")

    if summary:
        cache_file.write_text(summary)
        print("[CACHE: MISS]")
        print(summary)
    else:
        cache_file.write_text("(empty)")
        print("[CACHE: MISS] (empty)")

    print(f"[CACHED: {cache_file}]")


if __name__ == "__main__":
    main()
