"""Shared configuration for bilibili-use scripts."""

import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

CACHE_DIR = Path("~/.cache/bilibili-use/").expanduser()


def resolve_id(raw: str) -> str:
    """Parse any B站 link/ID and return canonical BV ID.

    Supported: BV1xxx, av123456, ep123456, full URLs, b23.tv short links.
    """
    raw = raw.strip()

    # b23.tv short link: follow redirect
    if "b23.tv" in raw and not raw.startswith("BV"):
        import urllib.request
        req = urllib.request.Request(raw, method="HEAD")
        req.add_header("User-Agent", "Mozilla/5.0")
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            raw = resp.geturl()
        except Exception:
            pass

    # Remove query string and fragment for ID extraction
    clean = raw.split("?")[0].split("#")[0]

    # BV ID
    m = re.search(r"(BV[0-9A-Za-z]{10})", clean)
    if m:
        return m.group(1)

    # AV ID
    m = re.search(r"av(\d+)", clean, re.IGNORECASE)
    if m:
        return f"av{m.group(1)}"

    # Episode ID
    m = re.search(r"ep(\d+)", clean, re.IGNORECASE)
    if m:
        return f"ep{m.group(1)}"

    raise ValueError(f"Cannot extract Bilibili video ID from: {raw}")
