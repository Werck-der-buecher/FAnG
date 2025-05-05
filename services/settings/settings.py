from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional, List
from pathlib import Path

from services.settings.settings_errors import InstantiationError, SettingsError, SettingsNotFoundError

DEBUG_LEVELS: List[str] = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "EXCEPTION"]

DEFAULTS: Dict[str, Any] = {
    # docker_service
    "docker_image_ocrd": 'flojoko/ocrd:latest',
    "docker_image_classifier": 'flojoko/glyphclassifier:latest',
    "max_pool_size": 1,

    # import
    "dpi": 600,
    "auto_convert": False,
    "numerical_ids": False,
    "workspace_parallelization": 'batch',
    "batch_size": 50,
    "mime_types": {'png': ('*.png', 'image/png'),
                   'jpeg': ('*.jpeg', 'image/jpeg'),
                   'jpg': ('*.jpg', 'image/jpeg'),
                   'tif': ('*.tif', 'image/tiff'),
                   'tiff': ('*.tif', 'image/tiff')},

    # ocrd
    "model_dir": Path.cwd().joinpath('models').as_posix(),

    # settings from settings tab
    "similarity_sort": "hdbscan",
    "temp_store": "file",
    "autosave": True,
    "app_theme": "light",

    # database
    "db_name": 'glyphs',

    # scripts
    "debug_level": 'INFO',
    "print_startup_log": True,
}
SETTINGS_FILENAME = "wdb_appsettings.conf"
DEFAULT_SETTINGS_PATH: str = str(Path.home().joinpath(".config", SETTINGS_FILENAME))


class Settings(object):
    """
    Manager responsible for interacting with WdB Glyph Extraction settings.
    See:
    https://github.com/KatharaFramework/Kathara/blob/fa03cea989d6be8ebdad179cb90cb2fc1b012787/src/Kathara/
    setting/Setting.py
    """
    __slots__ = ['docker_image_ocrd', 'docker_image_classifier', 'max_pool_size', 'dpi', 'auto_convert',
                 'numerical_ids', 'workspace_parallelization', 'batch_size', 'mime_types', 'model_dir',
                 'similarity_sort', 'temp_store', 'autosave', 'app_theme', 'db_name', 'debug_level',
                 'print_startup_log', 'last_checked', 'version']

    VERSION = 1.0

    __instance: Settings = None

    @staticmethod
    def get_instance() -> Settings:
        if Settings.__instance is None:
            Settings()

        return Settings.__instance

    def __init__(self) -> None:
        if Settings.__instance is not None:
            raise InstantiationError("This class is a singleton!")
        else:
            # Load default parameters to use
            for (name, value) in DEFAULTS.items():
                setattr(self, name, value)
            self.last_checked: float = time.time()
            self.version: float = Settings.VERSION
            Settings.__instance = self

    def load(self, path: Optional[str] = None) -> Dict:
        """Load settings from path on disk.

        Args:
            path (Optional[str]): A path where the .conf file is stored. If None, default path is used.

        Returns:
            None

        Raises:
            SettingsNotFound: If the settings file is not found in specified path.
            SettingsError: If the specified file is not a valid JSON.
        """
        settings_path = Path(path).joinpath(SETTINGS_FILENAME) if path is not None else Path(DEFAULT_SETTINGS_PATH)
        if not settings_path.exists():  # Requested adapters file doesn't exist, throw exception
            raise SettingsNotFoundError(settings_path.as_posix())
        else:  # Requested settings file exists, read it and check values
            settings = {}
            with open(settings_path, 'r') as settings_file:
                try:
                    settings = json.load(settings_file)
                except ValueError:
                    raise SettingsError("Not a valid JSON.")

            for name, value in settings.items():
                if hasattr(self, name):
                    setattr(self, name, value)

            return settings

    def save(self, path: Optional[str] = None) -> None:
        """Saves adapters to a .conf file in the specified path on disk.

        Args:
            path (Optional[str]): A path where the .conf file will be stored. If None, default path is used.

        Returns:
            None
        """
        settings_path = Path(path).joinpath(SETTINGS_FILENAME) if path is not None else Path(DEFAULT_SETTINGS_PATH)
        settings_path.parent.mkdir(exist_ok=True)  # Create folder if it doesn't exist
        to_save = self._to_dict()

        with open(settings_path, 'w') as settings_file:
            settings_file.write(json.dumps(to_save, indent=True))

    def reset(self):
        try:
            self.load()
        except SettingsNotFoundError:
            for (name, value) in DEFAULTS.items():
                setattr(self, name, value)
            self.last_checked: float = time.time()
            self.version: float = Settings.VERSION

    def wipe_file(self) -> None:
        """Remove adapters from the default adapters path on disk.

        Returns:
            None
        """
        if Path(DEFAULT_SETTINGS_PATH).exists():
            os.remove(DEFAULT_SETTINGS_PATH)

    def load_from_dict(self, settings: Dict[str, Any]) -> None:
        """Load settings from a dict.

        Args:
            settings (Dict[str, Any]): A dict containing the adapters name as key and its value.

        Returns:
            None
        """
        for name, value in settings.items():
            if hasattr(self, name):
                setattr(self, name, value)

    def _to_dict(self) -> Dict[str, Any]:
        return {'docker_image_ocrd': self.docker_image_ocrd,
                'docker_image_classifier': self.docker_image_classifier,
                'max_pool_size': self.max_pool_size,
                'dpi': self.dpi,
                'auto_convert': self.auto_convert,
                'numerical_ids': self.numerical_ids,
                'workspace_parallelization': self.workspace_parallelization,
                'batch_size': self.batch_size,
                'mime_types': self.mime_types,
                'model_dir': self.model_dir,
                'similarity_sort': self.similarity_sort,
                'temp_store': self.temp_store,
                'autosave': self.autosave,
                'app_theme': self.app_theme,
                'db_name': self.db_name,
                'debug_level': self.debug_level,
                'print_startup_log': self.print_startup_log,
                'last_checked': self.last_checked}
