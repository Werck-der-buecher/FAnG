# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Signal, Slot


class ImageScaleSelector(QComboBox):
    zoom_mode_changed = Signal()
    zoom_factor_changed = Signal(float)

    def __init__(self, parent):
        super().__init__(parent)
        self.setEditable(True)

        self.addItem("12%")
        self.addItem("25%")
        self.addItem("33%")
        self.addItem("50%")
        self.addItem("66%")
        self.addItem("75%")
        self.addItem("100%")
        self.addItem("125%")
        self.addItem("150%")
        self.addItem("200%")
        self.addItem("400%")
        self.addItem("800%")

        self.currentTextChanged.connect(self.on_current_text_changed)
        self.lineEdit().editingFinished.connect(self._editing_finished)

    @Slot(float)
    def set_zoom_factor(self, zoomFactor):
        percent = int(zoomFactor * 100)
        self.setCurrentText(f"{percent}%")

    @Slot()
    def reset(self):
        self.setCurrentIndex(6)  # 100%

    @Slot()
    def increment(self):
        if self.currentIndex() == self.count()-1:
            return
        self.setCurrentIndex(self.currentIndex() + 1)

    @Slot()
    def decrement(self):
        if self.currentIndex() == 0:
            return
        self.setCurrentIndex(self.currentIndex() - 1)

    @Slot(str)
    def on_current_text_changed(self, text):
        factor = 1.0
        zoom_level = int(text[:-1])
        factor = zoom_level / 100.0
        self.zoom_mode_changed.emit()
        self.zoom_factor_changed.emit(factor)

    @Slot()
    def _editing_finished(self):
        self.on_current_text_changed(self.lineEdit().text())
