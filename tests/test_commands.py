from unittest.mock import patch

from steam_client import commands
from steam_client.commands import SteamWindow, _create_uri


class TestCreateURI:
    def test_create_uri_single_path(self):
        assert _create_uri("rungameid", "12345") == "steam://rungameid/12345"

    def test_create_uri_multi_path(self):
        assert _create_uri("store", "app", "67890") == "steam://store/app/67890"

    def test_create_uri_int_segment(self):
        assert _create_uri("rungameid", 12345) == "steam://rungameid/12345"


class TestCommands:
    def test_run_game_id(self):
        with patch("webbrowser.open") as mock_open:
            commands.run_game_id("12345")
        mock_open.assert_called_once_with("steam://rungameid/12345")

    def test_store(self):
        with patch("webbrowser.open") as mock_open:
            commands.store("12345")
        mock_open.assert_called_once_with("steam://store/12345")

    def test_install(self):
        with patch("webbrowser.open") as mock_open:
            commands.install("12345")
        mock_open.assert_called_once_with("steam://install/12345")

    def test_uninstall(self):
        with patch("webbrowser.open") as mock_open:
            commands.uninstall("12345")
        mock_open.assert_called_once_with("steam://uninstall/12345")

    def test_update_news(self):
        with patch("webbrowser.open") as mock_open:
            commands.update_news("12345")
        mock_open.assert_called_once_with("steam://updatenews/12345")

    def test_open_window(self):
        with patch("webbrowser.open") as mock_open:
            commands.open_window(SteamWindow.SETTINGS)
        mock_open.assert_called_once_with("steam://open/settings")

    def test_open_url(self):
        with patch("webbrowser.open") as mock_open:
            commands.open_url("https://store.steampowered.com")
        mock_open.assert_called_once_with("steam://openurl/https://store.steampowered.com")
