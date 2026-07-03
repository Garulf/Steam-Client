from __future__ import annotations
from pathlib import Path

from .library import Library
from .login_users import LoginUser, LoginUsers

WIN_STEAM_PATH = r"c:\Program Files (x86)\Steam"


class Steam:
    """Represents the Steam client."""

    def __init__(self, base_path: str | Path = WIN_STEAM_PATH):
        self.base_path = Path(base_path)

    def __repr__(self) -> str:
        return f'Steam(base_path={str(self.base_path)!r})'

    @property
    def app_cache(self) -> Path:
        """Returns the path to the appcache folder."""
        return self.base_path / 'appcache'

    @property
    def user_data(self) -> Path:
        """Returns the path to the userdata folder."""
        return self.base_path / 'userdata'

    @property
    def library_folders_file(self) -> Path:
        """Returns the path to the libraryfolders.vdf file."""
        return self.base_path / 'config' / 'libraryfolders.vdf'

    @property
    def library_cache(self) -> Path:
        """Returns the path to the librarycache folder."""
        return self.app_cache / 'librarycache'

    @property
    def users(self) -> list[LoginUser]:
        """Returns the current and previously logged in Steam users."""
        return LoginUsers(self.base_path).users()

    @property
    def library(self) -> Library:
        """Returns the Steam library."""
        return Library(self)
