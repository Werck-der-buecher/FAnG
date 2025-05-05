import logging
from enum import Enum
from typing import Optional, Union

from PySide6.QtCore import QSortFilterProxyModel, QObject, Slot, Qt, QModelIndex, QPersistentModelIndex

from widgets.viewedit.glyphs.glyphs_roles import GlyphRole


class GlyphSortingStrategyFilterModel(Enum):
    NONE = "None"
    SIZE = "Size"
    HEIGHT = "Height"
    WIDTH = "Width"
    EMBEDDING_SIMILARITY = "Embedding Similarity"
    MARKED_STATE = "Marking State"


class GlyphsProxyModel(QSortFilterProxyModel):

    # rowCountChanged = Signal(QModelIndex, int, int)

    def __init__(self, parent: Optional[QObject] = None,
                 sorting_strategy: GlyphSortingStrategyFilterModel = GlyphSortingStrategyFilterModel.NONE,
                 height_col: int = 3, width_col: int = 4):
        super().__init__(parent)
        self.sorting_strategy = sorting_strategy
        self.height_min = 0
        self.width_min = 0
        self.height_max = float('inf')
        self.width_max = float('inf')
        self.height_col = height_col
        self.width_col = width_col
        self.ascending_order = 1

    @Slot()
    def set_filter_height_min(self, height: int):
        self.height_min = int(height) if height != '' else 0
        self.invalidate()

    @Slot()
    def set_filter_height_max(self, height: int):
        self.height_max = int(height) if height != '' else float('inf')
        self.invalidate()

    @Slot()
    def set_filter_width_min(self, width: int):
        self.width_min = int(width) if width != '' else 0
        self.invalidate()

    @Slot()
    def set_filter_width_max(self, width):
        self.height_max = int(width) if width != '' else float('inf')
        self.invalidate()

    @Slot(str)
    def set_sorting_strategy(self, sorting_strategy: str):
        self.sorting_strategy = GlyphSortingStrategyFilterModel(sorting_strategy)
        self.invalidate()

    @Slot(int)
    def set_sorting_order(self, ascending: int):
        self.sort(0, Qt.SortOrder.AscendingOrder if ascending else Qt.SortOrder.DescendingOrder)

    def filterAcceptsRow(self, source_row: int, source_parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        height_index = self.sourceModel().index(source_row, self.height_col, source_parent)
        width_index = self.sourceModel().index(source_row, self.width_col, source_parent)

        height = self.sourceModel().data(height_index, Qt.ItemDataRole.DisplayRole)
        width = self.sourceModel().data(width_index, Qt.ItemDataRole.DisplayRole)

        return self.height_min < height < self.height_max and self.width_min < width < self.width_max

    def lessThan(self, source_left: Union[QModelIndex, QPersistentModelIndex],
                 source_right: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        if self.sorting_strategy == GlyphSortingStrategyFilterModel.NONE:
            return super().lessThan(source_left, source_right)
        elif self.sorting_strategy == GlyphSortingStrategyFilterModel.SIZE:
            return self.sort_by_size(source_left, source_right)
        elif self.sorting_strategy == GlyphSortingStrategyFilterModel.HEIGHT:
            return self.sort_by_height(source_left, source_right)
        elif self.sorting_strategy == GlyphSortingStrategyFilterModel.WIDTH:
            return self.sort_by_width(source_left, source_right)
        elif self.sorting_strategy == GlyphSortingStrategyFilterModel.EMBEDDING_SIMILARITY:
            return self.sort_by_similarity(source_left, source_right)
        elif self.sorting_strategy == GlyphSortingStrategyFilterModel.MARKED_STATE:
            return self.sort_by_mstate(source_left, source_right)

    def sort_by_size(self, source_left: Union[QModelIndex, QPersistentModelIndex],
                     source_right: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        left_height = self.sourceModel().data(source_left, GlyphRole.height)
        left_width = self.sourceModel().data(source_left, GlyphRole.width)
        right_height = self.sourceModel().data(source_right, GlyphRole.height)
        right_width = self.sourceModel().data(source_right, GlyphRole.width)
        left_size = left_height * left_width
        right_size = right_height * right_width

        return left_size < right_size

    def sort_by_height(self, source_left: Union[QModelIndex, QPersistentModelIndex],
                       source_right: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        left_height = self.sourceModel().data(source_left, GlyphRole.height)
        right_height = self.sourceModel().data(source_right, GlyphRole.height)

        return left_height < right_height

    def sort_by_width(self, source_left: Union[QModelIndex, QPersistentModelIndex],
                      source_right: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        left_width = self.sourceModel().data(source_left, GlyphRole.width)
        right_width = self.sourceModel().data(source_right, GlyphRole.width)

        return left_width < right_width

    def sort_by_similarity(self, source_left: Union[QModelIndex, QPersistentModelIndex],
                           source_right: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        logging.warning("Similarity sorting is not implemented yet.")
        return False

    def sort_by_mstate(self, source_left: Union[QModelIndex, QPersistentModelIndex],
                       source_right: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        # left source
        # left_marked: bool = self.sourceModel().data(source_left, Roles.marked)
        left_delete_later: bool = self.sourceModel().data(source_left, GlyphRole.delete)
        left_reassign_later: bool = self.sourceModel().data(source_left, GlyphRole.reassign)

        # right source
        # right_marked: bool = self.sourceModel().data(source_right, Roles.marked)
        right_delete_later: bool = self.sourceModel().data(source_right, GlyphRole.delete)
        right_reassign_later: bool = self.sourceModel().data(source_right, GlyphRole.reassign)

        # (1) [1/0] or [0/1] - [0,0]
        if (left_delete_later or left_reassign_later) and not (right_delete_later or right_reassign_later):
            return True
        # (2) [1/1] - [0,0], [1,0], or [0,1]
        elif (left_delete_later and left_reassign_later) and not (right_delete_later and right_reassign_later):
            return True
        # (3)
        elif left_delete_later and not left_reassign_later and not right_delete_later and right_reassign_later:
            return True
        else:
            return False
