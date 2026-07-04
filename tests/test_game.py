from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from steam_client.game import (
    Game,
    UNKNOWN_GAME_NAME,
    HEADER,
    LIBRARY_600X900,
    LIBRARY_HERO,
    LIBRARY_HERO_BLUR,
)

LIBRARY_PATH = "/library"
APPID = "12345"
LIBRARY_CACHE_PATH = Path("/fake/steam/appcache/librarycache")


@pytest.fixture
def game():
    return Game(LIBRARY_CACHE_PATH, LIBRARY_PATH, APPID)


def test_game_appid(game):
    assert game.appid == APPID


def test_game_repr(game):
    r = repr(game)
    assert APPID in r
    assert LIBRARY_PATH in r


def test_manifest_path(game):
    assert game.manifest_path == Path(LIBRARY_PATH) / "steamapps" / f"appmanifest_{APPID}.acf"


def test_asset_dir(game):
    assert game.asset_dir == LIBRARY_CACHE_PATH / APPID


def test_header(game):
    assert game.header == LIBRARY_CACHE_PATH / APPID / HEADER


def test_grid(game):
    assert game.grid == LIBRARY_CACHE_PATH / APPID / LIBRARY_600X900


def test_hero(game):
    assert game.hero == LIBRARY_CACHE_PATH / APPID / LIBRARY_HERO


def test_hero_blur(game):
    assert game.hero_blur == LIBRARY_CACHE_PATH / APPID / LIBRARY_HERO_BLUR


def fake_entry(name, is_file=True):
    """Builds a mock os.DirEntry for the game's asset directory."""
    entry = Mock()
    entry.name = name
    entry.path = str(LIBRARY_CACHE_PATH / APPID / name)
    entry.is_file.return_value = is_file
    return entry


def patch_scandir(entries):
    """Patches os.scandir in steam_client.game with the given entries."""
    scandir_cm = MagicMock()
    scandir_cm.__enter__.return_value = iter(entries)
    return patch("steam_client.game.os.scandir", return_value=scandir_cm)


def test_icon_returns_first_non_asset_file(game):
    header = fake_entry("header.jpg")
    icon = fake_entry("icon_hash.ico")

    with patch_scandir([header, icon]):
        assert game.icon == Path(icon.path)


def test_icon_returns_none_when_no_valid_icon(game):
    header = fake_entry("header.jpg")
    logo = fake_entry("logo.png")

    with patch_scandir([header, logo]):
        assert game.icon is None


def test_icon_prefers_sha1_named_jpg(game):
    """Steam names icons after the SHA-1 of the file contents; prefer that over strays."""
    stray = fake_entry("leftover.tmp")
    icon = fake_entry("0f3e42a397a4bc4ded83f92cbcd4d0eeeb926a09.jpg")

    with patch_scandir([stray, icon]):
        assert game.icon == Path(icon.path)


def test_icon_falls_back_to_first_non_asset_file(game):
    """Without a SHA-1-named jpg (older layouts), the first non-asset file wins."""
    header = fake_entry("header.jpg")
    icon = fake_entry("game.ico")

    with patch_scandir([header, icon]):
        assert game.icon == Path(icon.path)


def test_icon_skips_directories(game):
    """Non-file entries (subdirectories) are never treated as icons."""
    subdir = fake_entry("screenshots", is_file=False)
    icon = fake_entry("game.ico")

    with patch_scandir([subdir, icon]):
        assert game.icon == Path(icon.path)


def test_icon_is_cached(game):
    icon = fake_entry("icon_hash.ico")

    with patch_scandir([icon]) as mock_scandir:
        first_icon = game.icon
        second_icon = game.icon

    assert first_icon == Path(icon.path)
    assert second_icon == Path(icon.path)
    assert mock_scandir.call_count == 1


def test_icon_missing_asset_directory_is_cached(game):
    """A missing asset dir yields None and is not re-scanned on later access."""
    with patch("steam_client.game.os.scandir", side_effect=FileNotFoundError) as mock_scandir:
        assert game.icon is None
        assert game.icon is None

    assert mock_scandir.call_count == 1


def test_game_name_from_manifest(game):
    game.__dict__["_manifest"] = {"AppState": {"name": "Portal 2"}}
    assert game.name == "Portal 2"


def test_game_name_unknown_when_manifest_missing_key(game):
    game.__dict__["_manifest"] = {}
    assert game.name == UNKNOWN_GAME_NAME


def test_game_name_unknown_when_manifest_empty(game):
    game.__dict__["_manifest"] = {"AppState": {}}
    assert game.name == UNKNOWN_GAME_NAME


def test_manifest_empty_when_file_missing(game):
    with patch("steam_client.game.load_vdf", side_effect=FileNotFoundError):
        assert game._manifest == {}
        assert game.name == UNKNOWN_GAME_NAME


def test_game_run_opens_steam_uri(game):
    with patch("webbrowser.open") as mock_open:
        game.run()
    mock_open.assert_called_once_with(f"steam://rungameid/{APPID}")


def test_game_open_store_page(game):
    with patch("webbrowser.open") as mock_open:
        game.open_store_page()
    mock_open.assert_called_once_with(f"steam://store/{APPID}")


def test_game_install(game):
    with patch("webbrowser.open") as mock_open:
        game.install()
    mock_open.assert_called_once_with(f"steam://install/{APPID}")


def test_game_uninstall(game):
    with patch("webbrowser.open") as mock_open:
        game.uninstall()
    mock_open.assert_called_once_with(f"steam://uninstall/{APPID}")
