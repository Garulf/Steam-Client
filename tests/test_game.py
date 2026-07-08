from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from steam_client.game import (
    Game,
    UNKNOWN_GAME_NAME,
    HEADER,
    LIBRARY_HEADER,
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


def is_file_for(*existing_paths):
    """Returns a Path.is_file replacement that is True only for the given paths."""
    existing = {str(p) for p in existing_paths}

    def _is_file(self):
        return str(self) in existing

    return _is_file


def is_dir_for(*existing_dirs):
    """Returns a Path.is_dir replacement that is True only for the given paths."""
    existing = {str(p) for p in existing_dirs}

    def _is_dir(self):
        return str(self) in existing

    return _is_dir


def dir_listing(mapping):
    """Returns a Path.iterdir replacement, mapping a directory Path to its child Paths."""
    listing = {str(k): v for k, v in mapping.items()}

    def _iterdir(self):
        key = str(self)
        if key not in listing:
            raise FileNotFoundError(key)
        return iter(listing[key])

    return _iterdir


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


def test_header_returns_direct_path_when_present(game):
    header_path = LIBRARY_CACHE_PATH / APPID / HEADER
    with patch.object(Path, "is_file", is_file_for(header_path)):
        assert game.header == header_path


def test_header_falls_back_to_library_header_name(game):
    """Some layouts name the header asset library_header.jpg instead of header.jpg."""
    library_header_path = LIBRARY_CACHE_PATH / APPID / LIBRARY_HEADER
    with patch.object(Path, "is_file", is_file_for(library_header_path)):
        assert game.header == library_header_path


def test_header_falls_back_to_nested_hash_subdir(game):
    """Steam sometimes nests an asset under its own unpredictable hash-named
    subdirectory instead of placing it directly in the asset directory."""
    asset_dir = LIBRARY_CACHE_PATH / APPID
    hash_dir = asset_dir / "b91f57c06260776c04648d061aba6e8de494ef59"
    nested_header = hash_dir / HEADER

    with patch.object(Path, "is_file", is_file_for(nested_header)), \
            patch.object(Path, "is_dir", is_dir_for(hash_dir)), \
            patch.object(Path, "iterdir", dir_listing({asset_dir: [hash_dir]})):
        assert game.header == nested_header


def test_header_returns_none_when_missing(game):
    asset_dir = LIBRARY_CACHE_PATH / APPID
    with patch.object(Path, "is_file", is_file_for()), \
            patch.object(Path, "is_dir", is_dir_for()), \
            patch.object(Path, "iterdir", dir_listing({asset_dir: []})):
        assert game.header is None


def test_grid_returns_direct_path_when_present(game):
    grid_path = LIBRARY_CACHE_PATH / APPID / LIBRARY_600X900
    with patch.object(Path, "is_file", is_file_for(grid_path)):
        assert game.grid == grid_path


def test_grid_falls_back_to_nested_hash_subdir(game):
    asset_dir = LIBRARY_CACHE_PATH / APPID
    hash_dir = asset_dir / "ac2f074d790656a06ef8305bd54a6f64e9a70082"
    nested_grid = hash_dir / LIBRARY_600X900

    with patch.object(Path, "is_file", is_file_for(nested_grid)), \
            patch.object(Path, "is_dir", is_dir_for(hash_dir)), \
            patch.object(Path, "iterdir", dir_listing({asset_dir: [hash_dir]})):
        assert game.grid == nested_grid


def test_hero_returns_direct_path_when_present(game):
    hero_path = LIBRARY_CACHE_PATH / APPID / LIBRARY_HERO
    with patch.object(Path, "is_file", is_file_for(hero_path)):
        assert game.hero == hero_path


def test_hero_falls_back_to_nested_hash_subdir(game):
    asset_dir = LIBRARY_CACHE_PATH / APPID
    hash_dir = asset_dir / "5925343a8312ea07f234d48170963aafae4158bf"
    nested_hero = hash_dir / LIBRARY_HERO

    with patch.object(Path, "is_file", is_file_for(nested_hero)), \
            patch.object(Path, "is_dir", is_dir_for(hash_dir)), \
            patch.object(Path, "iterdir", dir_listing({asset_dir: [hash_dir]})):
        assert game.hero == nested_hero


def test_hero_blur_returns_direct_path_when_present(game):
    hero_blur_path = LIBRARY_CACHE_PATH / APPID / LIBRARY_HERO_BLUR
    with patch.object(Path, "is_file", is_file_for(hero_blur_path)):
        assert game.hero_blur == hero_blur_path


def test_hero_blur_falls_back_to_nested_hash_subdir(game):
    asset_dir = LIBRARY_CACHE_PATH / APPID
    hash_dir = asset_dir / "5925343a8312ea07f234d48170963aafae4158bf"
    nested_hero_blur = hash_dir / LIBRARY_HERO_BLUR

    with patch.object(Path, "is_file", is_file_for(nested_hero_blur)), \
            patch.object(Path, "is_dir", is_dir_for(hash_dir)), \
            patch.object(Path, "iterdir", dir_listing({asset_dir: [hash_dir]})):
        assert game.hero_blur == nested_hero_blur


def test_icon_prefers_sha1_named_jpg(game):
    """Steam names icons after the SHA-1 of the file contents; prefer that over strays."""
    stray = Mock(spec=Path)
    stray.name = "leftover.tmp"

    icon = Mock(spec=Path)
    icon.name = "0f3e42a397a4bc4ded83f92cbcd4d0eeeb926a09.jpg"

    with patch.object(Path, "iterdir", return_value=[stray, icon]):
        assert game.icon == icon


def test_icon_returns_none_when_no_sha1_named_file(game):
    stray = Mock(spec=Path)
    stray.name = "leftover.tmp"

    with patch.object(Path, "iterdir", return_value=[stray]):
        assert game.icon is None


def test_icon_is_cached(game):
    icon = Mock(spec=Path)
    icon.name = "0f3e42a397a4bc4ded83f92cbcd4d0eeeb926a09.jpg"

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
