from __future__ import annotations
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

import pycrc.algorithms as crc  # type: ignore

if TYPE_CHECKING:
    from .login_users import LoginUser

from .app import App


CRC_WIDTH = 32
CRC_POLY = 0x04C11DB7
CRC_XOR_IN = 0xFFFFFFFF
CRC_XOR_OUT = 0xFFFFFFFF
SHORTCUT_TOP_BIT = 0x80000000
SHORTCUT_TAIL = 0x02000000
TOP32_SHIFT = 32

CRC32_ALGORITHM = crc.Crc(
    width=CRC_WIDTH,
    poly=CRC_POLY,
    reflect_in=True,
    xor_in=CRC_XOR_IN,
    reflect_out=True,
    xor_out=CRC_XOR_OUT,
)


class ShortcutEntry(TypedDict):
    appid: int
    AppName: str
    Exe: str
    StartDir: str
    LaunchOptions: str
    icon: str
    tags: dict[str, str]


class Shortcut(App):
    """Represents a Non-Steam Game shortcut."""

    def __init__(self, user: LoginUser, data: ShortcutEntry):
        self._data = data
        self._user = user

    def __repr__(self) -> str:
        return f'Shortcut(data={self._data!r})'

    @property
    def name(self) -> str:
        """Returns the shortcut's name."""
        return self._data["AppName"]

    @cached_property
    def appid(self) -> str:
        """Returns the shortcut's generated 64-bit app ID."""
        stored_appid = self._data["appid"]
        top_32 = int(stored_appid) & 0xFFFFFFFF
        full_64 = (top_32 << TOP32_SHIFT) | SHORTCUT_TAIL
        return str(full_64)


    @property
    def _short_id(self) -> str:
        """
        Returns the Steam shortened App ID.
        This is primarily used for shortcuts in the grid.
        """
        return str(int(self.appid) >> TOP32_SHIFT)

    @property
    def icon(self) -> Path:
        """Returns the path to the icon image."""
        icon_path = self._data["icon"]
        if icon_path and Path(icon_path).is_file():
            return Path(icon_path)
        return self._user.grid_path / f"{self._short_id}_icon.png"

    @property
    def header(self) -> Path:
        """Returns the path to the header image."""
        return self._user.grid_path / f"{self._short_id}.png"

    @property
    def grid(self) -> Path:
        """Returns the path to the grid image."""
        return self._user.grid_path / f"{self._short_id}p.png"

    @property
    def hero(self) -> Path:
        """Returns the path to the hero image."""
        return self._user.grid_path / f"{self._short_id}_hero.png"
