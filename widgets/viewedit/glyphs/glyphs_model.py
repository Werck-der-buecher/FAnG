import io
import re
from enum import IntEnum, Enum
from typing import Optional, Set, Tuple, Union, Any, List, Sequence

import numpy as np
from PIL import Image
from PySide6.QtCore import Signal, QObject, QTimeLine, QEasingCurve, QModelIndex, QPersistentModelIndex, Qt, QByteArray, \
    QRect, QMimeData, QDataStream, QIODevice, Slot, QItemSelection, QItemSelectionModel
from PySide6.QtGui import QPixmap
from PySide6.QtSql import QSqlQueryModel, QSqlQuery, QSqlDatabase

from services import GSQLService, GSQLSchema, WorkspacePersistenceService
from app_utils import runs
from widgets.viewedit.constants import Constants

from injector import inject

from widgets.viewedit.glyphs.glyphs_roles import GlyphRole

# from widgets.core.async_querymodel import AsyncSQLQueryModel
from widgets.core.async_sqlquerymodel import AsyncSqlQueryModel


class GlyphSortingStrategy(Enum):
    DEFAULT = "None"
    UID = "Unique ID"
    HEIGHT = "Height"
    WIDTH = "Width"
    SIZE = "Size"
    ENERGY = "Energy"
    SCORE = "Score"
    SIMILARITY = "Similarity"


class GlyphSortingOrder(IntEnum):
    ASC = 0
    DESC = 1


GlyphSortingDict = {
    (GlyphSortingStrategy.DEFAULT, GlyphSortingOrder.ASC): None,
    (GlyphSortingStrategy.DEFAULT, GlyphSortingOrder.DESC): None,
    (GlyphSortingStrategy.UID, GlyphSortingOrder.ASC): GSQLSchema._ORDER_BY_UID_ASC,
    (GlyphSortingStrategy.UID, GlyphSortingOrder.DESC): GSQLSchema._ORDER_BY_UID_DESC,

    (GlyphSortingStrategy.HEIGHT, GlyphSortingOrder.ASC): GSQLSchema._ORDER_BY_HEIGHT_ASC,
    (GlyphSortingStrategy.HEIGHT, GlyphSortingOrder.DESC): GSQLSchema._ORDER_BY_HEIGHT_DESC,
    (GlyphSortingStrategy.WIDTH, GlyphSortingOrder.ASC): GSQLSchema._ORDER_BY_WIDTH_ASC,
    (GlyphSortingStrategy.WIDTH, GlyphSortingOrder.DESC): GSQLSchema._ORDER_BY_WIDTH_DESC,
    (GlyphSortingStrategy.SIZE, GlyphSortingOrder.ASC): GSQLSchema._ORDER_BY_SIZE_ASC,
    (GlyphSortingStrategy.SIZE, GlyphSortingOrder.DESC): GSQLSchema._ORDER_BY_SIZE_DESC,

    (GlyphSortingStrategy.ENERGY, GlyphSortingOrder.ASC): GSQLSchema._ORDER_BY_ENERGY_ASC,
    (GlyphSortingStrategy.ENERGY, GlyphSortingOrder.DESC): GSQLSchema._ORDER_BY_ENERGY_DESC,
    (GlyphSortingStrategy.SCORE, GlyphSortingOrder.ASC): GSQLSchema._ORDER_BY_SCORE_ASC,
    (GlyphSortingStrategy.SCORE, GlyphSortingOrder.DESC): GSQLSchema._ORDER_BY_SCORE_DESC,

    (GlyphSortingStrategy.SIMILARITY, GlyphSortingOrder.ASC): GSQLSchema._ORDER_BY_SIMILARITY_ASC,
    (GlyphSortingStrategy.SIMILARITY, GlyphSortingOrder.DESC): GSQLSchema._ORDER_BY_SIMILARITY_DESC
}


