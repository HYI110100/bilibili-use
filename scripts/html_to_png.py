#!/usr/bin/env python3
"""Convert HTML file to PNG screenshot using Playwright.

Usage:
  html_to_png.py <input.html>  [--output output.png]  [--width 1600]  [--height 1200]

Requires: playwright (pip install playwright && python -m playwright install chromium)
"""

import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    html_path = Path(sys.argv[1])
    if not html_path.exists():
        print(f"[ERROR] File not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    output = html_path.with_suffix(".png")
    width = 1600
    height = 1200

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output = Path(args[i + 1])
            i += 2
        elif args[i] == "--width" and i + 1 < len(args):
            width = int(args[i + 1])
            i += 2
        elif args[i] == "--height" and i + 1 < len(args):
            height = int(args[i + 1])
            i += 2
        else:
            i += 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ERROR] playwright not installed. Run: pip install playwright && python -m playwright install chromium",
              file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"file://{html_path.absolute()}", wait_until="networkidle")
        # Wait for markmap to render (SVG animation)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(output), full_page=True)
        browser.close()

    print(f"[PNG] {output}")


if __name__ == "__main__":
    main()
