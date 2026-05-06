# Getting Started

## Install

```bash
pip install steam-client
```

## First script

```python
from steam_client.steam import Steam

steam = Steam()
print(steam.library_folders)
```

On Windows, you can use registry discovery:

```python
from steam_client.utils import steam_from_registry

steam = steam_from_registry()
print(steam.app_cache)
```
