from PIL import Image
from pathlib import Path
from typing import Union, Optional, List, Any, Tuple

import logging
import pickle
import io
import numpy as np

from PySide6.QtSql import QSqlDriver, QSqlDatabase, QSqlQuery, QSql
from PySide6.QtCore import QByteArray

from services.settings import Settings
from services.sql_service.schema import GSQLSchema
from services.sql_service.temp_storage_mode import DBTempStorageModes
from services.sql_service.transaction import Transaction
from services.sql_service.utils import check, dig_round, prune_label_name


class GSQLService(object):
    """
    Also see: https://raw.githubusercontent.com/jsj2008/kdegames/master/kajongg/src/query.py
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def init_db(self, workspace: Union[str, Path], db_name: Optional[str] = 'glyphs',
                connection_name: Optional[str] = 'default', keep_open: Optional[bool] = False,
                logging_level: int = logging.INFO):
        db_handle = QSqlDatabase.addDatabase("QSQLITE", connection_name)
        db_handle.setHostName("wdb")

        db_path = Path(workspace).joinpath(f"{db_name}.db")
        db_handle.setDatabaseName(str(db_path))

        logging.log(logging_level,
                    f"{'Using' if db_path.exists() else 'Creating'} database with name {db_name} in workspace at {workspace}.")

        db_handle.setConnectOptions("QSQLITE_BUSY_TIMEOUT=2000")
        check(logging_level, db_handle.open)

        assert db_handle.driver().hasFeature(QSqlDriver.DriverFeature.Transactions)

        if "glyph" not in db_handle.driver().tables(QSql.TableType.Tables):
            with Transaction(db_handle=db_handle, logging_level=logging_level, close_conn_on_exit=False):
                q = QSqlQuery(db_handle)
                q.exec(GSQLSchema.CREATE_TABLE_GLYPH)
                q.exec(GSQLSchema.CREATE_TABLE_ENCODING)

                # Single column index (ideally, this should already exist)
                q.exec(GSQLSchema.CREATE_LABEL_INDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_HEIGHT_INDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_WIDTH_INDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_SIZE_INDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_SIMILARITY_INDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_EMBEDDING_INDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_ENERGY_INDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_SCORE_INDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_UNIQUE_LABEL_ENCODING)

                # Multi column index
                q.exec(GSQLSchema.CREATE_LABEL_HEIGHT_MINDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_LABEL_WIDTH_MINDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_LABEL_SIZE_MINDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_LABEL_SIMILARITY_MINDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_LABEL_EMBEDDING_MINDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_LABEL_ENERGY_MINDEX_GLYPH)
                q.exec(GSQLSchema.CREATE_LABEL_SCORE_MINDEX_GLYPH)

                self.set_user_version(db_handle, GSQLSchema.CURRENT_SCHEMA_VERSION)

        # perform updates if necessary
        update1_status = self._inc_update_schema_UV1(db_handle, logging_level)
        if update1_status:
            logging.log(logging_level, f"Status for update 1: {update1_status}")

        update2_status = self._inc_update_schema_UV2(db_handle, logging_level)
        if update2_status:
            logging.log(logging_level, f"Status for update 2: {update2_status}")

        update3_status = self._inc_update_schema_UV3(db_handle, logging_level)
        if update3_status:
            logging.log(logging_level, f"Status for update 3: {update3_status}")

        update4_status = self._inc_update_schema_UV4(db_handle, logging_level)
        if update4_status:
            logging.log(logging_level, f"Status for update 4: {update4_status}")

        update5_status = self._inc_update_schema_UV5(db_handle, logging_level)
        if update5_status:
            logging.log(logging_level, f"Status for update 5: {update5_status}")

        update6_status = self._inc_update_schema_UV6(db_handle, logging_level)
        if update6_status:
            logging.log(logging_level, f"Status for update 6: {update6_status}")

        update7_status = self._inc_update_schema_UV7(db_handle, logging_level)
        if update7_status:
            logging.log(logging_level, f"Status for update 7: {update7_status}")

        # Views
        q = QSqlQuery(db_handle)
        q.exec(GSQLSchema.DROP_VIEW_LABEL)
        q.exec(GSQLSchema.CREATE_VIEW_LABEL)

        # Single column index
        q.exec(GSQLSchema.CREATE_LABEL_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_HEIGHT_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_WIDTH_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_SIZE_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_SIMILARITY_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_EMBEDDING_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_ENERGY_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_SCORE_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_UNIQUE_LABEL_ENCODING)

        # Multi column index
        q.exec(GSQLSchema.CREATE_LABEL_HEIGHT_MINDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_LABEL_WIDTH_MINDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_LABEL_SIZE_MINDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_LABEL_SIMILARITY_MINDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_LABEL_EMBEDDING_MINDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_LABEL_ENERGY_MINDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_LABEL_SCORE_MINDEX_GLYPH)

        # Performance tuning (pragmas)
        self.configure_connection(db_handle)

        if not keep_open:
            db_handle.close()

        return db_handle

    def get_or_create_connection(self, db_handle: str, db_default_handle: Optional[str] = "default",
                                 open: Optional[bool] = True, pragma_optim: Optional[bool] = True) -> QSqlDatabase:
        assert len(QSqlDatabase.connectionNames())
        if QSqlDatabase.contains(db_handle):
            conn = QSqlDatabase.database(db_handle, open=open)
        else:
            conn = QSqlDatabase.cloneDatabase(db_default_handle, db_handle)
            # default_conn = QSqlDatabase.database(db_default_handle, open=True)
            # database_name = Path(default_conn.databaseName()).parent.as_posix()
            # print(database_name)
            # conn = QSqlDatabase.addDatabase("QSQLITE", db_handle)
            # conn.setDatabaseName(r"D:\20_PostDoc\10_Data\10_Incunables\10_Processed\GW03182 0 Berlin SB\glyphs.db")
            if open:
                open_ok = conn.open()
                if open_ok and pragma_optim:
                    self.configure_connection(conn)
        return conn

    def close_connection(self, db_handle: str):
        if db_handle in QSqlDatabase.connectionNames():
            conn = QSqlDatabase.database(db_handle, open=False)
            conn.close()

    def close_all_connections(self) -> None:
        for conn_name in QSqlDatabase.connectionNames():
            QSqlDatabase.database(conn_name, False).close()
        # for conn_name in QSqlDatabase.connectionNames():
        #    print(conn_name, QSqlDatabase.database(conn_name, open=False).isOpen())

    def configure_connection(self, db_handle: QSqlDatabase):
        q = QSqlQuery(db_handle)
        q.exec(GSQLSchema.PRAGMA_JOURNAL_MODE)
        q.exec(GSQLSchema.PRAGMA_SYNCRONOUS)
        q.exec(GSQLSchema.PRAGMA_MMAP)
        q.exec(GSQLSchema.PRAGMA_PAGESIZE)
        q.exec(GSQLSchema.PRAGMA_CACHESIZE)
        q.exec(GSQLSchema.PRAGMA_LOCKINGMODE)

        temp_store = DBTempStorageModes[self.settings.temp_store.upper()]
        if temp_store == DBTempStorageModes.MEMORY:
            q.exec(GSQLSchema.PRAGMA_TEMP_MEMORY)
        elif temp_store == DBTempStorageModes.FILE:
            q.exec(GSQLSchema.PRAGMA_TEMP_FILE)
        else:
            q.exec(GSQLSchema.PRAGMA_TEMP_FILE)

    def _inc_update_schema_UV1(self, db_handle: QSqlDatabase, logging_level: int = logging.INFO) -> bool:
        tv = 1  # target schema version
        uv: int = self.get_user_version(db_handle)

        if uv >= tv:
            logging.log(logging_level, f"Current schema already at version {tv}. Continuing...")
            return False

        # changes
        logging.log(logging_level, f"Adding status column to encoding table.")
        q = QSqlQuery(db_handle)
        q.exec("""ALTER TABLE encoding ADD status INTEGER DEFAULT 0""")
        q.exec(GSQLSchema.CREATE_LABEL_INDEX_GLYPH)  # ideally, this should already exist
        q.exec(GSQLSchema.CREATE_HEIGHT_INDEX_GLYPH)  # ideally, this should already exist
        q.exec(GSQLSchema.CREATE_WIDTH_INDEX_GLYPH)  # ideally, this should already exist
        q.exec(GSQLSchema.CREATE_SIZE_INDEX_GLYPH)  # ideally, this should already exist

        # update to target version
        logging.log(logging_level, f"Updating schema version to {tv}.")
        self.set_user_version(db_handle, tv)
        return True

    def _inc_update_schema_UV2(self, db_handle: QSqlDatabase, logging_level: int = logging.INFO) -> bool:
        tv = 2  # target schema version
        uv: int = self.get_user_version(db_handle)

        if uv >= tv:
            logging.log(logging_level, f"Current schema already at version {tv}. Continuing...")
            return False

        # changes
        logging.log(logging_level, f"Adding similarity_index column to glyph table.")
        q = QSqlQuery(db_handle)
        q.exec("""ALTER TABLE glyph ADD similarity INTEGER DEFAULT -1""")
        q.exec(GSQLSchema.CREATE_SIMILARITY_INDEX_GLYPH)  # ideally, this should already exist

        # update to target version
        logging.log(logging_level, f"Updating schema version to {tv}.")
        self.set_user_version(db_handle, tv)
        return True

    def _inc_update_schema_UV3(self, db_handle: QSqlDatabase, logging_level: int = logging.INFO) -> bool:
        tv = 3  # target schema version
        uv: int = self.get_user_version(db_handle)

        if uv >= tv:
            logging.log(logging_level, f"Current schema already at version {tv}. Continuing...")
            return False

        # changes
        logging.log(logging_level, f"Adding embedding column to glyph table.")
        q = QSqlQuery(db_handle)
        q.exec("""ALTER TABLE glyph ADD embedding BLOB""")

        # update to target version
        logging.log(logging_level, f"Updating schema version to {tv}.")
        self.set_user_version(db_handle, tv)
        return True

    def _inc_update_schema_UV4(self, db_handle: QSqlDatabase, logging_level: int = logging.INFO) -> bool:
        tv = 4  # target schema version
        uv: int = self.get_user_version(db_handle)

        if uv >= tv:
            logging.log(logging_level, f"Current schema already at version {tv}. Continuing...")
            return False

        # changes
        logging.log(logging_level, f"Adding multi-column indices to glyph table.")
        q = QSqlQuery(db_handle)
        # Multi column index
        q.exec(GSQLSchema.CREATE_LABEL_HEIGHT_MINDEX_GLYPH)  # ideally, this should already exist
        q.exec(GSQLSchema.CREATE_LABEL_WIDTH_MINDEX_GLYPH)  # ideally, this should already exist
        q.exec(GSQLSchema.CREATE_LABEL_SIZE_MINDEX_GLYPH)  # ideally, this should already exist
        q.exec(GSQLSchema.CREATE_LABEL_SIMILARITY_MINDEX_GLYPH)  # ideally, this should already exist
        q.exec(GSQLSchema.CREATE_LABEL_EMBEDDING_MINDEX_GLYPH)  # ideally, this should already exist

        # update to target version
        logging.log(logging_level, f"Updating schema version to {tv}.")
        self.set_user_version(db_handle, tv)
        return True

    def _inc_update_schema_UV5(self, db_handle: QSqlDatabase, logging_level: int = logging.INFO) -> bool:
        tv = 5  # target schema version
        uv: int = self.get_user_version(db_handle)

        if uv >= tv:
            logging.log(logging_level, f"Current schema already at version {tv}. Continuing...")
            return False

        # changes
        q = QSqlQuery(db_handle)

        # Single-column index
        logging.log(logging_level, f"Adding additional single-column indices to glyph table.")
        q.exec(GSQLSchema.CREATE_ENERGY_INDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_SCORE_INDEX_GLYPH)

        logging.log(logging_level, f"Adding additional multi-label indices to glyph table.")
        q.exec(GSQLSchema.CREATE_LABEL_ENERGY_MINDEX_GLYPH)
        q.exec(GSQLSchema.CREATE_LABEL_SCORE_MINDEX_GLYPH)

        # update to target version
        logging.log(logging_level, f"Updating schema version to {tv}.")
        self.set_user_version(db_handle, tv)
        return True

    def _inc_update_schema_UV6(self, db_handle: QSqlDatabase, logging_level: int = logging.INFO) -> bool:
        tv = 6  # target schema version
        uv: int = self.get_user_version(db_handle)

        if uv >= tv:
            logging.log(logging_level, f"Current schema already at version {tv}. Continuing...")
            return False

        # changes
        q = QSqlQuery(db_handle)

        # Single-column index
        logging.log(logging_level, f"Adding additional single-column index to encoding table.")
        q.exec(GSQLSchema.CREATE_UNIQUE_LABEL_ENCODING)

        # update to target version
        logging.log(logging_level, f"Updating schema version to {tv}.")
        self.set_user_version(db_handle, tv)
        return True

    def _inc_update_schema_UV7(self, db_handle: QSqlDatabase, logging_level: int = logging.INFO) -> bool:
        tv = 7  # target schema version
        uv: int = self.get_user_version(db_handle)

        if uv >= tv:
            logging.log(logging_level, f"Current schema already at version {tv}. Continuing...")
            return False

        # changes
        logging.log(logging_level, f"Adding coordinate columns to glyph table.")
        q = QSqlQuery(db_handle)
        q.exec("""ALTER TABLE glyph ADD coords_rel TEXT""")
        q.exec("""ALTER TABLE glyph ADD coords_abs TEXT""")

        # update to target version
        logging.log(logging_level, f"Updating schema version to {tv}.")
        self.set_user_version(db_handle, tv)
        return True

    def populate_glyph(self, db_handle: QSqlDatabase, entities: List[Any], logging_level: int = logging.INFO):
        """
        :param entities: Glyph data entries
        :return:
        """
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.INSERT_VALS_GLYPH)

        s_bins = np.linspace(0, 1, 41)
        e_bins = np.linspace(-5, 5, 41)
        with Transaction(db_handle=db_handle, logging_level=logging_level):
            for ent in entities:
                vals = [
                    ent['file_id'], ent['region_id'], ent['line_id'], ent['word_id'], ent['glyph_id'], ent['extension'],
                    QByteArray(ent['img']), QByteArray(ent['embedding']) if 'embedding' in ent else None,
                    ent['img_size'][1], ent['img_size'][0], ent['description']['DPI'], ent['label']]

                for k in ['label_ocr', 'E', 'score_py']:
                    # Bin score and energy for efficient DB sorting
                    if k in ent:
                        if k == 'E':
                            v = dig_round(ent[k], e_bins).item()
                        elif k == 'score_py':
                            v = dig_round(ent[k], s_bins).item()
                        else:
                            v = ent[k]
                        vals.append(v)
                    else:
                        vals.append(None)

                # Append relative and absolute coordinates on the image.
                vals.append("_".join(f"{coords[0]}_{coords[1]}" for coords in ent["description"]['coords_rel']))
                vals.append("_".join(f"{coords[0]}_{coords[1]}" for coords in ent["description"]['coords_abs']))

                for val in vals:
                    query.addBindValue(val)
                query.exec()

    def populate_embeddings(self, db_handle: QSqlDatabase, entities: List[Any], logging_level: int = logging.INFO):
        """
        :param entities: Glyph data entries
        :return:
        """
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.UPDATE_GLYPH_EMBEDDING)
        with Transaction(db_handle, name='dnd_update_glyph_similarity', logging_level=logging_level):
            for ent in entities:
                query.addBindValue(QByteArray(ent['embedding']))
                query.addBindValue(ent['file_id'])
                query.addBindValue(ent['glyph_id'])
                query.exec()

    def populate_encoding(self, db_handle: QSqlDatabase, encodings: List[Any], logging_level: int = logging.INFO):
        """
        :param entities: Glyph data entries
        :return:
        """
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.INSERT_VALS_ENCODING)

        with Transaction(db_handle=db_handle, logging_level=logging_level):
            for enc in encodings:
                query.addBindValue(enc)
                query.addBindValue(0)
                query.exec()

    def retrieve_records(self, query: QSqlQuery, fetch_num: int = -1):
        record = query.record()
        count = record.count()
        fields = [record.field(x) for x in range(count)]
        records = []
        qi = 0

        while query.next():
            if fetch_num != -1 and qi >= fetch_num:
                break
            qi += 1
            records.append([query.value(idx) for idx in range(count)])

        return records, fields

    def fetch_records(self, db_handle: QSqlDatabase, label: str = None, return_fields: bool = False,
                      fetch_num: int = -1):
        if label is None:
            label = 'label'

        query = QSqlQuery(db_handle)
        query.setForwardOnly(True)
        query.prepare(GSQLSchema.SELECT_ALL_LABEL)
        query.addBindValue(label)
        query.exec()

        records, fields = self.retrieve_records(query, fetch_num)
        out = (records, fields) if return_fields else records
        return out

    def fetch_embeddings(self, db_handle: QSqlDatabase, label: str = None, return_fields: bool = False,
                         fetch_num: int = -1):
        if label is None:
            label = 'label'

        query = QSqlQuery(db_handle)
        query.setForwardOnly(True)
        query.prepare(GSQLSchema.SELECT_EMBEDDINGS)
        query.addBindValue(label)
        query.exec()

        records, fields = self.retrieve_records(query, fetch_num)
        out = (records, fields) if return_fields else records
        return out

    def fetch_nullemb_records(self, db_handle: QSqlDatabase, label: str = None, return_fields: bool = False,
                              fetch_num: int = -1):
        query = QSqlQuery(db_handle)
        query.setForwardOnly(True)
        if label is None:
            query.exec(GSQLSchema.SELECT_ALL_NULL_EMBD)
        else:
            query.prepare(GSQLSchema.SELECT_ALL_LABEL_NULL_EMBD)
            query.addBindValue(label)
            query.exec()

        records, fields = self.retrieve_records(query, fetch_num)
        out = (records, fields) if return_fields else records
        return out

    def get_distinct_labels(self, db_handle: QSqlDatabase):
        query = QSqlQuery(db_handle)
        query.exec(GSQLSchema.SELECT_LABEL_VIEW)
        records, fields = self.retrieve_records(query)
        return [lbl[0] for lbl in records]

    def get_label_count(self, db_handle: QSqlDatabase, label: str, similarity_group: Optional[int] = None):
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.SELECT_LABEL_COUNT)
        query.addBindValue(label)
        query.addBindValue(similarity_group)
        query.exec()
        records, _ = self.retrieve_records(query)
        return records[0][0]

    def update_label(self,
                     db_handle: QSqlDatabase,
                     current_label: str,
                     target_label: str,
                     current_similarity: Optional[int] = None,
                     target_similarity: Optional[int] = None) -> None:
        # Update label in glyph table
        queryA = QSqlQuery(db_handle)
        queryA.prepare(GSQLSchema.UPDATE_LABEL)
        queryA.addBindValue(target_label)
        queryA.addBindValue(target_similarity)
        queryA.addBindValue(current_label)
        queryA.addBindValue(current_similarity)
        queryA.exec()

        # Update label/encoding in encoding table
        # - Case 1: Overwrite encoding if the complete category shall be updated
        # - Case 2: Add new encoding if the partial category shall be updated
        queryB = QSqlQuery(db_handle)
        if current_similarity is None:
            queryB.prepare(GSQLSchema.UPDATE_ENCODING)
            queryB.addBindValue(target_label)
            queryB.addBindValue(current_label)
        else:
            queryB.prepare(GSQLSchema.INSERT_VALS_ENCODING)
            queryB.addBindValue(target_label)
            queryB.addBindValue(0)
        queryB.exec()

    def delete_label(self, db_handle: QSqlDatabase, label: str, deleted_value: Optional[str] = None,
                     similarity_group: Optional[int] = None):
        if deleted_value is not None:
            self.update_label(db_handle, label, deleted_value, similarity_group)
            return

        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.DELETE_LABEL)
        query.addBindValue(label)
        query.addBindValue(similarity_group)
        query.exec()

    def insert_encoding(self, db_handle: QSqlDatabase, enc: str):
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.INSERT_VALS_ENCODING)
        query.addBindValue(enc)
        query.addBindValue(0)
        query.exec()

    def delete_encoding(self, db_handle: QSqlDatabase, enc: str):
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.DELETE_ENCODING)
        query.addBindValue(enc)
        query.exec()

    def update_encoding_status(self, db_handle: QSqlDatabase, enc: str, status: int):
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.UPDATE_ENCODING_STATUS)
        query.addBindValue(status)
        query.addBindValue(enc)
        query.exec()

    def update_glyph_label(self, db_handle: QSqlDatabase, pk: Tuple[str, str], label: prune_label_name) -> int:
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.UPDATE_GLYPH_LABEL)
        query.addBindValue(label)
        query.addBindValue(pk[0])
        query.addBindValue(pk[1])

        if query.exec_():
            return query.numRowsAffected()
        else:
            print(query.lastError().text())
            return -1

    def update_glyph_labels(self, db_handle: QSqlDatabase, pks: List[Tuple[str, str]], label: prune_label_name) -> int:
        # UPDATE_GLYPH_LABEL = """
        #    UPDATE glyph SET label=? WHERE (file_id, glyph_id) in (%s)
        #    """
        query = QSqlQuery(db_handle)
        placeholder = ["(?, ?)"]
        placeholders = ', '.join(placeholder * len(pks))
        query.prepare(GSQLSchema.UPDATE_GLYPH_LABEL % placeholders)
        query.addBindValue(label)
        for pk in pks:
            query.addBindValue(pk[0])
            query.addBindValue(pk[1])

        if query.exec_():
            return query.numRowsAffected()
        else:
            print(query.lastError().text())
            return -1

    def get_glyph_similarities(self, db_handle: QSqlDatabase, label: str):
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.SELECT_GLYPH_SIMILARITIES)
        query.addBindValue(label)
        query.exec()
        records, fields = self.retrieve_records(query)

        return [sim[0] for sim in records]

    def update_glyph_similarity_index(self, db_handle: QSqlDatabase, pk: Tuple[str, str], sim_index: int) -> int:
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.UPDATE_GLYPH_SIMILARITY)
        query.addBindValue(sim_index)
        query.addBindValue(pk[0])
        query.addBindValue(pk[1])

        if query.exec_():
            return query.numRowsAffected()
        else:
            print(query.lastError().text())
            return -1

    def update_glyph_embedding(self, db_handle: QSqlDatabase, pk: Tuple[str, str], embedding: bytes):
        """
        Update fields of existing entries in the glyph database.
        :param db_handle: reference to sql_service database
        :param pk: primary key tuple (file_id, glyph_id)
        :param embedding: bytes array of glyph embedding
        :return:
        """
        query = QSqlQuery(db_handle)
        query.prepare(GSQLSchema.UPDATE_GLYPH_EMBEDDING)
        query.addBindValue(embedding)
        query.addBindValue(pk[0])
        query.addBindValue(pk[1])

        if query.exec_():
            return query.numRowsAffected()
        else:
            print(query.lastError().text())
            return -1

    def get_shape_for_label(self, db_handle: QSqlDatabase, label: str, agg: str = 'mean'):
        query = QSqlQuery(db_handle)
        if agg == 'mean':
            query.exec(GSQLSchema.SELECT_MEAN_SHAPE % label)
            records, _ = self.retrieve_records(query)
            return records[0]
        elif agg == 'median':
            query.exec(GSQLSchema.SELECT_MEDIAN_HEIGHT % (label, label))
            records, _ = self.retrieve_records(query)
            height = records[0][0]
            query.exec(GSQLSchema.SELECT_MEDIAN_WIDTH % (label, label))
            records, _ = self.retrieve_records(query)
            width = records[0][0]
            return f"[{height}, {width}]"
        else:
            return NotImplementedError("Provided value for argument 'agg' is not supported.")

    def table_has_field(self, db_handle: QSqlDatabase, field: str) -> bool:
        query = QSqlQuery(db_handle)
        query.exec("""SELECT * FROM glyph""")
        record = query.record()
        for idx in range(record.count()):
            if record.fieldName(idx) == field:
                return True

    def get_user_version(self, db_handle: QSqlDatabase) -> int:
        query = QSqlQuery(db_handle)
        query.exec(GSQLSchema.GET_USER_VERSION)
        records, _ = self.retrieve_records(query)

        return records[0][0]

    def set_user_version(self, db_handle: QSqlDatabase, version: int) -> None:
        current_version = self.get_user_version(db_handle)
        if version <= current_version:
            raise ValueError("Provided version is smaller or equal to the current schema version.")
        query = QSqlQuery(db_handle)
        query.exec(GSQLSchema.SET_USER_VERSION % version)

    def delete(self, db_handle: QSqlDatabase) -> bool:
        query = QSqlQuery(db_handle)
        query.exec(GSQLSchema.DROP_TABLE_GLYPH)
        return "glyph" not in db_handle.driver().hasFeature(QSqlDriver.DriverFeature.Transactions)

    def finalize_db(self, db_handle: QSqlDatabase, close=True) -> bool:
        query = QSqlQuery(db_handle)
        query.exec(GSQLSchema.PRAGMA_ANALYSISLIMIT)
        query.exec(GSQLSchema.PRAGMA_OPTIM)

        if close:
            db_handle.close()
        return not db_handle.isOpen()


if __name__ == '__main__':
    workspace = r"C:\PostDoc\GlyphExtractorApp\sample_workspace"
    file_name = "glyphs"

    entities = []
    for obj in Path(workspace).glob('*.pkl'):
        with open(obj, "rb") as f:
            while 1:
                try:
                    entities.append(pickle.load(f))
                except EOFError:
                    break

    encodings = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [chr(i) for i in range(ord('A'), ord('Z') + 1)] + [
        "TestABC"]

    gdb_client = GSQLService()
    db_handle = gdb_client.init_db(workspace, file_name, logging_level=logging.INFO)

    gdb_client.populate_glyph(db_handle, entities, logging_level=logging.INFO)
    gdb_client.populate_encoding(db_handle, encodings, logging_level=logging.INFO)
    glyphs_i, fields = gdb_client.fetch_records(db_handle, 'a', return_fields=True)
    distinct_labels = gdb_client.get_distinct_labels(db_handle)
    gdb_client.finalize_db(db_handle)

    print(distinct_labels)
    print(fields)
    image = Image.open(io.BytesIO(glyphs_i[300][7].data()))
    image.show()
