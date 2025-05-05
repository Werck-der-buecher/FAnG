import logging
import time

from PySide6.QtCore import (QRunnable)
from injector import inject

from services import WorkspacePersistenceService
from widgets.viewedit.glyphs.glyphs_model import GlyphSortingOrder
from widgets.viewedit.runnables.worker_signals import WorkerSignals


class AutoSaveRunner(QRunnable):
    @inject
    def __init__(self, workspace_path: str, persistence_service: WorkspacePersistenceService):
        super().__init__()
        self.workspace_path = workspace_path
        self.persistence = persistence_service

        self.signals = WorkerSignals()

    def run(self):
        try:
            self.persistence.last_saved = time.time()
            self.persistence.save_to_disk(self.workspace_path)

            self.signals.succeeded.emit()
            self.signals.finished.emit()

        except Exception as e:
            logging.error("AutoSaveRunner: ", e)
            self.signals.failed.emit()
            self.signals.finished.emit()
