from pathlib import Path

import pytest

from steam_client import SteamNotFoundError
from steam_client.library import Library
from steam_client.steam import Steam, WIN_STEAM_PATH


def test_steam_default_path():
    s = Steam()
    assert s.base_path == Path(WIN_STEAM_PATH)


def test_steam_custom_path():
    s = Steam("/custom/path")
    assert s.base_path == Path("/custom/path")


def test_steam_accepts_path_object():
    s = Steam(Path("/custom/path"))
    assert s.base_path == Path("/custom/path")


def test_steam_repr():
    s = Steam("/custom/path")
    assert repr(s) == f"Steam(base_path={str(s.base_path)!r})"


def test_app_cache(steam):
    assert steam.app_cache == Path("/fake/steam/appcache")


def test_user_data(steam):
    assert steam.user_data == Path("/fake/steam/userdata")


def test_library_folders_file(steam):
    assert steam.library_folders_file == Path("/fake/steam/config/libraryfolders.vdf")


def test_library_cache_is_inside_app_cache(steam):
    assert steam.library_cache == steam.app_cache / "librarycache"


def test_library_property(steam):
    assert isinstance(steam.library, Library)


def test_users_raise_steam_not_found_when_missing(steam):
    with pytest.raises(SteamNotFoundError):
        steam.users
