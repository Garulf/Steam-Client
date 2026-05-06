from __future__ import annotations
import functools
from pathlib import Path
from typing import TYPE_CHECKING

import vdf  # type: ignore

if TYPE_CHECKING:
    from .steam import Steam

from .app import App


UNKNOWN_GAME_NAME = 'UNKNOWN'

ASSETS = frozenset({
    "header.jpg",
    "library_600x900.jpg",
    "library_hero.jpg",
    "library_hero_blur.jpg",
    "logo.png"
})


class SteamGame(App):
    """Represents a Steam game."""

    def __init__(self, steam: Steam, library_path: str, appid: str):
        self.library_path = library_path
        self._appid = appid
        self._icon: Path | None = None
        self._name: str | None = None
        super().__init__(steam)

    def __repr__(self) -> str:
        return (
            f'Game(steam={self._steam.__repr__()}, '
            f'library_path={self.library_path.__repr__()}, '
            f'appid={self.appid.__repr__()})'
        )

    @property
    def asset_dir(self) -> Path:
        """Returns the path to the game's asset directory."""
        return Path(self._steam.library_cache).joinpath(self.appid)

    @property
    def icon(self) -> Path | None:
        """Returns the path to the icon image."""
        if self._icon is None:
            self._icon = next(
                (
                    asset
                    for asset in self.asset_dir.iterdir()
                    if asset.is_file() and asset.name not in ASSETS
                ),
                None,
            )
        return self._icon

    @property
    def header(self) -> Path:
        """Returns the path to the header image."""
        return Path(self._steam.library_cache).joinpath(f'{self.appid}_header.jpg')

    @property
    def grid(self) -> Path:
        """Returns the path to the 600x900 grid image."""
        return Path(self._steam.library_cache).joinpath(f'{self.appid}_library_600x900.jpg')

    @property
    def hero(self) -> Path:
        """Returns the path to the hero image."""
        return Path(self._steam.library_cache).joinpath(f'{self.appid}_library_hero.jpg')

    @property
    def hero_blur(self) -> Path:
        """Returns the path to the blurred hero image."""
        return Path(self._steam.library_cache).joinpath(f'{self.appid}_library_hero_blur.jpg')

    @property
    def manifest_path(self) -> Path:
        """Returns the path to the game's appmanifest."""
        return Path(self.library_path).joinpath('steamapps', f'appmanifest_{self.appid}.acf')

    @functools.cached_property
    def _manifest(self) -> dict:
        """Returns the data from the game's appmanifest."""
        try:
            with open(self.manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                manifest = vdf.load(f)
            return manifest
        except FileNotFoundError:
            return {}

    @property
    def name(self) -> str:
        """Returns the name of the game."""
        if self._name is None:
            self._name = self._get_name_from_manifest()
        return self._name

    def _get_name_from_manifest(self) -> str:
        try:
            return self._manifest['AppState']['name']
        except KeyError:
            return UNKNOWN_GAME_NAME

    @property
    def appid(self) -> str:
        """Returns the app ID."""
        return self._appid

    def open_store_page(self):
        """Opens the game's store page in the Steam client."""
        self._commands.store(self.appid)

    def install(self):
        """Installs the game."""
        self._commands.install(self.appid)

    def uninstall(self):
        """Uninstalls the game."""
        self._commands.uninstall(self.appid)
