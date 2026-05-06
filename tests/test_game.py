from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from steam_client.game import SteamGame, UNKNOWN_GAME_NAME

LIBRARY_PATH = "/library"
APPID = "12345"


@pytest.fixture
def game(steam):
    return SteamGame(steam, LIBRARY_PATH, APPID)


def test_game_appid(game):
    assert game.appid == APPID


def test_game_repr(game, steam):
    r = repr(game)
    assert APPID in r
    assert LIBRARY_PATH in r


def test_manifest_path(game):
    assert game.manifest_path == Path(LIBRARY_PATH) / "steamapps" / f"appmanifest_{APPID}.acf"


def test_asset_dir(game):
    assert game.asset_dir == Path("/fake/steam/appcache/librarycache") / APPID


def test_header(game):
    assert game.header == Path("/fake/steam/appcache/librarycache") / f"{APPID}_header.jpg"


def test_grid(game):
    assert game.grid == Path("/fake/steam/appcache/librarycache") / f"{APPID}_library_600x900.jpg"


def test_hero(game):
    assert game.hero == Path("/fake/steam/appcache/librarycache") / f"{APPID}_library_hero.jpg"


def test_hero_blur(game):
    assert game.hero_blur == Path("/fake/steam/appcache/librarycache") / f"{APPID}_library_hero_blur.jpg"


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


def test_game_name_from_manifest(game):
    game.__dict__["_manifest"] = {"AppState": {"name": "Portal 2"}}
    assert game.name == "Portal 2"


def test_game_name_unknown_when_manifest_missing_key(game):
    game.__dict__["_manifest"] = {}
    assert game.name == UNKNOWN_GAME_NAME


def test_game_name_unknown_when_manifest_empty(game):
    game.__dict__["_manifest"] = {"AppState": {}}
    assert game.name == UNKNOWN_GAME_NAME
