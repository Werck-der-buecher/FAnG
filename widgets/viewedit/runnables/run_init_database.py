from typing import List

import pickle
import logging
import numpy as np
from PIL import Image
from pathlib import Path
from PySide6.QtCore import (QRunnable, QByteArray)
from PySide6.QtSql import QSqlDatabase

from services import Settings, GSQLService, Transaction, SimilarityCalculationService
from widgets.viewedit.runnables.worker_signals import WorkerSignals

from injector import inject


class DBInitRunnable(QRunnable):
    @inject
    def __init__(self,
                 settings: Settings,
                 gsql_service: GSQLService,
                 workspace: str,
                 db_name: str,
                 pkl_list: List[str],
                 ocr_encodings: bool = False,
                 calc_similarities: bool = True,
                 ) -> None:
        super().__init__()
        self.settings = settings
        self.gsql = gsql_service

        self.workspace = workspace
        self.db_name = db_name
        self.pkl_list = pkl_list
        self.ocr_encodings = ocr_encodings
        self.calc_similarities = calc_similarities
        self.conn_name = "init_db"
        self.signals = WorkerSignals()

    def run(self):
        self.signals.status.emit("Initiating database")
        db_handle = self.gsql.init_db(self.workspace, self.db_name, connection_name=self.conn_name,
                                      logging_level=logging.INFO, keep_open=True)
        try:
            progress_count = 0
            encodings = [chr(i) for i in range(ord('a'), ord('z') + 1)] \
                        + [chr(i) + "_ood" for i in range(ord('a'), ord('z') + 1)] \
                        + [chr(i) for i in range(ord('A'), ord('Z') + 1)] \
                        + [chr(i) + "_ood" for i in range(ord('A'), ord('Z') + 1)] \
                        + ['--DELETED--']

            for pkl_file in sorted(self.pkl_list):
                entities = []
                self.signals.status.emit(f"Extracting glyphs from...\n'{Path(pkl_file).name}'")
                with open(pkl_file, "rb") as f:
                    while True:
                        try:
                            entities.append(pickle.load(f))
                        except EOFError:
                            break
                self.gsql.populate_glyph(db_handle, entities, logging_level=logging.INFO)
                progress_count += 1
                self.signals.progress.emit(progress_count)

                # append encoding
                for ent in entities:
                    if ent['label'] not in encodings:
                        encodings.append(ent['label'])
                    if (self.ocr_encodings and 'label_ocr' in ent
                            and ent['label_ocr'] is not None and ent['label_ocr'] not in encodings):
                        encodings.append(ent['label_ocr'])

            self.signals.status.emit("Generating encodings")
            self.gsql.populate_encoding(db_handle, encodings, logging_level=logging.INFO)
            self.signals.progress.emit(progress_count + 1)

            if self.calc_similarities:
                for enc in encodings:
                    self.signals.status.emit(f"Calculating similarity groups for category '<b>{enc}</b>'.")
                    self.calc_similarities_for_label(db_handle, enc)
                    print(enc)
            self.signals.progress.emit(progress_count + 1)

            self.gsql.finalize_db(db_handle)
            db_handle.close()
            del db_handle
            QSqlDatabase.removeDatabase(self.conn_name)
            self.signals.finished.emit()
            self.signals.succeeded.emit()
        except Exception as e:
            logging.error("DBInitRunnable: ", e)
            db_handle.close()
            del db_handle
            QSqlDatabase.removeDatabase(self.conn_name)
            self.signals.finished.emit()
            self.signals.failed.emit()

    def calc_similarities_for_label(self, db_handle: QSqlDatabase, label: str):
        # Fetch glyph images from database
        records = GSQLService.fetch_embeddings(db_handle, label, False)
        file_id_idx, glyph_id_idx, embedding_idx = 0, 1, 2

        # Parse image data from byte arrays
        X = []
        for i in range(len(records)):
            ba: QByteArray = records[i][embedding_idx]
            if isinstance(ba, str):
                raise TypeError(f"DB entry '{ba}' is a string, but must be a QByteArray. Cannot proceed...")

            embd: Image = np.frombuffer(ba.data(), dtype=np.dtype(np.float32))
            X.append(np.array(embd))

        if self.settings.similarity_sort == "hdbscan":
            sim_labels: List[int] = SimilarityCalculationService.pca_hdbscan(X)
        elif self.settings.similarity_sort == "kmeans":
            sim_labels: List[int] = SimilarityCalculationService.faiss(X)
        else:
            sim_labels: List[int] = SimilarityCalculationService.faiss(X)

        with Transaction(db_handle, name='dnd_update_glyph_similarity', close_conn_on_exit=False):
            for i in range(len(records)):
                pk = (records[i][file_id_idx], records[i][glyph_id_idx])
                GSQLService.update_glyph_similarity_index(db_handle, pk, sim_labels[i])
