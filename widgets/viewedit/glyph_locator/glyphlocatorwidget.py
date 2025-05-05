from typing import Optional, List
from os import startfile

from PySide6.QtWidgets import (
    QWidget
)
from PySide6.QtCore import (
    Qt,
    QThreadPool,
    Signal,
    Slot,
    QRect,
    QRectF,
    QPointF,
    QDir,
    QFile,
    QFileInfo,
    QMimeDatabase
)
from PySide6.QtGui import (
    QPixmap,
    QPen,
    QColor,
    QPixmapCache
)

from widgets.viewedit.glyph_locator.ui_glyphlocatorwidget import Ui_GlyphLocatorWidget

OVERVIEW_RESIZE_HEIGHT = 1920
ROI_PAD_FACTOR_HEIGHT = 2
ROI_PAD_FACTOR_WIDTH = 6


class GlyphLocatorWidget(QWidget):
    about_to_load = Signal()
    loaded = Signal(bool)
    awaiting_data = False

    def __init__(self):
        super().__init__()

        self.ui = Ui_GlyphLocatorWidget()
        self.ui.setupUi(self)
        self.setWindowTitle("Glyph Locator")

        self.overview_graphics_view = self.ui.overviewGraphicsView
        self.roi_graphics_view = self.ui.roiGraphicsView

        self.ui.label_imageDir.setText("n/a")
        self.ui.label_filename.setText("n/a")
        self.ui.label_glyphID.setText("n/a")
        self.ui.label_glyphLabel.setText("n/a")
        self.ui.label_BBox.setText("n/a")
        self.ui.label_heightWidth.setText("n/a")

        self.pixmap_cache = QPixmapCache()
        self.pixmap = QPixmap()

        self.img_dir: Optional[str] = None
        self.img_filename: Optional[str] = None
        self.img_extension: Optional[str] = None
        self.glyph_label: Optional[str] = None
        self.glyph_uid: Optional[str] = None
        self.glyph_bbox: Optional[List[float]] = None

        # self.threadpool = QThreadPool()

    @Slot(str, str, str, str, str, list)
    def on_request_update(self, img_dir: str, img_filename: str, img_extension: str, glyph_uid: str, glyph_label: str, bbox: list[float]):
        if self.isHidden() or self.isMinimized():
            print("Hidden or minimized")
            return

        if self.awaiting_data:
            return

        self.about_to_load.emit()
        self.awaiting_data = True

        # populate meta data
        self.img_dir = img_dir
        self.img_filename = img_filename
        self.img_extension = img_extension
        self.glyph_bbox = bbox
        self.glyph_label = glyph_label
        self.glyph_uid = glyph_uid

        # search in pixmap cache if already exists
        if not self.pixmap_cache.find(img_filename, self.pixmap):
            abs_file_path = QDir(img_dir).absoluteFilePath(img_filename)

            exists = False
            for suffix in ['.png', '.jpg', '.jpeg', '.tif']:
                fpath = abs_file_path + suffix
                if QFile.exists(fpath):
                    exists = True
                    break
            if not exists:
                self.awaiting_data = False
                self.loaded.emit(True)
                return

            self.pixmap.load(abs_file_path)
            self.pixmap_cache.insert(img_filename, self.pixmap)

        self.set_details()
        self.draw_overview()
        self.draw_roi()

        self.awaiting_data = False
        self.loaded.emit(True)

        # initialize worker that is tasked to load an image file from disk
        # worker = LoadPixmapRunnable(img_dir, img_filename)

        # Signals/Slots
        # worker.signals.succeeded.connect(self.on_success)
        # worker.signals.failed.connect(self.on_failure)
        # worker.signals.finished.connect(self.wpbar.on_removed)
        # worker.signals.finished.connect(self.wpbar.reset)
        # worker.signals.progress.connect(self.wpbar.on_count_changed)
        # worker.signals.status.connect(self.wpbar.on_status_changed)
        #worker.signals.payload.connect(self.on_receive_payload)

        # self.threadpool.start(worker)

    @Slot(dict)
    def on_receive_payload(self, payload: dict):
        print("On Receive Payload")

        # self.clear_scene()
        self.pixmap = payload['pixmap']
        self.draw_overview()

    def set_details(self):
        if not self.pixmap.isNull():
            self.ui.label_imageDir.setText(self.img_dir)
            self.ui.label_filename.setText(self.img_filename)
            self.ui.label_glyphID.setText(self.glyph_uid)
            self.ui.label_glyphLabel.setText(self.glyph_label)
            self.ui.label_BBox.setText(" ".join([str(f) for f in self.glyph_bbox]))

            xy = self.glyph_bbox
            width = max(xy[::2]) - min(xy[::2])
            height = max(xy[1::2]) - min(xy[1::2])
            self.ui.label_heightWidth.setText(f"{height} / {width} [px]")

    def draw_overview(self):
        if not self.pixmap.isNull():

            scaling_factor = OVERVIEW_RESIZE_HEIGHT / self.pixmap.height()
            pixmap_resized = self.pixmap.scaledToHeight(OVERVIEW_RESIZE_HEIGHT, Qt.TransformationMode.FastTransformation)
            self.overview_graphics_view.set_pixmap(pixmap_resized)

            xy = self.glyph_bbox
            tl_x = min(xy[::2]) * scaling_factor
            tl_y = min(xy[1::2]) * scaling_factor
            br_x = max(xy[::2]) * scaling_factor
            br_y = max(xy[1::2]) * scaling_factor

            # Draw glyph bounding box
            rect = QRectF(QPointF(tl_x, tl_y), QPointF(br_x, br_y))
            pen = QPen(QColor(255, 0, 0), 4)  # Red color, 2px width
            self.overview_graphics_view.scene().addRect(rect, pen)

            # Draw roi bounding box
            bbox_height = br_y - tl_y
            bbox_width = br_x - tl_x
            roi_height = ROI_PAD_FACTOR_HEIGHT * bbox_height
            roi_width = ROI_PAD_FACTOR_WIDTH * bbox_width
            roi_x = max(0, tl_x - 0.5 * (ROI_PAD_FACTOR_WIDTH - 1) * bbox_width)
            roi_y = max(0, tl_y - 0.5 * (ROI_PAD_FACTOR_HEIGHT - 1) * bbox_height)

            rect = QRect(roi_x, roi_y, roi_width, roi_height)
            pen = QPen(QColor(0, 255, 0), 4)  # Red color, 2px width
            self.overview_graphics_view.scene().addRect(rect, pen)

    def draw_roi(self):
        if not self.pixmap.isNull():
            xy = self.glyph_bbox
            tl_x = min(xy[::2])
            tl_y = min(xy[1::2])
            br_x = max(xy[::2])
            br_y = max(xy[1::2])

            bbox_height = br_y - tl_y
            bbox_width = br_x - tl_x

            crop_height = ROI_PAD_FACTOR_HEIGHT * bbox_height
            crop_width = ROI_PAD_FACTOR_WIDTH * bbox_width

            crop_x = max(0, tl_x - 0.5 * (ROI_PAD_FACTOR_WIDTH - 1) * bbox_width)
            crop_y = max(0, tl_y - 0.5 * (ROI_PAD_FACTOR_HEIGHT - 1) * bbox_height)
            crop_spec = QRect(crop_x, crop_y, crop_width, crop_height)
            pixmap_cropped = self.pixmap.copy(crop_spec)

            self.roi_graphics_view.set_pixmap(pixmap_cropped)
            self.roi_graphics_view.fitInView(self.roi_graphics_view.scene().itemsBoundingRect(), Qt.KeepAspectRatio)

            rect = QRectF(0.5 * (ROI_PAD_FACTOR_WIDTH - 1) * bbox_width,
                          0.5 * (ROI_PAD_FACTOR_HEIGHT - 1) * bbox_height,
                          bbox_width, bbox_height)
            pen = QPen(QColor(255, 0, 0), 2)
            self.roi_graphics_view.scene().addRect(rect, pen)

    def show_in_explorer(self):
        abs_file_path = QDir(self.img_dir).absoluteFilePath(self.img_filename)
        # for suffix in ['.png', '.jpg', '.jpeg', '.tif']:
        #     fpath = abs_file_path + suffix
        #     print(fpath)
        #     if QFile.exists(fpath):
        #         startfile(fpath)
        #         return
        startfile(QDir(self.img_dir).absolutePath())
