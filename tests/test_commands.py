from unittest.mock import patch
import pytest

from steam_client.commands import Command, Commands, SteamWindows, SCHEME


class TestCommand:
    def setup_method(self):
        self.command = Command(SCHEME)

    def test_create_uri_single_path(self):
        uri = self.command._create_uri(["rungameid"], "12345")
        assert uri == "steam://rungameid/12345"

    def test_create_uri_multi_path(self):
        uri = self.command._create_uri(["store", "app"], "67890")
        assert uri == "steam://store/app/67890"

    def test_call_opens_browser(self):
        with patch("webbrowser.open") as mock_open:
            self.command(["rungameid"], "12345")
        mock_open.assert_called_once_with("steam://rungameid/12345")


class TestCommands:
    def setup_method(self):
        self.commands = Commands()

    def test_run_game_id(self):
        with patch("webbrowser.open") as mock_open:
            self.commands.run_game_id("12345")
        mock_open.assert_called_once_with("steam://rungameid/12345")

    def test_store(self):
        with patch("webbrowser.open") as mock_open:
            self.commands.store("12345")
        mock_open.assert_called_once_with("steam://store/12345")

    def test_install(self):
        with patch("webbrowser.open") as mock_open:
            self.commands.install("12345")
        mock_open.assert_called_once_with("steam://install/12345")

    def test_uninstall(self):
        with patch("webbrowser.open") as mock_open:
            self.commands.uninstall("12345")
        mock_open.assert_called_once_with("steam://uninstall/12345")

    def test_update_news(self):
        with patch("webbrowser.open") as mock_open:
            self.commands.update_news("12345")
        mock_open.assert_called_once_with("steam://updatenews/12345")

    def test_open_window(self):
        with patch("webbrowser.open") as mock_open:
            self.commands.open(SteamWindows.SETTINGS)
        mock_open.assert_called_once_with(f"steam://open/{SteamWindows.SETTINGS}")

    def test_open_url(self):
        with patch("webbrowser.open") as mock_open:
            self.commands.open_url("https://store.steampowered.com")
        mock_open.assert_called_once_with("steam://openurl/https://store.steampowered.com")
