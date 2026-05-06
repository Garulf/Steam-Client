from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .game import Game


@dataclass
class LibraryFolder:
    """Represents a Steam library folder."""
    library_cache_path: Path
    path: str
    apps: List[str]

    def get_games(self) -> List[Game]:
        return [Game(self.library_cache_path, self.path, appid) for appid in self.apps]
