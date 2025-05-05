from itertools import groupby
from typing import Any, Union, Optional

from PySide6.QtCore import QObject, QAbstractProxyModel, QPersistentModelIndex, QModelIndex, Qt, QMimeData, Signal, \
    QRectF, QSize, QEvent
from PySide6.QtGui import QColor, QFont, QPen
from PySide6.QtWidgets import QAbstractItemView, QTreeView, QStyledItemDelegate, QStyle
from injector import inject

from services import WorkspacePersistenceService
from widgets.viewedit.labels.labels_roles import LabelRole


class Item(object):
    """Base class for an Item in the Group By Proxy"""

    def __init__(self):
        self._parent = None
        self._children = []

    def parent(self):
        return self._parent

    def addChild(self, node):
        node._parent = self
        self._children.append(node)

    def rowCount(self):
        return len(self._children)

    def row(self):
        parent = self.parent()
        if not parent:
            return 0
        else:
            return self.parent().children().index(self)

    def columnCount(self):
        return 1

    def child(self, row):
        return self._children[row]

    def children(self):
        return self._children

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = ...):
        return None

    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]):
        return Qt.NoItemFlags


class ProxySectionItem(Item):
    def __init__(self,
                 group_label: str,
                 persistence: WorkspacePersistenceService
                 ):
        super().__init__()
        self.group_label = group_label
        self.persistence = persistence

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = ...):
        if role == LabelRole.label or (role == Qt.ItemDataRole.DisplayRole and index.column() == 0):
            if (self.group_label, None) in self.persistence.cache.delete_labels:
                return f"{self.group_label} → DELETE"
            if self.group_label in self.persistence.cache.delete_encodings:
                return f"{self.group_label} → REMOVE"
            reassign = self.persistence.cache.reassign_labels.get((self.group_label, None))
            if reassign is not None:
                return f"{self.group_label} → {reassign}"
            return self.group_label
        elif role == LabelRole.similarity or (role == Qt.ItemDataRole.DisplayRole and index.column() == 1):
            return None
        elif role == LabelRole.count or (role == Qt.ItemDataRole.DisplayRole and index.column() == 2):
            count = 0
            for c in self.children():
                if hasattr(c, 'source_index'):
                    count += c.source_index.data(LabelRole.count)
            return count
        elif role == LabelRole.status or (role == Qt.ItemDataRole.DisplayRole and index.column() == 3):
            if len(self.children()):
                return self.children()[0].source_index.data(LabelRole.status)
            return 0
        elif role == LabelRole.label_persistent:
            return self.group_label
        elif role == LabelRole.similarity_persistent:
            return None
        elif role == LabelRole.count_persistent:
            if len(self.children()):
                return self.children()[0].source_index.data(LabelRole.status)
            return 0
        elif role == LabelRole.status_persistent:
            if len(self.children()):
                return self.children()[0].source_index.data(LabelRole.status_persistent)
            return 0
        else:
            return None

    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]):
        if not index.isValid():
            return Qt.NoItemFlags

        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable
        elif index.column() == 1:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        elif index.column() == 2:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        elif index.column() == 3:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        else:
            return Qt.NoItemFlags


class ProxyItem(Item):
    def __init__(self, source_index: QModelIndex):
        super().__init__()
        self.source_index: QModelIndex = source_index

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = ...):
        return self.source_index.siblingAtColumn(index.column()).data(role)

    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


