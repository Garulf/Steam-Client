import importlib
import sys

from .steam import Steam

STEAM_SUB_KEY = r'SOFTWARE\WOW6432Node\Valve\Steam'


def steam_install_path_from_registry() -> str:
    """Returns the Steam install path from the Windows registry."""
    if sys.platform != "win32":
        raise OSError("Windows registry is only available on Windows")

    reg = importlib.import_module("winreg")
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, STEAM_SUB_KEY) as hkey:
        return reg.QueryValueEx(hkey, "InstallPath")[0]


def steam_from_registry() -> Steam:
    """Returns a Steam instance located via the Windows registry."""
    return Steam(steam_install_path_from_registry())
