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
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR
RESOLVE_SCRIPT = Path(__file__).parent / "resolve_video_id.py"
SPLIT_THRESHOLD = 3000  # chars: above this, auto-split for subagent processing
CHUNK_SIZE = 1500        # chars per chunk when splitting


def resolve_bv_id(raw: str) -> str:
    result = subprocess.run(
        [sys.executable, str(RESOLVE_SCRIPT), raw],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip().split()[0]


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
        print(__doc__)
        sys.exit(1)

    raw_input = sys.argv[1]
    force = "--force" in sys.argv
    as_json = "--json" in sys.argv

    bv_id = resolve_bv_id(raw_input)
    cache_dir = CACHE_DIR / bv_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    srt_file = cache_dir / "subtitle.platform.srt"

    # Check cache
    if not force and srt_file.exists():
        cached_text = srt_file.read_text().strip()
        if cached_text and cached_text != "[NO SUBTITLE]":
            # Already have it. Check if compressed version exists.
            compressed = cache_dir / "subtitle.compressed.md"
            if compressed.exists():
                if as_json:
                    print(json.dumps({"status": "cached", "compressed": str(compressed),
                                      "raw": str(srt_file), "chars": len(cached_text)},
                                     ensure_ascii=False))
                else:
                    print(f"[CACHE: HIT] [COMPRESSED: {compressed}]")
                    print(f"[RAW: {srt_file}] ({len(cached_text)} chars)")
                return
            elif len(cached_text) <= SPLIT_THRESHOLD:
                # Small enough to return directly
                if as_json:
                    print(json.dumps({"status": "cached", "raw": str(srt_file),
                                      "chars": len(cached_text)}, ensure_ascii=False))
                else:
                    print(f"[CACHE: HIT] ({len(cached_text)} chars)")
                    print(cached_text[:SPLIT_THRESHOLD])
                    if len(cached_text) > SPLIT_THRESHOLD:
                        print(f"... [truncated at {SPLIT_THRESHOLD} chars, full: {srt_file}]")
                return
            else:
                # Large but needs re-split (chunks may have been cleaned)
                pass

    # Fetch from bili CLI
    sub_data = fetch_subtitle_srt(bv_id)

    if not sub_data.get("available"):
        srt_file.write_text("[NO SUBTITLE]")
        if as_json:
            print(json.dumps({"status": "no_subtitle"}, ensure_ascii=False))
        else:
            print("[NO SUBTITLE]")
        return

    text = subtitle_to_text_with_timestamps(sub_data)
    srt_file.write_text(text)
    chars = len(text)

    if chars <= SPLIT_THRESHOLD:
        # Small: return content directly
        if as_json:
            print(json.dumps({"status": "ok", "raw": str(srt_file), "chars": chars},
                             ensure_ascii=False))
        else:
            print(f"[CACHE: MISS] ({chars} chars)")
            print(text)
            print(f"[CACHED: {srt_file}]")
        return

    # Large: split into chunks, return paths for subagent processing
    chunks = split_into_chunks(text, cache_dir)
    if as_json:
        print(json.dumps({"status": "split", "chunks": chunks, "raw": str(srt_file),
                          "total_chars": chars}, ensure_ascii=False, indent=2))
    else:
        print(f"[SPLIT] {len(chunks)} chunks (total {chars} chars)")
        for c in chunks:
            print(f"  [{c['start']}-{c['end']}] {c['chars']} chars → {c['path']}")
        print(f"\n[RAW: {srt_file}]")
        print(f"[ACTION] Delegate each chunk to subagent for compression.")
        print(f"[ACTION] Save merged result to: {cache_dir / 'subtitle.compressed.md'}")


if __name__ == "__main__":
    main()
