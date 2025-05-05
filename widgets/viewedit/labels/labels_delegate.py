from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt, QAbstractItemModel, Slot, QObject, \
    QItemSelectionModel, QRectF, QSize
from PySide6.QtGui import QPalette, QColor, QPainter, QFont, QPen
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle, QWidget, QComboBox

from app_icons import AppIcons
from services import Settings
from widgets.viewedit.labels.labels_roles import LabelRole
from widgets.viewedit.utils import CategoryStatus, CategoryStatusNameDict, CategoryStatusIconDict, \
    CategoryStatusColorDictLight, CategoryStatusColorDictDark

from typing import Optional

from injector import inject



colors = {
    "warning": QColor("#ff4a4a"),
    "ok": QColor("#77AE24"),
    "active": QColor("#99CEEE"),
    "idle": Qt.black,
    "font": QColor("#DDD"),
    "inactive": QColor("#888"),
    "hover": QColor(255, 255, 255, 10),
    "selected": QColor(255, 255, 255, 20),
    "outline": QColor("#333")
}


record_colors = {
    "DEBUG": QColor("#ff66e8"),
    "INFO": QColor("#66abff"),
    "WARNING": QColor("#ffba66"),
    "ERROR": QColor("#ff4d58"),
    "CRITICAL": QColor("#ff4f75"),
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

        label = index.data(LabelRole.label_persistent)
        label = metrics.elidedText(label,
                                   Qt.ElideRight,
                                   label_rect.width())

        font_color = colors["idle"]
        #if not index.data(LabelRole.):
        #    font_color = colors["inactive"]

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


class LabelItemDelegate(QStyledItemDelegate):
    @inject
    def __init__(self,
                 settings: Settings,
                 selection_model: QItemSelectionModel,
                 parent: Optional[QObject] = None
                 ) -> None:
        super().__init__(parent)
        self.settings = settings
        self.selection_model = selection_model

    def initStyleOption(self, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]) -> None:
        super().initStyleOption(option, index)
        if index.column() == 2:
            cg = QPalette.Normal if option.state & QStyle.StateFlag.State_Enabled else QPalette.Disabled
            if option.state & QStyle.StateFlag.State_Enabled:
                option.palette.setColor(cg, QPalette.ColorRole.HighlightedText, Qt.GlobalColor.darkGray)
            option.palette.setBrush(QPalette.ColorRole.Text, Qt.GlobalColor.gray)

        elif index.column() == 3:
            status: int = index.data(LabelRole.status)
            icon = AppIcons.get_icon(CategoryStatusIconDict.get(CategoryStatus(status)), self.parent().style())

            if self.settings.app_theme == "light":
                cat_colors = CategoryStatusColorDictLight.get(CategoryStatus(status))
                enabled_color = Qt.GlobalColor.green
            elif self.settings.app_theme == "dark":
                cat_colors = CategoryStatusColorDictDark.get(CategoryStatus(status))
                enabled_color = Qt.GlobalColor.black
            else:
                raise ValueError("App Theme not supported!")
            text_color = QColor(cat_colors[0])
            text = CategoryStatusNameDict.get(CategoryStatus(status))

            option.features |= QStyleOptionViewItem.HasDecoration
            option.icon = icon.pixmap(24)
            option.text = text

            cg = QPalette.Normal if option.state & QStyle.StateFlag.State_Enabled else QPalette.Disabled
            if option.state & QStyle.StateFlag.State_Enabled:
                option.palette.setColor(cg, QPalette.ColorRole.HighlightedText, enabled_color)
            option.palette.setBrush(QPalette.ColorRole.Text, text_color)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
        if index.column() == 3:
            editor = QComboBox(parent)
            editor.setFrame(False)
            editor.addItem(AppIcons.get_icon(AppIcons.ICON_UNPROCESSED, self.parent().style()),
                           CategoryStatusNameDict.get(CategoryStatus.UNPROCESSED))
            editor.addItem(AppIcons.get_icon(AppIcons.ICON_PENDING, self.parent().style()),
                           CategoryStatusNameDict.get(CategoryStatus.DIRTY))
            editor.addItem(AppIcons.get_icon(AppIcons.ICON_DONE, self.parent().style()),
                           CategoryStatusNameDict.get(CategoryStatus.PROCESSED))
            editor.activated.connect(self.commit_and_close_editor)
            return editor

        return super().createEditor(parent, option, index)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem,
                             index: Union[QModelIndex, QPersistentModelIndex]) -> None:
        editor.setGeometry(option.rect)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: Union[QModelIndex, QPersistentModelIndex]) -> None:
        op = QStyleOptionViewItem(option)

        #model = index.model()
        #if model.is_header(index):
        #    Section().paint(painter, option, index)
        #    return

        if index.column() == 3:
            status: int = index.data(LabelRole.status)
            if self.settings.app_theme == "light":
                cat_colors = CategoryStatusColorDictLight.get(CategoryStatus(status))
            elif self.settings.app_theme == "dark":
                cat_colors = CategoryStatusColorDictDark.get(CategoryStatus(status))
            else:
                raise ValueError("App Theme not supported!")
            background_color = QColor(cat_colors[1])
            painter.save()
            painter.fillRect(option.rect, background_color)
            painter.restore()

        super(LabelItemDelegate, self).paint(painter, op, index)

    def setEditorData(self, editor: QWidget, index: Union[QModelIndex, QPersistentModelIndex]) -> None:
        if index.column() == 3:
            editor: QComboBox
            value = index.model().data(index, LabelRole.status)
            editor.setCurrentIndex(value)
            editor.showPopup()
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: Union[QModelIndex, QPersistentModelIndex]) -> None:
        if index.column() == 3:
            editor: QComboBox
            value = editor.currentIndex()
            model.setData(index, value, LabelRole.status)
        else:
            super().setModelData(editor, model, index)

    @Slot()
    def commit_and_close_editor(self):
        self.commitData.emit(self.sender())
        self.closeEditor.emit(self.sender())
