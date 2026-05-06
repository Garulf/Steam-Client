from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Dict
from typing import TypedDict

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
SHORT_ID_SHIFT = 32

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
    appname: str
    exe: str
    StartDir: str
    LaunchOptions: str
    icon: str
    tags: Dict[str, str]


class Shortcut(App):
    """Represents a Non-Steam Game shortcut."""

    def __init__(self, user: LoginUser, data: ShortcutEntry):
        self._data = data
        self._user = user
        super().__init__()

    def __repr__(self) -> str:
        return f'Shortcut(data={self._data.__repr__()})'

    @property
    def name(self) -> str:
        return self._data["appname"]

    @property
    def appid(self) -> str:
        input_string = self._data["exe"] + self._data["appname"]
        top_32 = CRC32_ALGORITHM.bit_by_bit(input_string) | SHORTCUT_TOP_BIT
        full_64 = (top_32 << SHORT_ID_SHIFT) | SHORTCUT_TAIL
        return str(full_64)

    def _short_id(self) -> str:
        """
        Return Steam shortened App ID.
        This is primarily used for shortcuts in the grid.
        """
        return str(int(self.appid) >> SHORT_ID_SHIFT)

    @property
    def icon(self) -> Path:
        icon_path = self._data["icon"]
        if icon_path and Path(icon_path).is_file():
            return Path(icon_path)
        return self._user.grid_path.joinpath(f"{self._short_id()}_icon.png")

    @property
    def header(self) -> Path:
        return self._user.grid_path.joinpath(f"{self._short_id()}.png")

    @property
    def grid(self) -> Path:
        return self._user.grid_path.joinpath(f"{self._short_id()}p.png")

    @property
    def hero(self) -> Path:
        return self._user.grid_path.joinpath(f"{self._short_id()}_hero.png")
