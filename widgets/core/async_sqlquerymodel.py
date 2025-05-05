from PySide6.QtSql import QSqlQueryModel, QSqlQuery, QSqlDatabase, QSqlDriver
from PySide6.QtCore import QObject, QThread, Signal, Slot, QModelIndex, QPersistentModelIndex

from typing import Optional, Union, List, Any
from .sqlquerymodel import SqlQueryModel


class QueryWorker(QObject):
    started = Signal()

    finished = Signal(QSqlQuery)
    error = Signal(Exception)

    def __init__(self, db_handle: QSqlDatabase, sql_statement: str,
                 bind_values: Optional[List[Union[str, int, None]]] = None):
        super().__init__()
        self.db_handle = db_handle
        self.sql_statement = sql_statement
        self.bind_values = bind_values

    @Slot()
    def run(self):
        try:
            self.started.emit()
            self.db_handle.open()
            query = QSqlQuery(self.db_handle)
            query.prepare(self.sql_statement)
            if self.bind_values is not None:
                for bv in self.bind_values:
                    query.addBindValue(bv)
            query.exec()
            while query.next():
                pass
            self.db_handle.close()
            self.finished.emit(query)
        except Exception as e:
            self.error.emit(e)


class AsyncSqlQueryModel(SqlQueryModel):
    aboutToProcess = Signal()
    processed = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.thread = None
        self.worker = None

        self.working = False

    def setAsyncQuery(self,
                      db_connection: QSqlDatabase,
                      query: str,
                      bind_values: Optional[List[Union[str, int, None]]] = None):
        if self.working:
            return

        self.working = True
        self.aboutToProcess.emit()
        self.thread = QThread()
        self.worker = QueryWorker(db_connection, query, bind_values)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_query_finished)
        self.worker.error.connect(self.on_query_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.start()

    @Slot(QSqlQuery)
    def on_query_finished(self, query):
        super().setQuery(query)
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.processed.emit(True)
        self.working = False

    @Slot(Exception)
    def on_query_error(self, error):
        print(error)
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.processed.emit(False)
