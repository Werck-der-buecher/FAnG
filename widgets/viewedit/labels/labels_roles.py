from enum import IntEnum

from PySide6.QtCore import Qt


class LabelRole(IntEnum):
    label = Qt.ItemDataRole.UserRole
    similarity = Qt.ItemDataRole.UserRole + 1
    count = Qt.ItemDataRole.UserRole + 2
    status = Qt.ItemDataRole.UserRole + 3

    label_persistent = Qt.ItemDataRole.UserRole + 4
    similarity_persistent = Qt.ItemDataRole.UserRole + 5
    count_persistent = Qt.ItemDataRole.UserRole + 6
    status_persistent = Qt.ItemDataRole.UserRole + 7