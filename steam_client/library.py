from __future__ import annotations
import hashlib
from typing import TYPE_CHECKING, List, Optional, Union, Generator

import vdf  # type: ignore

from steam_client.shortcut import Shortcut

if TYPE_CHECKING:
    from .steam import Steam
from .library_folder import LibraryFolder
from .game import Game


class Library:
    """Represents the Steam library."""

    def __init__(self, steam: 'Steam'):
        self._steam = steam
        self._libraries_hash: Optional[str] = None
        self._libraries: List[LibraryFolder] = []

    def _hash_steam_libraries(self) -> str:
        """Returns the MD5 hash of the Steam library folders file."""
        with open(str(self._steam.library_folders), 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _is_updated(self) -> bool:
        """Returns whether the Steam library folders have been updated."""
        return self._libraries_hash != self._hash_steam_libraries()

    def _update_libraries(self):
        """Updates the Steam library folders."""
        with open(self._steam.library_folders, 'r', encoding='utf-8', errors='ignore') as f:
            libraries = vdf.load(f)
        # The is not always formatted the same way, so we grab the first key
        folder_key = list(libraries.keys())[0]
        self._libraries = [LibraryFolder(self._steam.library_cache, libraries[folder_key][item]["path"],
                                         libraries[folder_key][item]["apps"]) for item in libraries[folder_key]]

    def libraries(self) -> Generator[LibraryFolder, None, None]:
        """Returns the Steam library folders."""
        if self._is_updated():
            self._libraries_hash = self._hash_steam_libraries()
            self._update_libraries()
        for library in self._libraries:
            yield library

    def games(self) -> Generator[Game, None, None]:
        """Returns the games from the Steam library."""
        for library in self.libraries():
            for game in library.get_games():
                yield game

    def game_by_id(self, appid: str) -> Optional[Game]:
        """Returns the game with the specified ID."""
        for game in self.games():
            if game.appid == appid:
                return game
        return None

    def game_by_name(self, name: str) -> Optional[Game]:
        """Returns the game with the specified name."""
        for game in self.games():
            if game.name.casefold() == name.casefold():
                return game
        return None

    def shortcuts(self) -> Generator[Shortcut, None, None]:
        """Returns the Non-Steam shortcuts from the Steam library."""
        for user in self._steam.users:
            for shortcut in user.shortcuts():
                yield shortcut

    def all(self) -> Generator[Union[Game, Shortcut], None, None]:
        """Returns all the games and shortcuts from the Steam library."""
        for game in self.games():
            yield game
        for shortcut in self.shortcuts():
            yield shortcut
