# Library

`Library` provides access to installed games and non-Steam shortcuts across all Steam library folders on the machine.

```python
for game in steam.library.games():
    print(game.appid, game.name)
```

::: steam_client.library

---

## LibraryFolder

A single Steam library folder on disk. Returned by `Library.libraries()`.

::: steam_client.library_folder
