#!/usr/bin/env python3
"""Get B站 video comments with cache support.

Usage:
  get_comments.py <bv_id_or_url>  [--mode hot|latest]  [--count N]  [--force]
  get_comments.py <bv_id_or_url>  --cache-dir <path>    [--mode hot|latest]

Output: YAML comment list with [CACHE: HIT/MISS] header.
Each comment: {id, author, like, message}
Cache TTL: 6h for hot, 1h for latest.
"""

import subprocess
import sys
import yaml
import time

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import resolve_cache_dir


def cache_fresh(path: Path, ttl: int) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < ttl


def fetch_and_strip(bv_id: str) -> list:
    """Fetch comments via bili CLI, return only [{id, author, like, message}]."""
    result = subprocess.run(
        ["bili", "video", bv_id, "--comments", "--yaml"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"[ERROR] bili CLI failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    data = yaml.safe_load(result.stdout)
    raw_comments = data.get("data", {}).get("comments", [])

    stripped = []
    for c in raw_comments:
        stripped.append({
            "id": c.get("id"),
            "author": c.get("author", {}).get("name", ""),
            "like": c.get("like", 0),
            "message": c.get("message", ""),
        })
    return stripped


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw_input = sys.argv[1]
    mode = "hot"
    force = False

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--mode" and i + 1 < len(args):
            mode = args[i + 1]
            i += 2
        elif args[i] == "--force":
            force = True
            i += 1
        else:
            i += 1

    cache_dir = resolve_cache_dir(raw_input, sys.argv)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"comments_{mode}.yaml"

    ttl = 1 * 3600 if mode == "latest" else 6 * 3600

    if not force and cache_fresh(cache_file, ttl):
        comments = yaml.safe_load(cache_file.read_text())
        cache_status = "HIT"
    else:
        # Resolve bv_id for API call
        from config import resolve_id, read_resolve
        r = read_resolve(cache_dir)
        bv_id = r.get("bv_id") or resolve_id(raw_input)
        comments = fetch_and_strip(bv_id)
        cache_file.write_text(yaml.dump(comments, allow_unicode=True, default_flow_style=False))
        cache_status = "MISS"

    print(f"[CACHE: {cache_status}] [{mode}] ({len(comments)} comments)")
    print(yaml.dump(comments, allow_unicode=True, default_flow_style=False))
    print(f"[CACHED: {cache_file}]")


if __name__ == "__main__":
    main()
