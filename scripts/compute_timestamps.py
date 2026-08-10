#!/usr/bin/env python3
"""Compute optimal frame extraction timestamps using heatmap strategy.

Usage:
  compute_timestamps.py --duration 600              # 10min video
  compute_timestamps.py --duration 3600 --max 10    # 1hr video, max 10 frames
  compute_timestamps.py --duration 94               # short video

Algorithm: piecewise logarithmic — front-dense, middle-normal, back-sparse.
Mirrors how videos are structured (hook → body → outro).
Total frames capped at 8 by default.

Output: comma-separated timestamps (e.g., "3,15,30,52,80,120,200,350")
"""

import sys


def heatmap_timestamps(duration: float, max_frames: int = 8) -> list:
    """Generate front-loaded timestamps mimicking video structure.

    Three-segment model:
      - Opening (0-15%): hook, intro → densest sampling
      - Body (15-70%): main content → medium density
      - Outro (70-100%): end screen, "like & subscribe" → sparsest

    Uses exponential distribution within each segment for natural spacing.
    """
    if duration <= 0:
        return []

    if duration <= 60:
        n = max(3, min(max_frames, int(duration / 8)))
        step = duration / (n + 1)
        return [round(step * (i + 1), 1) for i in range(n)]

    # Segment: (start_pct, end_pct, frame_budget_pct)
    segments = [
        (0.00, 0.15, 0.40),   # Opening: 40% of frames
        (0.15, 0.70, 0.40),   # Body: 40% of frames
        (0.70, 1.00, 0.20),   # Outro: 20% of frames
    ]

    all_ts = []
    for seg_start, seg_end, budget_pct in segments:
        seg_dur = duration * (seg_end - seg_start)
        n = max(1, round(max_frames * budget_pct))
        t_start = duration * seg_start
        t_end = duration * seg_end

        if n == 1:
            all_ts.append((t_start + t_end) / 2)
        else:
            # Exponential: frames cluster toward seg_start, spread toward seg_end
            for i in range(n):
                ratio = (i / (n - 1)) ** 1.5  # exponent < 2 = gentle front-bias
                ts = t_start + ratio * seg_dur
                # Avoid exact 0:00 (black frame)
                if ts < 1.0 and seg_start == 0.0 and i == 0:
                    ts = 1.0
                all_ts.append(ts)

    unique = sorted(set(round(t, 1) for t in all_ts))
    # Cap at max_frames by subsampling
    if len(unique) > max_frames:
        step = (len(unique) - 1) / (max_frames - 1)
        unique = [unique[round(i * step)] for i in range(max_frames)]

    # Ensure minimum spacing of 2s between frames
    result = [unique[0]]
    for t in unique[1:]:
        if t - result[-1] >= 2.0:
            result.append(t)
    return result[:max_frames]


def main():
    duration = None
    max_frames = 8
    as_json = "--json" in sys.argv

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--duration" and i + 1 < len(args):
            duration = float(args[i + 1])
            i += 2
        elif args[i] == "--max" and i + 1 < len(args):
            max_frames = int(args[i + 1])
            i += 2
        else:
            i += 1

    if duration is None:
        print("Usage: compute_timestamps.py --duration <seconds> [--max N] [--json]",
              file=sys.stderr)
        sys.exit(1)

    timestamps = heatmap_timestamps(duration, max_frames)

    if as_json:
        import json
        print(json.dumps({"duration": duration, "max_frames": max_frames,
                          "count": len(timestamps), "timestamps": timestamps},
                         ensure_ascii=False, indent=2))
    else:
        print(",".join(str(t) for t in timestamps))


if __name__ == "__main__":
    main()
