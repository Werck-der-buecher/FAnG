from typing import Optional

from PySide6.QtCore import (QRunnable, QAbstractItemModel)
from PySide6.QtSql import (QSqlDatabase)

from services import GSQLService, Transaction
from widgets.viewedit.runnables.worker_signals import WorkerSignals

from injector import inject
from services import GSQLService, WorkspacePersistenceService


class UpdateStatusRunnable(QRunnable):
    @inject
    def __init__(self,
                 gsql_service: GSQLService,
                 encoding: str,
                 old_status: int,
                 new_status: int):
        super().__init__()
        self.gsql = gsql_service
        self.encoding = encoding
        self.old_status = old_status
        self.new_status = new_status
        self.conn_name = "delete_encoding"
        self.signals = WorkerSignals()

    def run(self):
        db_handle = self.gsql.get_or_create_connection(self.conn_name)
        try:
            # Update category
            self.gsql.update_encoding_status(db_handle, self.encoding, self.new_status)
            db_handle.close()
            QSqlDatabase.removeDatabase(self.conn_name)
            self.signals.finished.emit()
            self.signals.succeeded.emit()
        except Exception as e:
            print("UpdateStatusRunnable: ", e)
            db_handle.close()
            QSqlDatabase.removeDatabase(self.conn_name)
            self.signals.finished.emit()
            self.signals.failed.emit()