class GroupProxyModel(QAbstractProxyModel):
    """Proxy that groups by based on a specific role
    """
    @inject
    def __init__(self,
                 persistence: WorkspacePersistenceService,
                 parent: Optional[QObject] = None
                 ) -> None:
        super(GroupProxyModel, self).__init__(parent)
        self.persistence = persistence
        self.root = Item()
        self.group_role = LabelRole.label_persistent

    def setSourceModel(self, source):
        super(GroupProxyModel, self).setSourceModel(source)
        self.rebuild()

        self.sourceModel().modelReset.connect(self.rebuild)

    def set_group_role(self, role):
        self.group_role = role

    def groupby_key(self, source_index):
        """Returns the data to group by.

        Override this in subclasses to group by customized data instead of
        by simply the currently set group role.

        Args:
            source_index (QtCore.QModelIndex): index from source to retrieve
                data from to group by.

        Returns:
            object: Collected data to group by for index.

        """
        return source_index.data(self.group_role)

    def groupby_label(self, section):
        """Returns the label for a section based on the collected group key.

        Override this in subclasses to format the name for a specific key.

        Args:
            section: key value for this group section

        Returns:
            str: Label of the section header based on group key
        """
        return section

    def rebuild(self):
        """Update proxy sections and items
        This should be called after changes in the source model that require
        changes in this list (for example new indices, less indices or update
        sections)
        """

        # self.layoutAboutToBeChanged.emit()
        self.beginResetModel()

        # Start with new root node
        self.root = Item()

        # Get indices from source model
        source = self.sourceModel()
        source_rows = source.rowCount()
        source_indices = [source.index(i, 0) for i in range(source_rows)]

        for section, group in groupby(source_indices,
                                      key=self.groupby_key):

            # section
            label = self.groupby_label(section)
            section_item = ProxySectionItem(label, self.persistence)
            self.root.addChild(section_item)

            #  items in section
            for i, index in enumerate(group):
                proxy_item = ProxyItem(index)
                section_item.addChild(proxy_item)

        # for cr in self.root.children():
        #    for c in cr.children():
        #        if isinstance(c, ProxyItem):
        #            print("Rebuild: ", c, hasattr(c, 'source_index'))

        # self.layoutChanged.emit()
        self.endResetModel()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return

        node = index.internalPointer()
        if not node:
            return

        return node.data(index, role)

    def setData(self, index: Union[QModelIndex, QPersistentModelIndex], value: Any, role: int = ...) -> bool:
        if isinstance(index.internalPointer(), ProxySectionItem):
            # source_idx = index.internalPointer().children()[0].source_index
            edit_idx = index
        else:
            edit_idx = self.mapToSource(index)

        if not edit_idx.isValid():
            return False

        self.sourceModel().setData(edit_idx, value, role)
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        node = index.internalPointer()
        if not node:
            return Qt.NoItemFlags

        return node.flags(index)

    def is_header(self, index):
        """Return whether index is a header"""
        if index.isValid() and not self.mapToSource(index).isValid():
            return True
        else:
            return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        return self.sourceModel().headerData(section, orientation, role)

    def find_index(self, label: str, similarity: Union[int, None]) -> QModelIndex:
        for ridx in range(self.rowCount()):
            section_index = self.index(ridx, 0, QModelIndex())
            lbl = section_index.data(LabelRole.label_persistent)
            sim = section_index.data(LabelRole.similarity_persistent)
            if lbl == label and sim == similarity:
                return section_index

            for cidx in range(self.rowCount(section_index)):
                child_index = self.index(cidx, 0, section_index)
                lbl = child_index.data(LabelRole.label_persistent)
                sim = child_index.data(LabelRole.similarity_persistent)
                if lbl == label and sim == similarity:
                    return child_index
        return QModelIndex()

    def mapFromSource(self, index):
        for section_item in self.root.children():
            for item in section_item.children():
                if item.source_index == index:
                    return self.createIndex(item.row(),
                                            index.column(),
                                            item)

        return QModelIndex()

    def mapToSource(self, index):
        if not index.isValid():
            return QModelIndex()

        node = index.internalPointer()
        if not node:
            return QModelIndex()

        if not hasattr(node, "source_index"):
            return QModelIndex()

        return node.source_index

    def columnCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> int:
        if self.sourceModel():
            return self.sourceModel().columnCount(QModelIndex())
        else:
            return 0

    def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()):
        if not parent.isValid():
            node = self.root
        else:
            node = parent.internalPointer()
        if not node:
            return 0

        return node.rowCount()

    def index(self, row: int, column: int, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()
              ) -> QModelIndex:
        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()

        item = parent_node.child(row)
        if item:
            return self.createIndex(row, column, item)
        else:
            return QModelIndex()

    def buddy(self, index):
        return index

    def parent(self, index: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()):
        if not index.isValid():
            return QModelIndex()

        node = index.internalPointer()
        if not node:
            return QModelIndex()
        else:
            parent = node.parent()
            if not parent:
                return QModelIndex()

            row = parent.row()
            return self.createIndex(row, 0, parent)

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int,
                        parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        return self.sourceModel().canDropMimeData(data, action, row, column, parent)

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int,
                     parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        res = self.sourceModel().dropMimeData(data, action, row, column, parent)
        return res


