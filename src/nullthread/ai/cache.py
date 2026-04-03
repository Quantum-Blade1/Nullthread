"""Disk cache for AI diagnosis keyed by finding hash."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from nullthread.models import Finding


def _finding_key(f: Finding) -> str:
    h = hashlib.sha256()
    h.update(f.kind.value.encode())
    h.update(f.kernel_name.encode())
    h.update(str(f.line).encode())
    h.update(f.evidence.encode("utf-8", errors="replace"))
    return h.hexdigest()


def load_cache(cache_dir: Path, f: Finding) -> dict | None:
    path = cache_dir / f"{_finding_key(f)}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_cache(cache_dir: Path, f: Finding, payload: dict) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{_finding_key(f)}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
