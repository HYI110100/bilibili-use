#!/usr/bin/env python3
"""STT (speech-to-text) for B站 videos — DELIBERATELY BLANK.

This skill intentionally ships NO STT implementation. It is a blank slot
for the agent to fill according to its user's preferences — typically a
request to an ASR / speech-recognition service.

Usage:
  extract_stt.py (any arguments; currently ignored)

Agent playbook:
  1. Audio input:  extract_audio.py produces ASR-ready WAV segments
     under <cache_dir>/audio/
  2. Transcribe them per your user's preference (usually a service call)
  3. Save transcript to <cache_dir>/subtitle.asr.txt
  4. Continue the watching flow

No transcription available → fall back to visual analysis.
"""

import sys

# Consume all arguments silently — this script is a deliberate blank slot
_ = sys.argv[1:]

print("[STT] 语音转写是本技能的留白项：不提供实现。")
print("[STT] 由你按你的用户偏好自行补充——通常就是调用一个语音识别服务（请求式）。")
print("[STT] 输入：extract_audio.py 已备好 ASR-ready WAV 分段（<cache_dir>/audio/）。")
print("[STT] 输出建议存 <cache_dir>/subtitle.asr.txt，然后继续 watching 流程。")
print("[STT] 无法补充实现时降级：视觉分析（compute_timestamps.py → extract_frames.py）。")
print("[FALLBACK: agent-supplied STT, else visual]")
