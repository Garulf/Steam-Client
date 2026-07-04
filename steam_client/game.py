from __future__ import annotations
import os
import re
from functools import cached_property
from pathlib import Path
from typing import Any

from . import commands
from .app import App
from .vdf_file import load_vdf


UNKNOWN_GAME_NAME = 'UNKNOWN'

HEADER = 'header.jpg'
LIBRARY_600X900 = 'library_600x900.jpg'
LIBRARY_HERO = 'library_hero.jpg'
LIBRARY_HERO_BLUR = 'library_hero_blur.jpg'
LOGO = 'logo.png'

ASSETS = frozenset({
    HEADER,
    LIBRARY_600X900,
    LIBRARY_HERO,
    LIBRARY_HERO_BLUR,
    LOGO
})

# Steam names icons after the SHA-1 hash of the file's own contents.
ICON_NAME_PATTERN = re.compile(r'^[0-9a-f]{40}\.jpg$')


class Game(App):
    """Represents a Steam game."""

    def __init__(self, library_cache_path: Path, library_path: str, appid: str):
        self._library_cache_path = Path(library_cache_path)
        self.library_path = library_path
        self._appid = appid

    def __repr__(self) -> str:
        return (
            f'Game(library_cache_path={self._library_cache_path!r}, '
            f'library_path={self.library_path!r}, '
            f'appid={self.appid!r})'
        )

    @property
    def asset_dir(self) -> Path:
        """Returns the path to the game's asset directory."""
        return self._library_cache_path / self.appid

    @cached_property
    def icon(self) -> Path | None:
        """Returns the path to the icon image.

        Prefers a SHA-1-named jpg (Steam's icon naming scheme), falling back
        to the first file that is not a known asset for older layouts.
        """
        fallback: Path | None = None
        try:
            with os.scandir(self.asset_dir) as entries:
                for entry in entries:
                    if not entry.is_file():
                        continue
                    if ICON_NAME_PATTERN.match(entry.name):
                        return Path(entry.path)
                    if fallback is None and entry.name not in ASSETS:
                        fallback = Path(entry.path)
        except (FileNotFoundError, NotADirectoryError):
            return None
        return fallback

    @property
    def header(self) -> Path:
        """Returns the path to the header image."""
        return self.asset_dir / HEADER

    @property
    def grid(self) -> Path:
        """Returns the path to the 600x900 grid image."""
        return self.asset_dir / LIBRARY_600X900

    @property
    def hero(self) -> Path:
        """Returns the path to the hero image."""
        return self.asset_dir / LIBRARY_HERO

    @property
    def hero_blur(self) -> Path:
        """Returns the path to the blurred hero image."""
        return self.asset_dir / LIBRARY_HERO_BLUR

    @property
    def manifest_path(self) -> Path:
        """Returns the path to the game's appmanifest."""
        return Path(self.library_path) / 'steamapps' / f'appmanifest_{self.appid}.acf'

    @cached_property
    def _manifest(self) -> dict[str, Any]:
        """Returns the data from the game's appmanifest."""
        try:
            return load_vdf(self.manifest_path)
        except FileNotFoundError:
            return {}

    @cached_property
    def name(self) -> str:
        """Returns the name of the game."""
        try:
            return self._manifest['AppState']['name']
        except KeyError:
            return UNKNOWN_GAME_NAME

    @property
    def appid(self) -> str:
        """Returns the app ID."""
        return self._appid

    def open_store_page(self) -> None:
        """Opens the game's store page in the Steam client."""
        commands.store(self.appid)

    def install(self) -> None:
        """Installs the game."""
        commands.install(self.appid)

    def uninstall(self) -> None:
        """Uninstalls the game."""
        commands.uninstall(self.appid)
