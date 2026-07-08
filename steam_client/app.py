from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path

from . import commands


class App(ABC):
    """Abstract base class for all Steam apps."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the app's name."""

    @property
    @abstractmethod
    def appid(self) -> str:
        """Returns the app's appid."""

    @property
    @abstractmethod
    def icon(self) -> Path | None:
        """Returns the path to the icon image."""

    @property
    @abstractmethod
    def header(self) -> Path | None:
        """Returns the path to the header image."""

    @property
    @abstractmethod
    def grid(self) -> Path | None:
        """Returns the path to the grid image."""

    @property
    @abstractmethod
    def hero(self) -> Path | None:
        """Returns the path to the hero image."""

    def run(self) -> None:
        """Launches the app in the Steam client."""
        commands.run_game_id(self.appid)
