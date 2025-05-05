from typing import Optional

from PySide6.QtCore import (QRunnable, QAbstractItemModel)
from PySide6.QtSql import (QSqlDatabase)

from services import GSQLService, Transaction
from widgets.viewedit.runnables.worker_signals import WorkerSignals

import random


class UpdateLabelRunnable(QRunnable):
    def __init__(self,
                 old_category: str,
                 new_category: str,
                 similarity_group: Optional[int] = None):
        super().__init__()
        self.old_category = old_category
        self.new_category = new_category
        self.similarity_group = similarity_group
        self.conn_name = "update_label"
        self.signals = WorkerSignals()

    def run(self):
        db_handle = GSQLService.get_or_create_connection(self.conn_name)
        try:
            # Update category
            GSQLService.update_label(db_handle, self.old_category, self.new_category,
                                     None if isinstance(self.similarity_group, str) else self.similarity_group)

            db_handle.close()
            del db_handle
            QSqlDatabase.removeDatabase(self.conn_name)
            self.signals.finished.emit()
            self.signals.succeeded.emit()
        except Exception as e:
            print("UpdateLabelRunnable: ", e)
            db_handle.close()
            del db_handle
            QSqlDatabase.removeDatabase(self.conn_name)
            self.signals.finished.emit()
            self.signals.failed.emit()
