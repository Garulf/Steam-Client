from pathlib import Path
from unittest.mock import MagicMock
import pytest

import pycrc.algorithms as crc

from steam_client.shortcut import Shortcut


@pytest.fixture
def shortcut(steam, login_user, shortcut_entry):
    return Shortcut(steam, login_user, shortcut_entry)


def _compute_appid(exe: str, appname: str) -> str:
    algorithm = crc.Crc(
        width=32,
        poly=0x04C11DB7,
        reflect_in=True,
        xor_in=0xFFFFFFFF,
        reflect_out=True,
        xor_out=0xFFFFFFFF,
    )
    input_string = exe + appname
    top_32 = algorithm.bit_by_bit(input_string) | 0x80000000
    full_64 = (top_32 << 32) | 0x02000000
    return str(full_64)


def test_shortcut_name(shortcut):
    assert shortcut.name == "Test Game"


def test_shortcut_appid_is_string(shortcut):
    assert isinstance(shortcut.appid, str)


def test_shortcut_appid_matches_crc(shortcut, shortcut_entry):
    expected = _compute_appid(shortcut_entry["exe"], shortcut_entry["appname"])
    assert shortcut.appid == expected


def test_shortcut_short_id(shortcut):
    expected = str(int(shortcut.appid) >> 32)
    assert shortcut._short_id() == expected


def test_shortcut_icon_uses_data_icon(shortcut, shortcut_entry):
    assert shortcut.icon == Path(shortcut_entry["icon"])


def test_shortcut_header(shortcut, login_user):
    short_id = shortcut._short_id()
    assert shortcut.header == login_user.grid_path / f"{short_id}.png"


def test_shortcut_grid(shortcut, login_user):
    short_id = shortcut._short_id()
    assert shortcut.grid == login_user.grid_path / f"{short_id}p.png"


def test_shortcut_hero(shortcut, login_user):
    short_id = shortcut._short_id()
    assert shortcut.hero == login_user.grid_path / f"{short_id}_hero.png"


def test_shortcut_repr(shortcut):
    r = repr(shortcut)
    assert "Shortcut" in r
    assert "Test Game" in r
