from typing import List

import logging
import numpy as np
from PIL import Image
from PySide6.QtCore import (QRunnable, QByteArray)
from PySide6.QtSql import (QSqlDatabase)

from services import GSQLService, Transaction, SimilarityCalculationService
from services import Settings
from widgets.viewedit.runnables.worker_signals import WorkerSignals

from injector import inject


class SimilarityCalcRunnable(QRunnable):
    NUM_STAGES = 5

    @inject
    def __init__(self,
                 gsql_service: GSQLService,
                 simcalc_service: SimilarityCalculationService,
                 settings: Settings,
                 label: str
                 ) -> None:
        super().__init__()
        self.gsql = gsql_service
        self.simcalc = simcalc_service
        self.settings = settings
        self.label = label
        self.conn_name = "sim_calc"
        self.messages = [
            f"Fetching glyph info for label '<b>{self.label}</b>",
            f"Parsing embedding data for label '<b>{self.label}</b>'",
            f"Calculating similarities for label '<b>{self.label}</b>'",
            "Updating entries in the database",
            "Done"
        ]
        assert len(self.messages) == SimilarityCalcRunnable.NUM_STAGES
        self.signals = WorkerSignals()

    def broadcast_status(self, prog: int) -> None:
        msg = self.messages[prog]
        msg = f"[{prog + 1}/{len(self.messages)}] {msg} ..."
        self.signals.progress.emit(prog)
        self.signals.status.emit(msg)

    def run(self):
        # establish connection
        db_handle = self.gsql.get_or_create_connection(self.conn_name)

        try:
            # Fetch glyph images from database
            prog_count = 0
            self.broadcast_status(prog_count)
            records = self.gsql.fetch_embeddings(db_handle, self.label, return_fields=False)
            file_id_idx, glyph_id_idx, embedding_idx = 0, 1, 2

            # Parse image data from byte arrays
            prog_count = 1
            self.broadcast_status(prog_count)
            X = []
            for i in range(len(records)):
                ba: QByteArray = records[i][embedding_idx]
                if isinstance(ba, str):
                    raise TypeError(f"DB entry '{ba}' is a string, but must be a QByteArray. Cannot proceed...")
                embd: Image = np.frombuffer(ba.data(), dtype=np.dtype(np.float32))
                X.append(np.array(embd))

            prog_count = 2
            self.broadcast_status(prog_count)
            if self.settings.similarity_sort == "hdbscan":
                sim_labels: List[int] = self.simcalc.pca_hdbscan(X)
            elif self.settings.similarity_sort == "kmeans":
                sim_labels: List[int] = self.simcalc.faiss(X)
            else:
                sim_labels: List[int] = self.simcalc.faiss(X)

            prog_count = 3
            self.broadcast_status(prog_count)
            with Transaction(db_handle, name='dnd_update_glyph_similarity', close_conn_on_exit=True):
                for i in range(len(records)):
                    pk = (records[i][file_id_idx], records[i][glyph_id_idx])
                    self.gsql.update_glyph_similarity_index(db_handle, pk, sim_labels[i])

            prog_count = 4
            self.broadcast_status(prog_count)

            db_handle.close()
            QSqlDatabase.removeDatabase(self.conn_name)

            self.signals.succeeded.emit()
            self.signals.finished.emit()

        except Exception as e:
            logging.error("SimilarityCalcRunnable: ", e)
            db_handle.close()
            QSqlDatabase.removeDatabase(self.conn_name)

            self.signals.failed.emit()
            self.signals.finished.emit()
