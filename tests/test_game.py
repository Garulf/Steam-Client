from pathlib import Path
from unittest.mock import patch

import pytest

import steam_client.game as game_module
from steam_client.game import (
    Game,
    UNKNOWN_GAME_NAME,
)

LIBRARY_PATH = "/library"
APPID = "12345"
LIBRARY_CACHE_PATH = Path("/fake/steam/appcache/librarycache")


@pytest.fixture
def game():
    return Game(LIBRARY_CACHE_PATH, LIBRARY_PATH, APPID)


@pytest.fixture(autouse=True)
def clear_asset_manifest_cache():
    game_module._asset_manifest_cache.clear()
    yield
    game_module._asset_manifest_cache.clear()


def fake_manifest(apps):
    """Builds a fake assetscache.vdf parse result, shaped like the real one:
    an unnamed top-level key wrapping cache_version/last_cleanup_time/apps."""
    return {'': {'cache_version': 2, 'last_cleanup_time': 0, '0': apps}}


def patch_manifest(apps, file_hash="hash1"):
    """Patches the manifest-loading boundary functions with fake data."""
    return (
        patch.object(game_module, "_hash_file", return_value=file_hash),
        patch.object(game_module, "load_binary_vdf", return_value=fake_manifest(apps)),
    )


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


def test_header_returns_path_from_manifest(game):
    hash_patch, load_patch = patch_manifest({APPID: {'3f': 'header.jpg'}})
    with hash_patch, load_patch:
        assert game.header == LIBRARY_CACHE_PATH / APPID / 'header.jpg'


def test_header_resolves_nested_hash_subdir_path(game):
    """Steam sometimes nests an asset under its own hash-named subdirectory;
    assetscache.vdf records that prefix directly in the relative path."""
    hash_patch, load_patch = patch_manifest(
        {APPID: {'3f': 'b91f57c06260776c04648d061aba6e8de494ef59/library_header.jpg'}}
    )
    with hash_patch, load_patch:
        assert game.header == (
            LIBRARY_CACHE_PATH / APPID / 'b91f57c06260776c04648d061aba6e8de494ef59/library_header.jpg'
        )


def test_header_returns_none_when_field_missing(game):
    hash_patch, load_patch = patch_manifest({APPID: {'0f': 'library_600x900.jpg'}})
    with hash_patch, load_patch:
        assert game.header is None


def test_header_returns_none_when_appid_missing(game):
    hash_patch, load_patch = patch_manifest({})
    with hash_patch, load_patch:
        assert game.header is None


def test_header_returns_none_when_manifest_file_missing(game):
    with patch.object(game_module, "_hash_file", side_effect=FileNotFoundError):
        assert game.header is None


def test_grid_returns_path_from_manifest(game):
    hash_patch, load_patch = patch_manifest({APPID: {'0f': 'library_600x900.jpg'}})
    with hash_patch, load_patch:
        assert game.grid == LIBRARY_CACHE_PATH / APPID / 'library_600x900.jpg'


def test_hero_returns_path_from_manifest(game):
    hash_patch, load_patch = patch_manifest({APPID: {'1f': 'library_hero.jpg'}})
    with hash_patch, load_patch:
        assert game.hero == LIBRARY_CACHE_PATH / APPID / 'library_hero.jpg'


def test_hero_blur_returns_path_from_manifest(game):
    hash_patch, load_patch = patch_manifest({APPID: {'5f': 'library_hero_blur.jpg'}})
    with hash_patch, load_patch:
        assert game.hero_blur == LIBRARY_CACHE_PATH / APPID / 'library_hero_blur.jpg'


def test_icon_returns_path_from_manifest(game):
    icon_name = '0f3e42a397a4bc4ded83f92cbcd4d0eeeb926a09.jpg'
    hash_patch, load_patch = patch_manifest({APPID: {'4f': icon_name}})
    with hash_patch, load_patch:
        assert game.icon == LIBRARY_CACHE_PATH / APPID / icon_name


def test_icon_returns_none_when_no_icon_field(game):
    hash_patch, load_patch = patch_manifest({APPID: {'3f': 'header.jpg'}})
    with hash_patch, load_patch:
        assert game.icon is None


def test_manifest_reparsed_only_when_file_changes(game):
    hash_patch, load_patch = patch_manifest({APPID: {'3f': 'header.jpg'}})
    with hash_patch, load_patch as mock_load:
        first = game.header
        second = game.header

    assert first == second
    # header is a cached_property, so a single access only calls load once
    # regardless; verify the manifest cache itself is keyed on the file hash.
    assert mock_load.call_count == 1

    other_game = Game(LIBRARY_CACHE_PATH, LIBRARY_PATH, APPID)
    # Same file hash as before but different (stale) manifest contents: a
    # cache hit should keep serving the manifest parsed above, not this one.
    hash_patch2, load_patch2 = patch_manifest(
        {APPID: {'3f': 'library_header.jpg'}}, file_hash="hash1"
    )
    with hash_patch2, load_patch2 as mock_load2:
        assert other_game.header == LIBRARY_CACHE_PATH / APPID / 'header.jpg'
        assert mock_load2.call_count == 0


def test_manifest_reparsed_when_file_hash_changes(game):
    hash_patch, load_patch = patch_manifest({APPID: {'3f': 'header.jpg'}}, file_hash="hash1")
    with hash_patch, load_patch:
        assert game.header == LIBRARY_CACHE_PATH / APPID / 'header.jpg'

    other_game = Game(LIBRARY_CACHE_PATH, LIBRARY_PATH, APPID)
    hash_patch2, load_patch2 = patch_manifest(
        {APPID: {'3f': 'library_header.jpg'}}, file_hash="hash2"
    )
    with hash_patch2, load_patch2 as mock_load2:
        assert other_game.header == LIBRARY_CACHE_PATH / APPID / 'library_header.jpg'
        assert mock_load2.call_count == 1


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
