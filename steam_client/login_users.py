from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from typing import TYPE_CHECKING
from typing import TypedDict

import vdf

if TYPE_CHECKING:
    from steam_client.steam import Steam

from .shortcut import Shortcut

STEAM64_OFFSET = 76561197960265728


class UserData(TypedDict):
    AccountName: str
    PersonaName: str
    RememberPassword: str
    WantsOfflineMode: str
    SkipOfflineModeWarning: str
    AllowAutoLogin: str
    MostRecent: str
    Timestamp: str


UserLoginsFile = Dict[str, Dict[str, UserData]]


class User:
    """Represents a current or previous logged in Steam user."""

    def __init__(self, steam: Steam, steam_id64: str, user_data: UserData):
        self._steam = steam
        self.steam_id64 = steam_id64
        self._user_data = user_data

    def __repr__(self) -> str:
        return f'User(steam={self._steam.__repr__()}, steam_id64={self.steam_id64.__repr__()}, user_data={self._user_data.__repr__()})'

    @property
    def is_most_recent(self) -> bool:
        """Returns whether the user is the most recent user."""
        return self._user_data['MostRecent'] == '1'

    @property
    def steam_id3(self) -> int:
        """Returns the last portion of the user's SteamID3."""
        steamidacct = (int(self.steam_id64) - STEAM64_OFFSET)
        return steamidacct

    @property
    def user_data_dir(self) -> Path:
        """Returns the path to the userdata folder."""
        return Path(self._steam.base_path).joinpath('userdata', str(self.steam_id3))

    @property
    def config(self) -> Path:
        """Returns the path to the config folder."""
        return Path(self.user_data_dir).joinpath('config')

    @property
    def shortcuts_file(self) -> Path:
        """Returns the path to the shortcuts.vdf file."""
        return Path(self.config).joinpath('shortcuts.vdf')

    @property
    def grid_path(self) -> Path:
        """Returns the path to the user's shortcut grid images."""
        return Path(self.user_data_dir).joinpath('config', 'grid')

    def shortcuts(self) -> List[Shortcut]:
        """Returns the data from the shortcuts.vdf file."""
        with open(self.shortcuts_file, 'rb') as f:
            shortcuts = vdf.binary_load(f)
        return [Shortcut(self._steam, self, shortcuts['shortcuts'][shortcut_idx]) for shortcut_idx in shortcuts['shortcuts']]


class LoginUsers:
    """Represents the loginusers.vdf file."""

    def __init__(self, steam: Steam):
        self._steam = steam

    @property
    def _path(self) -> Path:
        """Returns the path to the loginusers.vdf file."""
        return Path(self._steam.base_path).joinpath('config', 'loginusers.vdf')

    def users(self) -> List[User]:
        """Returns the users from the loginusers.vdf file."""
        with open(self._path, 'r', encoding='utf-8', errors='ignore') as f:
            login_users: UserLoginsFile = vdf.load(f)
        return [User(self._steam, steam_id64, user_data) for steam_id64, user_data in login_users['users'].items()]

    def most_recent_user(self) -> Optional[User]:
        """Returns the most recent user from the loginusers.vdf file."""
        return next((user for user in self.users() if user.is_most_recent), None)
