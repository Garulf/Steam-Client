from __future__ import annotations
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

from .vdf_file import load_binary_vdf


@dataclass
class ShortcutData:
    """Shortcut fields mirrored from shortcuts.vdf (names keep Valve's casing)."""
    appid: int = 0
    AppName: str = ''
    Exe: str = ''
    StartDir: str = ''
    icon: str = ''
    ShortcutPath: str = ''
    LaunchOptions: str = ''
    IsHidden: int = 0
    AllowDesktopConfig: int = 1
    AllowOverlay: int = 1
    OpenVR: int = 0
    Devkit: int = 0
    DevkitGameID: str = ''
    DevkitOverrideAppID: int = 0
    LastPlayTime: int = 0
    FlatpakAppID: str = ''
    tags: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_vdf(cls, data: dict[str, Any]) -> ShortcutData:
        """Builds ShortcutData from a raw shortcuts.vdf entry, ignoring unknown keys."""
        known_fields = {field.name for field in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in known_fields})


@dataclass
class Shortcuts:
    """Represents the shortcuts.vdf file."""
    shortcuts: list[ShortcutData] = field(default_factory=list)

    @classmethod
    def from_vdf(cls, data: dict[str, Any]) -> Shortcuts:
        """Builds Shortcuts from parsed shortcuts.vdf data."""
        return cls([ShortcutData.from_vdf(entry) for entry in data['shortcuts'].values()])

    @classmethod
    def load(cls, path: Path) -> Shortcuts:
        """Loads and parses a shortcuts.vdf file."""
        return cls.from_vdf(load_binary_vdf(path))
