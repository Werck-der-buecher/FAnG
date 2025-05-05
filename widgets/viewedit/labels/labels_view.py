from PySide6.QtWidgets import (QTreeView, QWidget, QApplication, QMenu)
from PySide6.QtCore import (Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint, QItemSelection,
                            QItemSelectionModel, QModelIndex, QRect, Slot, Signal, QEvent)
from PySide6.QtGui import (QMouseEvent, QKeyEvent, QDrag, QResizeEvent, QIcon, QAction)
from typing import Optional, List, Any
from app_icons import AppIcons
from functools import partial

from .labels_roles import LabelRole


class LabelsTreeView(QTreeView):
    request_new_encoding = Signal()
    # request_import_from_text = Signal()
    request_remove_labels = Signal(str, Any)
    request_reassign_label = Signal(str, Any, str)
    request_remove_encoding = Signal(str)
    request_revert = Signal(str, Any)
    request_edit_label = Signal(QModelIndex)
    request_sync_reload = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_request_context_menu)

        # Currently visible labels
        self._current_visible_labels = []

    @Slot(list)
    def on_visible_labels_changed(self, labels: List[str]):
        """ Update information about what labels are currently displayed in the list view"""
        self._current_visible_labels = labels
        self._current_visible_labels.sort(key=lambda x: (len(x), x.swapcase(), x.casefold()))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)

    @Slot(QPoint)
    def on_request_context_menu(self, pos: QPoint):
        event_pos = self.viewport().mapToGlobal(pos)

        menu = QMenu(self)

        index = self.indexAt(pos)
        label = index.data(LabelRole.label_persistent)
        similarity = index.data(LabelRole.similarity_persistent)

        # retrieve icons for the different menu options
        pstyle = self.parent().style()
        new_icon = AppIcons.get_icon(AppIcons.ICON_NEW, pstyle)
        text_icon = AppIcons.get_icon(AppIcons.ICON_TEXT, pstyle)
        import_icon = AppIcons.get_icon(AppIcons.ICON_IMPORT, pstyle)
        delete_icon = AppIcons.get_icon(AppIcons.ICON_DELETE, pstyle)
        delete_all_icon = AppIcons.get_icon(AppIcons.ICON_DELETE_ALL, pstyle)
        edit_icon = AppIcons.get_icon(AppIcons.ICON_EDIT, pstyle)
        transfer_icon = AppIcons.get_icon(AppIcons.ICON_TRANSFER, pstyle)
        processing_icon = AppIcons.get_icon(AppIcons.ICON_PROCESSING, pstyle)
        revert_icon = AppIcons.get_icon(AppIcons.ICON_REVERT, pstyle)

        # flag for new category creation
        new_action = QAction(new_icon, self.tr("&New category"), self)
        new_action.setStatusTip(self.tr("New label category"))
        new_action.triggered.connect(self.request_new_encoding.emit)
        menu.addAction(new_action)

        # flag for import
        # import_submenu = menu.addMenu(import_icon, self.tr("&Import"))
        # import_textfield_action = QAction(text_icon, self.tr("... from manual input"), self)
        # import_textfield_action.setStatusTip(self.tr("Import standard encoding schema from manual input"))
        # import_textfield_action.triggered.connect(self.request_import_from_text.emit)
        # import_submenu.addAction(import_textfield_action)

        # flag for delete
        menu.addSeparator()
        delete_action = QAction(delete_icon, self.tr("&Delete glyphs"), self)
        delete_action.setStatusTip(self.tr("Put all glyphs into the 'Deleted'"))
        delete_action.triggered.connect(partial(self.request_remove_labels.emit, label, similarity))
        delete_action.triggered.connect(partial(self.resizeColumnToContents, 0), Qt.ConnectionType.QueuedConnection)
        menu.addAction(delete_action)

        delete_all_action = QAction(delete_all_icon, self.tr("&Delete category"), self)
        delete_all_action.setStatusTip(self.tr("Delete category and all contained glyphs"))
        delete_all_action.triggered.connect(partial(self.request_remove_encoding.emit, label))
        delete_all_action.triggered.connect(partial(self.resizeColumnToContents, 0), Qt.ConnectionType.QueuedConnection)
        menu.addAction(delete_all_action)

        assign_submenu = menu.addMenu(transfer_icon, self.tr("&Assign to ..."))
        assign_submenu.setStyleSheet("QMenu { menu-scrollable: 1; }")
        for dlbl in self._current_visible_labels:
            assign_action = QAction(dlbl, self)
            assign_action.setStatusTip(self.tr(f"Assign to category: '{dlbl}'"))
            assign_action.triggered.connect(partial(self.request_reassign_label.emit, label, similarity, dlbl))
            assign_action.triggered.connect(partial(self.resizeColumnToContents, 0), Qt.ConnectionType.QueuedConnection)
            assign_submenu.addAction(assign_action)

        revert_action = QAction(revert_icon, self.tr("&Revert"))
        revert_action.setStatusTip(self.tr("Revert all current pending changes"))
        revert_action.triggered.connect(partial(self.request_revert.emit, label, similarity))
        menu.addAction(revert_action)

        menu.addSeparator()
        edit_action = QAction(edit_icon, self.tr("&Edit"), self)
        edit_action.setStatusTip(self.tr("Rename label category"))
        # edit_action.triggered.connect(partial(self.request_edit_label.emit, index))
        edit_action.triggered.connect(partial(self.edit, index))
        menu.addAction(edit_action)

        menu.addSeparator()
        refresh_action = QAction(processing_icon, self.tr("&Sync and Reload"), self)
        refresh_action.setStatusTip(self.tr("Sync and reload categories from disk"))
        refresh_action.triggered.connect(self.request_sync_reload.emit)
        menu.addAction(refresh_action)

        # Exec menu
        menu.exec(event_pos)
