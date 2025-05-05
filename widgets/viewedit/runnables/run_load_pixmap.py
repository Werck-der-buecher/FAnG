from PySide6.QtCore import (QRunnable, QDir, QFile)
from PySide6.QtGui import QPixmap

from widgets.viewedit.runnables.worker_signals import WorkerSignals


class LoadPixmapRunnable(QRunnable):
    def __init__(self, img_dir: str, img_filename: str) -> None:
        super().__init__()
        self.img_dir = img_dir
        self.img_filename = img_filename

        self.signals = WorkerSignals()

    def run(self):
        try:
            abs_file_path = QDir(self.img_dir).absoluteFilePath(self.img_filename)
            pixmap = QPixmap()
            success = pixmap.load(abs_file_path)

            if success:
                self.signals.succeeded.emit()
                self.signals.payload.emit({"pixmap": pixmap})
                self.signals.finished.emit()
            else:
                self.signals.failed.emit()


        except Exception as e:
            self.signals.failed.emit()
            self.signals.finished.emit()
