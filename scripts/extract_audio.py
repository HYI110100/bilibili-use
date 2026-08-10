#!/usr/bin/env python3
"""Extract audio from B站 video for ASR (speech-to-text).

Usage:
  extract_audio.py <bv_id_or_url>  [--segment 25]  [--no-split]  [--force]

Uses `bili audio` to download and split audio into ASR-ready WAV segments
(25s each, 16kHz mono by default). Falls back to yt-dlp if bili CLI unavailable.
Cache: ~/.cache/bilibili-use/<bv_id>/audio/

Requires: bili CLI with audio support (uv tool install 'bilibili-cli[audio]')
"""

import subprocess
import sys
import json

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import CACHE_DIR, resolve_id


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw_input = sys.argv[1]
    force = "--force" in sys.argv
    as_json = "--json" in sys.argv
    segment = 25
    no_split = "--no-split" in sys.argv

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--segment" and i + 1 < len(args):
            segment = int(args[i + 1])
            i += 2
        else:
            i += 1

    bv_id = resolve_id(raw_input)
    audio_dir = CACHE_DIR / bv_id / "audio"

    if not force and audio_dir.exists() and list(audio_dir.glob("*.wav")):
        wavs = sorted(audio_dir.glob("*.wav"))
        if as_json:
            print(json.dumps({"bv_id": bv_id, "cached": True, "segments": [str(w) for w in wavs]},
                             ensure_ascii=False, indent=2))
        else:
            print(f"[CACHE: HIT] {len(wavs)} segments")
            for w in wavs:
                print(f"  {w}")
        print(f"[CACHED: {audio_dir}/]")
        return

    audio_dir.mkdir(parents=True, exist_ok=True)
    cache_flag = audio_dir / ".cached"

    cmd = ["bili", "audio", bv_id, "-o", str(audio_dir)]
    if no_split:
        cmd.append("--no-split")
    else:
        cmd.extend(["--segment", str(segment)])

    print(f"[AUDIO] Extracting audio via bili CLI...", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        # Fallback: try yt-dlp for audio only
        print(f"[AUDIO] bili CLI failed, trying yt-dlp fallback...", file=sys.stderr)
        url = f"https://www.bilibili.com/video/{bv_id}"
        m4a_path = audio_dir / "full.m4a"
        dl = subprocess.run([
            "yt-dlp", "-f", "bestaudio", "-o", str(m4a_path),
            "--cookies-from-browser", "firefox", "--no-playlist", url
        ], capture_output=True, text=True, timeout=120)
        if dl.returncode != 0:
            print(f"[ERROR] Audio extraction failed: {dl.stderr[-300:]}", file=sys.stderr)
            sys.exit(1)
        cache_flag.touch()
        if as_json:
            print(json.dumps({"bv_id": bv_id, "cached": False, "file": str(m4a_path)},
                             ensure_ascii=False, indent=2))
        else:
            print(f"[CACHE: MISS] Downloaded as {m4a_path}")
            print(f"[CACHED: {audio_dir}/]")
        return

    cache_flag.touch()
    wavs = sorted(audio_dir.glob("*.wav"))

    if as_json:
        print(json.dumps({"bv_id": bv_id, "cached": False, "segments": [str(w) for w in wavs]},
                         ensure_ascii=False, indent=2))
    else:
        print(f"[CACHE: MISS] {len(wavs)} segments")
        for w in wavs:
            print(f"  {w}")

    print(f"[CACHED: {audio_dir}/]")


if __name__ == "__main__":
    main()
