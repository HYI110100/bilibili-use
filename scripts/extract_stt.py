#!/usr/bin/env python3
"""Local STT (speech-to-text) for B站 videos — PLACEHOLDER.

Usage:
  extract_stt.py <bv_id_or_url>  [--force]

Status: NOT IMPLEMENTED. Returns fallback instructions for the model.
When implemented, will:
  1. Check if audio already cached (extract_audio.py)
  2. If not, extract audio from video
  3. Run local STT model (whisper/faster-whisper/sherpa-onnx)
  4. Save transcript to subtitle.asr.txt
  5. Return transcript text

For now: tells the model to fall back to visual analysis (extract_frames.py).
"""

import sys

print("[STT] 本地语音转写尚未实现。")
print("[STT] 降级方案：使用抽帧进行视觉分析。")
print("[STT] 流程：compute_timestamps.py → extract_frames.py → 看图理解内容。")
print("[FALLBACK: visual]")
