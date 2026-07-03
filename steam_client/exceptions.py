class SteamNotFoundError(FileNotFoundError):
    """Raised when a required Steam data file is missing.

    This usually means Steam is not installed at the given base path.
    """
