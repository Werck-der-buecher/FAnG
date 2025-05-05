from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union, Tuple

from PySide6.QtCore import QObject, Signal, Slot
from injector import inject

from services.sql_service import GSQLService
from services.workspace.bookmark import WorkspaceBookmarkService
from services.workspace.cache import WorkspaceCacheService
from services.workspace.persistence_errors import WorkspaceSavingError, WorkspaceSaveStateNotFoundError


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


DEFAULTS: Dict[str, Any] = {
    # worspace configuration
    "current_label": None,
    "current_similarity": None,
    "sorting_strategy": None,
    "sorting_order": None,
}

DEFAULT_SAVESTATE_FILENAME = "autosave.json"
DEPRECATED_SAVESTATE_FILENMAE = "autosave.alog"


class WorkspacePersistenceService(QObject):
    __slots__ = ['current_label',
                 'current_similarity',
                 'sorting_strategy',
                 'sorting_order',
                 'last_saved',
                 'version']

    # Signals
    about_to_load = Signal()
    about_to_save = Signal()
    about_to_exit = Signal()

    loaded = Signal()
    saved = Signal()
    exited = Signal()

    pending_edits_changed = Signal(int)

    # Versioning
    VERSION = 1.1

    @inject
    def __init__(self, gsql_service: GSQLService, caching_service: WorkspaceCacheService, bookmark_service: WorkspaceBookmarkService):
        super().__init__()

        for (name, value) in DEFAULTS.items():
            setattr(self, name, value)
        self.last_saved: float = time.time()
        self.version: float = WorkspacePersistenceService.VERSION

        self._gsql_service = gsql_service
        self._caching_service = caching_service
        self._bookmark_service = bookmark_service

    @property
    def bookmarks(self) -> WorkspaceBookmarkService:
        return self._bookmark_service

    @property
    def cache(self) -> WorkspaceCacheService:
        return self._caching_service

    @Slot(str)
    def set_current_label(self, value: str) -> None:
        self.current_label = value

    @Slot()
    def set_current_similarity(self, value: Union[None, int]):
        self.current_similarity = value

    @Slot(str)
    def set_current_sorting_strategy(self, value: str) -> None:
        self.current_sorting_strategy = value

    @Slot(bool)
    def set_current_sorting_order(self, value: bool) -> None:
        self.current_sorting_order = value

    def load_from_disk(self, path: str) -> None:
        """Load adapters from a specific path on disk.

        Args:
            path (Optional[str]): A path where the kathara.conf file is stored. If None, default path is used.

        Returns:
            None

        Raises:
            SaveStateNotFoundError: If the SaveState file is not found in specified path.
            SaveStateError: If the specified file is not a valid JSON.
        """
        save_path = Path(path).joinpath(DEFAULT_SAVESTATE_FILENAME)

        if not save_path.exists():  # Requested adapters file doesn't exist, throw exception
            raise WorkspaceSaveStateNotFoundError(save_path.as_posix())
        else:  # Requested adapters file exists, read it and check values
            settings = {}
            with open(save_path, 'r') as settings_file:
                try:
                    settings = json.load(settings_file)
                except ValueError:
                    raise WorkspaceSavingError("Not a valid JSON.")

            for name, value in settings.items():
                if hasattr(self, name):
                    if name.casefold() == 'cache'.casefold():
                        self.cache.from_dict(value)
                    elif name.casefold() == 'bookmarks'.casefold():
                        self.bookmarks.from_dict(value)
                    else:
                        setattr(self, name, value)

    def save_to_disk(self, path: str) -> None:
        """Saves adapters to a .conf file in the specified path on disk.

        Args:
            path (Optional[str]): A path where the .conf file will be stored. If None, default path is used.

        Returns:
            None
        """
        save_path = Path(path).joinpath(DEFAULT_SAVESTATE_FILENAME)
        save_path.parent.mkdir(exist_ok=True)  # Create folder if it doesn't exist
        to_save = self.to_dict()

        with open(save_path, 'w') as savestate_file:
            savestate_file.write(json.dumps(to_save, indent=True, cls=SetEncoder))

        deprecated_save_path = Path(path).joinpath(DEPRECATED_SAVESTATE_FILENMAE)
        if deprecated_save_path.exists():
            deprecated_save_path.unlink()

    def from_dict(self, settings: Dict[str, Any]) -> None:
        """Load adapters from a dict.

        Args:
            settings (Dict[str, Any]): A dict containing the adapters name as key and its value.

        Returns:
            None
        """
        for name, value in settings.items():
            if hasattr(self, name):
                if name.casefold() == 'cache'.casefold():
                    self.cache.from_dict(value)
                elif name.casefold() == 'bookmarks'.casefold():
                    self.bookmarks.from_dict(value)
                else:
                    setattr(self, name, value)

    def to_dict(self) -> Dict[str, Any]:
        return {'current_label': self.current_label,
                'current_similarity': self.current_similarity,
                'sorting_strategy': self.sorting_strategy,
                'sorting_order': self.sorting_order,
                'cache': self.cache.to_dict(),
                'bookmarks': self.bookmarks.to_dict(),
                'last_saved': self.last_saved,
                'version': self.version}
