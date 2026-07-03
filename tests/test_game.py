from pathlib import Path
from unittest.mock import Mock, patch

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


def test_icon_returns_first_non_asset_file(game):
    header = Mock(spec=Path)
    header.name = "header.jpg"
    header.is_file.return_value = True

    icon = Mock(spec=Path)
    icon.name = "icon_hash.ico"
    icon.is_file.return_value = True

    with patch.object(Path, "iterdir", return_value=[header, icon]):
        assert game.icon == icon


def test_icon_returns_none_when_no_valid_icon(game):
    header = Mock(spec=Path)
    header.name = "header.jpg"
    header.is_file.return_value = True

    logo = Mock(spec=Path)
    logo.name = "logo.png"
    logo.is_file.return_value = True

    with patch.object(Path, "iterdir", return_value=[header, logo]):
        assert game.icon is None


def test_icon_prefers_sha1_named_jpg(game):
    """Steam names icons after the SHA-1 of the file contents; prefer that over strays."""
    stray = Mock(spec=Path)
    stray.name = "leftover.tmp"
    stray.is_file.return_value = True

    icon = Mock(spec=Path)
    icon.name = "0f3e42a397a4bc4ded83f92cbcd4d0eeeb926a09.jpg"
    icon.is_file.return_value = True

    with patch.object(Path, "iterdir", return_value=[stray, icon]):
        assert game.icon == icon


def test_icon_falls_back_to_first_non_asset_file(game):
    """Without a SHA-1-named jpg (older layouts), the first non-asset file wins."""
    header = Mock(spec=Path)
    header.name = "header.jpg"
    header.is_file.return_value = True

    icon = Mock(spec=Path)
    icon.name = "game.ico"
    icon.is_file.return_value = True

    with patch.object(Path, "iterdir", return_value=[header, icon]):
        assert game.icon == icon


def test_icon_is_cached(game):
    icon = Mock(spec=Path)
    icon.name = "icon_hash.ico"
    icon.is_file.return_value = True

    with patch.object(Path, "iterdir", return_value=[icon]) as mock_iterdir:
        first_icon = game.icon
        second_icon = game.icon

    assert first_icon == icon
    assert second_icon == icon
    assert mock_iterdir.call_count == 1


def test_icon_missing_asset_directory_is_cached(game):
    """A missing asset dir yields None and is not re-scanned on later access."""
    with patch.object(Path, "iterdir", side_effect=FileNotFoundError) as mock_iterdir:
        assert game.icon is None
        assert game.icon is None

    assert mock_iterdir.call_count == 1


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
