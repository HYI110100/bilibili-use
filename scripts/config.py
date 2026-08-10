"""Shared configuration for bilibili-use scripts."""

import re
from pathlib import Path

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

    clean = raw.split("?")[0].split("#")[0]

    m = re.search(r"(BV[0-9A-Za-z]{10})", clean)
    if m:
        return m.group(1)

    m = re.search(r"av(\d+)", clean, re.IGNORECASE)
    if m:
        return f"av{m.group(1)}"

    m = re.search(r"ep(\d+)", clean, re.IGNORECASE)
    if m:
        return f"ep{m.group(1)}"

    raise ValueError(f"Cannot extract Bilibili video ID from: {raw}")


def resolve_cache_dir(raw_input: str, args: list) -> Path:
    """Determine cache directory from --cache-dir flag or fall back to bv_id.

    Usage in scripts:
        cache_dir = resolve_cache_dir(sys.argv[1], sys.argv)
    """
    for i, arg in enumerate(args):
        if arg == "--cache-dir" and i + 1 < len(args):
            return Path(args[i + 1])
    bv_id = resolve_id(raw_input)
    return CACHE_DIR / bv_id


def read_resolve(cache_dir: Path) -> dict:
    """Read resolve.yaml from cache_dir, returning {bv_id, page, type, ...}."""
    import yaml
    rf = cache_dir / "resolve.yaml"
    if rf.exists():
        return yaml.safe_load(rf.read_text()) or {}
    return {}
