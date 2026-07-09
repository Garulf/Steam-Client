from pathlib import Path

import pytest

from steam_client.shortcut import SHORTCUT_TAIL, TOP32_SHIFT, Shortcut


@pytest.fixture
def shortcut(login_user, shortcut_entry):
    return Shortcut(login_user, shortcut_entry)


def test_shortcut_name(shortcut):
    assert shortcut.name == "Test Game"


def test_shortcut_appid_is_string(shortcut):
    assert isinstance(shortcut.appid, str)


def test_shortcut_appid_matches_stored_appid(shortcut, shortcut_entry):
    expected = ((int(shortcut_entry["appid"]) & 0xFFFFFFFF) << TOP32_SHIFT) | SHORTCUT_TAIL
    assert shortcut.appid == str(expected)


def test_shortcut_short_id(shortcut):
    assert shortcut._short_id == str(int(shortcut.appid) >> TOP32_SHIFT)


def test_shortcut_icon_uses_data_icon(shortcut, shortcut_entry):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(Path, "is_file", lambda *_: True)
        assert shortcut.icon == Path(shortcut_entry["icon"])


def test_shortcut_icon_falls_back_to_grid_icon_when_data_icon_missing(shortcut, login_user):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(Path, "is_file", lambda *_: False)
        assert shortcut.icon == login_user.grid_path / f"{shortcut._short_id}_icon.png"


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
