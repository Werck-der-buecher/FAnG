from enum import IntEnum

from PySide6.QtCore import Qt


class GlyphRole(IntEnum):
    uid = Qt.ItemDataRole.UserRole
    uid_str = Qt.ItemDataRole.UserRole + 1
    extension = Qt.ItemDataRole.UserRole + 2
    height = Qt.ItemDataRole.UserRole + 3
    width = Qt.ItemDataRole.UserRole + 4
    filename = Qt.ItemDataRole.UserRole + 5
    img_ndarray = Qt.ItemDataRole.UserRole + 6

    position_abs = Qt.ItemDataRole.UserRole + 7
    position_rel = Qt.ItemDataRole.UserRole + 8

    marked = Qt.ItemDataRole.UserRole + 9
    delete = Qt.ItemDataRole.UserRole + 10
    reassign = Qt.ItemDataRole.UserRole + 11

    highlight = Qt.ItemDataRole.UserRole + 12
    cached = Qt.ItemDataRole.UserRole + 13
    custom_bookmark = Qt.ItemDataRole.UserRole + 14