class FamilyGroupProxy(GroupProxyModel):
    """Proxy grouping by order by full range known.

    Before Collectors and after Integrators will be grouped as "Other".

    """

    def groupby_key(self, source_index):
        families = super(FamilyGroupProxy,
                         self).groupby_key(source_index)
        family = families[0]
        return family


class View(QTreeView):
    # An item is requesting to be toggled, with optional forced-state
    toggled = Signal("QModelIndex", object)

    # An item is requesting details
    inspected = Signal("QModelIndex")

    def __init__(self, parent=None):
        super(View, self).__init__(parent)

        self.horizontalScrollBar().hide()
        self.viewport().setAttribute(Qt.WA_Hover, True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setVerticalScrollMode(QTreeView.ScrollPerPixel)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setIndentation(0)

    def event(self, event):
        if not event.type() == QEvent.KeyPress:
            return super(View, self).event(event)

        elif event.key() == Qt.Key_Space:
            for index in self.selectionModel().selectedIndexes():
                self.toggled.emit(index, None)

            return True

        elif event.key() == Qt.Key_Backspace:
            for index in self.selectionModel().selectedIndexes():
                self.toggled.emit(index, False)

            return True

        elif event.key() == Qt.Key_Return:
            for index in self.selectionModel().selectedIndexes():
                self.toggled.emit(index, True)

            return True

        return super(View, self).event(event)

    def focusOutEvent(self, event):
        self.selectionModel().clear()

    def leaveEvent(self, event):
        self._inspecting = False
        super(View, self).leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MidButton:
            index = self.indexAt(event.pos())
            self.inspected.emit(index) if index.isValid() else None

        return super(View, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            indexes = self.selectionModel().selectedIndexes()
            if len(indexes) <= 1 and event.pos().x() < 20:
                for index in indexes:
                    self.toggled.emit(index, None)

        return super(View, self).mouseReleaseEvent(event)


colors = {
    "warning": QColor("#ff4a4a"),
    "ok": QColor("#77AE24"),
    "active": QColor("#99CEEE"),
    "idle": Qt.white,
    "font": QColor("#DDD"),
    "inactive": QColor("#888"),
    "hover": QColor(255, 255, 255, 10),
    "selected": QColor(255, 255, 255, 20),
    "outline": QColor("#333"),
}

fonts = {
    "h3": QFont("Open Sans", 10, 900),
    "h4": QFont("Open Sans", 8, 400),
    "h5": QFont("Open Sans", 8, 800),
    "smallAwesome": QFont("FontAwesome", 8),
    "largeAwesome": QFont("FontAwesome", 16),
}


class Section(QStyledItemDelegate):
    """Generic delegate for section header"""

    def paint(self, painter, option, index):
        """Paint text
         _
        My label
        """

        body_rect = QRectF(option.rect)

        metrics = painter.fontMetrics()

        label_rect = QRectF(option.rect.adjusted(0, 2, 0, -2))

        assert label_rect.width() > 0

        label = index.data(Qt.DisplayRole)
        label = metrics.elidedText(label,
                                   Qt.ElideRight,
                                   label_rect.width())

        font_color = colors["idle"]
        if not index.data(Qt.UserRole + 3):
            font_color = colors["inactive"]

        # Maintain reference to state, so we can restore it once we're done
        painter.save()

        # Draw label
        painter.setFont(fonts["h4"])
        painter.setPen(QPen(font_color))
        painter.drawText(label_rect, label)

        if option.state & QStyle.State_MouseOver:
            painter.fillRect(body_rect, colors["hover"])

        if option.state & QStyle.State_Selected:
            painter.fillRect(body_rect, colors["selected"])

        # Ok, we're done, tidy up.
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 20)


class ItemAndSection(Item):
    """Generic delegate for model items in proxy tree view"""

    def paint(self, painter, option, index):
        model = index.model()
        if model.is_header(index):
            Section().paint(painter, option, index)
            return

        super(ItemAndSection, self).paint(painter, option, index)
