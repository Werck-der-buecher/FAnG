class WorkspaceSavingError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Save state file is not valid: {message} Fix it or delete it before launching.")


class WorkspaceSaveStateNotFoundError(Exception):
    def __init__(self, path: str) -> None:
        super().__init__(f"Save state file not found in path `{path}`.")