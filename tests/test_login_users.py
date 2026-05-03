from pathlib import Path
from unittest.mock import MagicMock, patch

from steam_client.login_users import LoginUser, LoginUsers, User, UserData, STEAM64_OFFSET


FAKE_STEAM_ID3 = 12345678
FAKE_USER_ID = STEAM64_OFFSET + FAKE_STEAM_ID3


def test_login_user_is_most_recent(login_user):
    assert login_user.is_most_recent is True


def test_login_user_not_most_recent(steam, user_data):
    data = UserData(
        AccountName=user_data.AccountName,
        PersonaName=user_data.PersonaName,
        RememberPassword=user_data.RememberPassword,
        WantsOfflineMode=user_data.WantsOfflineMode,
        SkipOfflineModeWarning=user_data.SkipOfflineModeWarning,
        AllowAutoLogin=user_data.AllowAutoLogin,
        MostRecent="0",
        Timestamp=user_data.Timestamp,
    )
    user = User(id=FAKE_USER_ID, data=data)
    lu = LoginUser(steam, user)
    assert lu.is_most_recent is False


def test_steam_id3(login_user):
    assert login_user.steam_id3 == FAKE_STEAM_ID3


def test_user_data_dir(login_user):
    assert login_user.user_data_dir == Path("/fake/steam/userdata") / str(FAKE_STEAM_ID3)


def test_config(login_user):
    assert login_user.config == login_user.user_data_dir / "config"


def test_shortcuts_file(login_user):
    assert login_user.shortcuts_file == login_user.config / "shortcuts.vdf"


def test_grid_path(login_user):
    assert login_user.grid_path == login_user.user_data_dir / "config" / "grid"


def test_shortcuts_parses_vdf(steam, login_user):
    fake_shortcut_data = {
        "shortcuts": {
            "0": {
                "appid": 0,
                "appname": "My Game",
                "exe": "/path/game.exe",
                "StartDir": "/path",
                "LaunchOptions": "",
                "icon": "",
                "tags": {},
            }
        }
    }
    with patch("builtins.open", MagicMock()), \
         patch("vdf.binary_load", return_value=fake_shortcut_data):
        shortcuts = login_user.shortcuts()
    assert len(shortcuts) == 1
    assert shortcuts[0].name == "My Game"


def test_login_users_most_recent(steam, user_data):
    recent_user = User(id=FAKE_USER_ID, data=user_data)
    not_recent_data = UserData(
        AccountName="other",
        PersonaName="Other",
        RememberPassword="0",
        WantsOfflineMode="0",
        SkipOfflineModeWarning="0",
        AllowAutoLogin="0",
        MostRecent="0",
        Timestamp="0",
    )
    not_recent_user = User(id=FAKE_USER_ID + 1, data=not_recent_data)
    users = [LoginUser(steam, recent_user), LoginUser(steam, not_recent_user)]

    with patch.object(LoginUsers, "users", return_value=users):
        lu = LoginUsers(steam)
        most_recent = lu.most_recent_user()

    assert most_recent is not None
    assert most_recent.is_most_recent is True


def test_login_users_most_recent_none_when_no_recent(steam, user_data):
    data = UserData(
        AccountName="other",
        PersonaName="Other",
        RememberPassword="0",
        WantsOfflineMode="0",
        SkipOfflineModeWarning="0",
        AllowAutoLogin="0",
        MostRecent="0",
        Timestamp="0",
    )
    users = [LoginUser(steam, User(id=FAKE_USER_ID, data=data))]

    with patch.object(LoginUsers, "users", return_value=users):
        lu = LoginUsers(steam)
        most_recent = lu.most_recent_user()

    assert most_recent is None
