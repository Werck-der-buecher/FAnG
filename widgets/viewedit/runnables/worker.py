from PySide6.QtCore import QRunnable
from widgets.viewedit.runnables.worker_signals import WorkerSignals


class FunctionWorker(QRunnable):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.signals = WorkerSignals()

    def run(self) -> None:
        self.func()


class Worker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @staticmethod
    def create(func):
        return FunctionWorker(func)



