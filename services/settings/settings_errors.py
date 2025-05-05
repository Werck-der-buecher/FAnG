class SettingsError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Settings file is not valid: {message} Fix it or delete it before launching.")


class SettingsNotFoundError(Exception):
    def __init__(self, path: str) -> None:
        super().__init__(f"Settings file not found in path `{path}`.")


class InstantiationError(Exception):
    pass