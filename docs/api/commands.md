# Commands

The `commands` module builds and dispatches `steam://` URI commands to the local Steam client via `webbrowser.open`. `SteamWindow` is a `StrEnum` of all openable Steam windows.

```python
from steam_client import commands
from steam_client.commands import SteamWindow

commands.run_game_id("440")
commands.open_window(SteamWindow.FRIENDS)
```

::: steam_client.commands
