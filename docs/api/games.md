# Games & Apps

## App

Abstract base class shared by `Game` and `Shortcut`. Provides the common interface for `name`, `appid`, artwork paths, and launching.

::: steam_client.app

---

## Game

Represents an installed Steam game read from an `appmanifest_*.acf` file.

```python
game = steam.library.game_by_id("440")
print(game.name, game.header)
```

::: steam_client.game

---

## Shortcut

Represents a non-Steam game shortcut. App IDs are computed using the same CRC32 algorithm Steam uses internally.

```python
for shortcut in steam.library.shortcuts():
    print(shortcut.appname, shortcut.grid)
```

::: steam_client.shortcut
