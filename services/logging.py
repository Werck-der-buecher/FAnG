import asyncio
import logging
import logging.handlers
from queue import SimpleQueue as Queue
from typing import List

from .settings import Settings, SettingsError


def add_logging_level(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> add_logging_level('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


class LocalQueueHandler(logging.handlers.QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)


class LoggingService(object):
    def __init__(self, settings: Settings):
        self.settings = settings

    def setup_logging_queue(self) -> None:
        """Move log handlers to a separate thread.

        Replace handlers on the root logger with a LocalQueueHandler,
        and start a logging.QueueListener holding the original
        handlers.
        --> https://www.zopatista.com/python/2019/05/11/asyncio-logging/
        """
        queue = Queue()
        root = logging.getLogger()

        handlers: List[logging.Handler] = []

        handler = LocalQueueHandler(queue)
        root.addHandler(handler)
        for h in root.handlers[:]:
            if h is not handler:
                root.removeHandler(h)
                handlers.append(h)

        listener = logging.handlers.QueueListener(
            queue, *handlers, respect_handler_level=True
        )
        listener.start()

    def setup_logging(self) -> logging.Logger:
        # Logging
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()
        fileHandler = logging.FileHandler("wdb_app.log")
        fileHandler.setFormatter(logFormatter)
        root_logger.addHandler(fileHandler)

        add_logging_level('DOCKER_IMPORT', logging.INFO + 1)
        add_logging_level('DOCKER_WORKFLOW', logging.INFO + 2)
        try:
            debug_level = self.settings.debug_level
            debug_level = debug_level if debug_level != "EXCEPTION" else "DEBUG"
        except SettingsError:
            debug_level = "DEBUG"
        root_logger.setLevel(logging.getLevelNamesMapping()[debug_level])

        # move existing handlers to queue_listener
        self.setup_logging_queue()

        return root_logger






