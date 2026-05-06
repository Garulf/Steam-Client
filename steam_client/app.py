from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path

from .commands import Commands


class App(ABC):
    """Abstract base class for all Steam apps."""

    def __init__(self):
        self._commands = Commands()

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the app's name."""
        pass

    @property
    @abstractmethod
    def appid(self) -> str:
        """Returns the game's appid."""
        pass

    @property
    @abstractmethod
    def icon(self) -> Path | None:
        """Returns the path to the icon image."""
        pass

    @property
    @abstractmethod
    def header(self) -> Path:
        pass

    @property
    @abstractmethod
    def grid(self) -> Path:
        pass

    @property
    @abstractmethod
    def hero(self) -> Path:
        pass

    def run(self):
        """Launches app with the specified app ID in the Steam client."""
        self._commands.run_game_id(self.appid)
