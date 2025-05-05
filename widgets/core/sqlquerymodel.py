from typing import overload, Union, Optional, Any, Dict, List

from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex, QAbstractTableModel, QByteArray
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlError, QSqlRecord, QSqlDriver, QSqlField
from overrides import override


class SqlQueryModel(QAbstractTableModel):
    query: QSqlQuery
    error: QSqlError
    bottom: QModelIndex
    rec: QSqlRecord
    atEnd: bool
    headers: Dict
    colOffsets: List
    nestedResetLevel: int
    qsql_prefetch: int

    def __init__(self,
                 parent: Optional[Union[QModelIndex, QPersistentModelIndex]] = None,
                 qsql_prefetch: int = 255
                 ) -> None:
        super().__init__(parent)

        self.query = QSqlQuery()
        self.error = QSqlError()
        self.bottom = QModelIndex()
        self.rec = QSqlRecord()
        self.atEnd = False
        self.headers = {}
        self.colOffsets = []
        self.nestedResetLevel = 0
        self.qsql_prefetch = qsql_prefetch

    def prefetch(self, limit: int) -> None:
        # print("Prefetching", limit)
        if self.atEnd or limit <= self.bottom.row() or self.bottom.column() == -1:
            return

        newBottom: QModelIndex
        oldBottomRow = max(self.bottom.row(), 0)

        # try to seek directly
        if self.query.seek(limit):
            newBottom = self.createIndex(limit, self.bottom.column())

        # have to seek back to our old position for MS Access
        else:
            i = oldBottomRow
            if self.query.seek(i):
                while self.query.next():
                    i += 1
                newBottom = self.createIndex(i, self.bottom.column())
            else:
                # empty or invalid query
                newBottom = self.createIndex(-1, self.bottom.column())
            self.atEnd = True

        if newBottom.row() >= 0 and newBottom.row() > self.bottom.row():
            self.beginInsertRows(QModelIndex(), self.bottom.row() + 1, newBottom.row())
            self.bottom = newBottom
            self.endInsertRows()
        else:
            self.bottom = newBottom

    def initColOffsets(self, size: int) -> None:
        self.colOffsets = [0] * size

    def columnInQuery(self, modelColumn: int) -> int:
        if modelColumn < 0 or modelColumn >= self.rec.count() or not self.rec.isGenerated(
                modelColumn) or modelColumn >= len(self.colOffsets):
            return -1
        return modelColumn - self.colOffsets[modelColumn]

    @override
    def fetchMore(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> None:
        if parent.isValid():
            return
        self.prefetch(max(self.bottom.row(), 0) + self.qsql_prefetch)

    @override
    def canFetchMore(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> bool:
        return not parent.isValid() and not self.atEnd

    @override
    def roleNames(self) -> Dict[int, QByteArray]:
        return {Qt.ItemDataRole.DisplayRole: QByteArray(b"display")}

    @override
    def beginInsertRows(self, parent: Union[QModelIndex, QPersistentModelIndex], first: int, last: int) -> None:
        if not self.nestedResetLevel:
            super().beginInsertRows(parent, first, last)

    @override
    def endInsertRows(self) -> None:
        if not self.nestedResetLevel:
            super().endInsertRows()

    @override
    def beginRemoveRows(self, parent: Union[QModelIndex, QPersistentModelIndex], first: int, last: int) -> None:
        if not self.nestedResetLevel:
            super().beginRemoveRows(parent, first, last)

    @override
    def endRemoveRows(self) -> None:
        if not self.nestedResetLevel:
            super().endRemoveRows()

    @override
    def beginInsertColumns(self, parent: Union[QModelIndex, QPersistentModelIndex], first: int, last: int) -> None:
        if not self.nestedResetLevel:
            super().beginInsertColumns(parent, first, last)

    @override
    def endInsertColumns(self) -> None:
        if not self.nestedResetLevel:
            super().endInsertColumns()

    @override
    def beginRemoveColumns(self, parent: Union[QModelIndex, QPersistentModelIndex], first: int, last: int) -> None:
        if not self.nestedResetLevel:
            super().beginRemoveColumns(parent, first, last)

    @override
    def endRemoveColumns(self) -> None:
        if not self.nestedResetLevel:
            super().endRemoveColumns()

    @override
    def beginResetModel(self) -> None:
        if not self.nestedResetLevel:
            super().beginResetModel()
        self.nestedResetLevel += 1

    @override
    def endResetModel(self) -> None:
        self.nestedResetLevel -= 1
        if not self.nestedResetLevel:
            super().endResetModel()

    @override
    def rowCount(self, index: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()
                 ) -> int:
        return 0 if index.isValid() else self.bottom.row() + 1

    @override
    def columnCount(self, index: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()
                    ) -> int:
        return 0 if index.isValid() else self.rec.count()

    @override
    def data(self, item: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole
             ) -> Any:
        if not item.isValid():
            return None

        if role not in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            return None

        if not self.rec.isGenerated(item.column()):
            return None

        dItem: QModelIndex = self.indexInQuery(item)
        if dItem.row() > self.bottom.row():
            self.prefetch(dItem.row())

        if not self.query.seek(dItem.row()):
            self.error = self.query.lastError()
            return None

        return self.query.value(dItem.column())

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
                   ) -> Any:
        if orientation == Qt.Orientation.Horizontal and section in self.headers:
            val = self.headers[section].value(role)

            if role == Qt.ItemDataRole.DisplayRole and not val.isValid():
                val = self.headers[section].value(Qt.ItemDataRole.EditRole)
            if val.isValid():
                return val

            if role == Qt.ItemDataRole.DisplayRole and self.rec.count() > section or self.columnInQuery(section) != -1:
                return self.rec.fieldName(section)

        return super().headerData(section, orientation, role)

    @override
    def setHeaderData(self, section: int, orientation: Qt.Orientation, value: Any,
                      role: int = Qt.ItemDataRole.DisplayRole
                      ) -> bool:
        if orientation != Qt.Orientation.Horizontal or section < 0 or self.columnCount() <= section:
            return False

        if section not in self.headers:
            self.headers[section] = {}
        self.headers[section][role] = value
        self.headerDataChanged.emit(orientation, section, section)
        return True

    @override
    def insertColumns(self, column: int, count: int, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()
                      ) -> bool:
        if count <= 0 or parent.isValid() or column < 0 or column > self.rec.count():
            return False

        self.beginInsertColumns(parent, column, column + count - 1)
        for c in range(count):
            field: QSqlField = QSqlField()
            field.setReadOnly(True)
            field.setGenerated(False)
            self.rec.insert(column, field)
            if len(self.colOffsets) < self.rec.count():
                nVal = self.colOffsets[len(self.colOffsets) - 1] if len(self.colOffsets) else 0
                self.colOffsets.append(nVal)
                assert len(self.colOffsets) >= self.rec.count()

            for i in range(column + 1, len(self.colOffsets)):
                self.colOffsets[i] += 1

        self.endInsertColumns()
        return True

    @override
    def removeColumns(self, column: int, count: int, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()
                      ) -> bool:
        if count <= 0 or parent.isValid() or column < 0 or column >= self.rec.count():
            return False

        self.beginRemoveColumns(parent, column, column + count - 1)

        for i in range(count):
            self.rec.remove(column)

        for i in range(column, len(self.colOffsets)):
            self.colOffsets[i] -= count

        self.endRemoveColumns()
        return True

    @overload
    def setQuery(self, query: QSqlQuery) -> None:
        ...

    @overload
    def setQuery(self, query: str, db: QSqlDatabase) -> None:
        ...

    def setQuery(self, query: Union[QSqlQuery, str], db: Optional[QSqlDatabase] = None) -> None:
        if isinstance(query, str):
            assert db is not None
            query = QSqlQuery(query, db)

        self.beginResetModel()

        newRec: QSqlRecord = query.record()
        columnsChanged: bool = newRec != self.rec

        if len(self.colOffsets) != newRec.count() or columnsChanged:
            self.initColOffsets(newRec.count())

        self.bottom = QModelIndex()
        self.error = QSqlError()
        self.query = query
        self.rec = newRec
        self.atEnd = True

        if self.query.isForwardOnly():
            self.error = QSqlError("Forward-only queries cannot be used in a data model", "",
                                   QSqlError.ErrorType.ConnectionError)
            self.endResetModel()
            return

        if not self.query.isActive():
            self.error = self.query.lastError()
            self.endResetModel()
            return

        if self.query.driver().hasFeature(QSqlDriver.DriverFeature.QuerySize) and self.query.size() > 0:
            self.bottom = self.createIndex(self.query.size() - 1, self.rec.count() - 1)
        else:
            self.bottom = self.createIndex(-1, self.rec.count() - 1)
            self.atEnd = False

        self.fetchMore()

        self.endResetModel()
        self.queryChange()

    def clear(self) -> None:
        self.beginResetModel()
        self.error = QSqlError()
        self.atEnd = True
        self.query.clear()
        self.rec.clear()
        self.colOffsets.clear()
        self.bottom = QModelIndex()
        self.headers.clear()
        self.endResetModel()

    def lastError(self) -> QSqlError:
        return self.error

    def setLastError(self, error: QSqlError):
        self.error = error

    def queryChange(self) -> None:
        ...

    def indexInQuery(self, item: QModelIndex) -> QModelIndex:
        modelColumn: int = self.columnInQuery(item.column())
        if modelColumn < 0:
            return QModelIndex()

        return self.createIndex(item.row(), modelColumn, item.internalPointer())

    @overload
    def record(self) -> QSqlRecord:
        ...

    @overload
    def record(self, row: int) -> QSqlRecord:
        ...

    def record(self, row: Optional[int] = None) -> QSqlRecord:
        if row is None:
            return self.rec

        if row < 0:
            return self.rec

        rec: QSqlRecord = self.rec
        for i in range(self.rec.count()):
            self.rec.setValue(i, self.data(self.createIndex(row, i), Qt.ItemDataRole.EditRole))
        return rec