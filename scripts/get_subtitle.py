#!/usr/bin/env python3
"""Get B站 subtitles with auto-split for large content.

Usage:
  get_subtitle.py <bv_id_or_url>  [--force]  [--json]

Behavior:
  - Small subtitles (≤3000 chars): returns full content + cache path.
  - Large subtitles (>3000 chars): auto-splits into chunks by char count,
    returns chunk file paths (NOT content). Main model delegates chunks
    to subagents for compression. Compressed result saved to subtitle.compressed.md.

Cache:
  ~/.cache/bilibili-use/<bv_id>/subtitle.platform.srt   (raw, permanent)
  ~/.cache/bilibili-use/<bv_id>/chunks/                  (split chunks)
  ~/.cache/bilibili-use/<bv_id>/subtitle.compressed.md   (compressed)
"""

import subprocess
import sys
import json
import yaml

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import resolve_cache_dir, read_resolve

SPLIT_THRESHOLD = 3000
CHUNK_SIZE = 1500

def fetch_subtitle_srt(bv_id: str) -> dict:
    """Fetch subtitle via bili CLI. Returns parsed YAML."""
    result = subprocess.run(
        ["bili", "video", bv_id, "--subtitle-timeline", "--subtitle-format", "srt", "--yaml"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        return {"available": False, "items": []}
    data = yaml.safe_load(result.stdout)
    return data.get("data", {}).get("subtitle", {})


def subtitle_to_text_with_timestamps(sub_data: dict) -> str:
    """Convert subtitle items to timestamped text: [MM:SS] content"""
    items = sub_data.get("items", [])
    if not items:
        return ""
    lines = []
    for item in items:
        t = int(item.get("from", 0))
        mm, ss = divmod(t, 60)
        content = item.get("content", "").strip()
        if content:
            lines.append(f"[{mm:02d}:{ss:02d}] {content}")
    return "\n".join(lines)


def split_into_chunks(text: str, cache_dir: Path, chunk_size: int = CHUNK_SIZE) -> list:
    """Split subtitle text into char-based chunks, preserving timestamp lines."""
    chunks_dir = cache_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    # Clear old chunks
    for old in chunks_dir.glob("chunk_*.txt"):
        old.unlink()

    lines = text.split("\n")
    chunks = []
    current = []
    current_len = 0
    chunk_idx = 0

    for line in lines:
        if current_len + len(line) > chunk_size and current:
            # Save current chunk
            chunk_path = chunks_dir / f"chunk_{chunk_idx:03d}.txt"
            chunk_text = "\n".join(current)
            chunk_path.write_text(chunk_text)
            # Extract time range
            first_ts = _extract_timestamp(current[0]) if current else "00:00"
            last_ts = _extract_timestamp(current[-1]) if current else "00:00"
            chunks.append({"path": str(chunk_path), "start": first_ts, "end": last_ts,
                           "chars": len(chunk_text)})
            current = []
            current_len = 0
            chunk_idx += 1
        current.append(line)
        current_len += len(line)

    # Last chunk
    if current:
        chunk_path = chunks_dir / f"chunk_{chunk_idx:03d}.txt"
        chunk_text = "\n".join(current)
        chunk_path.write_text(chunk_text)
        first_ts = _extract_timestamp(current[0]) if current else "00:00"
        last_ts = _extract_timestamp(current[-1]) if current else "00:00"
        chunks.append({"path": str(chunk_path), "start": first_ts, "end": last_ts,
                       "chars": len(chunk_text)})

    return chunks


def _extract_timestamp(line: str) -> str:
    """Extract [MM:SS] from a subtitle line."""
    import re
    m = re.match(r"\[(\d{2}:\d{2})\]", line)
    return m.group(1) if m else "??:??"


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)

    raw_input = sys.argv[1]
    force = "--force" in sys.argv
    cache_dir = resolve_cache_dir(raw_input, sys.argv)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Resolve bv_id for API call
    r = read_resolve(cache_dir)
    from config import resolve_id
    bv_id = r.get("bv_id") or resolve_id(raw_input)
    srt_file = cache_dir / "subtitle.platform.srt"
    compressed = cache_dir / "subtitle.compressed.md"

    # Cache hit: already have subtitles
    if not force and srt_file.exists():
        cached_text = srt_file.read_text().strip()
        if cached_text and cached_text != "[NO SUBTITLE]":
            if compressed.exists():
                print(f"[CACHE: HIT] [COMPRESSED: {compressed}]")
                print(f"[RAW: {srt_file}] ({len(cached_text)} chars)")
                return
            if len(cached_text) <= SPLIT_THRESHOLD:
                print(f"[CACHE: HIT] ({len(cached_text)} chars)")
                print(cached_text[:SPLIT_THRESHOLD])
                return

    # Fetch from bili CLI
    sub_data = fetch_subtitle_srt(bv_id)
    if not sub_data.get("available"):
        srt_file.write_text("[NO SUBTITLE]")
        print("[NO SUBTITLE]")
        return

    text = subtitle_to_text_with_timestamps(sub_data)
    srt_file.write_text(text)

    if len(text) <= SPLIT_THRESHOLD:
        print(f"[CACHE: MISS] ({len(text)} chars)")
        print(text)
        print(f"[CACHED: {srt_file}]")
        return

    # Large: split into chunks
    chunks = split_into_chunks(text, cache_dir)
    print(f"[SPLIT] {len(chunks)} chunks (total {len(text)} chars)")
    for c in chunks:
        print(f"  [{c['start']}-{c['end']}] {c['chars']} chars → {c['path']}")
    print(f"[RAW: {srt_file}]")
    print(f"[ACTION] Compress each chunk in parallel, save to: {compressed}")


if __name__ == "__main__":
    main()
