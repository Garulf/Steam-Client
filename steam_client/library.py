from __future__ import annotations
import hashlib
from typing import TYPE_CHECKING, Iterator

from .exceptions import SteamNotFoundError
from .game import Game
from .library_folder import LibraryFolder
from .shortcut import Shortcut
from .vdf_file import load_vdf

if TYPE_CHECKING:
    from .steam import Steam


class Library:
    """Represents the Steam library."""

    def __init__(self, steam: Steam):
        self._steam = steam
        self._libraries_hash: str | None = None
        self._libraries: list[LibraryFolder] = []

    def _hash_library_folders_file(self) -> str:
        """Returns the MD5 hash of the libraryfolders.vdf file."""
        with open(self._steam.library_folders_file, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _load_library_folders(self) -> list[LibraryFolder]:
        """Parses libraryfolders.vdf into LibraryFolder objects."""
        data = load_vdf(self._steam.library_folders_file)
        # The top-level key is not always formatted the same way, so grab the first key.
        folders = data[next(iter(data))]
        return [
            LibraryFolder(self._steam.library_cache, folder["path"], folder["apps"])
            for folder in folders.values()
        ]

    def libraries(self) -> Iterator[LibraryFolder]:
        """Yields the Steam library folders, reparsing the file only when it changes."""
        try:
            current_hash = self._hash_library_folders_file()
        except FileNotFoundError as error:
            raise SteamNotFoundError(
                f'No Steam library found at {self._steam.base_path}'
            ) from error
        if current_hash != self._libraries_hash:
            self._libraries = self._load_library_folders()
            self._libraries_hash = current_hash
        yield from self._libraries

    def games(self) -> Iterator[Game]:
        """Yields the games from the Steam library."""
        for library in self.libraries():
            yield from library.games()

    def game_by_id(self, appid: str) -> Game | None:
        """Returns the game with the specified ID."""
        return next((game for game in self.games() if game.appid == appid), None)

    def game_by_name(self, name: str) -> Game | None:
        """Returns the game with the specified name (case-insensitive)."""
        return next(
            (game for game in self.games() if game.name.casefold() == name.casefold()),
            None,
        )

    def shortcuts(self) -> Iterator[Shortcut]:
        """Yields the Non-Steam shortcuts from the Steam library."""
        for user in self._steam.users:
            yield from user.shortcuts()

    def all_apps(self) -> Iterator[Game | Shortcut]:
        """Yields all the games and shortcuts from the Steam library."""
        yield from self.games()
        yield from self.shortcuts()
