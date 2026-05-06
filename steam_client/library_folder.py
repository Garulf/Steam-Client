from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .steam import Steam
from .game import SteamGame


@dataclass
class LibraryFolder:
    """Represents a Steam library folder."""
    _steam: Steam
    path: str
    apps: List[str]

    def get_games(self) -> List[SteamGame]:
        return [SteamGame(self._steam, self.path, appid) for appid in self.apps]
