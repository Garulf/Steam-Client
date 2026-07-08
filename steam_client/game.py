from __future__ import annotations
import hashlib
from functools import cached_property
from pathlib import Path
from typing import Any

from . import commands
from .app import App
from .vdf_file import load_binary_vdf, load_vdf


UNKNOWN_GAME_NAME = 'UNKNOWN'

# Field keys used by Steam's assetscache.vdf for each cached asset's
# relative path (which may include a hash-named subdirectory prefix).
_GRID_FIELD = '0f'
_HERO_FIELD = '1f'
_HEADER_FIELD = '3f'
_ICON_FIELD = '4f'
_HERO_BLUR_FIELD = '5f'

_asset_manifest_cache: dict[Path, tuple[str, dict[str, dict[str, str]]]] = {}


def _hash_file(path: Path) -> str:
    """Returns the MD5 hash of a file's contents."""
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def _load_asset_manifest(library_cache_path: Path) -> dict[str, dict[str, str]]:
    """Parses assetscache.vdf, mapping appid to its asset field paths.

    Steam records the resolved relative path (including any hash-named
    subdirectory prefix) for each cached asset there, so it's the
    authoritative source rather than guessing filenames on disk. Reparsed
    only when the file's contents change.
    """
    path = library_cache_path / 'assetscache.vdf'
    try:
        current_hash = _hash_file(path)
    except FileNotFoundError:
        return {}
    cached = _asset_manifest_cache.get(library_cache_path)
    if cached is not None and cached[0] == current_hash:
        return cached[1]
    data = load_binary_vdf(path)
    # The top-level keys are not always formatted the same way, so grab the
    # first dict value at each level generically rather than by name.
    root = data[next(iter(data))]
    apps = next(value for value in root.values() if isinstance(value, dict))
    _asset_manifest_cache[library_cache_path] = (current_hash, apps)
    return apps


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

    def _manifest_asset(self, field: str) -> Path | None:
        """Returns the path to an asset recorded in assetscache.vdf, if any."""
        entry = _load_asset_manifest(self._library_cache_path).get(self.appid)
        if entry is None:
            return None
        relative_path = entry.get(field)
        if relative_path is None:
            return None
        return self.asset_dir / relative_path

    @cached_property
    def icon(self) -> Path | None:
        """Returns the path to the icon image."""
        return self._manifest_asset(_ICON_FIELD)

    @cached_property
    def header(self) -> Path | None:
        """Returns the path to the header image."""
        return self._manifest_asset(_HEADER_FIELD)

    @cached_property
    def grid(self) -> Path | None:
        """Returns the path to the 600x900 grid image."""
        return self._manifest_asset(_GRID_FIELD)

    @cached_property
    def hero(self) -> Path | None:
        """Returns the path to the hero image."""
        return self._manifest_asset(_HERO_FIELD)

    @cached_property
    def hero_blur(self) -> Path | None:
        """Returns the path to the blurred hero image."""
        return self._manifest_asset(_HERO_BLUR_FIELD)

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
