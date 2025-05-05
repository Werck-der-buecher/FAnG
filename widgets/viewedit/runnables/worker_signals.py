from PySide6.QtCore import (Signal, QObject)


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    succeeded = Signal()
    failed = Signal()
    finished = Signal()
    progress = Signal(int)
    status = Signal(str)
    error = Signal(Exception)
    payload = Signal(dict)