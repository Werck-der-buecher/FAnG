from PySide6.QtWidgets import (QListView, QWidget, QApplication, QMenu)
from PySide6.QtCore import (Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint, QItemSelection,
                            QItemSelectionModel, QModelIndex, QRect, Slot, Signal)
from PySide6.QtGui import (QMouseEvent, QKeyEvent, QDrag, QResizeEvent, QIcon, QAction)
from typing import Optional
from app_icons import AppIcons
from functools import partial
from typing import List, Tuple
from widgets.viewedit.glyphs.glyphs_roles import GlyphRole


class GlyphsListView(QListView):
    flag_marked_delete = Signal()
    flag_marked_reassign = Signal(str)
    flag_selection_delete = Signal()
    flag_selection_reassign = Signal(str)
    flag_selection_clear = Signal()
    flag_selection_bookmark = Signal()

    request_shape_info = Signal()
    request_toggle_glyph_details = Signal()
    request_similarity_calc = Signal()
    request_locate_glyph = Signal()

    request_jump_bookmark = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.drag_start_position = QPoint()
        self.possibly_preserve_selection_post_click = False
        self.user_visible_columns = 0
        self.user_visible_rows = 0

        # Currently visible labels
        self._current_visible_labels = []

    @Slot(bool)
    def on_pause_updates(self, pause):
        """ Explicitely pause updates (e.g., during heavy rebuilds)"""
        self.setUpdatesEnabled(not pause)

    @Slot(list)
    def on_visible_labels_changed(self, labels: List[str]):
        """ Update information about what labels are currently displayed in the list view"""
        self._current_visible_labels = labels
        self._current_visible_labels.sort(key=lambda x: (len(x), x.swapcase(), x.casefold()))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self.flag_selection_delete.emit()
        elif event.key() == Qt.Key.Key_Q:
            self.request_locate_glyph.emit()

        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            event_pos = self.viewport().mapToGlobal(event.pos())
            self.display_context_menu(event_pos)
        elif event.buttons() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            clicked_row = index.row()

            if clicked_row >= 0:
                rect: QRect = self.visualRect(index)
                delegate = self.itemDelegate(index)
                checkboxRect = delegate.getCheckBoxRect(rect)
                checkbox_clicked = checkboxRect.contains(event.pos())
                if not checkbox_clicked and clicked_row >= 0:
                    pass
                else:
                    self.possibly_preserve_selection_post_click = True
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super(GlyphsListView, self).mouseMoveEvent(event)
        if event.buttons() != Qt.MouseButton.LeftButton:
            return

        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # Encode data according to mime type
        mime_data = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        for index in self.selectionModel().selectedIndexes():
            if index.isValid():
                r, c = index.row(), index.column()
                file_id = self.model().index(r, c + 1).data(Qt.ItemDataRole.DisplayRole)
                glyph_id = self.model().index(r, c + 2).data(Qt.ItemDataRole.DisplayRole)
                stream << file_id << glyph_id

        mime_data.setData("application/vnd.sql_fields", encodedData)

        # Initiate drag event
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.DropAction.MoveAction)

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        super().selectionChanged(deselected, selected)
        if self.possibly_preserve_selection_post_click:
            self.possibly_preserve_selection_post_click = False

            current = self.currentIndex()
            if not (len(selected.indexes()) == 1 and selected.indexes()[0] == current):
                deselected.merge(self.selectionModel().selection(), QItemSelectionModel.Select)
                self.selectionModel().select(deselected, QItemSelectionModel.Select)

    def top_row_index(self) -> Optional[QModelIndex]:
        # index of top left item

        index: QModelIndex
        for y_off in [10, 20, 30]:
            index: QModelIndex = self.indexAt(QPoint(self.spacing(), self.spacing() + y_off))
            if not index.isValid():
                continue

            # Determine index of item in user visible row with the earliest time
            row = index.row()
            indices = [index.sibling(row + i, 0) for i in range(self.user_visible_columns)]

            # Filter out invalid indicies
            indices = [idx for idx in indices if idx.isValid()]
            if not len(indices):
                continue

            # Get the index with the earliest time
            # Inspiration: https://stackoverflow.com/a/11825864
            data = [idx.data() for idx in indices]
            index_min = min(range(len(data)), key=data.__getitem__)
            return indices[index_min]
        return None

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Resize, then calculate and store how many columns the user sees
        """
        super().resizeEvent(event)
        spacing = self.spacing()
        item_width = self.itemDelegate().fixedSizeHint.width() + spacing
        view_width = self.viewport().contentsRect().width() - spacing - 1
        item_height = self.itemDelegate().fixedSizeHint.height() + spacing
        view_height = self.viewport().contentsRect().height() - spacing - 1

        self.user_visible_columns = view_width // item_width
        self.user_visible_rows = view_height // item_height

    def display_context_menu(self, event_pos):
        menu = QMenu(self)

        # retrieve icons for the different menu options
        pstyle = self.parent().style()
        del_icon = AppIcons.get_icon(AppIcons.ICON_DELETE, pstyle)
        assign_icon = AppIcons.get_icon(AppIcons.ICON_TRANSFER, pstyle)
        clear_edit_icon = AppIcons.get_icon(AppIcons.ICON_REVERT, pstyle)
        delete_marks_icon = AppIcons.get_icon(AppIcons.ICON_DELETE, pstyle)
        assign_marks_icon = AppIcons.get_icon(AppIcons.ICON_TRANSFER, pstyle)
        details_icon = AppIcons.get_icon(AppIcons.ICON_CHECK, pstyle) if self.itemDelegate()._show_details else QIcon(None)
        bookmarks_icon = AppIcons.get_icon(AppIcons.ICON_BOOKMARK, pstyle)
        bookmarks_jump_icon = AppIcons.get_icon(AppIcons.ICON_BOOKMARK_JUMP, pstyle)
        glyph_locate_icon = AppIcons.get_icon(AppIcons.ICON_GLYPH_LOCATE, pstyle)

        # set bookmarking options
        bookmark_sel_action = QAction(bookmarks_icon, self.tr("&Set bookmark"), self)
        bookmark_sel_action.setStatusTip(self.tr("Set a custom bookmark that can be jumped to"))
        bookmark_sel_action.triggered.connect(self.flag_selection_bookmark.emit)
        menu.addAction(bookmark_sel_action)

        jump_bookmark_submenu = menu.addMenu(bookmarks_jump_icon, self.tr("Jump to ..."))
        for dlbl, bookmark_mode in zip(['Custom bookmark', 'Last selection', 'Last deletion', 'Last reassignment', ],
                                       ['custom', 'select', 'delete', 'reassign']):
            assign_action = QAction(dlbl, self)
            assign_action.setStatusTip(self.tr(f"Jump to bookmark for the current label according to the '{dlbl}'"))
            assign_action.triggered.connect(partial(self.request_jump_bookmark.emit, bookmark_mode))
            jump_bookmark_submenu.addAction(assign_action)

        menu.addSeparator()
        # flag items for deletion
        delete_sel_action = QAction(del_icon, self.tr("&Delete selection"), self)
        delete_sel_action.setStatusTip(self.tr("Delete currently selected items"))
        delete_sel_action.triggered.connect(self.flag_selection_delete.emit)
        menu.addAction(delete_sel_action)

        # flag items for reassign
        assign_sel_submenu = menu.addMenu(assign_icon, self.tr("Assign selection to ..."))
        assign_sel_submenu.setStyleSheet("QMenu { menu-scrollable: 1; }")
        for dlbl in self._current_visible_labels:
            assign_action = QAction(dlbl, self)
            assign_action.setStatusTip(self.tr(f"Assign currently selected items to category: '{dlbl}'"))
            assign_action.triggered.connect(partial(self.flag_selection_reassign.emit, dlbl))
            assign_sel_submenu.addAction(assign_action)

        # clear item deletion/reassignment
        clear_sel_action = QAction(clear_edit_icon, self.tr("&Clear selection"), self)
        clear_sel_action.setStatusTip(self.tr("Reset currently selected items and keep them in the current category"))
        clear_sel_action.triggered.connect(self.flag_selection_clear.emit)
        menu.addAction(clear_sel_action)

        # flag marked items for deletion
        menu.addSeparator()
        delete_marked_action = QAction(delete_marks_icon, self.tr("&Delete marked items"), self)
        delete_marked_action.setStatusTip(self.tr("Delete currently marked items"))
        delete_marked_action.triggered.connect(self.flag_marked_delete.emit)
        menu.addAction(delete_marked_action)

        # flag marked items for reassign
        assign_marked_submenu = menu.addMenu(assign_marks_icon, self.tr("Assign marked items to ..."))
        assign_marked_submenu.setStyleSheet("QMenu { menu-scrollable: 1; }")
        for dlbl in self._current_visible_labels:
            assign_action = QAction(dlbl, self)
            assign_action.setStatusTip(self.tr(f"Assign currently marked items to category: '{dlbl}'"))
            assign_action.triggered.connect(partial(self.flag_marked_reassign.emit, dlbl))
            assign_marked_submenu.addAction(assign_action)

        menu.addSeparator()
        # show glyph details
        show_details_action = QAction(details_icon, "Show/Hide details")
        show_details_action.triggered.connect(self.request_toggle_glyph_details.emit)
        menu.addAction(show_details_action)

        # show glyph statistics
        show_shapestats_action = QAction("Show shape statistics")
        show_shapestats_action.triggered.connect(self.request_shape_info.emit)
        menu.addAction(show_shapestats_action)

        # caclulate similarities
        calculate_similarity_action = QAction("(Re)calculate similarities")
        calculate_similarity_action.triggered.connect(self.request_similarity_calc.emit)
        menu.addAction(calculate_similarity_action)

        menu.addSeparator()
        locate_glyph_action = QAction(glyph_locate_icon, "Locate glyph in source image")
        locate_glyph_action.triggered.connect(self.request_locate_glyph.emit)
        menu.addAction(locate_glyph_action)

        # call menu with the specified options
        menu.exec(event_pos)

