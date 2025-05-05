from PySide6.QtWidgets import QWidget, QProgressBar, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import QSize, Slot, Qt


class PopUpProgressBar(QWidget):

    def __init__(self, title: str):
        super().__init__()
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(25, 25, 325, 75)
        self.statbar = QLabel(self)
        self.statbar.setGeometry(25, 100, 325, 25)
        self.statbar.setText("")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pbar)
        self.layout.addWidget(self.statbar)
        self.setLayout(self.layout)
        # self.setGeometry(300, 300, 350, 100)
        self.setMinimumSize(QSize(350, 120))
        self.setMaximumSize(QSize(350, 120))
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

    @Slot()
    def on_requested(self):
        self.show()

    @Slot()
    def on_removed(self):
        self.hide()

    @Slot()
    def setRange(self, min: int, max: int):
        self.pbar.setRange(min, max)

    @Slot()
    def on_count_changed(self, value: int):
        self.pbar.setValue(value)

    @Slot()
    def on_status_changed(self, text: str):
        self.statbar.setText(text)

    @Slot()
    def reset(self):
        self.pbar.setValue(0)
        self.statbar.setText("")

    def setStatus(self, text: str):
        self.statbar.setText(text)

    def setCount(self, value: int):
        self.pbar.setValue(value)
