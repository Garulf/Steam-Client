from unittest.mock import Mock, patch, MagicMock, PropertyMock

import pytest

from steam_client.library import Library
from steam_client.library_folder import LibraryFolder
from steam_client.game import SteamGame


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


class TestLibrary:
    def test_libraries_parses_vdf_on_first_call(self, library, mock_vdf_data):
        """Verify that libraries() parses libraryfolders.vdf on first call."""
        with patch("builtins.open", MagicMock()):
            with patch("vdf.load", return_value=mock_vdf_data):
                with patch("hashlib.md5") as mock_md5:
                    mock_md5.return_value.hexdigest.return_value = "hash1"
                    libs = list(library.libraries())

        assert len(libs) == 2
        assert isinstance(libs[0], LibraryFolder)
        assert libs[0].path == "/library1"
        assert libs[1].path == "/library2"

    def test_libraries_cached_when_hash_unchanged(self, library, mock_vdf_data):
        """Verify that libraries are cached when hash doesn't change."""
        with patch("builtins.open", MagicMock()):
            with patch("vdf.load", return_value=mock_vdf_data) as mock_vdf_load:
                with patch("hashlib.md5") as mock_md5:
                    mock_md5.return_value.hexdigest.return_value = "hash1"
                    # First call
                    list(library.libraries())
                    # Second call with same hash
                    list(library.libraries())

        # vdf.load should only be called once
        assert mock_vdf_load.call_count == 1

    def test_libraries_reparsed_when_hash_changes(self, library, mock_vdf_data):
        """Verify that libraries are reparsed when hash changes."""
        # Sequence: first _is_updated->hash1, store->hash1, second _is_updated->hash2, store->hash2
        hashes = ["hash1", "hash1", "hash2", "hash2"]
        hash_iter = iter(hashes)

        with patch("builtins.open", MagicMock()):
            with patch("vdf.load", return_value=mock_vdf_data) as mock_vdf_load:
                with patch("hashlib.md5") as mock_md5:
                    # Create a callable that returns a new mock with the next hash
                    def create_hash_mock(*args, **kwargs):
                        mock = MagicMock()
                        mock.hexdigest.return_value = next(hash_iter)
                        return mock
                    mock_md5.side_effect = create_hash_mock
                    # First call: detects update (None != hash1), stores hash1
                    list(library.libraries())
                    # Second call: detects update (hash1 != hash2), stores hash2 and re-parses
                    list(library.libraries())

        # vdf.load should be called twice because hash changed on second call
        assert mock_vdf_load.call_count == 2

    def test_games_aggregates_across_folders(self, library, mock_vdf_data, steam):
        """Verify that games() yields games from all library folders."""
        with patch("builtins.open", MagicMock()):
            with patch("vdf.load", return_value=mock_vdf_data):
                with patch("hashlib.md5") as mock_md5:
                    mock_md5.return_value.hexdigest.return_value = "hash1"
                    games = list(library.games())

        appids = [game.appid for game in games]
        assert appids == ["440", "570", "730", "271590"]

    def test_game_by_id_returns_matching_game(self, library, mock_vdf_data):
        """Verify that game_by_id() returns the game with matching appid."""
        with patch("builtins.open", MagicMock()):
            with patch("vdf.load", return_value=mock_vdf_data):
                with patch("hashlib.md5") as mock_md5:
                    mock_md5.return_value.hexdigest.return_value = "hash1"
                    game = library.game_by_id("570")

        assert game is not None
        assert game.appid == "570"

    def test_game_by_id_returns_none_when_not_found(self, library, mock_vdf_data):
        """Verify that game_by_id() returns None when game not found."""
        with patch("builtins.open", MagicMock()):
            with patch("vdf.load", return_value=mock_vdf_data):
                with patch("hashlib.md5") as mock_md5:
                    mock_md5.return_value.hexdigest.return_value = "hash1"
                    game = library.game_by_id("999999")

        assert game is None

    def test_game_by_name_case_insensitive(self, library, mock_vdf_data, steam):
        """Verify that game_by_name() is case-insensitive."""
        with patch("builtins.open", MagicMock()):
            with patch("vdf.load", return_value=mock_vdf_data):
                with patch("hashlib.md5") as mock_md5:
                    mock_md5.return_value.hexdigest.return_value = "hash1"
                    with patch.object(
                        SteamGame, "_get_name_from_manifest", return_value="Portal 2"
                    ):
                        game1 = library.game_by_name("PORTAL 2")
                        game2 = library.game_by_name("portal 2")
                        game3 = library.game_by_name("Portal 2")

        assert game1 is not None
        assert game2 is not None
        assert game3 is not None
        assert game1.appid == game2.appid == game3.appid

    def test_game_by_name_returns_none_when_not_found(self, library, mock_vdf_data):
        """Verify that game_by_name() returns None when game not found."""
        with patch("builtins.open", MagicMock()):
            with patch("vdf.load", return_value=mock_vdf_data):
                with patch("hashlib.md5") as mock_md5:
                    mock_md5.return_value.hexdigest.return_value = "hash1"
                    with patch.object(
                        SteamGame, "_get_name_from_manifest", return_value="Portal 2"
                    ):
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

        mock_users = [mock_user1, mock_user2]
        with patch.object(type(library._steam), "users", new_callable=PropertyMock) as mock_users_prop:
            mock_users_prop.return_value = mock_users
            shortcuts = list(library.shortcuts())

        assert len(shortcuts) == 3
        assert mock_shortcut1 in shortcuts
        assert mock_shortcut2 in shortcuts
        assert mock_shortcut3 in shortcuts

    def test_all_yields_games_then_shortcuts(self, library, mock_vdf_data):
        """Verify that all() yields games then shortcuts."""
        mock_shortcut = Mock()
        mock_user = Mock()
        mock_user.shortcuts.return_value = [mock_shortcut]
        mock_users = [mock_user]

        with patch.object(type(library._steam), "users", new_callable=PropertyMock) as mock_users_prop:
            mock_users_prop.return_value = mock_users
            with patch("builtins.open", MagicMock()):
                with patch("vdf.load", return_value=mock_vdf_data):
                    with patch("hashlib.md5") as mock_md5:
                        mock_md5.return_value.hexdigest.return_value = "hash1"
                        items = list(library.all())

        assert len(items) == 5
        games = [item for item in items if isinstance(item, SteamGame)]
        shortcuts = [item for item in items if item is mock_shortcut]
        assert len(games) == 4
        assert len(shortcuts) == 1
        assert items[-1] is mock_shortcut


class TestLibraryFolder:
    def test_library_folder_get_games_creates_steam_games(self, steam):
        """Verify that get_games() creates a list of SteamGame objects."""
        appids = ["440", "570", "730"]
        folder = LibraryFolder(steam, "/library", appids)

        games = folder.get_games()

        assert len(games) == 3
        assert all(isinstance(game, SteamGame) for game in games)
        assert [game.appid for game in games] == appids

    def test_library_folder_get_games_preserves_order(self, steam):
        """Verify that get_games() preserves appid order."""
        appids = ["999", "111", "555"]
        folder = LibraryFolder(steam, "/library", appids)

        games = folder.get_games()
        retrieved_appids = [game.appid for game in games]

        assert retrieved_appids == appids

    def test_library_folder_get_games_empty_list(self, steam):
        """Verify that get_games() handles empty app list."""
        folder = LibraryFolder(steam, "/library", [])

        games = folder.get_games()

        assert games == []
