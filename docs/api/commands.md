# Commands

`Commands` builds and dispatches `steam://` URI commands to the local Steam client via `webbrowser.open`. `SteamWindows` is a `StrEnum` of all openable Steam windows.

```python
from steam_client.commands import Commands, SteamWindows

commands = Commands()
commands.run_game_id("440")
commands.open(SteamWindows.FRIENDS)
```

::: steam_client.commands
