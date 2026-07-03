from contextlib import contextmanager
from itertools import chain, repeat
from pathlib import Path
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

from steam_client import SteamNotFoundError
from steam_client.library import Library
from steam_client.library_folder import LibraryFolder
from steam_client.game import Game


@pytest.fixture
def library(steam):
    return Library(steam)


@pytest.fixture
def mock_vdf_data():
    """Mock libraryfolders.vdf structure."""
    return {
        "LibraryFolders": {
            "0": {
                "path": "/library1",
                "apps": {"440": None, "570": None},
            },
            "1": {
                "path": "/library2",
                "apps": {"730": None, "271590": None},
            },
        }
    }


@contextmanager
def fake_library_folders_file(vdf_data, hashes=("hash1",)):
    """Fakes libraryfolders.vdf: its parsed content and one hash per libraries() call.

    The last hash repeats for any further calls, like an unchanged file would.
    """
    hash_iter = chain(hashes, repeat(hashes[-1]))

    def next_hash(*args, **kwargs):
        mock = MagicMock()
        mock.hexdigest.return_value = next(hash_iter)
        return mock

    with patch("builtins.open", MagicMock()), \
         patch("steam_client.library.load_vdf", return_value=vdf_data) as mock_load, \
         patch("hashlib.md5", side_effect=next_hash):
        yield mock_load


class TestLibrary:
    def test_libraries_parses_vdf_on_first_call(self, library, mock_vdf_data):
        """Verify that libraries() parses libraryfolders.vdf on first call."""
        with fake_library_folders_file(mock_vdf_data):
            libs = list(library.libraries())

        assert len(libs) == 2
        assert isinstance(libs[0], LibraryFolder)
        assert libs[0].path == "/library1"
        assert libs[1].path == "/library2"

    def test_libraries_cached_when_hash_unchanged(self, library, mock_vdf_data):
        """Verify that libraries are cached when hash doesn't change."""
        with fake_library_folders_file(mock_vdf_data, hashes=("hash1", "hash1")) as mock_load:
            list(library.libraries())
            list(library.libraries())

        assert mock_load.call_count == 1

    def test_libraries_reparsed_when_hash_changes(self, library, mock_vdf_data):
        """Verify that libraries are reparsed when hash changes."""
        with fake_library_folders_file(mock_vdf_data, hashes=("hash1", "hash2")) as mock_load:
            list(library.libraries())
            list(library.libraries())

        assert mock_load.call_count == 2

    def test_libraries_raise_steam_not_found_when_file_missing(self, library):
        """Verify that libraries() raises SteamNotFoundError when the vdf is missing."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(SteamNotFoundError):
                list(library.libraries())

    def test_games_aggregates_across_folders(self, library, mock_vdf_data):
        """Verify that games() yields games from all library folders."""
        with fake_library_folders_file(mock_vdf_data):
            games = list(library.games())

        appids = [game.appid for game in games]
        assert appids == ["440", "570", "730", "271590"]

    def test_game_by_id_returns_matching_game(self, library, mock_vdf_data):
        """Verify that game_by_id() returns the game with matching appid."""
        with fake_library_folders_file(mock_vdf_data):
            game = library.game_by_id("570")

        assert game is not None
        assert game.appid == "570"

    def test_game_by_id_returns_none_when_not_found(self, library, mock_vdf_data):
        """Verify that game_by_id() returns None when game not found."""
        with fake_library_folders_file(mock_vdf_data):
            game = library.game_by_id("999999")

        assert game is None

    def test_game_by_name_case_insensitive(self, library, mock_vdf_data):
        """Verify that game_by_name() is case-insensitive."""
        with fake_library_folders_file(mock_vdf_data):
            with patch.object(Game, "name", new_callable=PropertyMock, return_value="Portal 2"):
                game1 = library.game_by_name("PORTAL 2")
                game2 = library.game_by_name("portal 2")
                game3 = library.game_by_name("Portal 2")

        assert game1 is not None
        assert game2 is not None
        assert game3 is not None
        assert game1.appid == game2.appid == game3.appid

    def test_game_by_name_returns_none_when_not_found(self, library, mock_vdf_data):
        """Verify that game_by_name() returns None when game not found."""
        with fake_library_folders_file(mock_vdf_data):
            with patch.object(Game, "name", new_callable=PropertyMock, return_value="Portal 2"):
                game = library.game_by_name("Nonexistent Game")

        assert game is None

    def test_shortcuts_aggregates_across_users(self, library):
        """Verify that shortcuts() aggregates shortcuts from all users."""
        mock_shortcut1 = Mock()
        mock_shortcut2 = Mock()
        mock_shortcut3 = Mock()

        mock_user1 = Mock()
        mock_user1.shortcuts.return_value = [mock_shortcut1, mock_shortcut2]

        mock_user2 = Mock()
        mock_user2.shortcuts.return_value = [mock_shortcut3]

        with patch.object(type(library._steam), "users", new_callable=PropertyMock) as mock_users:
            mock_users.return_value = [mock_user1, mock_user2]
            shortcuts = list(library.shortcuts())

        assert shortcuts == [mock_shortcut1, mock_shortcut2, mock_shortcut3]

    def test_all_apps_yields_games_then_shortcuts(self, library, mock_vdf_data):
        """Verify that all_apps() yields games then shortcuts."""
        mock_shortcut = Mock()
        mock_user = Mock()
        mock_user.shortcuts.return_value = [mock_shortcut]

        with patch.object(type(library._steam), "users", new_callable=PropertyMock) as mock_users:
            mock_users.return_value = [mock_user]
            with fake_library_folders_file(mock_vdf_data):
                items = list(library.all_apps())

        assert len(items) == 5
        assert all(isinstance(item, Game) for item in items[:4])
        assert items[-1] is mock_shortcut


class TestLibraryFolder:
    def test_library_folder_games_creates_steam_games(self, steam):
        """Verify that games() creates a list of Game objects."""
        appids = ["440", "570", "730"]
        folder = LibraryFolder(Path(steam.library_cache), "/library", appids)

        games = folder.games()

        assert len(games) == 3
        assert all(isinstance(game, Game) for game in games)
        assert [game.appid for game in games] == appids

    def test_library_folder_games_preserves_order(self, steam):
        """Verify that games() preserves appid order."""
        appids = ["999", "111", "555"]
        folder = LibraryFolder(Path(steam.library_cache), "/library", appids)

        games = folder.games()

        assert [game.appid for game in games] == appids

    def test_library_folder_games_empty_list(self, steam):
        """Verify that games() handles empty app list."""
        folder = LibraryFolder(Path(steam.library_cache), "/library", [])

        assert folder.games() == []
