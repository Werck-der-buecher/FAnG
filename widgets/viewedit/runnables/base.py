import logging

from PySide6.QtCore import QRunnable
from PySide6.QtSql import QSqlDatabase

from widgets.viewedit.runnables.worker_signals import WorkerSignals
from widgets.viewedit.constants import Constants
from widgets.viewedit.glyphs.glyphs_model import GlyphsSQLModel

from injector import inject
from services import GSQLService, Transaction, WorkspacePersistenceService

from typing import List, Tuple, Union, Set, Dict


class DBCommitRunnable(QRunnable):
    NUM_STAGES = 5

    @inject
    def __init__(self, gsql_service: GSQLService, persistence_service: WorkspacePersistenceService):
        super().__init__()
        self.gsql = gsql_service
        self.persistence = persistence_service
        self.conn_name = "commit_changes"
        self.messages = [
            "Committing status changes",
            "Committing encoding changes",
            "Committing label changes",
            "Committing glyph changes",
            "Done"
        ]
        assert len(self.messages) == DBCommitRunnable.NUM_STAGES
        self.signals = WorkerSignals()

    def broadcast_status(self, prog: int) -> None:
        msg = self.messages[prog]
        msg = f"[{prog + 1}/{len(self.messages)}] {msg} ..."
        self.signals.progress.emit(prog)
        self.signals.status.emit(msg)

    def run(self):
        try:
            # establish connection
            db_handle = self.gsql.get_or_create_connection(self.conn_name)

            # persist status changes
            prog_count = 0
            self.broadcast_status(prog_count)
            status_labels = self.persistence.cache.status_labels
            if len(status_labels):
                self.commit_changes_status(db_handle, status_labels)

            # persist the cached deletions of complete encodings
            prog_count = 1
            self.broadcast_status(prog_count)
            delete_encoding = self.persistence.cache.delete_encodings
            if len(delete_encoding):
                self.commit_changes_encoding(db_handle, delete_encoding)

            # persist the cached deletions and reassignments of the label model/view
            prog_count = 2
            self.broadcast_status(prog_count)
            delete_labels = self.persistence.cache.delete_labels
            if len(delete_labels):
                self.commit_changes_labels(db_handle, delete_labels, Constants.CATEGORY_DELETED)

            reassign_labels = self.persistence.cache.reassign_labels
            if len(reassign_labels):
                self.commit_changes_labels(db_handle, list(reassign_labels.keys()), list(reassign_labels.values()))

            # persist the cached deletions reassignments of the glyph model/view
            prog_count = 3
            self.broadcast_status(prog_count)
            delete_glyphs = self.persistence.cache.delete_glyphs
            if len(delete_glyphs):
                self.commit_changes_glyphs(db_handle, delete_glyphs, Constants.CATEGORY_DELETED)

            reassign_glyphs = self.persistence.cache.reassign_glyphs
            if len(reassign_glyphs):
                self.commit_changes_glyphs(db_handle, list(reassign_glyphs.keys()), list(reassign_glyphs.values()))

            # perform cleanup
            prog_count = 4
            QSqlDatabase.removeDatabase(self.conn_name)
            self.broadcast_status(prog_count)
            self.persistence.cache.clear()
            self.persistence.cache.notify_pending_edits()

            self.signals.succeeded.emit()
            self.signals.finished.emit()

        except Exception as e:
            logging.error("DBCommitRunnable", e)
            QSqlDatabase.removeDatabase(self.conn_name)

            self.signals.failed.emit()
            self.signals.finished.emit()

    def commit_changes_status(self,
                              db_connection: QSqlDatabase,
                              status_changes: Dict[str, int]):
        with Transaction(db_connection, name=f"trans_status", close_conn_on_exit=False):
            for enc, new_status in status_changes.items():
                self.gsql.update_encoding_status(db_connection, enc, new_status)

    def commit_changes_encoding(self,
                                db_connection: QSqlDatabase,
                                encodings: Set[str]):
        # Update category
        with Transaction(db_connection, name='trans_category', close_conn_on_exit=False):
            for enc in encodings:
                self.gsql.update_label(db_connection, enc, Constants.CATEGORY_DELETED, current_similarity=None,
                                       target_similarity=-1)
                self.gsql.delete_encoding(db_connection, enc)

    def commit_changes_labels(self,
                              db_connection: QSqlDatabase,
                              current: Union[List[Tuple[str, int]], Set[Tuple[str, int]]],
                              target: Union[str, List[str]]
                              ) -> None:
        if isinstance(target, list):
            assert len(current) == len(target)
        else:
            target = [target] * len(current)

        with Transaction(db_connection, name=f"trans_labels", close_conn_on_exit=False):
            for (current_label, current_similarity), tgt_label in zip(current, target):
                self.gsql.update_label(db_connection, current_label, tgt_label, current_similarity,
                                       target_similarity=-1)

    def commit_changes_glyphs(self,
                              db_connection: QSqlDatabase,
                              pks: Union[List[Tuple[str, str]], Set[Tuple[str, str]]],
                              target: Union[str, List[str]]
                              ) -> None:
        if isinstance(target, list):
            assert len(pks) == len(target)
        else:
            target = [target] * len(pks)

        with Transaction(db_connection, name=f"trans_glyphs", close_conn_on_exit=False):
            for (file_id, glyph_id), tgt_label in zip(pks, target):
                self.gsql.update_glyph_label(db_connection, pk=(file_id, glyph_id), label=tgt_label)
