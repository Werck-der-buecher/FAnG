from __future__ import annotations

import ast
from functools import wraps
import dataclasses
from typing import List, Tuple, Dict, Any, Optional, Union

from PySide6.QtCore import QObject, Signal, Slot


def notify_change(method):
    @wraps(method)
    def decorated_method(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.notify_bookmarks_changed()
        return result

    return decorated_method


class WorkspaceBookmarkService(QObject):
    bookmarks_changed = Signal()

    def __init__(self):
        super().__init__()

        # bookmarked items
        self.noflag: Dict[Tuple[str, Union[int, None]], List[Tuple[str, str], int]] = {}
        self.delete: Dict[Tuple[str, Union[int, None]], List[Tuple[str, str], int]] = {}
        self.reassign: Dict[Tuple[str, Union[int, None]], List[Tuple[str, str], int]] = {}
        self.select: Dict[Tuple[str, Union[int, None]], List[Tuple[str, str], int]] = {}
        self.custom: Dict[Tuple[str, Union[int, None]], List[Tuple[str, str], int]] = {}

    @property
    def has_active_items(self):
        return len(self.noflag) or len(self.delete) or len(self.reassign) or self.select or self.custom

    @Slot()
    def notify_bookmarks_changed(self) -> None:
        self.bookmarks_changed.emit()

    @Slot()
    @notify_change
    def add_noflag(self, label: str, similarity: Union[int, None], uid: Tuple[str, str], row: Optional[int]) -> None:
        self.noflag[(label, similarity)] = [uid, row]

    @Slot()
    @notify_change
    def remove_noflag(self, label: str, similarity: Union[int, None]) -> None:
        self.noflag.pop((label, similarity), None)

    @Slot()
    @notify_change
    def add_delete(self, label: str, similarity: Union[int, None], uid: Tuple[str, str], row: Optional[int]) -> None:
        self.delete[(label, similarity)] = [uid, row]

    @Slot()
    @notify_change
    def remove_delete(self, label: str, similarity: Union[int, None]) -> None:
        self.delete.pop((label, similarity), None)

    @Slot()
    @notify_change
    def add_reassign(self, label: str, similarity: Union[int, None], uid: Tuple[str, str], row: Optional[int]) -> None:
        self.reassign[(label, similarity)] = [uid, row]

    @Slot()
    @notify_change
    def remove_reassign(self, label: str, similarity: Union[int, None]) -> None:
        self.reassign.pop((label, similarity), None)

    @Slot()
    @notify_change
    def add_select(self, label: str, similarity: Union[int, None], uid: Tuple[str, str], row: Optional[int]) -> None:
        self.select[(label, similarity)] = [uid, row]

    @Slot()
    @notify_change
    def remove_select(self, label: str, similarity: Union[int, None]) -> None:
        self.select.pop((label, similarity), None)

    @Slot()
    @notify_change
    def add_custom(self, label: str, similarity: Union[int, None], uid: Tuple[str, str], row: Optional[int]) -> None:
        self.custom[(label, similarity)] = [uid, row]

    @Slot()
    @notify_change
    def remove_custom(self, label: str, similarity: Union[int, None]) -> None:
        self.custom.pop((label, similarity), None)

    @Slot()
    @notify_change
    def clear(self) -> None:
        self.noflag.clear()
        self.delete.clear()
        self.reassign.clear()
        self.select.clear()
        self.custom.clear()

    def from_dict(self, bookmarks: Dict[str, Any]) -> None:
        if bookmarks['noflag'] is not None:
            noflag = {}
            for k, v in bookmarks['noflag'].items():
                k1, k2 = k.split(':')
                k2 = ast.literal_eval(k2)
                v1, v2 = v
                noflag[(k1, k2)] = [tuple(v1), v2]
            self.noflag = noflag

        if bookmarks['delete'] is not None:
            delete = {}
            for k, v in bookmarks['delete'].items():
                k1, k2 = k.split(':')
                k2 = ast.literal_eval(k2)
                v1, v2 = v
                delete[(k1, k2)] = [tuple(v1), v2]
            self.delete = delete

        if bookmarks['reassign'] is not None:
            reassign = {}
            for k, v in bookmarks['reassign'].items():
                k1, k2 = k.split(':')
                k2 = ast.literal_eval(k2)
                v1, v2 = v
                reassign[(k1, k2)] = [tuple(v1), v2]
            self.reassign = reassign
        if bookmarks['select'] is not None:
            select = {}
            for k, v in bookmarks['select'].items():
                k1, k2 = k.split(':')
                k2 = ast.literal_eval(k2)
                v1, v2 = v
                select[(k1, k2)] = [tuple(v1), v2]
            self.select = select
        if bookmarks['custom'] is not None:
            custom = {}
            for k, v in bookmarks['custom'].items():
                k1, k2 = k.split(':')
                k2 = ast.literal_eval(k2)
                v1, v2 = v
                custom[(k1, k2)] = [tuple(v1), v2]
            self.custom = custom

    def to_dict(self) -> Dict[str, Any]:
        return {"noflag": {f"{k[0]}:{str(k[1])}": v for k, v in self.noflag.items()},
                "delete": {f"{k[0]}:{str(k[1])}": v for k, v in self.delete.items()},
                "reassign": {f"{k[0]}:{str(k[1])}": v for k, v in self.reassign.items()},
                "select": {f"{k[0]}:{str(k[1])}": v for k, v in self.select.items()},
                "custom": {f"{k[0]}:{str(k[1])}": v for k, v in self.custom.items()}}
