"""Shared configuration for bilibili-use scripts.

All scripts import CACHE_DIR from here instead of hardcoding paths.
"""

from pathlib import Path

# Platform-agnostic cache root
CACHE_DIR = Path.home() / ".cache" / "bilibili-use"

# Cache TTLs (in seconds)
TTL_METADATA = 24 * 3600      # 24 hours
TTL_COMMENTS_HOT = 6 * 3600    # 6 hours
TTL_COMMENTS_LATEST = 1 * 3600  # 1 hour
