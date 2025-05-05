from __future__ import annotations

import ast
from functools import wraps
from typing import Dict, Optional, Any
from typing import Tuple, Set

from PySide6.QtCore import QObject, Signal, Slot
from injector import inject

from services.sql_service import GSQLService


def notify_edits(method):
    @wraps(method)
    def decorated_method(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.notify_pending_edits()
        return result

    return decorated_method


class WorkspaceCacheService(QObject):
    about_to_commit = Signal()
    committed = Signal()

    pending_edits_changed = Signal(int)

    @inject
    def __init__(self, gsql_service: GSQLService):
        super().__init__()

        # cache items related to the glyph widgets (glyph model, glyph view, ...)
        self.marked_glyphs: Set[Tuple[str, str]] = set()
        self.delete_glyphs: Set[Tuple[str, str]] = set()
        self.reassign_glyphs: Dict[Tuple[str, str], str] = {}
        self.delete_glyphs_stats: Dict[str, int] = {}
        self.reassign_glyphs_stats: Dict[str, int] = {}

        # cache items related to the label widgets (label model, label view, ...)
        self.status_labels: Dict[str, int] = {}  # e.g., {'a', '2'}
        self.delete_labels: Set[Tuple[str, int]] = set()  # e.g., ('a', 2)
        self.reassign_labels: Dict[Tuple[str, int], str] = {}  # e.g., {('a', 2), 'b'}
        self.delete_encodings: Set[str] = set()  # e.g., ('a')

        # connect signals and slots
        self.committed.connect(self.notify_pending_edits)

        # services
        self._gsql_service = gsql_service

    @property
    def is_dirty(self) -> bool:
        return bool(len(self.delete_glyphs) or len(self.reassign_glyphs) or len(self.delete_labels) or len(
            self.delete_encodings) or len(self.reassign_labels) or len(self.status_labels))

    @property
    def num_pending_changes(self) -> int:
        return len(self.delete_glyphs) + len(self.reassign_glyphs) + len(self.delete_labels) + len(
            self.delete_encodings) + len(self.reassign_labels) + len(self.status_labels)

    def num_pending_changes_for_label(self, label: Optional[str] = None) -> int:
        if label is not None:
            return self.delete_glyphs_stats.get(label, 0) + self.reassign_glyphs_stats.get(label, 0)
        return self.num_pending_changes

    @Slot()
    def notify_pending_edits(self) -> None:
        self.pending_edits_changed.emit(self.num_pending_changes)

    @Slot()
    @notify_edits
    def add_mark_glyph(self, uid: Tuple[str, str]) -> None:
        self.marked_glyphs.add(uid)

    @Slot()
    @notify_edits
    def remove_mark_glyph(self, uid: Tuple[str, str]) -> None:
        self.marked_glyphs.discard(uid)

    @Slot()
    @notify_edits
    def add_delete_glyph(self, uid: Tuple[str, str], label: Optional[str] = None) -> None:
        if label is not None:
            # Increment cached deletions by one
            if label not in self.delete_glyphs_stats:
                self.delete_glyphs_stats[label] = 0
            self.delete_glyphs_stats[label] += 1
            if uid in self.reassign_glyphs:
                self.reassign_glyphs_stats[label] -= 1
        self.delete_glyphs.add(uid)
        self.reassign_glyphs.pop(uid, None)

    @Slot()
    @notify_edits
    def remove_delete_glyph(self, uid: Tuple[str, str], label: Optional[str] = None) -> None:
        self.delete_glyphs.discard(uid)
        if label is not None and label in self.delete_glyphs_stats:
            self.delete_glyphs_stats[label] -= 1

    @Slot()
    @notify_edits
    def add_reassign_glyph(self, uid: Tuple[str, str], value: str, label: Optional[str] = None) -> None:
        if label is not None:
            if label not in self.reassign_glyphs_stats:
                self.reassign_glyphs_stats[label] = 0
            self.reassign_glyphs_stats[label] += 1
            if uid in self.delete_glyphs_stats:
                self.delete_glyphs_stats[label] -= 1
        self.reassign_glyphs[uid] = value
        self.delete_glyphs.discard(uid)

    @Slot()
    @notify_edits
    def remove_reassign_glyph(self, uid: Tuple[str, str], label: Optional[str] = None) -> None:
        self.reassign_glyphs.pop(uid, None)
        if label is not None and label in self.reassign_glyphs_stats:
            self.reassign_glyphs_stats[label] -= 1

    @Slot()
    @notify_edits
    def add_delete_labels(self, label: str, similarity_group: Optional[int] = None) -> None:
        self.delete_labels.add((label, similarity_group))
        self.reassign_labels.pop((label, similarity_group), None)

    @Slot()
    @notify_edits
    def remove_delete_labels(self, label: str, similarity_group: Optional[int] = None) -> None:
        self.delete_labels.discard((label, similarity_group))

    @Slot()
    @notify_edits
    def add_reassign_labels(self, source_label: str, target_label: str, similarity_group: Optional[int] = None) -> None:
        self.reassign_labels[(source_label, similarity_group)] = target_label
        self.delete_labels.discard((source_label, similarity_group))

    @Slot()
    @notify_edits
    def remove_reassign_labels(self, source_label: str, similarity_group: Optional[int] = None) -> None:
        self.reassign_labels.pop((source_label, similarity_group), None)

    @Slot()
    @notify_edits
    def add_delete_encodings(self, label: str) -> None:
        self.delete_encodings.add(label)

    @Slot()
    @notify_edits
    def remove_delete_encodings(self, label: str) -> None:
        self.delete_encodings.discard(label)

    @Slot()
    @notify_edits
    def add_status_labels(self, label: str, status: int) -> None:
        self.status_labels[label] = status

    @Slot()
    @notify_edits
    def remove_status_labels(self, label: str) -> None:
        self.status_labels.pop(label, None)

    @Slot()
    @notify_edits
    def set(self,
            marked_glyphs: Set[Tuple[str, str]],
            delete_glyphs: Set[Tuple[str, str]],
            reassign_glyphs: Dict[Tuple[str, str], str],
            delete_glyphs_stats: Dict[str, int],
            reassign_glyphs_stats: Dict[str, int]
            ) -> None:
        self.marked_glyphs = marked_glyphs
        self.delete_glyphs = delete_glyphs
        self.reassign_glyphs = reassign_glyphs
        self.delete_glyphs_stats = delete_glyphs_stats
        self.reassign_glyphs_stats = reassign_glyphs_stats

    @Slot()
    @notify_edits
    def clear(self) -> None:
        self.status_labels.clear()
        self.delete_labels.clear()
        self.reassign_labels.clear()
        self.delete_encodings.clear()
        self.delete_glyphs.clear()
        self.reassign_glyphs.clear()
        self.delete_glyphs_stats.clear()
        self.reassign_glyphs_stats.clear()

    @Slot()
    def clear_marks(self):
        self.marked_glyphs.clear()

    def from_dict(self, cache: Dict[str, Any]) -> None:
        self.clear()

        # labels
        if cache['status_labels'] is not None:
            self.status_labels = cache['status_labels']
        if cache['delete_labels'] is not None:
            self.delete_labels = set(tuple(e) for e in cache['delete_labels'])
        if cache['reassign_labels'] is not None:
            reassign_labels = {}
            for k, v in cache['reassign_labels'].items():
                k1, k2 = k.split(':')
                k2 = ast.literal_eval(k2)
                reassign_labels[(k1, k2)] = v
            self.reassign_labels = reassign_labels
        if cache['delete_encodings'] is not None:
            self.delete_encodings = set(e for e in cache['delete_encodings'])

        # glyphs
        if cache['marked_glyphs'] is not None:
            self.marked_glyphs = set(tuple(e) for e in cache['marked_glyphs'])
        if cache['delete_glyphs'] is not None:
            self.delete_glyphs = set(tuple(e) for e in cache['delete_glyphs'])
        if cache['reassign_glyphs'] is not None:
            self.reassign_glyphs = {tuple(k.split(':')): v for k, v in cache['reassign_glyphs'].items()}
        if cache['delete_glyphs_stats'] is not None:
            self.delete_glyphs_stats = cache['delete_glyphs_stats']
        if cache['reassign_glyphs_stats'] is not None:
            self.reassign_glyphs_stats = cache['reassign_glyphs_stats']

        self.notify_pending_edits()

    def to_dict(self) -> Dict[str, Any]:
        return {'status_labels': self.status_labels,
                'delete_labels': self.delete_labels,
                'reassign_labels': {f"{k[0]}:{str(k[1])}": v for k, v in self.reassign_labels.items()},
                'delete_encodings': self.delete_encodings,

                'marked_glyphs': self.marked_glyphs,
                "delete_glyphs": self.delete_glyphs,
                "reassign_glyphs": {f"{k[0]}:{str(k[1])}": v for k, v in self.reassign_glyphs.items()},
                "delete_glyphs_stats": self.delete_glyphs_stats,
                "reassign_glyphs_stats": self.reassign_glyphs_stats}
