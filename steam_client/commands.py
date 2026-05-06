import webbrowser
from enum import StrEnum


def _create_uri(*segments: str) -> str:
    return f'steam://{"/".join(segments)}'


class SteamWindows(StrEnum):
    """Enumeration of Steam client windows."""
    MAIN = 'main'
    GAMES = 'games'
    GAMES_DETAILS = 'games/details'
    GAMES_GRID = 'games/grid'
    GAMES_LIST = 'games/list'
    FRIENDS = 'friends'
    CHAT = 'chat'
    BIGPICTURE = 'bigpicture'
    NEWS = 'news'
    SETTINGS = 'settings'
    TOOLS = 'tools'
    CONSOLE = 'console'


class Command():
    def _create_uri(self, *segments: str) -> str:
        return _create_uri(*segments)

    def open(self, *segments: str) -> None:
        """Executes the command with the specified endpoint."""
        webbrowser.open(_create_uri(*segments))


class Commands:
    """A collection of commands for the Steam client."""

    def _open(self, *segments: str) -> None:
        webbrowser.open(_create_uri(*segments))

    def run_game_id(self, app_id: str) -> None:
        """Launches game with the specified ID in the Steam client."""
        self._open('rungameid', app_id)

    def store(self, app_id: str) -> None:
        """Opens the game's store page in the Steam client."""
        self._open('store', app_id)

    def install(self, app_id: str) -> None:
        """Opens the game's install prompt in the Steam client."""
        self._open('install', app_id)

    def uninstall(self, app_id: str) -> None:
        """Opens the game's uninstall prompt in the Steam client."""
        self._open('uninstall', app_id)

    def update_news(self, app_id: str) -> None:
        """Opens the game's update news in the Steam client."""
        self._open('updatenews', app_id)

    def open(self, window: SteamWindows) -> None:
        """Opens the specified window in the Steam client."""
        self._open('open', window)

    def open_url(self, url: str) -> None:
        """Opens the specified URL in the Steam client."""
        self._open('openurl', url)
