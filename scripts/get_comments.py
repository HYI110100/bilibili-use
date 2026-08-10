#!/usr/bin/env python3
"""Get B站 video comments with cache support.

Usage:
  get_comments.py <bv_id_or_url>  [--mode hot|latest]  [--count N]  [--force]  [--json]

Output: YAML comment list with [CACHE: HIT/MISS] header.
Cache: ~/.cache/bilibili-use/<bv_id>/comments.yaml
       TTL: 6h for hot, 1h for latest
"""

import subprocess
import sys
import json
import yaml
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR, resolve_id


def cache_fresh(path: Path, ttl: int) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < ttl


def fetch_comments(bv_id: str, count: int) -> dict:
    result = subprocess.run(
        ["bili", "video", bv_id, "--comments", "--yaml"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"[ERROR] bili CLI failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    data = yaml.safe_load(result.stdout)
    return data


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw_input = sys.argv[1]
    mode = "hot"
    count = 20
    force = False
    as_json = "--json" in sys.argv

    # Parse flags
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--mode" and i + 1 < len(args):
            mode = args[i + 1]
            i += 2
        elif args[i] == "--count" and i + 1 < len(args):
            count = int(args[i + 1])
            i += 2
        elif args[i] == "--force":
            force = True
            i += 1
        else:
            i += 1

    bv_id = resolve_id(raw_input)
    cache_dir = CACHE_DIR / bv_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "comments.yaml"

    ttl = 1 * 3600 if mode == "latest" else 6 * 3600

    data = None
    if not force and cache_fresh(cache_file, ttl):
        data = yaml.safe_load(cache_file.read_text())
        cache_status = "HIT"
    else:
        data = fetch_comments(bv_id, count)
        cache_file.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        cache_status = "MISS"

    status_line = f"[CACHE: {cache_status}] [{mode}]"
    if as_json:
        print(status_line)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(status_line)
        print(yaml.dump(data, allow_unicode=True, default_flow_style=False))
    print(f"[CACHED: {cache_file}]")


if __name__ == "__main__":
    main()
