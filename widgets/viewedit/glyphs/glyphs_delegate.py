import logging
from typing import Optional, Dict, List

from PySide6.QtCore import QObject, QRectF, QModelIndex, Qt, QSizeF, QSize, QEvent, QAbstractItemModel, \
    QItemSelectionModel, QItemSelection, QRect, Slot, QPointF
from PySide6.QtGui import QColor, QGuiApplication, QPen, QFont, QFontMetricsF, QPainter, QPixmap, QBrush
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionButton, QApplication, QStyle, QStyleOptionViewItem, \
    QWidget
from colour import Color
from injector import inject

from services import Settings, GSQLService
from widgets.viewedit.constants import Constants
from widgets.viewedit.glyphs.glyphs_roles import GlyphRole
from widgets.viewedit.utils import GlyphSize, FileExtension, CustomColors, extensionColor


class GlyphItemDelegate(QStyledItemDelegate):

    @inject
    def __init__(self,
                 settings: Settings,
                 gsql_service: GSQLService,
                 selection_model: QItemSelectionModel,
                 parent: Optional[QObject] = None
                 ) -> None:
        super().__init__(parent)

        # service injection
        self.settings = settings
        self.gsql_service = gsql_service
        self.selection_model = selection_model

        # fields
        self.device_pixel_ratio = 1.0
        self.devicePixelF = True

        self.checkboxStyleOption = QStyleOptionButton()
        self.checkboxRect = QRectF(
            QApplication.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, self.checkboxStyleOption, None)
        )
        self.checkbox_size = self.checkboxRect.height()

        self.dimmed_opacity = 0.5

        self.image_width = float(max(GlyphSize.width, GlyphSize.height))
        self.image_height = self.image_width
        self.horizontal_margin = float(Constants.GlyphMargin)
        self.vertical_margin = float(Constants.GlyphMargin)
        self.image_footer = float(self.checkbox_size)
        self.footer_padding = 5.0

        self.shadow_size = 2.0
        self.width = self.image_width + self.horizontal_margin * 2
        self.height = (self.image_height + self.footer_padding + self.image_footer + self.vertical_margin * 2)

        self.image_area_size = float(max(GlyphSize.width, GlyphSize.height))
        self.image_frame_bottom = self.vertical_margin + self.image_area_size

        self.color3 = QColor(CustomColors.color3.value)

        self.veryLightGray = QColor(Constants.VeryLightGray)
        self.lightGray = QColor(Constants.LightGray)
        self.paleGray = QColor(Constants.PaleGray)
        self.mediumGray = QColor(Constants.MediumGray)
        self.darkGray = QColor(Constants.DarkGray)

        palette = QGuiApplication.palette()
        self.highlight: QColor = palette.highlight().color()
        self.highlight_size = 3
        self.highlight_offset = self.highlight_size / 2
        self.highlightPen = QPen()
        self.highlightPen.setColor(self.highlight)
        self.highlightPen.setWidth(self.highlight_size)
        self.highlightPen.setStyle(Qt.SolidLine)
        self.highlightPen.setJoinStyle(Qt.MiterJoin)

        self.emblemFont = QFont()
        self.emblemFont.setPointSize(self.emblemFont.pointSize() - 2)
        metrics = QFontMetricsF(self.emblemFont)

        # Determine the actual height of the largest extension, and the actual
        # width of all extensions.
        # For our purposes, this is more accurate than the generic metrics.height()
        self.emblem_width = {}  # type: Dict[str, int]
        height = 0
        # Include the emblems for which memory card on a camera the file came from
        for ext in ["jpg", "jpeg", "png", "raw"]:
            ext = ext.upper()
            tbr = metrics.tightBoundingRect(ext)  # type: QRectF
            self.emblem_width[ext] = tbr.width()
            height = max(height, tbr.height())

        # Set and calculate the padding to go around each emblem
        self.emblem_pad = height / 3
        self.emblem_height = height + self.emblem_pad * 2
        self.emblem_width = {
            emblem: width + self.emblem_pad * 2
            for emblem, width in self.emblem_width.items()
        }

        self.scode_font = QFont()
        self.scode_font.setPointSize(self.scode_font.pointSize() - 2)
        self.scode_metrics = QFontMetricsF(self.scode_font)
        height = self.scode_metrics.height()
        self.scode_pad = height / 4
        self.scode_height = height + self.scode_pad * 2
        self.scode_width = self.image_width
        self.scode_text_width = self.scode_width - self.scode_pad * 2
        self.scode_lru = dict()  # type: Dict[str, str]

        # Generate the range of colors to be displayed when highlighting
        # files from a particular device
        ch = Color(self.paleGray.name())
        cg_light = Color(self.lightGray.name())
        cg_dark = Color(self.darkGray.name())
        self.color_gradient_light = [QColor(c.hex) for c in cg_light.range_to(ch, Constants.FadeSteps)]
        self.color_gradient_dark = [QColor(c.hex) for c in cg_dark.range_to(ch, Constants.FadeSteps)]

        # Size is always fixed, so calculate it here
        self.fixedSizeHint = QSizeF(self.width + self.shadow_size, self.height + self.shadow_size).toSize()

        # Toggle switch indicating whether to render individual glyph details
        self._show_details = False

    @Slot()
    def on_toggle_details(self):
        self._show_details = not self._show_details

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        if index is None:
            return

        if not index.isValid():
            return

        # Save state of painter, restore on function exit
        painter.save()

        # Get meta information about the current item
        marked = index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked

        delete = index.data(GlyphRole.delete)
        reassign = index.data(GlyphRole.reassign)
        extension = index.data(GlyphRole.extension)
        height = index.data(GlyphRole.height)
        width = index.data(GlyphRole.width)
        highlight = index.data(GlyphRole.highlight)
        custom_bookmark = index.data(GlyphRole.custom_bookmark)
        is_selected = option.state & QStyle.StateFlag.State_Selected
        dimmed = delete or reassign

        x = option.rect.x()
        y = option.rect.y()

        ###
        # Tile layout and draw
        boxRect = QRectF(x, y, self.width, self.height)
        shadowRect = QRectF(x + self.shadow_size, y + self.shadow_size, self.width, self.height)

        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(self.darkGray)
        painter.fillRect(shadowRect, self.darkGray)
        painter.drawRect(shadowRect)
        painter.setRenderHint(QPainter.Antialiasing, False)
        if highlight != 0:
            if self.settings.app_theme == "dark":
                painter.fillRect(boxRect, self.color_gradient_dark[highlight - 1])
            else:
                painter.fillRect(boxRect, self.color_gradient_light[highlight - 1])
            # painter.setPen(QColor(CustomColors.color7.value))
            # painter.drawRect(boxRect)
        elif dimmed:
            painter.fillRect(boxRect, self.paleGray)
        else:
            if self.settings.app_theme == "dark":
                painter.fillRect(boxRect, self.darkGray)
            else:
                painter.fillRect(boxRect, self.lightGray)

        painter.setPen(self.paleGray)
        painter.drawRect(boxRect)

        if is_selected:
            hightlightRect = QRectF(
                boxRect.left() + self.highlight_offset,
                boxRect.top() + self.highlight_offset,
                boxRect.width() - self.highlight_size,
                boxRect.height() - self.highlight_size,
            )
            painter.setPen(self.highlightPen)
            painter.drawRect(hightlightRect)

        ###
        # Glyph image drawing
        glyph: QPixmap = index.model().data(index, Qt.DecorationRole)

        # Perform glyph cropping
        # glyph = self.resize_pixmap_to_size(glyph, QSize(GlyphSize.height, GlyphSize.width))
        glyph = self.crop_pixmap_to_size(glyph, QSize(GlyphSize.height, GlyphSize.width))

        # If on high DPI screen, scale the thumbnail using a smooth transform
        if self.device_pixel_ratio > 1.0:
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        if dimmed:
            disabled = QPixmap(glyph.size())
            if self.devicePixelF:
                disabled.setDevicePixelRatio(glyph.devicePixelRatioF())
            else:
                disabled.setDevicePixelRatio(glyph.devicePixelRatio())
            disabled.fill(Qt.GlobalColor.transparent)
            p = QPainter(disabled)
            p.setBackgroundMode(Qt.TransparentMode)
            p.setBackground(QBrush(Qt.transparent))
            p.eraseRect(glyph.rect())
            p.setOpacity(self.dimmed_opacity)
            p.drawPixmap(0, 0, glyph)
            p.end()
            glyph = disabled

        thumbnail_width = glyph.size().width()
        thumbnail_height = glyph.size().height()
        if self.devicePixelF:
            ratio = glyph.devicePixelRatioF()
        else:
            ratio = glyph.devicePixelRatio()

        thumbnailX = (
                self.horizontal_margin
                + (self.image_area_size - thumbnail_width / ratio) / 2
                + x
        )
        thumbnailY = (
                self.vertical_margin
                + (self.image_area_size - thumbnail_height / ratio) / 2
                + y
        )

        target = QRectF(
            thumbnailX, thumbnailY, thumbnail_width / ratio, thumbnail_height / ratio
        )
        source = QRectF(0, 0, thumbnail_width, thumbnail_height)
        painter.drawPixmap(target, glyph, source)

        if delete:
            scode = "Delete"
            scolor = QColor(Constants.DoubleDarkGray)
        elif reassign:
            scode = f"Assign → '{reassign}'"
            scolor = QColor(CustomColors.color1.value)
        elif custom_bookmark:
            scode = "Custom Bookmark"
            scolor = QColor(CustomColors.color3.value)
        else:
            scode = False
            scolor = None

        if scode:
            if is_selected:
                scolor = self.highlight
                painter.setOpacity(1.0)
            else:
                if not dimmed:
                    painter.setOpacity(0.75)
                else:
                    painter.setOpacity(self.dimmed_opacity)

            scode_rect = QRectF(
                x + self.horizontal_margin,
                y + self.vertical_margin,
                self.scode_width,
                self.scode_height,
            )
            painter.fillRect(scode_rect, scolor)
            painter.setFont(self.scode_font)
            painter.setPen(QColor(Qt.white))
            if scode in self.scode_lru:
                text = self.scode_lru[scode]
            else:
                text = self.scode_metrics.elidedText(
                    scode, Qt.ElideRight, self.scode_text_width
                )
                self.scode_lru[scode] = text
            if not dimmed:
                painter.setOpacity(1.0)
            else:
                painter.setOpacity(self.dimmed_opacity)
            painter.drawText(scode_rect, Qt.AlignCenter, text)

        if dimmed:
            painter.setOpacity(self.dimmed_opacity)

        # painter.setPen(QColor(Qt.blue))
        # painter.drawText(x + 2, y + 15, str(index.row()))

        if self._show_details:
            # Draw a small coloured box containing the file extension in the
            #  bottom right corner
            extension: str = extension.lstrip('.').upper()
            # Calculate size of extension text
            painter.setFont(self.emblemFont)
            # em_width = self.emblemFontMetrics.width(extension)
            emblem_width = self.emblem_width.get(extension, self.emblem_width['JPG'])
            emblem_rect_x = self.width - self.horizontal_margin - emblem_width + x
            emblem_rect_y = self.image_frame_bottom + self.footer_padding + y - 1

            emblemRect = QRectF(emblem_rect_x, emblem_rect_y, emblem_width, self.emblem_height)

            color = extensionColor(ext_type=FileExtension.jpeg)

            # Use an angular rect, because a rounded rect with anti-aliasing doesn't look
            # too good
            painter.fillRect(emblemRect, color)
            painter.setPen(QColor(Qt.white))
            painter.drawText(emblemRect, Qt.AlignCenter, extension)

            # Assume the attribute is already upper case
            size_str = f"{height}x{width}"
            tbr = QFontMetricsF(self.emblemFont).tightBoundingRect(size_str)
            size_width = tbr.width() + self.emblem_pad * 2
            size_rect_x = emblem_rect_x - self.footer_padding - size_width
            color = QColor(self.color3)
            secRect = QRectF(size_rect_x, emblem_rect_y, size_width, self.emblem_height)
            painter.fillRect(secRect, color)
            painter.drawText(secRect, Qt.AlignCenter, size_str)

        if dimmed:
            painter.setOpacity(1.0)

        checkboxStyleOption = QStyleOptionButton()
        if marked:
            checkboxStyleOption.state |= QStyle.StateFlag.State_On
        else:
            checkboxStyleOption.state |= QStyle.StateFlag.State_Off
        checkboxStyleOption.state |= QStyle.StateFlag.State_Enabled
        checkboxStyleOption.rect = self.getCheckBoxRect(option.rect).toRect()
        QApplication.style().drawControl(QStyle.ControlElement.CE_CheckBox, checkboxStyleOption, painter)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return self.fixedSizeHint

    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem,
                    index: QModelIndex) -> bool:
        if event.type() == QEvent.MouseButtonRelease or event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.RightButton:
                return False
            if event.button() != Qt.LeftButton or not self.getCheckBoxRect(option.rect).contains(event.pos()):
                return False
            if event.type() == QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QEvent.KeyPress:
            if event.key() != Qt.Key_Space and event.key() != Qt.Key_Select:
                return False
        else:
            return False

        # Change the checkbox-state
        self.setModelData(editor=None, model=model, index=index)
        return True

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        if not index.isValid():
            return

        newValue = not (index.data(Qt.CheckStateRole) == Qt.CheckState.Checked)
        selection: QItemSelectionModel = self.parent().glyph_view.selectionModel()
        if selection.hasSelection():
            selected: QItemSelection = selection.selection()
            if index in selected.indexes():
                for i in selected.indexes():
                    model.setData(i, newValue, Qt.CheckStateRole)
            else:
                # The user has clicked on a checkbox that for a
                # thumbnail that is outside their previous selection
                selection.clear()
                selection.select(index, QItemSelectionModel.Select)
                model.setData(index, newValue, Qt.CheckStateRole)
        else:
            # The user has previously selected nothing, so mark this
            # thumbnail as selected
            selection.select(index, QItemSelectionModel.Select)
            model.setData(index, newValue, Qt.CheckStateRole)

    def crop_pixmap(self, pixmap: QPixmap, crop: int) -> QPixmap:
        if crop <= 0:
            logging.debug("Cropping with negative cropping value not possible. Skipping...")
            return pixmap
        H, W = pixmap.height(), pixmap.width()
        crop_spec = QRect(crop, crop, W - 2 * crop, H - 2 * crop)
        return pixmap.copy(crop_spec)

    def crop_pixmap_to_size(self, pixmap: QPixmap, size: QSize) -> QPixmap:
        H, W = pixmap.height(), pixmap.width()
        H_diff, W_diff = H - size.height(), W - size.width()
        H_crop = H_diff / 2 if H_diff > 0 else 0
        W_crop = W_diff / 2 if W_diff > 0 else 0
        crop_spec = QRect(W_crop, H_crop, W - 2 * W_crop, H - 2 * H_crop)
        return pixmap.copy(crop_spec)

    def resize_pixmap(self, pixmap: QPixmap, scale_factor: float) -> QPixmap:
        if scale_factor == 1.0:
            return pixmap
        return pixmap.scaledToHeight(pixmap.height() * scale_factor, Qt.TransformationMode.FastTransformation)

    def resize_pixmap_to_size(self, pixmap: QPixmap, size: QSize) -> QPixmap:
        return pixmap.scaled(size, aspectMode=Qt.AspectRatioMode.KeepAspectRatio)

    @Slot()
    def toggle_show_details(self) -> None:
        self._show_details = not self._show_details

    def getLeftPoint(self, rect: QRect) -> QPointF:
        return QPointF(rect.x() + self.horizontal_margin, rect.y() + self.image_frame_bottom + self.footer_padding - 1)

    def getCheckBoxRect(self, rect: QRect) -> QRectF:
        return QRectF(
            self.getLeftPoint(rect), QSizeF(self.checkboxRect.toRect().size())
        )

    def selected_indexes(self) -> Optional[List[QModelIndex]]:
        if self.selection_model.hasSelection():
            selected: QItemSelection = self.selection_model.selection()
            return selected.indexes()
        return None
