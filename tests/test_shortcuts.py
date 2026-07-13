import pytest

from steam_client.shortcuts import ShortcutData, Shortcuts


@pytest.fixture
def raw_entry():
    return {
        "appid": -1059188172,
        "AppName": "Test Game",
        "Exe": '"/path/to/game.exe"',
        "StartDir": "/path/to",
        "icon": "/path/to/icon.png",
        "ShortcutPath": "",
        "LaunchOptions": "--windowed",
        "IsHidden": 0,
        "AllowDesktopConfig": 1,
        "AllowOverlay": 1,
        "OpenVR": 0,
        "Devkit": 0,
        "DevkitGameID": "",
        "DevkitOverrideAppID": 0,
        "LastPlayTime": 1700000000,
        "FlatpakAppID": "",
        "tags": {"0": "favorite"},
    }


def test_shortcut_data_from_vdf(raw_entry):
    data = ShortcutData.from_vdf(raw_entry)
    assert data.AppName == "Test Game"
    assert data.Exe == '"/path/to/game.exe"'
    assert data.LastPlayTime == 1700000000
    assert data.tags == {"0": "favorite"}


def test_shortcut_data_from_vdf_ignores_unknown_keys(raw_entry):
    raw_entry["SomeFutureField"] = "1"
    data = ShortcutData.from_vdf(raw_entry)
    assert data.AppName == "Test Game"


def test_shortcut_data_defaults():
    data = ShortcutData.from_vdf({"AppName": "Minimal"})
    assert data.Exe == ""
    assert data.IsHidden == 0
    assert data.tags == {}


def test_shortcut_data_tags_default_is_not_shared():
    assert ShortcutData().tags is not ShortcutData().tags


def test_shortcuts_from_vdf(raw_entry):
    data = Shortcuts.from_vdf({"shortcuts": {"0": raw_entry, "1": raw_entry}})
    assert len(data.shortcuts) == 2
    assert all(isinstance(entry, ShortcutData) for entry in data.shortcuts)


def test_shortcuts_from_vdf_empty():
    assert Shortcuts.from_vdf({"shortcuts": {}}).shortcuts == []
