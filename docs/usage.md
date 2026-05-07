# Usage

## List games

```python
from steam_client.steam import Steam

steam = Steam()
for game in steam.library.games():
    print(game.appid, game.name)
```

## Find a game

```python
game = steam.library.game_by_id("440")
if game:
    print(game.name)
```

```python
game = steam.library.game_by_name("Portal 2")
if game:
    print(game.appid)
```

## Use Steam URI commands

```python
from steam_client.commands import Commands, SteamWindows

commands = Commands()
commands.run_game_id("440")
commands.open(SteamWindows.FRIENDS)
```

## Read users and shortcuts

```python
for user in steam.users:
    print(user.user.data.PersonaName)

for shortcut in steam.library.shortcuts():
    print(shortcut.appname)
```
