# Utilities

Helper functions for platform-specific setup.

!!! note "Windows only"
    `steam_from_registry()` and `get_steam_from_registry()` read from the Windows registry and raise `OSError` on other platforms.

```python
from steam_client.utils import steam_from_registry

steam = steam_from_registry()
```

::: steam_client.utils
