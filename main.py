import asyncio
import functools
import logging
import logging.handlers
import os
import sys
from queue import SimpleQueue as Queue
from typing import List
import gc

import coloredlogs
import nest_asyncio
import qasync
from PySide6.QtWidgets import QApplication

from mainwindow import MainWindow
from services import Settings, SettingsNotFoundError, LoggingService
from modules import AppModule, WorkspaceModule
from config import Config, DefaultConfig

from injector import Injector



os.environ['QT_PLUGIN_PATH'] = './PySide6/plugins'
os.environ['QT_DEBUG_PLUGINS'] = '1'
basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.

    myappid = 'wdb.glyphextractor'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def setup_injector(config) -> Injector:
    def setup_configuration(binder):
        binder.bind(Config, to=config)

    return Injector([setup_configuration, AppModule])


def main():
    config = DefaultConfig()
    injector = setup_injector(config=config)

    settings = injector.get(Settings)
    logging_service = injector.get(LoggingService)

    try:
        settings.load()
    except SettingsNotFoundError:
        settings.save()

    logging_service.setup_logging()

    # Qt Application
    a = QApplication(sys.argv)
    a.addLibraryPath('plugins/sqldrivers')
    a.setWheelScrollLines(1)
    loop = qasync.QEventLoop(a)
    asyncio.set_event_loop(loop)

    w = injector.get(MainWindow)
    w.show()

    with loop:
        loop.run_forever()

    # sys.exit(QCoreApplication.exec())


async def asyncmain():
    Settings.get_instance().save()

    # Logging
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    fileHandler = logging.FileHandler("wdb_app.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(logging.DEBUG)
    add_logging_level('DOCKER_IMPORT', logging.INFO + 1)
    add_logging_level('DOCKER_WORKFLOW', logging.INFO + 2)
    try:
        debug_level = Settings.get_instance().debug_level
        debug_level = debug_level if debug_level != "EXCEPTION" else "DEBUG"
    except ConfigError:
        debug_level = "DEBUG"
    test = coloredlogs.install(fmt='%(levelname)s - %(message)s', level=debug_level)

    # move existing handlers to queue_listener
    setup_logging_queue()

    # Qt Application
    def close_future(future, loop):
        loop.call_later(10, future.cancel)
        future.cancel()

    loop = asyncio.get_event_loop()
    nest_asyncio.apply(loop)
    future = asyncio.Future()

    a = QApplication(sys.argv)
    if hasattr(a, "aboutToQuit"):
        getattr(a, "aboutToQuit").connect(
            functools.partial(close_future, future, loop)
        )
    a.addLibraryPath('plugins/sqldrivers')
    a.setWheelScrollLines(1)

    w = MainWindow()
    #w.show()

    await future
    return True


if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#    try:
#        qasync.run(main())
#    except asyncio.exceptions.CancelledError:
#        sys.exit(0)
