from __future__ import annotations
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from .exceptions import SteamNotFoundError
from .shortcut import Shortcut
from .shortcuts import Shortcuts
from .vdf_file import load_vdf

STEAM64_OFFSET = 76561197960265728


@dataclass
class UserData:
    """User fields mirrored from loginusers.vdf (names keep Valve's casing)."""
    AccountName: str = ''
    PersonaName: str = ''
    RememberPassword: str = '0'
    WantsOfflineMode: str = '0'
    SkipOfflineModeWarning: str = '0'
    AllowAutoLogin: str = '0'
    MostRecent: str = '0'
    Timestamp: str = '0'

    @classmethod
    def from_vdf(cls, data: dict[str, Any]) -> UserData:
        """Builds UserData from a raw loginusers.vdf entry, ignoring unknown keys."""
        known_fields = {field.name for field in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in known_fields})


@dataclass
class User:
    id: int
    data: UserData


class LoginUser:
    """Represents a current or previous logged in Steam user."""

    def __init__(self, base_path: str | Path, user: User):
        self._base_path = Path(base_path)
        self.user = user

    @property
    def is_most_recent(self) -> bool:
        """Returns whether the user is the most recently logged in user."""
        return self.user.data.MostRecent == '1'

    @property
    def account_id(self) -> int:
        """Returns the account ID (the lower 32 bits of the user's SteamID64)."""
        return int(self.user.id) - STEAM64_OFFSET

    @property
    def user_data_dir(self) -> Path:
        """Returns the path to the user's userdata folder."""
        return self._base_path / 'userdata' / str(self.account_id)

    @property
    def config(self) -> Path:
        """Returns the path to the user's config folder."""
        return self.user_data_dir / 'config'

    @property
    def shortcuts_file(self) -> Path:
        """Returns the path to the shortcuts.vdf file."""
        return self.config / 'shortcuts.vdf'

    @property
    def grid_path(self) -> Path:
        """Returns the path to the user's shortcut grid images."""
        return self.config / 'grid'

    def shortcuts(self) -> list[Shortcut]:
        """Returns the user's Non-Steam shortcuts; empty if none have been created."""
        try:
            data = Shortcuts.load(self.shortcuts_file)
        except FileNotFoundError:
            return []
        return [Shortcut(self, entry) for entry in data.shortcuts]


class LoginUsers:
    """Represents the loginusers.vdf file."""

    def __init__(self, base_path: str | Path):
        self._base_path = Path(base_path)

    @property
    def _path(self) -> Path:
        """Returns the path to the loginusers.vdf file."""
        return self._base_path / 'config' / 'loginusers.vdf'

    def users(self) -> list[LoginUser]:
        """Returns the users from the loginusers.vdf file."""
        try:
            login_users = load_vdf(self._path)
        except FileNotFoundError as error:
            raise SteamNotFoundError(
                f'No Steam login data found at {self._base_path}'
            ) from error
        return [
            LoginUser(self._base_path, User(int(user_id), UserData.from_vdf(user_data)))
            for user_id, user_data in login_users['users'].items()
        ]

    def most_recent_user(self) -> LoginUser | None:
        """Returns the most recently logged in user."""
        return next((user for user in self.users() if user.is_most_recent), None)
