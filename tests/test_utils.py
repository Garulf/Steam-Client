import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from steam_client import utils
from steam_client.steam import Steam


def test_registry_lookup_raises_on_non_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    with pytest.raises(OSError):
        utils.steam_install_path_from_registry()


def test_steam_from_registry_builds_steam(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    fake_winreg = MagicMock()
    fake_winreg.QueryValueEx.return_value = (r"C:\Steam", 1)

    with patch("steam_client.utils.importlib.import_module", return_value=fake_winreg):
        steam = utils.steam_from_registry()

    assert isinstance(steam, Steam)
    assert steam.base_path == Path(r"C:\Steam")
