# Steam Client

A Python library for interacting with a locally installed Steam client — enumerate your game library/non-steam games, read game metadata and artwork paths, and send Steam URI commands.

[![Docs](https://img.shields.io/badge/docs-mkdocs%20material-0A7BBB?style=flat&logo=materialformkdocs&logoColor=white)](docs/index.md)

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-garulf-FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/garulf)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-garulf-FF5E5B?style=flat&logo=ko-fi&logoColor=white)](https://ko-fi.com/garulf)

---

## Installation

Requires Python 3.8+.

```bash
pip install steam-client
```

Or install from source:

```bash
pip install -e .
```

---

## Quickstart

```python
from steam_client.steam import Steam

steam = Steam()  # Uses default path: C:\Program Files (x86)\Steam

# On Windows, auto-detect path from registry:
from steam_client.utils import steam_from_registry
steam = steam_from_registry()
```

---

## Common Operations

### List all installed games

```python
for game in steam.library.games():
    print(game.appid, game.name)
```

### Find a game

```python
game = steam.library.game_by_id("440")       # by app ID
game = steam.library.game_by_name("Portal 2") # by name (case-insensitive)
```

### Artwork paths

```python
game.header   # Path to header image    (460×215 jpg)
game.grid     # Path to grid image      (600×900 jpg)
game.hero     # Path to hero image
game.icon     # Path to icon file, or None
```

### Launch and manage games via Steam URI commands

```python
from steam_client.commands import Commands, SteamWindows

commands = Commands()
commands.run_game_id("440")         # Launch a game
commands.store("440")               # Open store page
commands.install("440")             # Prompt install
commands.uninstall("440")           # Prompt uninstall
commands.open(SteamWindows.FRIENDS) # Open a Steam window
commands.open_url("https://store.steampowered.com")
```

Or launch a game directly from a `SteamGame` object:

```python
game.run()
```

### Users and shortcuts

```python
for user in steam.users:
    print(user.user.data.PersonaName)

for shortcut in steam.library.shortcuts():
    print(shortcut.appname)
```

## Platform Notes

| Platform | Default path                   | Registry helper         |
|----------|--------------------------------|-------------------------|
| Windows  | `C:\Program Files (x86)\Steam` | `steam_from_registry()` |
| Linux    | `~/.local/share/steam`         | Not available           |

Pass a custom path to override the default:

```python
steam = Steam("/custom/steam/path")
```

Requires read access to local Steam config files (`libraryfolders.vdf`, `shortcuts.vdf`, appmanifest files).

---

## Development

```bash
pytest          # Run tests
flake8 steam_client  # Lint
mypy steam_client    # Type check
mkdocs serve         # Preview docs locally
mkdocs build --strict # Validate docs build
tox             # Run all environments (lint, type, docs, py311–314)
```
