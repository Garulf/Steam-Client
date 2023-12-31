from typing import Literal
import os


SteamWindow = Literal[
    'main',
    'games',
    'games/details',
    'games/grid',
    'games/list',
    'friends',
    'chat',
    'bigpicture',
    'news',
    'settings',
    'tools',
    'console'
]


class Commands:

    def run_game_id(self, app_id: str) -> None:
        """Launches game with the specified ID in the Steam client."""
        os.startfile(f'steam://rungameid/{app_id}')

    def store(self, app_id: str) -> None:
        """Opens the game's store page in the Steam client."""
        os.startfile(f'steam://store/{app_id}')

    def install(self, app_id: str) -> None:
        """Opens the game's install prompt in the Steam client."""
        os.startfile(f'steam://install/{app_id}')

    def uninstall(self, app_id: str) -> None:
        """Opens the game's uninstall prompt in the Steam client."""
        os.startfile(f'steam://uninstall/{app_id}')

    def update_news(self, app_id: str) -> None:
        """Opens the game's update news in the Steam client."""
        os.startfile(f'steam://updatenews/{app_id}')

    def open(self, window: SteamWindow) -> None:
        """Opens the specified window in the Steam client."""
        os.startfile(f'steam://open/{window}')

    def open_url(self, url: str) -> None:
        """Opens the specified URL in the Steam client."""
        os.startfile(f'steam://openurl/{url}')
