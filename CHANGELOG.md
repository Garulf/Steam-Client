# Changelog

## [6.0.0](https://github.com/Garulf/Steam-Client/compare/v5.0.3...v6.0.0) (2026-07-13)


### ⚠ BREAKING CHANGES

* Shortcut() now takes ShortcutData instead of a dict; ShortcutEntry has been removed.

### Features

* model shortcuts.vdf with ShortcutData dataclass ([#17](https://github.com/Garulf/Steam-Client/issues/17)) ([cfcb6cf](https://github.com/Garulf/Steam-Client/commit/cfcb6cfad26c3170621dc718753db2898e00adb7))

## [5.0.3](https://github.com/Garulf/Steam-Client/compare/v5.0.2...v5.0.3) (2026-07-09)


### Bug Fixes

* shortcut id generation ([#15](https://github.com/Garulf/Steam-Client/issues/15)) ([df1e37a](https://github.com/Garulf/Steam-Client/commit/df1e37a22399cf82c0e2a8811148aa82041c4910))

## [5.0.2](https://github.com/Garulf/Steam-Client/compare/v5.0.1...v5.0.2) (2026-07-08)


### Bug Fixes

* resolve game assets from assetcache.vdf ([#13](https://github.com/Garulf/Steam-Client/issues/13)) ([e4c9ef4](https://github.com/Garulf/Steam-Client/commit/e4c9ef49607f58e77f8e4e17e7280f5a8941ac41))

## [5.0.1](https://github.com/Garulf/Steam-Client/compare/v5.0.0...v5.0.1) (2026-07-05)


### Performance Improvements

* scan game icon directory with os.scandir instead of iterdir+stat ([#10](https://github.com/Garulf/Steam-Client/issues/10)) ([d094aa1](https://github.com/Garulf/Steam-Client/commit/d094aa18a00e2fa44f8d75b562f12e02b4c86624))

## [5.0.0](https://github.com/Garulf/Steam-Client/compare/v4.1.2...v5.0.0) (2026-07-04)


### ⚠ BREAKING CHANGES

* Steam.library_folders renamed to library_folders_file; Steam.command() and LINUX_STEAM_PATH removed; Steam.base_path is now a pathlib.Path; the Commands class is replaced by module-level functions, with SteamWindows renamed to SteamWindow and open() to open_window(); Library.all() renamed to all_apps(); LibraryFolder.get_games() renamed to games(); LoginUser.steam_id3 renamed to account_id; get_steam_from_registry() renamed to steam_install_path_from_registry().

### Features

* add release-please automated release workflow ([d8e068f](https://github.com/Garulf/Steam-Client/commit/d8e068f78b4c738ec7c68723d04ae56e2a13cf32))
* code quality overhaul with breaking API cleanup ([#8](https://github.com/Garulf/Steam-Client/issues/8)) ([86c4e57](https://github.com/Garulf/Steam-Client/commit/86c4e577af7c6bfcce4863daae83c5a443ea5dfe))

## Changelog
