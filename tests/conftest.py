import pytest

from steam_client.steam import Steam
from steam_client.login_users import STEAM64_OFFSET, LoginUser, User, UserData
from steam_client.shortcut import ShortcutEntry

FAKE_BASE_PATH = "/fake/steam"
FAKE_ACCOUNT_ID = 12345678
FAKE_USER_ID = STEAM64_OFFSET + FAKE_ACCOUNT_ID


@pytest.fixture
def steam():
    return Steam(base_path=FAKE_BASE_PATH)


@pytest.fixture
def user_data():
    return UserData(
        AccountName="testuser",
        PersonaName="Test User",
        RememberPassword="1",
        AllowAutoLogin="1",
        MostRecent="1",
        Timestamp="1700000000",
    )


@pytest.fixture
def user(user_data):
    return User(id=FAKE_USER_ID, data=user_data)


@pytest.fixture
def login_user(steam, user):
    return LoginUser(steam.base_path, user)


@pytest.fixture
def shortcut_entry() -> ShortcutEntry:
    return {
        "appid": 0,
        "AppName": "Test Game",
        "Exe": "/path/to/game.exe",
        "StartDir": "/path/to",
        "LaunchOptions": "",
        "icon": "/path/to/icon.png",
        "tags": {},
    }
