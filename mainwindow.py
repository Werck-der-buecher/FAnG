from injector import inject, noninjectable
import asyncio
import logging
import os
import re
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Optional

import pyuac
import qdarktheme
from PySide6.QtCore import (Qt, QThreadPool, QStandardPaths, QUrl, Slot, QTimer,
                            QDir, QFile, QFileInfo, QIODevice, QDirIterator, QTextStream)
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog, QMainWindow, QMessageBox,
                               QWidget, QFrame, QPushButton, QProgressBar, QLabel, QFileSystemModel, QCompleter)
from aiodocker.exceptions import DockerError
from qasync import asyncSlot, asyncClose

from app_icons import AppIcons
from services.docker_service import AsyncDockerService
from services import OCRDService, GlyphClassifierService, DBTempStorageModes, Settings, WorkspacePersistenceService
from ui_mainwindow import Ui_MainWindow
from widgets import DirValidator, IntValidator, QLogHandler, LogLevelFilter, PopUpProgressBar
from widgets.viewedit.glyphs.glyphs_model import GlyphsSQLModel
from widgets.viewedit.vieweditwidget import ViewEditWidget


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


class SortingAlgorithms(Enum):
    KMEANS = "K-Means -- (Fast Execution / Moderate Grouping)"
    HDBSCAN = "HDBSCAN -- (Slow Execution / Strong Grouping)"


class AppThemes(Enum):
    LIGHT = "Light Theme"
    DARK = "Dark Theme"


