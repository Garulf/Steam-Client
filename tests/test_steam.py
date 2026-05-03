from pathlib import Path

from steam_client.steam import Steam, WIN_STEAM_PATH


def test_steam_default_path():
    s = Steam()
    assert s.base_path == WIN_STEAM_PATH


def test_steam_custom_path():
    s = Steam("/custom/path")
    assert s.base_path == "/custom/path"


def test_steam_repr():
    s = Steam("/custom/path")
    assert repr(s) == "Steam(base_path='/custom/path')"


def test_app_cache(steam):
    assert steam.app_cache == Path("/fake/steam/appcache")


def test_user_data(steam):
    assert steam.user_data == Path("/fake/steam/userdata")


def test_library_folders(steam):
    assert steam.library_folders == Path("/fake/steam/config/libraryfolders.vdf")


def test_library_cache(steam):
    assert steam.library_cache == Path("/fake/steam/appcache/librarycache")
