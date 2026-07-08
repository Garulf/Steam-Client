from __future__ import annotations
import re
from functools import cached_property
from pathlib import Path
from typing import Any

from . import commands
from .app import App
from .vdf_file import load_vdf


UNKNOWN_GAME_NAME = 'UNKNOWN'

HEADER = 'header.jpg'
LIBRARY_HEADER = 'library_header.jpg'
LIBRARY_600X900 = 'library_600x900.jpg'
LIBRARY_HERO = 'library_hero.jpg'
LIBRARY_HERO_BLUR = 'library_hero_blur.jpg'
LOGO = 'logo.png'

# Steam names icons after the SHA-1 hash of the file's own contents.
ICON_NAME_PATTERN = re.compile(r'^[0-9a-f]{40}\.jpg$')


def _find_asset(asset_dir: Path, *names: str) -> Path | None:
    """Locates an asset by name within the asset directory.

    Steam sometimes nests an asset under its own unpredictable hash-named
    subdirectory instead of placing it directly in the asset directory, so
    each immediate subdirectory is checked too.
    """
    for name in names:
        path = asset_dir / name
        if path.is_file():
            return path
    try:
        entries = list(asset_dir.iterdir())
    except (FileNotFoundError, NotADirectoryError):
        return None
    for entry in entries:
        if not entry.is_dir():
            continue
        for name in names:
            path = entry / name
            if path.is_file():
                return path
    return None


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

        Steam names the icon after the SHA-1 hash of its own contents.
        """
        try:
            files = self.asset_dir.iterdir()
        except (FileNotFoundError, NotADirectoryError):
            return None
        return next((f for f in files if ICON_NAME_PATTERN.match(f.name)), None)

    @cached_property
    def header(self) -> Path | None:
        """Returns the path to the header image."""
        return _find_asset(self.asset_dir, HEADER, LIBRARY_HEADER)

    @cached_property
    def grid(self) -> Path | None:
        """Returns the path to the 600x900 grid image."""
        return _find_asset(self.asset_dir, LIBRARY_600X900)

    @cached_property
    def hero(self) -> Path | None:
        """Returns the path to the hero image."""
        return _find_asset(self.asset_dir, LIBRARY_HERO)

    @cached_property
    def hero_blur(self) -> Path | None:
        """Returns the path to the blurred hero image."""
        return _find_asset(self.asset_dir, LIBRARY_HERO_BLUR)

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
