import dataclasses
import zlib
from pathlib import Path

import pytest

from steam_client.shortcut import SHORTCUT_TAIL, SHORTCUT_TOP_BIT, TOP32_SHIFT, Shortcut


@pytest.fixture
def shortcut(login_user, shortcut_data):
    return Shortcut(login_user, shortcut_data)


def test_shortcut_name(shortcut):
    assert shortcut.name == "Test Game"


def test_shortcut_appid_is_string(shortcut):
    assert isinstance(shortcut.appid, str)


def test_shortcut_appid_matches_stored_appid(shortcut, shortcut_data):
    expected = ((int(shortcut_data.appid) & 0xFFFFFFFF) << TOP32_SHIFT) | SHORTCUT_TAIL
    assert shortcut.appid == str(expected)


def test_shortcut_appid_generated_by_crc32_when_not_stored(login_user, shortcut_data):
    """Old shortcuts.vdf files store no appid; Steam generates it from Exe + AppName."""
    data = dataclasses.replace(shortcut_data, appid=0)
    shortcut = Shortcut(login_user, data)
    # zlib.crc32 is an independent implementation of the CRC-32 Steam uses.
    crc = zlib.crc32((data.Exe + data.AppName).encode())
    expected = ((crc | SHORTCUT_TOP_BIT) << TOP32_SHIFT) | SHORTCUT_TAIL
    assert shortcut.appid == str(expected)


def test_shortcut_short_id(shortcut):
    assert shortcut._short_id == str(int(shortcut.appid) >> TOP32_SHIFT)


def test_shortcut_icon_uses_data_icon(shortcut, shortcut_data):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(Path, "is_file", lambda *_: True)
        assert shortcut.icon == Path(shortcut_data.icon)


def test_shortcut_icon_falls_back_to_grid_icon_when_data_icon_missing(shortcut, login_user):
    grid_icon = login_user.grid_path / f"{shortcut._short_id}_icon.png"
    with pytest.MonkeyPatch.context() as m:
        m.setattr(Path, "is_file", lambda self: self == grid_icon)
        assert shortcut.icon == grid_icon


def test_shortcut_icon_falls_back_to_exe_when_no_icon_exists(shortcut, shortcut_data):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(Path, "is_file", lambda *_: False)
        assert shortcut.icon == Path(shortcut_data.Exe)


def test_shortcut_icon_exe_fallback_strips_quotes(login_user, shortcut_data):
    data = dataclasses.replace(shortcut_data, Exe='"/path/to/game.exe"')
    shortcut = Shortcut(login_user, data)
    with pytest.MonkeyPatch.context() as m:
        m.setattr(Path, "is_file", lambda *_: False)
        assert shortcut.icon == Path("/path/to/game.exe")


def test_shortcut_header(shortcut, login_user):
    assert shortcut.header == login_user.grid_path / f"{shortcut._short_id}.png"


def test_shortcut_grid(shortcut, login_user):
    assert shortcut.grid == login_user.grid_path / f"{shortcut._short_id}p.png"


def test_shortcut_hero(shortcut, login_user):
    assert shortcut.hero == login_user.grid_path / f"{shortcut._short_id}_hero.png"


def test_shortcut_repr(shortcut):
    r = repr(shortcut)
    assert "Shortcut" in r
    assert "Test Game" in r
