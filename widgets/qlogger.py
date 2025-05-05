import logging
from PySide6.QtCore import Signal, QObject


class LogDisplayHandler(logging.Handler, QObject):
    new_record = Signal(object)

    def __init__(self, parent):
        super().__init__(parent)
        super(logging.Handler).__init__()
        formatter = LogDisplayFormatter('%(asctime)s|%(levelname)s|%(message)s|', '%d/%m/%Y %H:%M:%S')
        self.setFormatter(formatter)

    def emit(self, record):
        msg = self.format(record)
        self.new_record.emit(msg)


class LogDisplayFormatter(logging.Formatter):
    def formatException(self, ei):
        result = super(LogDisplayFormatter, self).formatException(ei)
        return result

    def format(self, record):
        s = super(LogDisplayFormatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '')
        return s


class QLogHandler(logging.Handler):
    class Emitter(QObject):
        log = Signal(str)

    def __init__(self):
        super().__init__()

        # Create a QObject which will emit a signal for each log. This implicitly queues each
        # appendPlainText() call which makes it thread-safe
        self.emitter = QLogHandler.Emitter()

    # override Handler's emit method (this happens to share a name with Qt's emit method.
    # Don't get confused)
    def emit(self, record):
        msg = self.format(record)
        self.emitter.log.emit(msg) # emit a signal containing the log (emit in the Qt sense)


class LogLevelFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno == self.__level