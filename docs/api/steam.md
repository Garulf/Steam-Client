# Steam

The `Steam` class is the main entry point for the library. Instantiate it with a path to a local Steam installation, or use [`steam_from_registry()`](utils.md) on Windows to auto-detect the path.

```python
from steam_client import Steam

steam = Steam()
```

::: steam_client.steam
