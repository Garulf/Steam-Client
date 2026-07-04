import webbrowser
from enum import StrEnum


class SteamWindow(StrEnum):
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


def _create_uri(*segments: str) -> str:
    return f'steam://{"/".join(segments)}'


def _open(*segments: str) -> None:
    webbrowser.open(_create_uri(*segments))


def run_game_id(app_id: str) -> None:
    """Launches game with the specified ID in the Steam client."""
    _open('rungameid', app_id)


def store(app_id: str) -> None:
    """Opens the game's store page in the Steam client."""
    _open('store', app_id)


def install(app_id: str) -> None:
    """Opens the game's install prompt in the Steam client."""
    _open('install', app_id)


def uninstall(app_id: str) -> None:
    """Opens the game's uninstall prompt in the Steam client."""
    _open('uninstall', app_id)


def update_news(app_id: str) -> None:
    """Opens the game's update news in the Steam client."""
    _open('updatenews', app_id)


def open_window(window: SteamWindow) -> None:
    """Opens the specified window in the Steam client."""
    _open('open', window)


def open_url(url: str) -> None:
    """Opens the specified URL in the Steam client."""
    _open('openurl', url)