class GlyphsSQLModel(AsyncSqlQueryModel):
    fetch_count_changed = Signal(int, int)

    @inject
    def __init__(self,
                 gsql_service: GSQLService,
                 persistence_service: WorkspacePersistenceService,
                 selection_model: QItemSelectionModel,
                 parent: Optional[QObject] = None
                 ) -> None:
        super().__init__(parent=parent)

        # services
        self.gsql = gsql_service
        self.persistence = persistence_service
        self.selection_model = selection_model

        # properties
        self._img_crop = 0
        self._scale_factor = 1.0

        # fields
        self.current_label = None
        self.current_sim_group = None
        self.current_label_max_count = 0
        self.sorting_strategy = GlyphSortingStrategy.DEFAULT
        self.sorting_order = GlyphSortingOrder.ASC

        # Highlighting
        self.highlighted_uids: Set[Tuple[str, str]] = set()
        self.highlighted_rows: Set[int] = set()
        self.highlighting_timeline = QTimeLine(Constants.FadeMilliseconds // 2)
        self.highlighting_timeline.setEasingCurve(QEasingCurve.Type.SineCurve)
        self.highlighting_timeline.frameChanged.connect(self.on_highlight_requested)
        self.highlighting_timeline.setLoopCount(2)
        self.highlighting_timeline.finished.connect(self.highlight_phase_finished)
        self.highlighting_timeline_mint = 0
        self.highlighting_timeline_max = Constants.FadeSteps
        self.highlighting_timeline.setFrameRange(self.highlighting_timeline_mint, self.highlighting_timeline_max)
        self.highlight_value = 0

        # signals
        self.dataChanged.connect(self.persistence.cache.notify_pending_edits)
        self.aboutToProcess.connect(self.beginResetModel)
        self.processed.connect(self.endResetModel)

    @property
    def img_crop(self):
        return self._img_crop

    @img_crop.setter
    def img_crop(self, img_crop: int):
        self._img_crop = img_crop

    @property
    def scale_factor(self):
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, scale_factor: float):
        self._scale_factor = scale_factor

    @property
    def current_label_count(self) -> int:
        return self.current_label_max_count

    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        elif index.column() != 0:
            return Qt.ItemFlag.NoItemFlags
        else:
            default_flags = super().flags(index)
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | default_flags

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = ...) -> Any:
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()
        if column == 0:
            file_id = index.siblingAtColumn(1).data(Qt.ItemDataRole.DisplayRole)
            glyph_id = index.siblingAtColumn(2).data(Qt.ItemDataRole.DisplayRole)
            uid = (file_id, glyph_id)

            if role in [Qt.ItemDataRole.DisplayRole, GlyphRole.uid]:
                return uid
            elif role == GlyphRole.filename:
                static_prefix = "OCR-D-EXTGLYPHS-tesseract_"
                return file_id[len(static_prefix):]
            elif role == Qt.ItemDataRole.DecorationRole:
                ba: QByteArray = super().data(index, Qt.ItemDataRole.DisplayRole)
                pixmap = QPixmap()
                load_status = pixmap.loadFromData(ba, "PNG")
                assert load_status
                if self.img_crop > 0:
                    H, W = pixmap.height(), pixmap.width()
                    crop_spec = QRect(self.img_crop, self.img_crop, W - 2 * self.img_crop, H - 2 * self.img_crop)
                    pixmap = pixmap.copy(crop_spec)
                if self.scale_factor != 1.0:
                    pixmap = pixmap.scaledToHeight(pixmap.height() * self.scale_factor,
                                                   Qt.TransformationMode.FastTransformation)
                return pixmap
            elif role == GlyphRole.highlight:
                return self.highlight_value if (uid in self.highlighted_uids) else 0
            elif role == Qt.ItemDataRole.CheckStateRole:
                return Qt.CheckState.Checked if uid in self.persistence.cache.marked_glyphs else Qt.CheckState.Unchecked
            elif role == GlyphRole.marked:
                return uid in self.persistence.cache.marked_glyphs
            elif role == GlyphRole.delete:
                return uid in self.persistence.cache.delete_glyphs
            elif role == GlyphRole.reassign:
                return self.persistence.cache.reassign_glyphs.get(uid, None)
            elif role == GlyphRole.custom_bookmark:
                custom = self.persistence.bookmarks.custom.get((self.current_label, self.current_sim_group), None)
                return custom == [uid, row]
            elif role == GlyphRole.cached:
                return uid in self.persistence.cache.delete_glyphs or uid in self.persistence.cache.reassign_glyphs
            elif role == GlyphRole.uid_str:
                return f"{file_id}_{glyph_id}"
            elif role == GlyphRole.height:
                return index.siblingAtColumn(3).data(Qt.ItemDataRole.DisplayRole)
            elif role == GlyphRole.width:
                return index.siblingAtColumn(4).data(Qt.ItemDataRole.DisplayRole)
            elif role == GlyphRole.extension:
                return index.siblingAtColumn(5).data(Qt.ItemDataRole.DisplayRole)
            elif role == GlyphRole.img_ndarray:
                ba: QByteArray = super().data(index, Qt.ItemDataRole.DisplayRole)
                image = Image.open(io.BytesIO(ba.data()))
                return np.array(image)
            elif role == GlyphRole.position_abs:
                pos_str: str = index.siblingAtColumn(6).data(Qt.ItemDataRole.DisplayRole)
                if pos_str is not None and len(pos_str):
                    bbox = [float(xy) for xy in pos_str.split('_')]
                    return bbox

            elif role == GlyphRole.position_rel:
                pos_str: str = index.siblingAtColumn(7).data(Qt.ItemDataRole.DisplayRole)
                if pos_str is not None and len(pos_str):
                    bbox = [float(xy) for xy in pos_str.split('_')]
                    return bbox
            return

        return super().data(index, role)

    def setData(self, index: Union[QModelIndex, QPersistentModelIndex], value: Any,
                role: int = Qt.ItemDataRole.DisplayRole) -> bool:
        if not index.isValid():
            return False

        row = index.row()
        if row >= self.rowCount() or row < 0:
            return False

        file_id = index.siblingAtColumn(1).data(Qt.ItemDataRole.DisplayRole)
        glyph_id = index.siblingAtColumn(2).data(Qt.ItemDataRole.DisplayRole)
        uid = (file_id, glyph_id)

        if role == Qt.CheckStateRole:
            if value:
                self.persistence.cache.add_mark_glyph(uid)
            else:
                self.persistence.cache.remove_mark_glyph(uid)
            self.dataChanged.emit(index, index)
            return True
        elif role == GlyphRole.delete:
            if value:
                self.persistence.cache.add_delete_glyph(uid, self.current_label)
            else:
                self.persistence.cache.remove_delete_glyph(uid, self.current_label)
            self.dataChanged.emit(index, index)
            return True
        elif role == GlyphRole.reassign:
            if isinstance(value, bool):
                if not value:
                    self.persistence.cache.remove_reassign_glyph(uid, self.current_label)
                    self.dataChanged.emit(index, index)
            elif isinstance(value, str):
                self.persistence.cache.add_reassign_glyph(uid, value, self.current_label)
                self.dataChanged.emit(index, index)
            else:
                return False
            return True
        elif role == GlyphRole.custom_bookmark:
            self.persistence.bookmarks.add_custom(self.current_label, self.current_sim_group, uid, row)
            self.dataChanged.emit(index, index)
            return True
        return False

    def mimeTypes(self) -> List[str]:
        return ["application/vnd.sql_fields"]

    def mimeData(self, indexes: Sequence[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        encodedData = QByteArray()

        stream = QDataStream(encodedData, QIODevice.WriteOnly)

        for index in indexes:
            if index.isValid():
                c = index.column()
                file_id = index.siblingAtColumn(c + 1).data(Qt.ItemDataRole.DisplayRole)
                glyph_id = index.siblingAtColumn(c + 2).data(Qt.ItemDataRole.DisplayRole)
                stream << file_id << glyph_id

        mime_data.setData("application/vnd.sql_fields", encodedData)
        return mime_data

    @Slot(str, str, int)
    def update_query(self, label: str, order_by: Optional[str] = None, similarity_group: Optional[int] = None):

        # We don't want to retain markings upon changing the label category.
        self.persistence.cache.clear_marks()

        # Query from database
        db_handle = self.gsql.get_or_create_connection("glyphs", open=False)
        statement = GSQLSchema.SELECT_GLYPHS + (order_by if order_by is not None else "")
        bind_values = ([label, similarity_group])
        self.setAsyncQuery(db_handle, statement, bind_values)

        self.current_label = label
        self.current_sim_group = similarity_group
        db_handle = self.gsql.get_or_create_connection("label_count")
        self.current_label_max_count = self.gsql.get_label_count(db_handle, label, similarity_group)
        db_handle.close()

    @Slot(bool, int)
    def refresh(self, prefetch: bool = True, fetch_until: int = None):
        """
        :param suppress_signal: Boolean value indicating whether to suppress the model reset signal. Default is False.
        :param prefetch: Boolean value indicating whether to prefetch data from the database. Default is True.
        :param fetch_until: Integer value indicating until which row to fetch data from the database. Default is None.
        :return: None

        This method refreshes the model data by updating the query and fetching new data from the database. It takes three optional parameters:
        - `prefetch`: Set this to False to disable prefetching data from the database. By default, it is set to True.
        - `fetch_until`: Set this to an integer value indicating until which row to fetch data from the database. By default, it is set to None.

        Example usage:
        ```python
        model = GlyphsSQLModel()
        model.refresh(suppress_signal=True, prefetch=True, fetch_until=100)
        ```
        """
        self.beginResetModel()

        # After committing the pending changes, we want to fetch enough items.
        if prefetch:
            if fetch_until is None:
                row_count = self.rowCount()
                current_view_changes = self.persistence.cache.num_pending_changes_for_label(self.current_label)
                fetch_until = max(256, row_count - current_view_changes)

        order_by = GlyphSortingDict.get((self.sorting_strategy, self.sorting_order), GSQLSchema._ORDER_BY_UID_ASC)
        sim_group = self.current_sim_group
        self.update_query(self.current_label, order_by=order_by, similarity_group=sim_group)

        if prefetch:
            self.fetch_until(fetch_until, self.index(-1, -1))

        self.endResetModel()

    @Slot(str)
    def set_sorting_strategy(self, sorting_strategy: str):
        self.sorting_strategy = GlyphSortingStrategy(sorting_strategy)

    @Slot(Qt.CheckState)
    def set_sorting_order(self, sorting_order: Qt.CheckState):
        if sorting_order == Qt.CheckState.Checked.value:
            self.sorting_order = GlyphSortingOrder.ASC
        else:
            self.sorting_order = GlyphSortingOrder.DESC

    def fetch_until(self, row: int, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> None:
        for _ in range(row // 256):
            super().fetchMore(parent)

    def start_highlight_glyphs(self, uids: Set[Tuple[str, str]], rows: Set[int]) -> None:
        # cuids = uids.difference(self.current_highlighted)
        # if not len(cuids):
        #    return
        self.reset_highlighting()
        self.set_highlighted(uids, rows)
        self.highlighting_timeline.setDirection(QTimeLine.Forward)
        self.highlighting_timeline.start()

    def set_highlighted(self, uids: Set[Tuple[str, str]], rows: Set[int]) -> None:
        self.highlighted_uids.clear()
        self.highlighted_rows.clear()
        for uid, row in zip(uids, rows):
            self.highlighted_uids.add(uid)
            self.highlighted_rows.add(row)

    def reset_highlighting(self) -> None:
        if len(self.highlighted_uids):
            self.highlighting_timeline.stop()
            self.on_highlight_requested(value=0)
            self.highlighted_uids.clear()
            self.highlighted_rows.clear()

    @Slot(int)
    def on_highlight_requested(self, value: int) -> None:
        self.highlight_value = value
        for first, last in runs(self.highlighted_rows):
            self.dataChanged.emit(self.index(first, 0), self.index(last, 0))

    @Slot()
    def highlight_phase_finished(self):
        self.highlighted_uids.clear()

    @Slot()
    def on_flag_selection_delete(self) -> None:
        """
        Flag current glyphs in the selection model for deletion. This propagates the UIDs of those glyphs to the
        cache service, where they are stored until persisting the changes to the DB.
        """
        if not self.selection_model.hasSelection():
            return

        selected: QItemSelection = self.selection_model.selection()
        idx: QModelIndex
        for idx in selected.indexes():
            self.setData(idx, True, GlyphRole.delete)

    @Slot(str)
    def on_flag_selection_reassign(self, target_label: str) -> None:
        """
        Flag current glyphs in the selection model for label reassignment. This propagates the UIDs of those glyphs
        to the cache service, where they are stored until persisting the changes to the DB.
        """
        if not self.selection_model.hasSelection():
            return
        if target_label == Constants.CATEGORY_DELETED:
            self.on_flag_selection_delete()
            return

        selected: QItemSelection = self.selection_model.selection()
        idx: QModelIndex
        for idx in selected.indexes():
            self.setData(idx, target_label, GlyphRole.reassign)

    @Slot()
    def on_flag_selection_clear(self) -> None:
        """
        Remove cache entries for all currently selected glyphs.
        """
        if not self.selection_model.hasSelection():
            return

        selected: QItemSelection = self.selection_model.selection()
        idx: QModelIndex
        for idx in selected.indexes():
            self.setData(idx, False, GlyphRole.delete)
            self.setData(idx, False, GlyphRole.reassign)

    @Slot()
    def on_flag_selection_bookmark(self) -> None:
        if not self.selection_model.hasSelection():
            return

        selected: QItemSelection = self.selection_model.selection()
        idx: QModelIndex = selected.indexes()[-1]
        self.setData(idx, None, GlyphRole.custom_bookmark)

    @Slot()
    def on_flag_marked_delete(self) -> None:
        """
        Flag current glyphs that are marked/checked for deletion. This propagates the UIDs of those glyphs to the
        cache service, where they are stored until persisting the changes to the DB.
        """
        if not len(self.persistence.cache.marked_glyphs):
            return

        uid: Tuple[str, str]
        for uid in self.persistence.cache.marked_glyphs:
            self.persistence.cache.add_delete_glyph(uid, self.current_label)

    @Slot(str)
    def on_flag_marked_reassign(self, target_label: str) -> None:
        """
        Flag current glyphs that are marked/checked for label reassignment. This propagates the UIDs of those glyphs
        to the cache service, where they are stored until persisting the changes to the DB.
        """
        if not len(self.persistence.cache.marked_glyphs):
            return

        uid: Tuple[str, str]
        for uid in self.persistence.cache.marked_glyphs:
            self.persistence.cache.add_reassign_glyph(uid, target_label, self.current_label)
