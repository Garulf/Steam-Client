# Utilities

Helper functions for platform-specific setup and VDF file parsing.

!!! note "Windows only"
    `steam_from_registry()` and `steam_install_path_from_registry()` read from the Windows registry and raise `OSError` on other platforms.

```python
from steam_client.utils import steam_from_registry

steam = steam_from_registry()
```

::: steam_client.utils

---

## VDF files

Loaders for Valve's VDF data format, used by all modules that read Steam data files.

::: steam_client.vdf_file

---

## Exceptions

`SteamNotFoundError` is raised when a required Steam data file is missing — usually a sign that Steam is not installed at the given base path. It subclasses `FileNotFoundError`.

::: steam_client.exceptions
