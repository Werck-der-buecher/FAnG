from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsView,
    QGraphicsPixmapItem,
    QFrame,
    QGraphicsScene,
    QPushButton
)
from PySide6.QtCore import (
    Qt,
    QPoint,
    Signal,
    QRectF,
    QSize,
    QEvent
)
from PySide6.QtGui import (
    QResizeEvent,
    QMouseEvent,
    QWheelEvent,
    QKeyEvent,
    QCursor,
    QBrush,
    QColor,
    QPixmap,
    QIcon
)

from app_icons import AppIcons

SCALE_FACTOR = 1.25


class ZoomableGraphicsView(QGraphicsView):
    coordinatesChanged = Signal(QPoint)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._zoom = 0
        self._pinned = False
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._graphics_pixmap = QGraphicsPixmapItem()
        self._graphics_pixmap.setShapeMode(
            QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        self._scene.addItem(self._graphics_pixmap)
        self.setScene(self._scene)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.Shape.NoFrame)

        # self.zoom_in_btn = QPushButton(self)
        # self.zoom_in_btn.setIcon(AppIcons.get_icon(AppIcons.ICON_ZOOMIN, self.style()))

        # self.zoom_out_btn = QPushButton(self)
        # self.zoom_out_btn.setIcon(AppIcons.get_icon(AppIcons.ICON_ZOOMOUT, self.style()))

        # self._scene.addWidget(self.zoom_in_btn)
        # self._scene.addWidget(self.zoom_out_btn)

    def has_pixmap(self):
        return not self._empty

    def reset_view(self, scale: float = 1.):
        rect = QRectF(self._graphics_pixmap.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if (scale := max(1, scale)) == 1:
                self._zoom = 0
            if self.has_pixmap():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height()) * scale
                self.scale(factor, factor)
                if not self.zoomPinned():
                    self.centerOn(self._graphics_pixmap)
                self.updateCoordinates()

    def set_pixmap(self, pixmap=None):
        self.clear_patches()
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self._graphics_pixmap.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self._graphics_pixmap.setPixmap(QPixmap())
        if not (self.zoomPinned() and self.has_pixmap()):
            self._zoom = 0
        self.reset_view(SCALE_FACTOR ** self._zoom)

    def zoomLevel(self):
        return self._zoom

    def zoomPinned(self):
        return self._pinned

    def setZoomPinned(self, enable):
        self._pinned = bool(enable)

    def zoom(self, step):
        zoom = max(0, self._zoom + (step := int(step)))
        if zoom != self._zoom:
            self._zoom = zoom
            if self._zoom > 0:
                if step > 0:
                    factor = SCALE_FACTOR ** step
                else:
                    factor = 1 / SCALE_FACTOR ** abs(step)
                self.scale(factor, factor)
            else:
                self.reset_view()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.reset_view()

    def toggleDragMode(self) -> None:
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif not self._graphics_pixmap.pixmap().isNull():
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def updateCoordinates(self, pos: QPoint = None) -> None:
        if self._graphics_pixmap.isUnderMouse():
            if pos is None:
                pos = self.mapFromGlobal(QCursor.pos())
            point = self.mapToScene(pos).toPoint()
        else:
            point = QPoint()
        self.coordinatesChanged.emit(point)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.updateCoordinates(event.position().toPoint())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self.coordinatesChanged.emit(QPoint())
        super().leaveEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        self.zoom(delta and delta // abs(delta))

    # def wheelEvent(self, event: QWheelEvent) -> None:
    #     if event.modifiers() and Qt.KeyboardModifier.ControlModifier:
    #         anchor: QGraphicsView.ViewportAnchor = self.transformationAnchor()
    #         self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    #         angle: int = event.angleDelta().y()
    #         factor: float = 1.1 if angle > 0 else 0.9
    #         self.scale(factor, factor)
    #         self.setTransformationAnchor(anchor)
    #     else:
    #         super().wheelEvent(event)

    def clear_patches(self) -> None:
        # Remove all items except the pixmap
        for item in self._scene.items():
            if not isinstance(item, QGraphicsPixmapItem):
                self._scene.removeItem(item)
