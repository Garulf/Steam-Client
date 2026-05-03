import pytest
from unittest.mock import MagicMock
from dataclasses import dataclass

from steam_client.steam import Steam
from steam_client.login_users import LoginUser, User, UserData
from steam_client.shortcut import ShortcutEntry

FAKE_BASE_PATH = "/fake/steam"
STEAM64_OFFSET = 76561197960265728


@pytest.fixture
def steam():
    return Steam(base_path=FAKE_BASE_PATH)


@pytest.fixture
def user_data():
    return UserData(
        AccountName="testuser",
        PersonaName="Test User",
        RememberPassword="1",
        WantsOfflineMode="0",
        SkipOfflineModeWarning="0",
        AllowAutoLogin="1",
        MostRecent="1",
        Timestamp="1700000000",
    )


@pytest.fixture
def user(user_data):
    return User(id=STEAM64_OFFSET + 12345678, data=user_data)


@pytest.fixture
def login_user(steam, user):
    return LoginUser(steam, user)


@pytest.fixture
def shortcut_entry() -> ShortcutEntry:
    return {
        "appid": 0,
        "appname": "Test Game",
        "exe": "/path/to/game.exe",
        "StartDir": "/path/to",
        "LaunchOptions": "",
        "icon": "/path/to/icon.png",
        "tags": {},
    }
