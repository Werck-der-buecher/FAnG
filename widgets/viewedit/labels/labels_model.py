from typing import Optional, Union, Any, List, Tuple

import numpy as np
from PySide6.QtCore import Signal, QObject, QThreadPool, QModelIndex, QPersistentModelIndex, Qt, QMimeData, QDataStream, \
    QIODevice, Slot
from PySide6.QtSql import QSqlQueryModel, QSqlQuery
from injector import inject

from services import GSQLService, GSQLSchema, WorkspacePersistenceService
from widgets.viewedit.constants import Constants
from widgets.viewedit.labels.labels_roles import LabelRole


class LabelsSqlModel(QSqlQueryModel):
    labels_changed = Signal(list)

    @inject
    def __init__(self,
                 persistence: WorkspacePersistenceService,
                 gsql_service: GSQLService,
                 parent: Optional[QObject] = None
                 ) -> None:
        super().__init__(parent)

        # services
        self.persistence = persistence
        self.gsql = gsql_service

        self._current_label = None
        self._threadpool = QThreadPool()

    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.NoItemFlags

        default_flags = super(QSqlQueryModel, self).flags(index)

        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDropEnabled | default_flags
        elif index.column() == 1:
            return default_flags
        elif index.column() == 2:
            return default_flags
        elif index.column() == 3:
            return Qt.ItemFlag.ItemIsEditable | default_flags  # & ~Qt.ItemFlag.ItemIsSelectable
        else:
            return Qt.NoItemFlags

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == LabelRole.label or (role == Qt.ItemDataRole.DisplayRole and index.column() == 0):
            enc = super().data(index.siblingAtColumn(0), Qt.ItemDataRole.DisplayRole)
            similarity = super().data(index.siblingAtColumn(1), Qt.ItemDataRole.DisplayRole)
            if (enc, similarity) in self.persistence.cache.delete_labels:
                return f"{enc} → DELETE" # → 🗑
            if enc in self.persistence.cache.delete_encodings:
                return f"{enc} → REMOVE" # → 🗑
            reassign = self.persistence.cache.reassign_labels.get((enc, similarity))
            if reassign is not None:
                return f"{enc} → {reassign}"
            return enc
        elif role == LabelRole.similarity or (role == Qt.ItemDataRole.DisplayRole and index.column() == 1):
            return super().data(index.siblingAtColumn(1), Qt.ItemDataRole.DisplayRole)
        elif role == LabelRole.count or (role == Qt.ItemDataRole.DisplayRole and index.column() == 2):
            return super().data(index.siblingAtColumn(2), Qt.ItemDataRole.DisplayRole)
        elif role == LabelRole.status or (role == Qt.ItemDataRole.DisplayRole and index.column() == 3):
            enc = super().data(index.siblingAtColumn(0), Qt.ItemDataRole.DisplayRole)
            cached_status = self.persistence.cache.status_labels.get(enc)
            if cached_status is None:
                return super().data(index.siblingAtColumn(3), Qt.ItemDataRole.DisplayRole)
            return cached_status
        elif role == LabelRole.label_persistent:
            return super().data(index.siblingAtColumn(0), Qt.ItemDataRole.DisplayRole)
        elif role == LabelRole.similarity_persistent:
            return super().data(index.siblingAtColumn(1), Qt.ItemDataRole.DisplayRole)
        elif role == LabelRole.count_persistent:
            return super().data(index.siblingAtColumn(2), Qt.ItemDataRole.DisplayRole)
        elif role == LabelRole.status_persistent:
            return super().data(index.siblingAtColumn(3), Qt.ItemDataRole.DisplayRole)
        return super().data(index, role)

    def setData(self, index: Union[QModelIndex, QPersistentModelIndex], value: Any, role: int = Qt.ItemDataRole.DisplayRole) -> bool:

        if not index.isValid():
            return False

        row, column = index.row(), index.column()
        if row >= self.rowCount() or row < 0:
            return False

        if role == LabelRole.label or (role == Qt.ItemDataRole.EditRole and index.column() == 0):
            new_cat = value
            curr_cat = index.data(LabelRole.label_persistent)
            curr_similarity = index.data(LabelRole.similarity_persistent)
            if new_cat == curr_cat:
                return False
            elif new_cat == Constants.CATEGORY_DELETED:
                self.persistence.cache.add_delete_labels(curr_cat, curr_similarity)
            else:
                self.persistence.cache.add_reassign_labels(curr_cat, new_cat, curr_similarity)
            self.dataChanged.emit(index, index)
            return True

        elif role == LabelRole.status or (role == Qt.ItemDataRole.EditRole and index.column() == 3):
            new_status = value
            enc = index.data(LabelRole.label_persistent)
            curr_status = index.data(LabelRole.status)
            persistent_status = index.data(LabelRole.status_persistent)
            if new_status == curr_status:
                return False
            elif new_status == persistent_status:
                self.persistence.cache.remove_status_labels(enc)
            else:
                self.persistence.cache.add_status_labels(enc, new_status)
            self.dataChanged.emit(index, index)
            return True

        return False

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int,
                        parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        if not data.hasFormat("application/vnd.sql_fields"):
            return False

        return True

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int,
                     parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if action == Qt.DropAction.IgnoreAction:
            return True

        encoded_data = data.data("application/vnd.sql_fields")
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.ReadOnly)

        target_label = parent.data(Qt.ItemDataRole.DisplayRole)
        uids = []
        while not stream.atEnd():
            file_id = stream.readQString()
            glyph_id = stream.readQString()
            uids.append((file_id, glyph_id))
        self.flag_dropped_uids_for_reassign(uids, target_label)
        return True

    def fetchMore(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> None:
        while self.canFetchMore(parent):
            super().fetchMore(parent)

    #def fetchMore(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> None:
    #    super().fetchMore(parent)

    def canFetchMore(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> bool:
        #print("CanFetchMore . . ?", super().canFetchMore(parent))
        return super().canFetchMore(parent)

    def flag_dropped_uids_for_delete(self, dropped_uids: List[Tuple[str, str]]):
        if not len(dropped_uids):
            return

        uid: Tuple[str, str]
        for uid in dropped_uids:
            self.persistence.cache.add_delete_glyph(uid, self.persistence.current_label)

    def flag_dropped_uids_for_reassign(self, dropped_uids: List[Tuple[str, str]], target_label: str):
        if not len(dropped_uids):
            return

        if target_label == Constants.CATEGORY_DELETED:
            self.flag_dropped_uids_for_delete(dropped_uids)
            return

        uid: Tuple[str, str]
        for uid in dropped_uids:
            self.persistence.cache.add_reassign_glyph(uid, target_label, self.persistence.current_label)

    @Slot(bool)
    def refresh(self):
        db_handle = self.gsql.get_or_create_connection("labels")
        query = QSqlQuery(GSQLSchema.SELECT_LABEL_VIEW, db_handle)
        query.exec()
        self.setQuery(query)
        db_handle.close()
        self.labels_changed.emit(self.get_visible_labels())

    def get_visible_labels(self) -> List[str]:
        return np.unique([self.index(ridx, 0).data(Qt.ItemDataRole.DisplayRole) for ridx in
                          range(self.rowCount())]).tolist()

    @Slot(str, Any)
    def on_request_remove_label(self, label: str, similarity: Union[int, None]) -> None:
        self.persistence.cache.add_delete_labels(label, similarity)

    @Slot(str, Any, str)
    def on_request_reassign_label(self, label: str, similarity: Union[int, None], target_label: str) -> None:
        self.persistence.cache.add_reassign_labels(label, target_label, similarity)

    @Slot(str)
    def on_request_remove_encoding(self, label: str) -> None:
        self.persistence.cache.add_delete_encodings(label)

    @Slot(str, Any)
    def on_request_revert(self, label: str, similarity: Union[int, None]) -> None:
        self.persistence.cache.remove_reassign_labels(label, similarity)
        self.persistence.cache.remove_delete_labels(label, similarity)
        self.persistence.cache.remove_delete_encodings(label)
