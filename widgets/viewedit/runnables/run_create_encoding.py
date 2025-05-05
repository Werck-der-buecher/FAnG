from PySide6.QtCore import (QRunnable)
from PySide6.QtSql import (QSqlDatabase)
from injector import inject

from services import GSQLService
from widgets.viewedit.runnables.worker_signals import WorkerSignals


class CreateEncodingRunnable(QRunnable):
    NUM_STAGES = 2

    @inject
    def __init__(self,
                 gsql_service: GSQLService,
                 encoding: str):
        super().__init__()
        self.gsql = gsql_service
        self.encoding = encoding
        self.conn_name = "create_encoding"
        self.messages = [
            f"Creating encoding <b>{self.encoding}</b>'",
            "Done"
        ]
        assert len(self.messages) == CreateEncodingRunnable.NUM_STAGES
        self.signals = WorkerSignals()

    def broadcast_status(self, prog: int) -> None:
        msg = self.messages[prog]
        msg = f"[{prog + 1}/{len(self.messages)}] {msg} ..."
        self.signals.progress.emit(prog)
        self.signals.status.emit(msg)

    def run(self):
        db_handle = self.gsql.get_or_create_connection(self.conn_name)

        try:
            # Fetch glyph images from database
            prog_count = 0
            self.broadcast_status(prog_count)

            # Update category
            self.gsql.insert_encoding(db_handle, self.encoding)

            prog_count = 1
            self.broadcast_status(prog_count)

            db_handle.close()
            QSqlDatabase.removeDatabase(self.conn_name)

            self.signals.succeeded.emit()
            self.signals.finished.emit()

        except Exception as e:
            print("CreateEncodingRunnable", e)
            db_handle.close()
            QSqlDatabase.removeDatabase(self.conn_name)

            self.signals.failed.emit()
            self.signals.finished.emit()
