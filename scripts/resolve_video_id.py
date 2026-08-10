#!/usr/bin/env python3
"""Resolve any B站 link/ID to a canonical BV ID.

Usage:
  resolve_video_id.py <input>            # BV ID, URL, or short link
  resolve_video_id.py BV1xxx --json      # JSON output

Supported formats:
  - BV ID:    BV1ABcsztEcY
  - AV ID:    av21877586
  - Episode:  ep198381
  - Full URL: https://www.bilibili.com/video/BV1ABcsztEcY?p=2
  - Short:    https://b23.tv/xxxxx

Output (default text):
  BV_ID [PAGE] [TIMESTAMP]

Output (--json):
  {"bv_id": "BV1xxx", "page": 1, "timestamp": 0, "aid": ..., "original": "..."}
"""

import subprocess
import sys
import json
import re
import urllib.request
from urllib.parse import urlparse, parse_qs

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR


def follow_redirect(url: str, timeout: int = 10) -> str:
    """Follow b23.tv short link redirects to resolve the real URL."""
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.geturl()
    except Exception as e:
        print(f"[ERROR] Failed to resolve short link: {e}", file=sys.stderr)
        sys.exit(1)


def parse_bv_id(raw: str) -> dict:
    """Parse raw input into {"bv_id", "page", "timestamp", "aid"}."""
    raw = raw.strip()

    # b23.tv short link — follow redirect first
    if "b23.tv" in raw or ("b23.tv" not in raw and raw.startswith("http") and "/s/" in raw):
        raw = follow_redirect(raw)

    # Extract page (p=) and timestamp (t=) from URL query
    page = 1
    timestamp = 0
    if "?" in raw:
        qs = parse_qs(urlparse(raw).query)
        page = int(qs.get("p", [1])[0])
        timestamp = int(qs.get("t", [0])[0])

    # Strip query/fragment for matching
    clean = raw.split("?")[0].split("#")[0]

    bv_id = None
    aid = None

    # Direct BV ID
    m = re.search(r"(BV[0-9A-Za-z]{10})", clean)
    if m:
        bv_id = m.group(1)

    # AV number
    m = re.search(r"av(\d+)", clean, re.IGNORECASE)
    if m:
        aid = int(m.group(1))
        if not bv_id:
            bv_id = f"av{aid}"  # bili CLI accepts AV numbers too

    # Episode (bangumi)
    m = re.search(r"ep(\d+)", clean, re.IGNORECASE)
    if m and not bv_id:
        bv_id = f"ep{m.group(1)}"

    if not bv_id:
        # Last resort: try as bare number (AV)
        m = re.search(r"(\d{6,})", clean)
        if m:
            aid = int(m.group(1))
            bv_id = f"av{aid}"

    if not bv_id:
        print(f"[ERROR] Cannot extract Bilibili video ID from: {raw}", file=sys.stderr)
        sys.exit(1)

    return {"bv_id": bv_id, "page": page, "timestamp": timestamp, "aid": aid}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw = sys.argv[1]
    as_json = "--json" in sys.argv

    result = parse_bv_id(raw)

    # Ensure cache dir for this video
    cache_path = CACHE_DIR / result["bv_id"]
    cache_path.mkdir(parents=True, exist_ok=True)

    # Cache the resolution result
    resolve_cache = cache_path / "resolve.json"
    resolve_cache.write_text(json.dumps({**result, "original": raw}, ensure_ascii=False, indent=2))

    if as_json:
        print(json.dumps({**result, "original": raw, "[CACHED]": str(resolve_cache)},
                         ensure_ascii=False, indent=2))
    else:
        parts = [result["bv_id"]]
        if result["page"] > 1:
            parts.append(f"p{result['page']}")
        if result["timestamp"] > 0:
            parts.append(f"t{result['timestamp']}s")
        print(" ".join(parts))
        print(f"[CACHED: {resolve_cache}]")


if __name__ == "__main__":
    main()