class MainWindow(QMainWindow):
    @inject
    @noninjectable('parent')
    @noninjectable('flags')
    def __init__(self,
                 settings: Settings,
                 docker_service: AsyncDockerService,
                 ocrd_service: OCRDService,
                 classifier_service: GlyphClassifierService,
                 parent: Optional[QWidget] = None,
                 flags: Qt.WindowFlags = Qt.WindowFlags.Window,
                 ) -> None:
        super().__init__(parent, flags)
        # Docker manager and dockerized services
        self.settings = settings
        self.docker_service: AsyncDockerService = docker_service
        self.ocrd_service: OCRDService = ocrd_service
        self.classifier_service: GlyphClassifierService = classifier_service

        # Init app theme
        self.init_app_theme()

        # Import UI component (based off Qt Designer UI file) & load UI components and set signal/slot handlers
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set completer based on the local filesystem
        self.fs_model = QFileSystemModel()
        self.fs_model.setFilter(QDir.AllDirs | QDir.Drives)
        self.fs_model.setRootPath('')
        self.completer = QCompleter()
        self.completer.setModel(self.fs_model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        ### UI Setup
        self.toggle_app_availability(False)
        self.init_ui_setupTab()
        self.init_ui_importTab()
        self.init_ui_extractTab()
        self.init_ui_viewEditTab()
        self.init_ui_exportTab()
        self.init_ui_settingsTab()

        # Set setup page to first page
        self.ui.tabWidget.setCurrentWidget(self.ui.tabWidget.findChild(QWidget, 'setupTab'))

        # Initial setup
        self.check_docker_system_status()

        # Worker Thread
        self.threadpool = QThreadPool()
        self.wpbar = PopUpProgressBar("Task Progress")
        self.wpbar.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.wpbar.hide()

    def init_app_theme(self):
        qss = """       
            QFrame {
                border: 0px;
            }    

            LabelTreeView {
                border: 1px solid grey;
            }  

            GlyphListView {
                border: 1px solid grey;
            }
        """
        custom_colors = {
            "[light]": {
                "background": "#e8e8e8",
                "border": "#f2f1ef",
                "foreground": "#bfbfbf"
            }
        }

        # Load app theme from autosave
        app_theme = self.settings.app_theme
        qdarktheme.setup_theme(app_theme, corner_shape="sharp", additional_qss=qss)  # , custom_colors=custom_colors

    def init_ui_setupTab(self):
        # Set icon
        self.ui.tabWidget.setTabIcon(0, AppIcons.get_icon(AppIcons.ICON_SETUP, self.style()))

        # Disable Local Docker Image loading
        self.ui.pushButtonDockerOCRDLocal.setEnabled(False)
        self.ui.pushButtonDockerEBMLocal.setEnabled(False)

        # Set Event handlers for Docker Image pull QPushButtons
        self.ui.pushButtonDockerOCRDRemote.clicked.connect(
            lambda docker_image=self.settings.docker_image_ocrd,
                   btn=self.ui.pushButtonDockerOCRDRemote,
                   pbar=self.ui.progressBarDockerOCRD,
                   status_label=self.ui.labelDockerOCRDStatus: self.pull_remote_docker_image(docker_image, btn, pbar,
                                                                                             status_label))
        self.ui.pushButtonDockerEBMRemote.clicked.connect(
            lambda docker_image=self.settings.docker_image_classifier,
                   btn=self.ui.pushButtonDockerEBMRemote,
                   pbar=self.ui.progressBarDockerEBM,
                   status_label=self.ui.labelDockerEBMStatus: self.pull_remote_docker_image(docker_image, btn, pbar,
                                                                                            status_label))

    def init_ui_importTab(self) -> None:
        """ Initialize data/workspace import tab.
        :return: None
        """
        # Set icon
        self.ui.tabWidget.setTabIcon(1, AppIcons.get_icon(AppIcons.ICON_IMPORT, self.style()))

        # Set validator and completer to data directory selection & change color upon validation change
        dir_validator = DirValidator()
        dir_validator.validationChanged.connect(partial(self.handle_validation_change,
                                                        qwidget=self.ui.lineEditDataSel,
                                                        reset_time=5000))
        self.ui.lineEditDataSel.setValidator(dir_validator)
        self.ui.lineEditDataSel.setCompleter(self.completer)

        # Parallelization options
        self.ui.radioButtonImportNone.toggle()
        self.ui.lineEditBatchSize.setEnabled(False)
        self.ui.radioButtonImportBatchSize.toggled.connect(self.on_batchSize_toggled)
        bs_validator = IntValidator(1, 100)
        self.ui.lineEditBatchSize.setValidator(bs_validator)
        bs_validator.validationChanged.connect(partial(self.handle_validation_change,
                                                       qwidget=self.ui.lineEditBatchSize,
                                                       reset_time=5000))

        # Data format options
        self.ui.checkBoxConvert.setChecked(False)
        self.ui.checkBoxNoNumIDs.setChecked(False)
        dpi_validator = IntValidator(100, 900)
        self.ui.lineEditDPI.setValidator(dpi_validator)
        dpi_validator.validationChanged.connect(partial(self.handle_validation_change,
                                                        qwidget=self.ui.lineEditDPI,
                                                        reset_time=5000))

        # Connect custom docker logger for workflow
        qlogger_import = QLogHandler()
        qlogger_import.setLevel("DOCKER_IMPORT")
        qlogger_import.addFilter(LogLevelFilter(logging._checkLevel("DOCKER_IMPORT")))
        logging.getLogger().addHandler(qlogger_import)
        qlogger_import.emitter.log.connect(self.ui.plainTextEditCreateWorkspace.appendPlainText)

        # Connect push button for data directory selection
        self.ui.pushButtonDataSel.clicked.connect(self.on_openDataDirectory_triggered)

        # Connect push button for data workspace creation/data import
        self.ui.pushButtonImport.clicked.connect(self.run_workspace_import)

    def init_ui_extractTab(self):
        # Set icon
        self.ui.tabWidget.setTabIcon(2, AppIcons.get_icon(AppIcons.ICON_EXTRACT, self.style()))

        # Populate workflow selection combo box
        it = QDirIterator(":/workflows")
        while it.hasNext():
            fn = it.next()
            self.ui.comboBoxWorkflowSel.addItem(str(Path(fn).name), userData=fn)
        self.ui.comboBoxWorkflowSel.model().sort(0, Qt.SortOrder.DescendingOrder)
        self.ui.comboBoxWorkflowSel.setCurrentIndex(0)

        # Set validator and completer to workspace selection & change color upon validation change
        dir_validator = DirValidator(self.ui.lineEditWorkspaceSel)
        dir_validator.validationChanged.connect(partial(self.handle_validation_change,
                                                        qwidget=self.ui.lineEditWorkspaceSel,
                                                        reset_time=5000))
        self.ui.lineEditWorkspaceSel.setValidator(dir_validator)
        self.ui.lineEditWorkspaceSel.setCompleter(self.completer)

        # Connect push button for workspace directory selection
        self.ui.pushButtonWorkspaceSel.clicked.connect(self.on_openWorkspaceDirectory_triggered)

        # Connect horizontal slider and spinbox for workflow parallelization
        self.ui.horizontalSliderParalellization.valueChanged.connect(self.ui.spinBoxParallelization.setValue)
        self.ui.spinBoxParallelization.valueChanged.connect(self.ui.horizontalSliderParalellization.setValue)
        # self.ui.horizontalSliderParalellization.setEnabled(False)
        # self.ui.spinBoxParallelization.setEnabled(False)

        # Connect push button for workflow execution
        self.ui.pushButtonRunWorkflow.clicked.connect(self.on_workflow_execution_triggered)

        # Connect custom docker logger for workflow execution
        qlogger_workflow = QLogHandler()
        # formatter = coloredlogs.ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # qlogger_workflow.setFormatter(formatter)
        qlogger_workflow.setLevel("DOCKER_WORKFLOW")
        qlogger_workflow.addFilter(LogLevelFilter(logging._checkLevel("DOCKER_WORKFLOW")))
        logging.getLogger().addHandler(qlogger_workflow)
        qlogger_workflow.emitter.log.connect(self.ui.plainTextEditWorkflowLogs.appendPlainText)

    def init_ui_viewEditTab(self):
        # Set icon
        self.ui.tabWidget.setTabIcon(3, AppIcons.get_icon(AppIcons.ICON_VIEWEDIT, self.style()))

        # Set label icon
        self.ui.labelDBImport.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_FAIL, self.style()))

        # Set validator and completer to data directory selection & change color upon validation change
        dir_validator = DirValidator()
        dir_validator.validationChanged.connect(partial(self.handle_validation_change,
                                                        qwidget=self.ui.lineEditViewEdit,
                                                        reset_time=5000))
        self.ui.lineEditViewEdit.setValidator(dir_validator)
        self.ui.lineEditViewEdit.setCompleter(self.completer)
        self.ui.pushButtonViewEdit.clicked.connect(self.on_openWorkspaceViewEdit_triggered)
        self.ui.pushButtonViewEditImport.clicked.connect(self.run_load_reload_viewedit)

        # Signal is called when database has been initialized or if initialization failed.
        self.ui.viewEditDynFrame.about_to_load.connect(self.on_workspace_about_to_load)
        self.ui.viewEditDynFrame.loaded.connect(self.on_workspace_loaded)
        self.ui.viewEditDynFrame.setEnabled(False)

    def init_ui_exportTab(self):
        # Set icon
        self.ui.tabWidget.setTabIcon(4, AppIcons.get_icon(AppIcons.ICON_EXPORT, self.style()))
        pass

    def init_ui_settingsTab(self):
        # Set icon
        self.ui.tabWidget.setTabIcon(5, AppIcons.get_icon(AppIcons.ICON_SETTINGS, self.style()))

        # Sorting algorithm
        for e in SortingAlgorithms:
            self.ui.similaritySortAlgorithmComboBox.addItem(e.value)

        sort_alg = SortingAlgorithms[self.settings.similarity_sort.upper()].value
        self.ui.similaritySortAlgorithmComboBox.setCurrentText(sort_alg)
        self.ui.similaritySortAlgorithmComboBox.currentTextChanged.connect(self.on_set_similarity_sorting_algorithm)

        # Database temporary storage
        for e in DBTempStorageModes:
            self.ui.tempStoreComboBox.addItem(e.value)

        temp_store = DBTempStorageModes[self.settings.temp_store.upper()].value
        self.ui.tempStoreComboBox.setCurrentText(temp_store)
        self.ui.tempStoreComboBox.currentTextChanged.connect(self.on_set_temp_store)

        # Autosave
        autosave = self.settings.autosave
        self.ui.autosaveCheckBox.setChecked(autosave)
        self.ui.autosaveCheckBox.stateChanged.connect(self.on_set_autosave)

        # App color theme
        for e in AppThemes:
            self.ui.appThemeComboBox.addItem(e.value)
        app_theme = AppThemes[self.settings.app_theme.upper()].value
        self.ui.appThemeComboBox.setCurrentText(app_theme)
        self.ui.appThemeComboBox.currentTextChanged.connect(self.on_toggle_apptheme)

    ### GENERAL
    @asyncClose
    async def closeEvent(self, event):
        """
        Safe close routine invoked upon exiting the app.
        """
        logging.info("Closing application safely")
        if not self.check_dirty_workspace_state():
            event.ignore()

        autosave = self.settings.autosave
        if autosave:
            logging.info("Saving workspace")
            self.save_workspace()

        if self.docker_service is not None:
            await self.docker_service.close()

    @Slot(bool)
    def toggle_app_availability(self, active_state: bool):
        # for ti in range(1, self.ui.tabWidget.count()):
        self.ui.tabWidget.setTabEnabled(1, active_state)
        self.ui.tabWidget.setTabEnabled(2, active_state)
        self.ui.tabWidget.setTabEnabled(4, active_state)

    @Slot()
    def check_dirty_workspace_state(self) -> bool:
        ve_widget: ViewEditWidget = self.ui.viewEditDynFrame
        glyph_model: GlyphsSQLModel = ve_widget.glyph_model
        workspace_persistence: WorkspacePersistenceService = ve_widget.persistence
        if (glyph_model is not None
                and workspace_persistence is not None
                and workspace_persistence.cache.is_dirty):
            num_pending_changes = workspace_persistence.cache.num_pending_changes
            msg = f"<p>There are currently <b>{num_pending_changes}</b> pending changes that are not saved in the database.</p>" \
                  f"<p>Do you really want to close the application?</p>"
            return self.question_message("Unsaved changes", msg)
        else:
            return True

    @Slot()
    def save_workspace(self):
        ve_widget: ViewEditWidget = self.ui.viewEditDynFrame
        ve_widget.dispatch_autosave()

    @Slot(QValidator.State, QWidget, int)
    def handle_validation_change(self, state: QValidator.State, qwidget: QWidget, reset_time: int = 0):
        if state == QValidator.State.Invalid:
            color = 'red'
        elif state == QValidator.State.Intermediate:
            color = 'gold'
        elif state == QValidator.State.Acceptable:
            color = 'lime'
        else:
            color = 'black'
        qwidget.setStyleSheet(f'border: 2px solid {color}')
        if reset_time:
            QTimer.singleShot(reset_time, lambda: qwidget.setStyleSheet(''))

    @Slot()
    def question_message(self, title, msg: str) -> bool:
        reply = QMessageBox.question(self, title, msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        return reply == QMessageBox.StandardButton.Yes

    @Slot()
    def is_windows(self) -> bool:
        return os.name == 'nt'

    @Slot()
    def check_win_dev_mode(self) -> bool:
        from winreg import OpenKey, HKEY_LOCAL_MACHINE, EnumValue

        with OpenKey(HKEY_LOCAL_MACHINE, "SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock") as key:
            return EnumValue(key, 0)[1]

    ### SETUP TAB
    @asyncSlot()
    async def check_docker_system_status(self):
        docker_status = AsyncDockerService.check_system_status()
        if docker_status:
            logging.info("Docker installation found.")
            self.ui.labelDockerStatusImage.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_SUCCESS, style=self.style()))
            self.ui.labelDockerStatusMessage.setText(self.tr("Docker installed and Daemon is running!"))

            # Populate service handlers and activate remaining app tabs

            self.docker_service.setup_service()
            ocrd_status = await self.check_docker_image_status(self.settings.docker_image_ocrd,
                                                               self.ui.labelDockerOCRDStatus)
            clas_status = await self.check_docker_image_status(self.settings.docker_image_classifier,
                                                               self.ui.labelDockerEBMStatus)
            setupTab: QWidget = self.ui.tabWidget.findChild(QWidget, 'setupTab')
            setupTab.findChild(QFrame, 'setup2').setEnabled(True)
            if ocrd_status and clas_status:
                logging.info("Application is ready")
                self.toggle_app_availability(True)
        else:
            logging.error("Docker not installed or WSL is not running.")
            self.ui.labelDockerStatusImage.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_FAIL, style=self.style()))
            self.ui.labelDockerStatusMessage.setText(
                self.tr("No docker installation found! Please make sure Docker is installed and running."))
            # Deactivate remaining app tabs
            self.toggle_app_availability(False)
            setupTab: QWidget = self.ui.tabWidget.findChild(QWidget, 'setupTab')
            setupTab.findChild(QFrame, 'setup2').setEnabled(False)

            # check periodically whether Docker is installed correctly.
            QTimer().singleShot(5000, self.check_docker_system_status)

    @asyncSlot(str, QLabel)
    async def check_docker_image_status(self, docker_image: str, status_label: QLabel) -> bool:
        try:
            await self.docker_service.docker_image.get_local(docker_image)
            logging.info(f"Found image '{docker_image}'!")
            status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_SUCCESS, self.style()))
            return True
        except DockerError as de:
            logging.error(f"DockerError: Docker image '{docker_image}' could not be found. \nReason: {de}")
            status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_FAIL, self.style()))
            return False

    @asyncSlot(str, QPushButton, QProgressBar, QLabel)
    async def pull_remote_docker_image(self, docker_image: str, btn: QPushButton, pbar: QProgressBar,
                                       status_label: QLabel):
        btn.setEnabled(False)
        pbar.setRange(0, 0)  # Show progress by oscillating the progress bar
        status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_PROCESSING, self.style()))
        try:
            await self.docker_service.docker_image.pull(docker_image)
            logging.info(f"Succesfully pulled image '{docker_image}'")

            ocrd_status = await self.check_docker_image_status(self.settings.docker_image_ocrd,
                                                               self.ui.labelDockerOCRDStatus)
            clas_status = await self.check_docker_image_status(self.settings.docker_image_classifier,
                                                               self.ui.labelDockerEBMStatus)
            if ocrd_status and clas_status:
                logging.info("Application is ready")
                self.toggle_app_availability(True)

        except DockerError as de:
            logging.warning(f"DockerError: Could not pull remote Docker image. \nReason: {de}")
        finally:
            btn.setEnabled(True)
            pbar.setRange(0, 100)

    ### DATA/IMPORT TAB
    @Slot()
    def on_openDataDirectory_triggered(self):
        directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        m_fileDialog = QFileDialog(self, "Choose a Workspace Directory", directory)
        m_fileDialog.setFileMode(QFileDialog.FileMode.Directory)
        m_fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        if m_fileDialog.exec() == QDialog.DialogCode.Accepted:
            to_open = m_fileDialog.selectedUrls()[0]
            if to_open.isValid():
                self.open_datadir(to_open)

    @Slot(QUrl)
    def open_datadir(self, dir_location):
        def critical(msg: str) -> None:
            logging.error(msg)
            QMessageBox.critical(self, "Failed to open", msg)

        if not dir_location.isLocalFile():
            critical(f"{dir_location} is not a valid local directory.")
            return

        locdir = dir_location.toLocalFile()
        # Check if folder already contains a mets file
        it = QDirIterator(locdir, ['mets.xml'], QDir.Filter.Files, QDirIterator.IteratorFlag.Subdirectories)
        if it.hasNext():
            critical(f"{locdir} is dirty and already contains a 'mets.xml' file.")
            return

        # Check if the folder contains any relevant image data
        mime_type_info = self.settings.mime_types
        it = QDirIterator(locdir,
                          [val[0] for val in mime_type_info.values()],
                          QDir.Filter.Files,
                          QDirIterator.IteratorFlag.Subdirectories)
        if not it.hasNext():
            critical(
                f"{locdir} does not contain any image data according to the following mimetypes:\n - " + "\n - ".join(
                    [val[1] for val in mime_type_info.values()]))
            return

        self.ui.lineEditDataSel.setText(locdir)

    @Slot(bool)
    def on_batchSize_toggled(self, active: bool):
        if active:
            if self.is_windows() and not pyuac.isUserAdmin() and not self.check_win_dev_mode():
                mb_title = "Elevated environment required"
                mb_msg = "<p>We rely on symlinks to create sub-workspaces. On windows, this needs elevated rights or the 'Windows Developer Mode' activated.</p>" \
                         "<p>Do you want to restart the application in an elevated environment?</p>"
                if self.question_message(mb_title, mb_msg):
                    QApplication.quit()
                    pyuac.runAsAdmin()
                else:
                    self.ui.radioButtonImportNone.toggle()
                    return
            self.ui.lineEditBatchSize.setEnabled(True)
        else:
            self.ui.lineEditBatchSize.setEnabled(False)
            self.ui.lineEditBatchSize.setText("")
            self.ui.lineEditBatchSize.setStyleSheet("")

    @asyncSlot()
    async def run_workspace_import(self) -> None:
        """ Execute workspace import using an OCRD Docker container.
        :return: None
        """

        def critical(msg: str) -> None:
            logging.error(msg)
            QMessageBox.critical(self, "Failed to import the directory content to a workspace", msg)

        # Workspace string is empty
        data_dir: str = self.ui.lineEditDataSel.text()
        if data_dir.strip() == "":
            critical("Empty data directory. Please select a valid workspace for processing.")
            return

        # Workspace already contains a mets.xml file
        it = QDirIterator(data_dir, ['mets.xml'], QDir.Filter.Files)
        if it.next():
            critical(f"{data_dir} is dirty and already contains a 'mets.xml' file.")
            return

        # Workspace is not a folder in the local file tree
        ddir_valid: QValidator.State = self.ui.lineEditDataSel.validator().validate(data_dir, -1)[0]
        if ddir_valid != QValidator.State.Acceptable:
            critical(f"{data_dir} is not a valid directory. Please review your entry.")
            return

        # Workspace does not contain any image data (can only happen if the user manually inserts the dir string)
        mime_type_info = self.settings.mime_types
        it = QDirIterator(data_dir,
                          [val[0] for val in mime_type_info.values()],
                          QDir.Filter.Files,
                          QDirIterator.IteratorFlag.Subdirectories)
        if not it.next():
            critical(
                f"Folder {data_dir} does not contain any image data according to the following mimetypes:\n - " + "\n - ".join(
                    [val[1] for val in mime_type_info.values()]))
            return

        # Get selected workflow parallelization options
        bs = None
        if self.ui.radioButtonImportBatchSize.isChecked():
            bs = self.ui.lineEditBatchSize.text()
            bs_valid: QValidator.State = self.ui.lineEditDataSel.validator().validate(bs, len(bs))[0]
            if not bs_valid:
                critical(
                    f"The selected batch size '{bs}' is not in the valid range of 1-100. Please set it accordingly.")
                return

        # Get selected data import options
        num_ids = self.ui.checkBoxNoNumIDs.isChecked()
        auto_convert = self.ui.checkBoxConvert.isChecked()
        dpi = self.ui.lineEditDPI.text()
        if dpi == "":
            dpi = self.ui.lineEditDPI.placeholderText()

        # Update UI
        btn = self.ui.pushButtonImport
        pbar = self.ui.progressBarImport
        status_label = self.ui.labelIconImport
        btn.setEnabled(False)
        pbar.setRange(0, 0)  # Show progress by oscillating the progress bar
        status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_PROCESSING, self.style()))

        # Split workspace if necessary
        if bs is not None:
            workspaces = await self.ocrd_service.split_workspaces_batch_size(data_dir, batch_size=int(bs))
        else:
            workspaces = [data_dir]

        try:
            ws_dir: str
            for ws_dir in workspaces:
                # Set mount information: data directory if data is symlinked in the workspace, else directly the workspace
                # directory.
                mount_point = data_dir
                model_dir = self.settings.model_dir

                # Docker configuration
                volumes = [f"{mount_point}:/data", f"{model_dir}:/usr/local/share/ocrd-resources"]
                working_dir = '/data' + (f'/{str(Path(ws_dir).name)}' if data_dir != ws_dir else '')
                env_variables = ['TESSDATA_PREFIX=/usr/local/share/ocrd-resources/ocrd-tesserocr-recognize']
                docker_cfg = self.ocrd_service.config_import_workspace(
                    auto_convert=auto_convert,
                    num_ids=num_ids,
                    dpi=dpi,
                    docker_image=self.settings.docker_image_ocrd,
                    volumes=volumes,
                    working_dir=working_dir,
                    environment_variables=env_variables)
                await self.docker_service.exec_command(docker_cfg,
                                                       logging_level=logging._checkLevel("DOCKER_IMPORT"))
            status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_SUCCESS, self.style()))
            msg = "Workspace creation finished."
            logging.info(msg)
            QMessageBox.information(self, "Workspace status", msg)

        except DockerError as de:
            msg = f"DockerError: Workflow execution was not successful. \nReason: {de}"
            logging.warning(msg)
            QMessageBox.critical(self, "Workspace status", msg)
            status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_FAIL, self.style()))
        finally:
            btn.setEnabled(True)
            pbar.setRange(0, 100)

    ### WORKSPACE TAB
    @Slot()
    def on_openWorkspaceDirectory_triggered(self):
        directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        m_fileDialog = QFileDialog(self, "Choose a Workspace Directory", directory)
        m_fileDialog.setFileMode(QFileDialog.FileMode.Directory)
        m_fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        if m_fileDialog.exec() == QDialog.DialogCode.Accepted:
            to_open = m_fileDialog.selectedUrls()[0]
            if to_open.isValid():
                self.open_workspace(to_open)

    @Slot(QUrl)
    def open_workspace(self, dir_location):
        def critical(msg: str) -> None:
            logging.error(msg)
            QMessageBox.critical(self, "Failed to open", msg)

        if not dir_location.isLocalFile():
            critical(f"{dir_location} is not a valid local file.")
            return

        locdir = dir_location.toLocalFile()
        single_it = QDirIterator(locdir, ['mets.xml'], QDir.Filter.Files)
        multi_it = QDirIterator(locdir, ['mets.xml'], QDir.Filter.Files,
                                QDirIterator.IteratorFlag.Subdirectories)
        if not (single_it.hasNext() or multi_it.hasNext()):
            critical(f"Workspace at {locdir} does not contain a 'mets.xml' file.")
            return
        if not single_it.hasNext() and multi_it.hasNext():
            msg = "Workspace contains multiple subspaces. It is advised to run them in parallel mode."
            logging.info(msg)
            QMessageBox.information(self, "Parallelization advised", msg)

        self.ui.lineEditWorkspaceSel.setText(locdir)

    @asyncSlot()
    async def on_workflow_execution_triggered(self) -> None:
        """ Dispatch workflow execution using an OCRD Docker container
        :return: None
        """

        # Workspace string is empty
        base_dir: str = self.ui.lineEditWorkspaceSel.text()
        wf = self.ui.comboBoxWorkflowSel.currentData()
        wf_name = self.ui.comboBoxWorkflowSel.currentText()
        padding = int(self.ui.lineEditPadding.text())
        num_workers = self.ui.spinBoxParallelization.value()

        def critical(msg: str) -> None:
            logging.error(msg)
            QMessageBox.critical(self, "Failed to run workflow", msg)

        if base_dir.strip() == "":
            critical("Empty workspace location. Please select a valid workspace for processing.")
            return

        # Workspace is not a folder in the local file tree
        ws_valid: QValidator.State = self.ui.lineEditWorkspaceSel.validator().validate(base_dir, -1)[0]
        if ws_valid != QValidator.State.Acceptable:
            critical(f"{base_dir} is not a valid directory. Please review your entry.")
            return

        # Workspace does not contain a mets file (can only happen if the user manually inserts the String)
        single_it = QDirIterator(base_dir, ['mets.xml'], QDir.Filter.Files)
        multi_it = QDirIterator(base_dir, ['mets.xml'], QDir.Filter.Files, QDirIterator.IteratorFlag.Subdirectories)
        if not (single_it.hasNext() or multi_it.hasNext()):
            critical(f"Workspace at {base_dir} does not contain a 'mets.xml' file.")
            return

        # Collect workspaces to execute
        workspaces = []
        if not single_it.hasNext() and multi_it.hasNext():
            while multi_it.hasNext():
                sdm = multi_it.next()
                mk_it = QDirIterator(sdm, ['*.mk'], QDir.Filter.Files)
                if mk_it.hasNext():
                    fn = mk_it.next()
                    if Path(fn).name != wf_name:
                        critical(f"The workspace at '{sdm}' already contains another workflow configuration. "
                                 f"Please clean up your workspace!")
                        return
                workspaces.append(Path(sdm).parent.as_posix())
        elif single_it.hasNext():
            mk_it = QDirIterator(base_dir, ['*.mk'], QDir.Filter.Files)
            if mk_it.hasNext():
                fn = mk_it.next()
                if Path(fn).name != wf_name:
                    critical(f"The workspace at '{base_dir}' already contains another workflow configuration. "
                             f"Please clean up your workspace!")
                    return
            workspaces.append(base_dir)

        # if len(workspaces) > 1 and num_workers == 1:
        #    msg = f"The workspace contains {len(workspaces)} sub-workspaces, but the number of workers is set to "
        #    QMessageBox.information(self, "Parallelization advised", msg)

        # Update UI
        btn = self.ui.pushButtonRunWorkflow
        pbar = self.ui.progressBarRunWorkflow
        status_label = self.ui.labelIconRunWorkflow
        btn.setEnabled(False)
        pbar.setRange(0, 0)  # Show progress by oscillating the progress bar
        status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_PROCESSING, self.style()))

        try:
            special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss',
                                ord('á'): 'a', ord('à'): 'a', ord('ú'): 'u', ord('ù'): 'u',
                                ord('é'): 'e', ord('è'): 'e', ord('í'): 'i', ord('ì'): 'i',
                                ord('ó'): 'o', ord('ò'): 'o'}
            # Define worker logic
            async def extraction_worker(name, queue, wf, wf_name, padding):
                while True:
                    workspace = await queue.get()
                    if "OCR-D_batch" in workspace:
                        dcont_name = f'ocrd_workflow_{Path(workspace).name[6:]}'
                    else:
                        dcont_name = f"ocrd_workflow_{Path(workspace).name}".strip().replace(' ', '')[:128]
                    dcont_name = dcont_name.translate(special_char_map)
                    await self.run_workflow(workspace, wf=wf, wf_name=wf_name, dcont_name=dcont_name, padding=padding)
                    queue.task_done()

            async def classification_worker(name, queue, wf, wf_name, padding):
                while True:
                    workspace = await queue.get()
                    if "OCR-D_batch" in workspace:
                        dcont_name = f'glyph_classifier_{Path(workspace).name[6:]}'
                    else:
                        dcont_name = f"glyph_classifier_{Path(workspace).name}".strip().replace(' ', '')[:128]
                    dcont_name = dcont_name.translate(special_char_map)
                    await self.run_classification(workspace, wf=wf, wf_name=wf_name, dcont_name=dcont_name,
                                                  padding=padding)
                    queue.task_done()

            # Populate queues
            extraction_queue = asyncio.Queue()
            classification_queue = asyncio.Queue()
            for ws in workspaces:
                extraction_queue.put_nowait(ws)
                classification_queue.put_nowait(ws)

            # Create workers to process the queue concurrently.
            extraction_tasks = []
            for i in range(num_workers):
                task = asyncio.create_task(
                    extraction_worker(f'worker-{i}', extraction_queue, wf, wf_name, padding))
                extraction_tasks.append(task)

            # Wait until the queue is fully processed.
            await extraction_queue.join()
            # Cancel our worker tasks.
            for task in extraction_tasks:
                task.cancel()
            # Wait until all worker tasks are cancelled.
            await asyncio.gather(*extraction_tasks, return_exceptions=True)

            # Create workers to process the queue concurrently.
            classification_tasks = []
            for i in range(min(num_workers, 2)):
                task = asyncio.create_task(
                    classification_worker(f'worker-{i}', classification_queue, wf, wf_name, padding))
                classification_tasks.append(task)

            # Wait until the queue is fully processed.
            await classification_queue.join()
            # Cancel our worker tasks.
            for task in classification_tasks:
                task.cancel()
            # Wait until all worker tasks are cancelled.
            await asyncio.gather(*classification_tasks, return_exceptions=True)

            msg = "Workspace extraction, classification, and pruning finished."
            logging.info(msg)
            QMessageBox.information(self, "Workspace status", msg)
            status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_SUCCESS, self.style()))

            # batch_counter = 0
            # for batch_ws in batch(workspaces, num_workers):
            #    extraction_tasks = [self.run_workflow(ws, wf, wf_name, dcont_name=f'ocrd_workflow_batch_{batch_counter + t_idx}') for t_idx, ws in enumerate(batch_ws)]
            #    classification_tasks = [self.run_classification(ws, dcont_name=f'glyph_classifier_batch_{batch_counter + t_idx}') for t_idx, ws in enumerate(batch_ws)]
            #    await asyncio.gather(*extraction_tasks)
            #    await asyncio.gather(*classification_tasks)
            #    batch_counter += len(batch_ws)

        except DockerError as de:
            msg = f"DockerError: Workflow execution was not successful. \nReason: {de}"
            logging.warning(msg)
            QMessageBox.warning(self, "Extraction failed", msg)
            status_label.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_FAIL, self.style()))
        finally:
            btn.setEnabled(True)
            pbar.setRange(0, 100)

    @asyncSlot()
    async def run_workflow(self, ws_dir: str, wf, wf_name: str, dcont_name: str = 'ocrd_workflow',
                           padding: int = 10) -> None:
        """ Execute workflow using an OCRD Docker container
        :return: None
        """
        # Copy workflow configuration to workspace
        # QFile.copy(wf, str(Path(ws_dir).joinpath(wf_name)))

        # Overwrite padding configuration in template workflow and save in workspace
        wf_source = QFile(wf)
        wf_source.open(QIODevice.OpenModeFlag.ReadOnly | QFile.Text)
        stream = QTextStream(wf_source)
        wf_config = stream.readAll()
        wf_source.close()
        query = re.search(r'padding\": (.*?),', wf_config)
        if query is not None:
            s, e = query.start(), query.end()
            old = wf_config[s - 1:e]
            new = f'"padding": {padding},'
            wf_config = wf_config.replace(old, new)

        wf_target = QFile(str(Path(ws_dir).joinpath(wf_name)))
        wf_target.open(QIODevice.OpenModeFlag.ReadWrite | QFile.Text)
        stream = QTextStream(wf_target)
        stream << wf_config
        wf_target.close()

        # Validate if we need to bind the data directory due to data symlinks
        # --> This is the case if we split up the data into multiple workspaces.
        data_dir = None
        it = QDirIterator(ws_dir, flags=QDirIterator.IteratorFlag.Subdirectories)
        while it.hasNext():
            fi = QFileInfo(it.next())
            if fi.isSymLink():
                symlink_tgt = fi.symLinkTarget()
                # QFileInfo(symlink_tgt).dir().absolutePath().parent())
                data_dir = Path(symlink_tgt).parent.as_posix()
                break

        # Set mount information: data directory if data is symlinked in the workspace, else directly the workspace
        # directory.
        mount_point = data_dir if data_dir is not None else ws_dir
        model_dir = self.settings.model_dir
        print(model_dir)

        # Docker configuration for OCRD Workflow
        volumes = [f"{mount_point}:/data", f"{model_dir}:/usr/local/share/ocrd-resources"]
        working_dir = '/data' + (f'/{str(Path(ws_dir).name)}' if data_dir is not None else '')
        env_variables = ['TESSDATA_PREFIX=/usr/local/share/ocrd-resources/ocrd-tesserocr-recognize']
        docker_cfg = self.ocrd_service.config_exec_workflow(workflow_config=wf_name,
                                                            docker_image=self.settings.docker_image_ocrd,
                                                            docker_container_name=dcont_name,
                                                            volumes=volumes,
                                                            working_dir=working_dir,
                                                            environment_variables=env_variables)
        await self.docker_service.exec_command(docker_cfg, logging_level=logging._checkLevel("DOCKER_WORKFLOW"))

    @asyncSlot()
    async def run_classification(self, ws_dir: str, wf, wf_name: str, dcont_name: str = 'glyph_classifier',
                                 padding: int = 10) -> None:
        # Dispatch classification service
        mount_point = ws_dir
        it = QDirIterator(ws_dir, ['*.pkl'], QDir.Filter.Files, QDirIterator.IteratorFlag.Subdirectories)
        if it.hasNext():
            # Docker configuration for Glyph Classifier Pruner
            volumes = [f"{mount_point}:/data"]
            working_dir = '/data'
            env_variables = []
            docker_cfg = self.classifier_service.config_exec_workflow(
                docker_image=self.settings.docker_image_classifier,
                docker_container_name=dcont_name,
                volumes=volumes,
                working_dir=working_dir,
                environment_variables=env_variables,
                request_gpu=True,
                padding=padding)
            await self.docker_service.exec_command(docker_cfg, logging_level=logging._checkLevel("DOCKER_WORKFLOW"))

    @Slot()
    def on_actionQuit_triggered(self):
        self.close()

    @Slot()
    def on_actionAbout_triggered(self):
        QMessageBox.about(self, "About PdfViewer",
                          "An example using QPdfDocument")

    @Slot()
    def on_actionAbout_Qt_triggered(self):
        QMessageBox.aboutQt(self)

    ### VIEW/EDIT TAB
    @Slot()
    def on_openWorkspaceViewEdit_triggered(self):
        directory = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        m_fileDialog = QFileDialog(self, "Choose a Workspace Directory", directory)
        m_fileDialog.setFileMode(QFileDialog.FileMode.Directory)
        m_fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        if m_fileDialog.exec() == QDialog.DialogCode.Accepted:
            to_open = m_fileDialog.selectedUrls()[0]
            if to_open.isValid():
                self.open_viewedit_workspace(to_open)

    @Slot(QUrl)
    def open_viewedit_workspace(self, dir_location):
        def critical(msg: str) -> None:
            logging.error(msg)
            QMessageBox.critical(self, "Failed to open", msg)

        if dir_location.isLocalFile():
            locdir = dir_location.toLocalFile()

            # Check if glyphs database exists
            it = QDirIterator(locdir, ['glyphs.db'], QDir.Filter.Files)
            if not it.hasNext():
                # must contain a mets xml file
                it = QDirIterator(locdir, ['mets.xml'], QDir.Filter.Files, QDirIterator.IteratorFlag.Subdirectories)
                if not it.hasNext():
                    critical(f"{locdir} does not contain a 'mets.xml' file.")
                    return

                it = QDirIterator(locdir, ['*.pkl'], QDir.Filter.Files, QDirIterator.IteratorFlag.Subdirectories)
                if not it.hasNext():
                    critical(f"{locdir} does not contain any pickled glyph images ('.pkl' files).")
                    return
            self.ui.lineEditViewEdit.setText(locdir)
        else:
            critical(f"{dir_location} is not a valid local file.")
            return

    @asyncSlot(str)
    async def run_load_reload_viewedit(self):
        # Check if there is already an active workspace which is dirty (has unsaved changes)
        if not self.check_dirty_workspace_state():
            return

        # Workspace string is empty
        ws_dir: str = self.ui.lineEditViewEdit.text()
        if ws_dir.strip() == "":
            msg = "Empty workspace location. Please select a valid workspace for processing."
            logging.error(msg)
            QMessageBox.critical(self, "Workspace error", msg)
            return

        # Workspace is not a folder in the local file tree
        ws_valid: QValidator.State = self.ui.lineEditViewEdit.validator().validate(ws_dir, -1)[0]
        if ws_valid != QValidator.State.Acceptable:
            msg = "f{ws_dir} is not a valid directory. Please review your entry."
            logging.error(msg)
            QMessageBox.critical(self, "Workspace error", msg)
            return

        db_name = self.settings.db_name
        db_it = QDirIterator(ws_dir, ['*.db'], QDir.Filter.Files)

        # Handle case where no database could be found.
        ve_widget: ViewEditWidget = self.ui.viewEditDynFrame
        if not db_it.hasNext():
            ve_widget.init_workspace(ws_dir, db_name)
        else:
            ve_widget.load_and_restore_workspace(ws_dir, db_name)

    @Slot()
    def on_workspace_about_to_load(self):
        self.ui.labelDBImport.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_PROCESSING, self.style()))
        self.ui.pushButtonViewEditImport.setEnabled(False)
        self.ui.viewEditDynFrame.setEnabled(False)

    @Slot(bool)
    def on_workspace_loaded(self, success: bool):
        if success:
            self.ui.labelDBImport.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_SUCCESS, self.style()))
        else:
            self.ui.viewEditDynFrame.setEnabled(False)
            self.ui.labelDBImport.setPixmap(AppIcons.get_pixmap(AppIcons.ICON_FAIL, self.style()))
        self.ui.pushButtonViewEditImport.setEnabled(True)
        self.ui.viewEditDynFrame.setEnabled(True)

    ### SETTINGS TAB
    @Slot(str)
    def on_set_autosave(self, enabled: bool):
        self.settings.autosave = bool(enabled)
        self.settings.save()

    @Slot(str)
    def on_set_similarity_sorting_algorithm(self, sort_alg: str):
        self.settings.similarity_sort = SortingAlgorithms(sort_alg).name.lower()
        self.settings.save()

    @Slot(str)
    def on_set_temp_store(self, temp_store: str):
        self.settings.temp_store = DBTempStorageModes(temp_store).name.lower()
        self.settings.save()

    @Slot(str)
    def on_toggle_apptheme(self, theme: str):
        self.settings.app_theme = AppThemes(theme).name.lower()
        self.settings.save()
        qss = """       
            QFrame {
                border: 0px;
            }    

            LabelTreeView {
                border: 1px solid grey;
            }  

            GlyphListView {
                border: 1px solid grey;
            }
        """
        qdarktheme.setup_theme(AppThemes(theme).name.lower(), corner_shape="sharp", additional_qss=qss)
