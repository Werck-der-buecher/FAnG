import datetime
import logging
import traceback
from typing import Optional

from PySide6.QtSql import QSqlDatabase


class Transaction(object):
    """
    Transaction context manager
    see https://raw.githubusercontent.com/jsj2008/kdegames/master/kajongg/src/query.py
    """

    def __init__(self, db_handle: QSqlDatabase, name: Optional[str] = None, close_conn_on_exit: Optional[bool] = False,
                 logging_level: int = logging.INFO) -> None:
        """ Enter transaction
        :param name: Transaction name
        :param db_handle: Database connection
        :param close_conn_on_exit: Close the connection resource automatically after exiting the context.
        """
        self.db_handle = db_handle
        if name is None:
            dummy, dummy, name, dummy = traceback.extract_stack()[-2]
        self.name = f"{name or ''} on {self.db_handle.databaseName()}"
        self.close_on_exit = close_conn_on_exit
        self.logging_level = logging_level

        # Start database transaction
        if not self.db_handle.transaction():
            logging.log(self.logging_level, f'{self.name} cannot start: {self.db_handle.lastError().text()}')
        self.active = True
        self.start_time = datetime.datetime.now()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trback) -> None:
        """ Exit transaction
        :param exc_type:
        :param exc_value:
        :param trback:
        :return:
        """
        diff = datetime.datetime.now() - self.start_time
        if diff > datetime.timedelta(seconds=1.0):
            logging.log(self.logging_level, '%s took %d.%06d seconds' % (
                self.name, diff.seconds, diff.microseconds))
        if self.active and trback is None:
            if not self.db_handle.commit():
                logging.log(self.logging_level, f"{self.name}: cannot commit: {self.db_handle.lastError().text()}")
        else:
            if not self.db_handle.rollback():
                logging.log(self.logging_level, f"{self.name}: cannot rollback: {self.db_handle.databaseName()}")
            if exc_type:
                exc_type(exc_value)

        if self.close_on_exit:
            self.db_handle.close()

    def rollback(self) -> None:
        """ Explicit rollback.
        :return:
        """
        self.db_handle.rollback()
        self.active = False
        if self.close_on_exit:
            self.db_handle.close()
