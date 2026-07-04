from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .game import Game


@dataclass
class LibraryFolder:
    """Represents a Steam library folder."""
    library_cache_path: Path
    path: str
    apps: Iterable[str]

    def games(self) -> list[Game]:
        """Returns the games installed in this library folder."""
        return [Game(self.library_cache_path, self.path, appid) for appid in self.apps]
