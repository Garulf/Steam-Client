# Changelog

## [5.0.0](https://github.com/Garulf/Steam-Client/compare/v4.1.2...v5.0.0) (2026-07-04)


### ⚠ BREAKING CHANGES

* Steam.library_folders renamed to library_folders_file; Steam.command() and LINUX_STEAM_PATH removed; Steam.base_path is now a pathlib.Path; the Commands class is replaced by module-level functions, with SteamWindows renamed to SteamWindow and open() to open_window(); Library.all() renamed to all_apps(); LibraryFolder.get_games() renamed to games(); LoginUser.steam_id3 renamed to account_id; get_steam_from_registry() renamed to steam_install_path_from_registry().

### Features

* add release-please automated release workflow ([d8e068f](https://github.com/Garulf/Steam-Client/commit/d8e068f78b4c738ec7c68723d04ae56e2a13cf32))
* code quality overhaul with breaking API cleanup ([#8](https://github.com/Garulf/Steam-Client/issues/8)) ([86c4e57](https://github.com/Garulf/Steam-Client/commit/86c4e577af7c6bfcce4863daae83c5a443ea5dfe))

## Changelog
