from enum import IntEnum, Enum
from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QFontMetrics, QFont, QIcon

from app_icons import AppIcons
from widgets.viewedit.constants import Constants


class GlyphSize(IntEnum):
    width = 80
    height = 80


class FileExtension(Enum):
    raw = 1
    jpeg = 2
    heif = 3
    other_photo = 4
    video = 5
    audio = 6
    unknown = 7


class CustomColors(Enum):
    color1 = "#7a9c38"  # green
    color2 = "#cb493f"  # red
    color3 = "#d17109"  # orange
    color4 = "#4D8CDC"  # blue
    color5 = "#5f6bfe"  # purple
    color6 = "#6d7e90"  # greyish
    color7 = "#ffff00"  # bright yellow


class CategoryStatus(IntEnum):
    UNPROCESSED = 0
    DIRTY = 1
    PROCESSED = 2


CategoryStatusNameDict = {
    CategoryStatus.UNPROCESSED: "Undone",
    CategoryStatus.DIRTY: "Pending",
    CategoryStatus.PROCESSED: "Done"
}
CategoryStatusIconDict = {
    CategoryStatus.UNPROCESSED: AppIcons.ICON_UNPROCESSED,
    CategoryStatus.DIRTY: AppIcons.ICON_PENDING,
    CategoryStatus.PROCESSED: AppIcons.ICON_DONE
}
CategoryStatusColorDictLight = {
    CategoryStatus.UNPROCESSED: (Constants.DarkGray, Constants.LightGray),
    CategoryStatus.DIRTY: (Constants.LightYellowText, Constants.LightYellowBackground),
    CategoryStatus.PROCESSED: (Constants.LightGreenText, Constants.LightGreenBackground)
}
CategoryStatusColorDictDark = {
    CategoryStatus.UNPROCESSED: (Constants.LightGray, Constants.DarkBackground),
    CategoryStatus.DIRTY: (Constants.DarkYellowText, Constants.DarkYellowBackground),
    CategoryStatus.PROCESSED: (Constants.DarkGreenText, Constants.DarkGreenBackground)
}
ExtensionColorDict = {
    FileExtension.raw: CustomColors.color1,
    FileExtension.jpeg: CustomColors.color4,
}


def extensionColor(ext_type: FileExtension) -> QColor:
    try:
        return QColor(ExtensionColorDict[ext_type].value)
    except KeyError:
        return QColor(0, 0, 0)


def standard_font_size(shrink_on_odd: bool = True) -> int:
    h = QFontMetrics(QFont()).height()
    if h % 2 == 1:
        if shrink_on_odd:
            h -= 1
        else:
            h += 1
    return h


def scaledIcon(path: str, size: Optional[QSize] = None) -> QIcon:
    """
    Create a QIcon that scales well
    Uses .addFile()

    :param path:
    :param scale:
    :param size:
    :return:
    """
    i = QIcon()
    if size is None:
        s = standard_font_size()
        size = QSize(s, s)
    i.addFile(path, size)
    return i
