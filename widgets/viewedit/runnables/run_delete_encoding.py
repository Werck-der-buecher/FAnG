from typing import Optional

from PySide6.QtCore import (QRunnable, QAbstractItemModel)
from PySide6.QtSql import (QSqlDatabase)

from services import GSQLService, Transaction
from widgets.viewedit.runnables.worker_signals import WorkerSignals
from widgets.viewedit.constants import Constants

import random


class DeleteEncodingRunnable(QRunnable):
    def __init__(self,
                 encoding: str):
        super().__init__()
        self.encoding = encoding
        self.conn_name = "delete_encoding"
        self.signals = WorkerSignals()

    def run(self):
        db_handle = GSQLService.get_or_create_connection(self.conn_name)
        try:
            # Update category
            with Transaction(db_handle, name='delete_encoding', close_conn_on_exit=True):
                GSQLService.update_label(db_handle, self.encoding, Constants.CATEGORY_DELETED, None)
                GSQLService.delete_encoding(db_handle, self.encoding)

            db_handle.close()
            del db_handle
            QSqlDatabase.removeDatabase(self.conn_name)
            self.signals.finished.emit()
            self.signals.succeeded.emit()
        except Exception as e:
            print("DeleteEncodingRunnable: ", e)
            db_handle.close()
            del db_handle
            QSqlDatabase.removeDatabase(self.conn_name)
            self.signals.finished.emit()
            self.signals.failed.emit()
