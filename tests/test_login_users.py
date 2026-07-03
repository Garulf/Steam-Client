import dataclasses
from pathlib import Path
from unittest.mock import patch

import pytest

from steam_client import SteamNotFoundError
from steam_client.login_users import LoginUser, LoginUsers, User, UserData

from tests.conftest import FAKE_ACCOUNT_ID, FAKE_USER_ID


def test_login_user_is_most_recent(login_user):
    assert login_user.is_most_recent is True


def test_login_user_not_most_recent(steam, user_data):
    data = dataclasses.replace(user_data, MostRecent="0")
    user = User(id=FAKE_USER_ID, data=data)
    lu = LoginUser(steam.base_path, user)
    assert lu.is_most_recent is False


def test_account_id(login_user):
    assert login_user.account_id == FAKE_ACCOUNT_ID


def test_user_data_dir(login_user):
    assert login_user.user_data_dir == Path("/fake/steam/userdata") / str(FAKE_ACCOUNT_ID)


def test_config(login_user):
    assert login_user.config == login_user.user_data_dir / "config"


def test_shortcuts_file(login_user):
    assert login_user.shortcuts_file == login_user.config / "shortcuts.vdf"


def test_grid_path(login_user):
    assert login_user.grid_path == login_user.config / "grid"


def test_user_data_from_vdf_ignores_unknown_keys():
    data = UserData.from_vdf({
        "AccountName": "testuser",
        "MostRecent": "1",
        "SomeFutureSteamKey": "surprise",
    })
    assert data.AccountName == "testuser"
    assert data.MostRecent == "1"
    assert data.PersonaName == ""


def test_shortcuts_parses_vdf(login_user):
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
    with patch("steam_client.login_users.load_binary_vdf", return_value=fake_shortcut_data):
        shortcuts = login_user.shortcuts()
    assert len(shortcuts) == 1
    assert shortcuts[0].name == "My Game"


def test_shortcuts_empty_when_file_missing(login_user):
    """A user who never created a shortcut has no shortcuts.vdf; that is not an error."""
    with patch("steam_client.login_users.load_binary_vdf", side_effect=FileNotFoundError):
        assert login_user.shortcuts() == []


def test_users_builds_user_data_from_raw_vdf(steam):
    """users() must convert raw vdf dicts into UserData (regression test)."""
    raw = {
        "users": {
            str(FAKE_USER_ID): {
                "AccountName": "testuser",
                "PersonaName": "Test User",
                "MostRecent": "1",
            }
        }
    }
    with patch("steam_client.login_users.load_vdf", return_value=raw):
        users = LoginUsers(steam.base_path).users()

    assert len(users) == 1
    assert isinstance(users[0].user.data, UserData)
    assert users[0].user.data.AccountName == "testuser"
    assert users[0].is_most_recent is True


def test_users_raise_steam_not_found_when_file_missing(steam):
    with patch("steam_client.login_users.load_vdf", side_effect=FileNotFoundError):
        with pytest.raises(SteamNotFoundError):
            LoginUsers(steam.base_path).users()


def test_login_users_most_recent(steam, user_data):
    recent_user = User(id=FAKE_USER_ID, data=user_data)
    not_recent_user = User(id=FAKE_USER_ID + 1, data=dataclasses.replace(user_data, MostRecent="0"))
    users = [LoginUser(steam.base_path, recent_user), LoginUser(steam.base_path, not_recent_user)]

    with patch.object(LoginUsers, "users", return_value=users):
        most_recent = LoginUsers(steam.base_path).most_recent_user()

    assert most_recent is not None
    assert most_recent.is_most_recent is True


def test_login_users_most_recent_none_when_no_recent(steam, user_data):
    data = dataclasses.replace(user_data, MostRecent="0")
    users = [LoginUser(steam.base_path, User(id=FAKE_USER_ID, data=data))]

    with patch.object(LoginUsers, "users", return_value=users):
        most_recent = LoginUsers(steam.base_path).most_recent_user()

    assert most_recent is None
