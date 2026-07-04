from __future__ import annotations

from pathlib import Path
from typing import Any

import vdf  # type: ignore


def load_vdf(path: Path) -> dict[str, Any]:
    """Returns the parsed contents of a text VDF file."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return vdf.load(f)


def load_binary_vdf(path: Path) -> dict[str, Any]:
    """Returns the parsed contents of a binary VDF file."""
    with open(path, 'rb') as f:
        return vdf.binary_load(f)
