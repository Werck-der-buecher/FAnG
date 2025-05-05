import io
import logging
import re
from functools import partial
from typing import Optional, Union, List, Tuple, Literal, Any

import numpy as np
from PIL import Image
from PySide6.QtCore import (Qt, QModelIndex, QPersistentModelIndex, QObject, QItemSelectionModel,
                            QItemSelection, QByteArray, Signal, Slot, QSize, QRunnable, QThreadPool, QDir, QDirIterator,
                            QTimer)
from PySide6.QtSql import (QSqlDatabase)
from PySide6.QtWidgets import (QWidget, QAbstractItemView, QListView, QInputDialog, QLineEdit, QFrame,
                               QMessageBox, QProgressDialog)
from injector import Injector

from app_icons import AppIcons
from modules import WorkspaceModule
from services import GSQLService, GSQLSchema, Transaction, SimilarityCalculationService, Settings, \
    WorkspacePersistenceService, WorkspaceSaveStateNotFoundError
from widgets import IntValidator, PopUpProgressBar
from widgets.viewedit.constants import Constants
from widgets.viewedit.glyphs.glyphs_delegate import GlyphItemDelegate
from widgets.viewedit.glyphs.glyphs_model import GlyphsSQLModel, GlyphSortingStrategy, GlyphSortingDict
from widgets.viewedit.glyphs.glyphs_proxy import GlyphsProxyModel
from widgets.viewedit.glyphs.glyphs_roles import GlyphRole
from widgets.viewedit.labels.labels_delegate import LabelItemDelegate
from widgets.viewedit.labels.labels_model import LabelsSqlModel
from widgets.viewedit.labels.labels_roles import LabelRole
from widgets.viewedit.labels.labels_proxy import GroupProxyModel
from widgets.viewedit.runnables import WorkerSignals, SimilarityCalcRunnable, DBInitRunnable, DBCommitRunnable, \
    AutoSaveRunner, UpdateLabelRunnable, UpdateStatusRunnable, CreateEncodingRunnable
from widgets.viewedit.ui_vieweditwidget import Ui_EditWidget
from widgets.viewedit.glyph_locator.glyphlocatorwidget import GlyphLocatorWidget


def setup_base_injector(parent: QObject):
    """ Closure to configure base injector with parent reference."""

    def setup_binder(binder):
        binder.bind(QObject, to=parent)

    return Injector([setup_binder, WorkspaceModule])


def setup_delegate_injector(injector: Injector, selection_model: QItemSelectionModel):
    """ Closure to configure child injector with parent and custom selection model."""

    def setup_binder(binder):
        binder.bind(QItemSelectionModel, to=selection_model)

    return injector.create_child_injector(setup_binder)


class ViewEditWidget(QWidget):
    about_to_initialize = Signal()
    initialized = Signal(bool)
    about_to_load = Signal()
    loaded = Signal(bool)

    # signal for communication between main view/edit widget and the glyph locator/tracker
    # param1: str: image directory
    # param2: str: image filename
    # param3: str: image extension
    # param4: str: glyph uid
    # param5: str: glyph label
    # param6: list: xy bounding box coordinates
    glyph_selected = Signal(str, str, str, str, str, list)

    def __init__(self,
                 parent: Optional[QWidget] = None
                 ) -> None:
        super().__init__(parent)

        self.ui = Ui_EditWidget()
        self.ui.setupUi(self)

        # Service injection
        self.injector = setup_base_injector(self)
        self.settings = self.injector.get(Settings)
        self.gsql_service = self.injector.get(GSQLService)
        self.persistence = self.injector.get(WorkspacePersistenceService)

        # Splitter and toolbar
        self.ui.workSplitter.setStretchFactor(0, 3)
        self.ui.workSplitter.setStretchFactor(1, 2)
        self.ui.treeViewLabelsToolbar.hide()

        # Style "Commit Changes" Button
        self.cclabel = self.ui.labelCommitChanges
        self.cclabel.setText("")
        self.ccbutton = self.ui.pushButtonCommitChanges
        self.ccbutton.setEnabled(False)
        self.ccbutton.pressed.connect(self.on_commit_changes_pressed)

        # Populate sorting options
        for e in GlyphSortingStrategy:
            self.ui.comboBoxSortingStrategy.addItem(e.value)
        self.ui.comboBoxSortingStrategy.setCurrentIndex(0)
        self.ui.checkBoxSortingStrategy.setChecked(True)
        self.ui.comboBoxSortingStrategy.currentTextChanged.connect(self.on_set_sorting_strategy)
        self.ui.checkBoxSortingStrategy.stateChanged.connect(self.on_set_sorting_order)

        # Scaling functionality
        scale_selector = self.ui.comboBoxZoom
        self.ui.pushButtonZoomIn.setIcon(AppIcons.get_icon(AppIcons.ICON_ZOOMIN, self.style()))
        self.ui.pushButtonZoomIn.pressed.connect(scale_selector.increment)
        self.ui.pushButtonZoomOut.setIcon(AppIcons.get_icon(AppIcons.ICON_ZOOMOUT, self.style()))
        self.ui.pushButtonZoomOut.pressed.connect(scale_selector.decrement)
        scale_selector.reset()
        scale_selector.zoom_factor_changed.connect(self.on_scale_factor_changed)

        # Cropping functionality
        crop_selector = self.ui.lineEditImageCrop
        crop_selector.setPlaceholderText('0')
        crop_validator = IntValidator(0, 20)
        crop_selector.setValidator(crop_validator)
        crop_selector.textChanged.connect(self.on_crop_value_changed)

        # Size Filter Functionality
        size_validator = IntValidator()
        filter_height_min = self.ui.lineEditMinHeight
        filter_height_max = self.ui.lineEditMaxHeight
        filter_width_min = self.ui.lineEditMinWidth
        filter_width_max = self.ui.lineEditMaxWidth
        filter_height_min.setPlaceholderText('0')
        filter_height_min.setValidator(size_validator)
        filter_width_min.setPlaceholderText('0')
        filter_width_min.setValidator(size_validator)
        filter_height_max.setPlaceholderText('max')
        filter_height_max.setValidator(size_validator)
        filter_width_max.setPlaceholderText('max')
        filter_width_max.setValidator(size_validator)

        # General background worker (can/should be used for all sorts of (background) tasks)
        self.threadpool = QThreadPool()

        # Progress (general and dynamic)
        self.wpbar = PopUpProgressBar("Background task")
        self.wpbar.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.wpbar.hide()
        self.timed_progress = None

        # Autosave thread/worker
        self.workspace = None
        self.db_name = None
        self.autosave_timer = None

        # Label view & model
        self.label_selection_model = QItemSelectionModel()
        self.injector_label = setup_delegate_injector(self.injector, selection_model=self.label_selection_model)
        self.label_model = None
        self.label_proxy_model = None
        self.label_item_delegate = self.injector_label.create_object(LabelItemDelegate)
        self.label_view = self.ui.treeViewLabels
        self.label_view.setItemDelegate(self.label_item_delegate)
        self.configure_labelview(self.label_view)

        # Glyph view & model
        self.glyph_selection_model = QItemSelectionModel()
        self.injector_glyph = setup_delegate_injector(self.injector, selection_model=self.glyph_selection_model)
        self.glyph_model = None
        self.glyph_proxy_model = None
        self.glyph_item_delegate = self.injector_glyph.create_object(GlyphItemDelegate)
        self.glyph_view = self.ui.listViewGlyphs
        self.glyph_view.setItemDelegate(self.glyph_item_delegate)
        self.configure_glyphview(self.glyph_view)

        # Glyph locate widget
        self.image_directory = None
        self.glyph_locator = GlyphLocatorWidget()
        self.glyph_locator.hide()

        # State
        self.awaiting_data = True
        self.is_autosaving = False
        self.is_calc_similarity = False

    def configure_labelview(self, labelview):
        labelview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        labelview.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        labelview.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        labelview.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        labelview.setAnimated(False)
        labelview.setAllColumnsShowFocus(True)
        labelview.header().setStretchLastSection(True)
        labelview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        labelview.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        labelview.setDropIndicatorShown(True)
        labelview.setAcceptDrops(True)
        labelview.setStyleSheet("QFrame {border:1px solid gray;}")
        labelview.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        labelview.setLineWidth(1)
        return labelview

    def configure_glyphview(self, glyphview):
        glyphview.setViewMode(QListView.ViewMode.IconMode)
        glyphview.setSpacing(10)
        glyphview.setMovement(QListView.Movement.Static)
        glyphview.setResizeMode(QListView.ResizeMode.Adjust)
        glyphview.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        glyphview.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        glyphview.setAutoScroll(True)
        glyphview.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        glyphview.setDragEnabled(True)
        glyphview.setAcceptDrops(False)
        glyphview.setGridSize(QSize())
        glyphview.setFrameShadow(QFrame.Shadow.Plain)
        glyphview.setStyleSheet("QFrame {border:1px solid gray;}")
        return glyphview

    def setup_and_connect(self):
        # Reset tools
        self.ui.comboBoxZoom.reset()
        self.ui.lineEditImageCrop.setText('')
        self.ui.comboBoxSortingStrategy.setCurrentIndex(0)

        # Label model and view
        self.label_model = self.injector_label.create_object(LabelsSqlModel)
        self.label_proxy_model = self.injector_label.create_object(GroupProxyModel)
        self.label_proxy_model.setSourceModel(self.label_model)
        self.label_selection_model.setModel(self.label_proxy_model)
        self.label_view.setModel(self.label_proxy_model)
        self.label_view.setSelectionModel(self.label_selection_model)

        # Glyph model and view
        self.glyph_model = self.injector_glyph.create_object(GlyphsSQLModel)
        self.glyph_proxy_model = GlyphsProxyModel(self)
        self.glyph_proxy_model.setSourceModel(self.glyph_model)
        self.glyph_selection_model.setModel(self.glyph_proxy_model)
        self.glyph_view.setModel(self.glyph_proxy_model)
        self.glyph_view.setSelectionModel(self.glyph_selection_model)

        # Signals and Slots
        self.glyph_model.modelReset.connect(self.on_update_glyph_view_info)
        self.glyph_model.rowsInserted.connect(self.on_update_glyph_view_info)
        self.glyph_model.rowsRemoved.connect(self.on_update_glyph_view_info)
        self.glyph_model.layoutChanged.connect(self.on_update_glyph_view_info)
        self.glyph_model.dataChanged.connect(self.on_update_glyph_view_info)
        self.glyph_model.aboutToProcess.connect(self.on_glyph_model_processing)
        self.glyph_model.processed.connect(self.on_glyph_model_processed)

        self.glyph_view.flag_marked_delete.connect(self.glyph_model.on_flag_marked_delete)
        self.glyph_view.flag_marked_reassign.connect(self.glyph_model.on_flag_marked_reassign)
        self.glyph_view.flag_selection_delete.connect(self.glyph_model.on_flag_selection_delete)
        self.glyph_view.flag_selection_reassign.connect(self.glyph_model.on_flag_selection_reassign)
        self.glyph_view.flag_selection_clear.connect(self.glyph_model.on_flag_selection_clear)
        self.glyph_view.flag_selection_bookmark.connect(self.glyph_model.on_flag_selection_bookmark)
        self.glyph_view.request_jump_bookmark.connect(self.on_request_bookmark_jump, Qt.ConnectionType.DirectConnection)
        self.glyph_view.request_shape_info.connect(self.on_toggle_show_shape_statistics)
        self.glyph_view.request_toggle_glyph_details.connect(self.glyph_item_delegate.toggle_show_details)
        self.glyph_view.request_similarity_calc.connect(partial(self.dispatch_similarity_calculation, None, True))
        self.glyph_view.request_locate_glyph.connect(self.on_request_locate_glyph, Qt.ConnectionType.DirectConnection)

        self.glyph_view.selectionModel().selectionChanged.disconnect()
        self.glyph_view.selectionModel().selectionChanged.connect(self.on_glyph_selection_changed)
        self.glyph_selected.connect(self.glyph_locator.on_request_update)

        self.label_model.labels_changed.connect(self.glyph_view.on_visible_labels_changed)
        self.label_model.labels_changed.connect(self.label_view.on_visible_labels_changed)
        self.label_view.selectionModel().selectionChanged.disconnect()
        self.label_view.selectionModel().selectionChanged.connect(self.on_label_selection_changed)
        self.label_view.request_remove_labels.connect(self.label_model.on_request_remove_label)
        self.label_view.request_reassign_label.connect(self.label_model.on_request_reassign_label)
        self.label_view.request_remove_encoding.connect(self.label_model.on_request_remove_encoding)
        self.label_view.request_revert.connect(self.label_model.on_request_revert)
        self.label_view.request_new_encoding.connect(self.on_new_encoding)

        self.persistence.cache.pending_edits_changed.connect(self.on_pending_edits_changed)

        self.ui.lineEditMinHeight.textChanged.connect(self.glyph_proxy_model.set_filter_height_min)
        self.ui.lineEditMaxHeight.textChanged.connect(self.glyph_proxy_model.set_filter_height_max)
        self.ui.lineEditMinWidth.textChanged.connect(self.glyph_proxy_model.set_filter_width_min)
        self.ui.lineEditMaxWidth.textChanged.connect(self.glyph_proxy_model.set_filter_width_max)

    def init_workspace(self, workspace: str, db_name: str):
        logging.info("Trying to initialize DB")

        # Search directory for pickled glyph files
        it = QDirIterator(workspace, ['*.pkl'], QDir.Filter.Files, QDirIterator.IteratorFlag.Subdirectories)
        if not it.hasNext():
            # Handle case where no pickled glyphs could be found
            msg = f"Your specified workspace at '{workspace}' does not contain " \
                  f"any pickled glyph images ('.pkl' files)."
            logging.error(msg)
            QMessageBox.critical(self, "Workspace error", msg)
            return

        msg = "<p>No glyph database found. The app will now create a new database with all glyphs.<\p>" \
              "<p>This process may take several minutes.</p>"
        logging.info(msg)
        QMessageBox.information(self, "Workspace initialization", msg)

        ocr_encodings = False
        pkl_it = QDirIterator(workspace, ['*_pruned.pkl'], QDir.Filter.Files,
                              QDirIterator.IteratorFlag.Subdirectories)
        if not pkl_it.hasNext():
            title = "Pruning results not found"
            msg = ("<p>The extracted glyphs in the workspace were not pruned and classified. "
                   "Continue with raw OCR build?</p>")
            reply = QMessageBox.question(self, title, msg,
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                ocr_encodings = True
                pkl_it = QDirIterator(workspace, ['*.pkl'], QDir.Filter.Files,
                                      QDirIterator.IteratorFlag.Subdirectories)
            else:
                self.on_init_failure()

        pkl_list = []
        while pkl_it.hasNext():
            pkl_list.append(pkl_it.next())

        worker = self.injector.create_object(DBInitRunnable,
                                             additional_kwargs={'workspace': workspace, 'db_name': db_name,
                                                                'pkl_list': pkl_list, 'ocr_encodings': ocr_encodings,
                                                                'calc_similarities': False})
        self.wpbar.setWindowTitle("Database import...")
        self.wpbar.setRange(min=0, max=len(pkl_list) + 2)
        self.wpbar.show()

        # Signals/Slots
        worker.signals.succeeded.connect(partial(self.on_init_success, workspace=workspace, db_name=db_name))
        worker.signals.failed.connect(self.on_init_failure)
        worker.signals.finished.connect(self.wpbar.on_removed)
        worker.signals.finished.connect(self.wpbar.reset)
        worker.signals.progress.connect(self.wpbar.on_count_changed)
        worker.signals.status.connect(self.wpbar.on_status_changed)

        self.about_to_initialize.emit()
        self.threadpool.start(worker)

    @Slot(str, str)
    def on_init_success(self, workspace: str, db_name: str):
        logging.info("DB initialization finished")
        self.initialized.emit(True)
        msg = "Database creation was successful!"
        QMessageBox.information(self, "Workspace", msg)
        self.load_and_restore_workspace(workspace, db_name)

    @Slot()
    def on_init_failure(self):
        logging.info("DB initialization failed")
        self.initialized.emit(False)
        msg = "Database creation failed!"
        QMessageBox.critical(self, "Workspace", msg)

    def load_and_restore_workspace(self, workspace, db_name):
        """
        :param workspace: The path to the workspace directory.
        :param db_name: The name of the database.
        :return: None

        Loads the workspace and database specified by the given workspace path and database name.
        This method restores the state of the workspace, including the sorting strategy, sorting order, current label,
        current similarity, current UID, and current loaded glyphs. If a save state is found, the method restores the
        state and updates the label and glyph models accordingly. If no save state is found, the method saves the
        current state of the workspace and updates the glyph model.

        The method also initializes the default database connection and fetches the data from the database.

        Note: This method runs asynchronously and updates the progress bar while loading the workspace.

        Usage:
            load_workspace("path/to/workspace", "database_name")
        """
        self.about_to_load.emit()
        self.awaiting_data = True

        # 1) Setup models, proxies and views. Also do signal/slot coupling
        self.setup_and_connect()

        # 2) Establish default database connection
        self.gsql_service.init_db(workspace, db_name, connection_name="default", keep_open=False)

        # 3) Fetch data
        self.workspace = workspace
        self.db_name = db_name

        # restore savestate
        try:
            self.persistence.about_to_load.emit()
            self.persistence.load_from_disk(workspace)
        except WorkspaceSaveStateNotFoundError as e:
            self.persistence.save_to_disk(workspace)
        finally:
            self.persistence.loaded.emit()

        self.update_label_model()
        self.ui.comboBoxSortingStrategy.setCurrentText(self.persistence.sorting_strategy)
        self.ui.checkBoxSortingStrategy.setChecked(bool(self.persistence.sorting_order))

        current_label = self.persistence.current_label
        current_similarity = self.persistence.current_similarity
        self.label_view.selectionModel().clearSelection()
        sel_flags = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows

        sel_idx = self.label_proxy_model.index(0, 0)
        # Check if UID is set and used for selection and scoll-to.
        if current_label is not None:
            match_idx: QModelIndex = self.label_proxy_model.find_index(current_label, current_similarity)
            if match_idx.isValid():
                sel_idx = match_idx
            if sel_idx.parent().isValid():
                self.label_view.expand(sel_idx.parent())

        self.label_view.selectionModel().select(sel_idx, sel_flags)
        self.label_view.scrollTo(sel_idx, QAbstractItemView.ScrollHint.EnsureVisible)

        self.awaiting_data = False
        self.loaded.emit(True)

        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.dispatch_autosave)
        self.autosave_timer.start(10000)

    @Slot(str, str)
    def on_load_success(self):
        logging.info("Workspace loading finished")
        self.setEnabled(True)
        self.loaded.emit(True)
        msg = "Workspace loading was successful!"
        QMessageBox.information(self, "Workspace", msg)

    @Slot()
    def on_load_failure(self):
        logging.info("Workspace loading failed")
        self.loaded.emit(False)
        msg = "Workspace creation failed!"
        QMessageBox.critical(self, "Workspace", msg)

    def scan_vp_for_bookmark(self, role: GlyphRole = GlyphRole.cached, return_noflag: bool = False) -> Optional[List]:
        """
        Scan the viewport for the bookmark with the given role.

        :param role: The role of the bookmark. Default is 'GlyphRole.cached'.
        :return: Returns a tuple of the bookmark's name and value if found, else returns None.
        """
        vp_first_index = self.glyph_view.top_row_index()

        if vp_first_index is None:
            return None

        # Search in viewport and additional row
        vp_num_items = self.glyph_view.user_visible_columns * (self.glyph_view.user_visible_rows + 2)
        row = vp_first_index.row()
        vp_indexes = [vp_first_index.sibling(row + i, 0) for i in range(vp_num_items)]
        vp_indexes = [idx for idx in vp_indexes if idx.isValid()]

        # Get the index with the 'latest' active flags
        f_data = [idx.data(role) for idx in vp_indexes]
        f_idx_cand = [i for i, x in enumerate(f_data) if x]
        if not len(f_idx_cand):
            return [vp_first_index.data(GlyphRole.uid), vp_first_index.row()]

        f_idx_last = f_idx_cand[-1]
        f_idx: QModelIndex = vp_indexes[f_idx_last]

        if return_noflag:
            # check if the index is the last displayed item
            mplier = -1 if f_idx.row() == self.glyph_model.rowCount() -1 else 1
            for i in range(0, (vp_num_items + 1) * mplier, mplier):
                f_idx_next = f_idx.sibling(f_idx.row() + i, 0)
                if not f_idx_next.data(role):
                    uf_idx = f_idx_next
                    break

            if uf_idx is None:
                return [vp_first_index.data(GlyphRole.uid), vp_first_index.row()]

            return [uf_idx.data(GlyphRole.uid), uf_idx.row()]

        return [f_idx.data(GlyphRole.uid), f_idx.row()]

    def scroll_to_bookmark(self, uf_uid: Tuple[str, str], search_rstart: int = 0, highlight=False) -> bool:
        uf_uid_str = f"{uf_uid[0]}_{uf_uid[1]}"
        search_results: List[QModelIndex] = self.glyph_model.match(self.glyph_model.index(search_rstart, 0),
                                                                   GlyphRole.uid_str, uf_uid_str, 1,
                                                                   Qt.MatchFlag.MatchFixedString)
        if not len(search_results):
            return False
        uf_idx = search_results[0]
        proxy_model = self.glyph_proxy_model
        proxy_idx = proxy_model.mapFromSource(uf_idx)
        if proxy_idx.isValid():
            self.glyph_view.scrollTo(proxy_idx, QAbstractItemView.ScrollHint.EnsureVisible)
        else:
            return False
        if highlight:
            self.glyph_model.start_highlight_glyphs({uf_uid}, {uf_idx.row()})
        return True

    def set_bookmarks(self, label: str, similarity: Union[str, None]) -> None:
        last_noflag = self.scan_vp_for_bookmark(GlyphRole.cached, return_noflag=True)
        last_delete = self.scan_vp_for_bookmark(GlyphRole.delete)
        last_reassign = self.scan_vp_for_bookmark(GlyphRole.reassign)
        selection = self.glyph_selection_model.selectedIndexes()
        last_select = [selection[-1].data(GlyphRole.uid), selection[-1].row()] if len(selection) else None

        if last_noflag is not None:
            self.persistence.bookmarks.add_noflag(label, similarity, *last_noflag)
        if last_delete is not None:
            self.persistence.bookmarks.add_delete(label, similarity, *last_delete)
        if last_reassign is not None:
            self.persistence.bookmarks.add_reassign(label, similarity, *last_reassign)
        if last_select is not None:
            self.persistence.bookmarks.add_select(label, similarity, *last_select)

    @Slot(str)
    def on_request_bookmark_jump(self, cmd: Literal["select", "delete", "reassign", "custom"]) -> None:
        current_label = self.persistence.current_label
        current_similarity = self.persistence.current_similarity
        if cmd == "select":
            bookmark = self.persistence.bookmarks.select.get((current_label, current_similarity))
        elif cmd == "delete":
            bookmark = self.persistence.bookmarks.delete.get((current_label, current_similarity))
        elif cmd == "reassign":
            bookmark = self.persistence.bookmarks.reassign.get((current_label, current_similarity))
        elif cmd == "custom":
            bookmark = self.persistence.bookmarks.custom.get((current_label, current_similarity))
        else:
            raise ValueError(f"Specified bookmark of type '{cmd}' is not valid.")

        if bookmark is not None:
            uid, row = bookmark
            # self.glyph_model.fetch_until(row)
            self.glyph_model.prefetch(row)
            if self.scroll_to_bookmark(uid, highlight=True):
                return
        QMessageBox.information(self, "Bookmark", "Requested bookmark does not exist or was deleted!")

    def update_label_model(self):
        """
        Update label model by querying the database. This emits a modelReset signal.
        """
        self.label_model.refresh()

    def update_glyph_model(self):
        """
        Refresh model
        """
        self.glyph_model.refresh()

    @Slot()
    def on_glyph_model_processing(self) -> None:
        # disable user selection
        self.label_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.glyph_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        # set progressbar timer
        self.timed_progress = QProgressDialog("Operation in progress...", None, 0, 0, self)
        self.timed_progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.timed_progress.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)
        self.timed_progress.setWindowTitle("FAnG")
        self.timed_progress.setValue(0)
        self.timed_progress.setMinimumDuration(200)

        if not self.awaiting_data:
            # update the bookmarks
            self.set_bookmarks(self.persistence.current_label, self.persistence.current_similarity)

    @Slot(bool)
    def on_glyph_model_processed(self, value: bool) -> None:
        self.timed_progress.cancel()
        self.timed_progress.reset()

        # restore user selection
        self.label_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.glyph_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # try to recover
        if value:
            bookmark = self.persistence.bookmarks.noflag.get((self.persistence.current_label,
                                                              self.persistence.current_similarity))
            if bookmark is not None:
                uid, row = bookmark
                # self.glyph_model.fetch_until(row)
                self.glyph_model.prefetch(row)
                self.scroll_to_bookmark(uid, highlight=True)

    @Slot(QItemSelection, QItemSelection)
    def on_label_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        """
        :param selected: a QItemSelection object representing the selected items in the label view
        :param deselected: a QItemSelection object representing the deselected items in the label view
        :return: None

        This slot function is called when the selection in the label view changes.
        It updates the information in the persistence service with the new label and similarity group, and then updates
        the glyph model to show the glyphs associated with the new label and similarity group.
        If the selected sorting strategy is "Similarity", it dispatches a similarity calculation for the new label.
        """
        current_selection: List[QModelIndex] = selected.indexes()
        current_deselection: List[QModelIndex] = deselected.indexes()
        if len(current_selection):
            new_lbl = current_selection[0].data(LabelRole.label_persistent)  # group element
            sim_group = current_selection[0].data(LabelRole.similarity_persistent)  # first element in subgroup
            if isinstance(sim_group, str):
                sim_group = None

            # update glyph model by setting a new query based on the selected label
            order_by = GlyphSortingDict.get((self.glyph_model.sorting_strategy, self.glyph_model.sorting_order),
                                            GSQLSchema._ORDER_BY_UID_ASC)
            self.glyph_model.update_query(new_lbl, order_by=order_by, similarity_group=sim_group)

            # update information in persistence service
            self.persistence.set_current_label(new_lbl)
            self.persistence.set_current_similarity(sim_group)

        if not self.awaiting_data:
            self.dispatch_autosave()

    @Slot()
    def on_toggle_show_shape_statistics(self) -> None:
        conn_name = "statistics"
        db_handle = self.gsql_service.get_or_create_connection(conn_name)
        current_label = self.persistence.current_label
        mean_shape = self.gsql_service.get_shape_for_label(db_handle, current_label, agg='mean')
        median_shape = self.gsql_service.get_shape_for_label(db_handle, current_label, agg='median')
        db_handle.close()
        QSqlDatabase.removeDatabase(conn_name)
        msg = f"Shape information for currently selected label <b>{current_label}</b>: " \
              f"<br>" \
              f'<table align="left">' \
              f"<tr><th align='left' width='60'>Statistic</th><th align='left' width='100'>[Height/Width]</th><th align='left' width='40'>Unit</th></tr>" \
              f"<tr><td>Mean</td><td>{mean_shape}</td><td>px</td></tr>" \
              f"<tr><td>Median</td><td>{median_shape}</td><td>px</td></tr>" \
              f"</table>"
        QMessageBox.information(self, "Shape information", msg)

    @Slot()
    def on_request_locate_glyph(self) -> None:
        if not self.glyph_selection_model.hasSelection():
            return

        self.glyph_locator.raise_()
        self.glyph_locator.activateWindow()
        self.glyph_locator.showNormal()

        selected: QItemSelection = self.glyph_selection_model.selection()
        self.on_glyph_selection_changed(selected, QItemSelection())

    @Slot(QItemSelection, QItemSelection)
    def on_glyph_selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        current_selection: List[QModelIndex] = selected.indexes()
        if len(current_selection):
            img_dir = self.workspace
            img_filename = current_selection[0].data(GlyphRole.filename)
            img_extension = current_selection[0].data(GlyphRole.extension)
            img_label = self.persistence.current_label
            glyph_uid = current_selection[0].data(GlyphRole.uid_str)
            glyph_bbox = current_selection[0].data(GlyphRole.position_abs)
            self.glyph_selected.emit(img_dir, img_filename, img_extension, img_label, glyph_uid, glyph_bbox)

    @Slot()
    def on_remove_label(self, index: Union[QModelIndex, QPersistentModelIndex]):
        enc = index.data(LabelRole.label)
        similarity_group = index.data(LabelRole.similarity)
        self.label_model.update_labels(old_encoding=enc, new_encoding=Constants.CATEGORY_DELETED,
                                       similarity_group=similarity_group, wpbar=self.wpbar)

    @Slot()
    def on_rebase_label(self, index: Union[QModelIndex, QPersistentModelIndex], value: str):
        enc = index.data(LabelRole.label)
        similarity_group = index.data(LabelRole.similarity)
        self.label_model.update_labels(old_encoding=enc, new_encoding=value, similarity_group=similarity_group,
                                       wpbar=self.wpbar)

    @Slot()
    def on_edit_label(self, index: Union[QModelIndex, QPersistentModelIndex]):
        self.ui.treeViewLabels.edit(index)

    @Slot()
    def on_new_encoding(self):
        enc, ok = QInputDialog.getText(self.ui.treeViewLabels, "Add new label",
                                       "Label name:", QLineEdit.EchoMode.Normal)
        if ok and enc != '':
            @Slot(QModelIndex)
            def on_createencoding_success():
                logging.info("Label creation was successful")
                self.update_label_model()
                self.update_glyph_model()

            @Slot()
            def on_createencoding_failure():
                logging.info("Label creation failed")
                msg = "Label creation failed!"
                QMessageBox.information(self, "Label creation", msg)

            worker = self.injector.create_object(CreateEncodingRunnable, {'encoding': enc})
            worker.signals.succeeded.connect(on_createencoding_success)
            worker.signals.failed.connect(on_createencoding_failure)
            self.threadpool.start(worker)

    @Slot()
    def on_remove_encoding(self, index: Union[QModelIndex, QPersistentModelIndex]):
        enc: str = index.data(LabelRole.label)
        self.label_model.delete_encodings(enc, wpbar=self.wpbar)

    @Slot()
    def on_import_encoding_from_text(self):
        text: str
        ok: bool
        text, ok = QInputDialog.getMultiLineText(self.ui.treeViewLabels,
                                                 "Import encoding schema as individual comma-separated characters",
                                                 "Label names:", "")
        if ok and text != '':
            encodings = re.split('; |;|, |,|\s|\*|\n', text.rstrip())
            for enc in encodings:
                if enc:
                    self.label_model.create_encoding(enc)

    @Slot()
    def on_sync_reload(self):
        # Close all connections to allow the WAL to be synced with the DB, afterwards
        # reconnect glyph and labels connection needed in the models and views
        for conn in ['glyphs', 'labels']:
            self.gsql_service.close_connection(conn)
        for conn in ['glyphs', 'labels']:
            self.gsql_service.get_or_create_connection(conn, open=True)

    @Slot(float)
    def on_scale_factor_changed(self, scale_factor: float):
        if self.glyph_model is not None:
            self.glyph_model.scale_factor = scale_factor
            self.update_glyph_model()

    @Slot(int)
    def on_crop_value_changed(self, crop_value: int):
        if self.glyph_model is not None:
            self.glyph_model.img_crop = int(crop_value) if crop_value != '' else 0
            self.update_glyph_model()

    @Slot()
    def on_update_glyph_view_info(self):
        if self.glyph_model is not None:
            curr_count = self.glyph_proxy_model.rowCount()
            max_count = self.glyph_model.current_label_count
            count_hint = f"{curr_count}/{max_count}"
        else:
            count_hint = "0/0"
        self.ui.listViewGlyphsInfo.setText(count_hint)

    @Slot(int)
    def on_pending_edits_changed(self, edit_count: int):
        if self.glyph_model is not None:
            self.ccbutton.setEnabled(edit_count)
            self.cclabel.setText(f"{edit_count} pending changes" if edit_count else "")

    @Slot(str, int, int, QModelIndex)
    def on_status_update(self, encoding: str, old_status: int, new_status: int):
        @Slot(QModelIndex)
        def on_statusupdate_success():
            logging.info("Status update successful")
        @Slot()
        def on_statusupdate_failure():
            logging.info("Status update failed")

        worker = self.injector.create_object(UpdateStatusRunnable,
                                             additional_kwargs={'encoding': encoding,
                                                                'old_status': old_status,
                                                                'new_status': new_status})
        # set progressbar timer
        self.timed_progress = QProgressDialog("Operation in progress...", None, 0, 0, self)
        self.timed_progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.timed_progress.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)
        self.timed_progress.setWindowTitle("FAnG")
        self.timed_progress.setValue(0)
        self.timed_progress.setMinimumDuration(200)

        # Signals/Slots
        worker.signals.succeeded.connect(on_statusupdate_success)
        worker.signals.failed.connect(on_statusupdate_failure)
        worker.signals.finished.connect(self.timed_progress.close)
        worker.signals.finished.connect(self.timed_progress.reset)

        self.threadpool.start(worker)

    def update_labels(self, old_encoding, new_encoding, similarity_group: Optional[int] = None):
        @Slot(QModelIndex)
        def on_lblupdate_success():
            logging.info("Label update successful")

        @Slot()
        def on_lblupdate_failure(self):
            logging.info("Label update failed")

        worker = self.injector.create_object(UpdateLabelRunnable,
                                             additional_kwargs={'old_encoding': old_encoding,
                                                                'new_encoding': new_encoding,
                                                                'similarity_group': similarity_group})

        worker.signals.succeeded.connect(on_lblupdate_success)
        worker.signals.failed.connect(on_lblupdate_failure)

        self.wpbar.setWindowTitle("Update Labels Progress")
        self.wpbar.setRange(min=0, max=0)  # oscillating progress bar
        self.wpbar.setStatus(f"Moving glyphs from '<b>{old_encoding}</b>' "
                        f"to '<b>{new_encoding}</b>'...")
        self.wpbar.show()

        worker.signals.finished.connect(self.wpbar.on_removed)
        worker.signals.finished.connect(self.wpbar.reset)
        worker.signals.progress.connect(self.wpbar.on_count_changed)
        worker.signals.status.connect(self.wpbar.on_status_changed)
        self.threadpool.start(worker)

    @Slot()
    def on_commit_changes_pressed(self):
        @Slot()
        def _on_commit_success():
            logging.info("Commit to database was successful")
            msg = "Commit to database was successful!"
            QMessageBox.information(self, "Database transaction", msg)

            self.update_label_model()
            self.update_glyph_model()

        @Slot()
        def _on_commit_failure():
            logging.info("Commit to database failed")
            msg = "Commit to database failed!"
            QMessageBox.information(self, "Database transaction", msg)

        if self.glyph_model is None:
            return

        worker = self.injector.create_object(DBCommitRunnable)
        self.wpbar.setWindowTitle("Commit Changes Progress")
        self.wpbar.setRange(min=0, max=worker.NUM_STAGES)
        self.wpbar.show()

        # Worker signals
        worker.signals.succeeded.connect(_on_commit_success)
        worker.signals.failed.connect(_on_commit_failure)
        worker.signals.failed.connect(self.wpbar.on_removed)

        worker.signals.finished.connect(self.wpbar.on_removed)
        worker.signals.finished.connect(self.wpbar.reset)
        worker.signals.progress.connect(self.wpbar.on_count_changed)
        worker.signals.status.connect(self.wpbar.on_status_changed)

        self.threadpool.start(worker)

    @Slot(str)
    def on_set_sorting_strategy(self, sorting_strategy: str):
        """
        :param sorting_strategy: A string representing the sorting strategy to be set for the glyph model.
        :return: None

        This method sets the sorting strategy for the glyph model in the ViewEditWidget.
        If the sorting strategy is "Similarity", it dispatches a similarity calculation for the current label
        and updates the glyph model accordingly. Otherwise, it updates the glyph model without performing
        any other actions.
        """
        if self.awaiting_data:
            return

        self.glyph_model: GlyphsSQLModel
        self.glyph_model.set_sorting_strategy(sorting_strategy)
        self.persistence.set_current_sorting_strategy(sorting_strategy)
        if sorting_strategy.casefold() == "Similarity".casefold():
            self.dispatch_similarity_calculation(self.glyph_model.current_label)
        else:
            self.update_glyph_model()

    @Slot(Qt.CheckState)
    def on_set_sorting_order(self, sorting_order: Qt.CheckState):
        """
        :param sorting_order: The sorting order to set for the glyph model. It should be of type Qt.CheckState.
        :return: None

        This method sets the sorting order for the glyph model in the ViewEditWidget.
        If the sorting strategy is set to "SIMILARITY", it dispatches a similarity calculation for the current label.
        Otherwise, it updates the glyph model without prefetching, scanning and scrolling, and highlighting.
        """
        if self.awaiting_data:
            return

        self.glyph_model: GlyphsSQLModel
        self.glyph_model.set_sorting_order(sorting_order)
        self.persistence.set_current_sorting_order(sorting_order)
        if self.glyph_model.sorting_strategy == GlyphSortingStrategy.SIMILARITY:
            self.dispatch_similarity_calculation(self.glyph_model.current_label)
        else:
            self.update_glyph_model()

    @Slot(Any, bool)
    def dispatch_similarity_calculation(self, label: Union[str, None], force_calc: bool = False):
        if label is None:
            label = self.persistence.current_label

        @Slot()
        def _on_calc_success():
            logging.info("Similarity calculation finished")
            msg = "Similarity calculation finished!"
            QMessageBox.information(self, "Similarity calculation", msg)
            self.update_label_model()
            self.update_glyph_model()
            self.is_calc_similarity = False

        @Slot()
        def _on_calc_failure():
            logging.info("Similarity calculation failed")
            msg = f"Similarity calculation failed."
            QMessageBox.information(self, "Similarity calculation", msg)
            self.is_calc_similarity = False

        if self.is_calc_similarity:
            return

        self.glyph_model: GlyphsSQLModel

        # Check if ALL embeddings are calculated and return if nothing is missing
        conn_name = "calc_embeddings"
        db_handle = self.gsql_service.get_or_create_connection(conn_name)
        glyph_embeddings = self.gsql_service.fetch_nullemb_records(db_handle, label=None, return_fields=False)
        db_handle.close()
        QSqlDatabase.removeDatabase(conn_name)

        if len(glyph_embeddings):
            # Provide user with information and ask whether he wants to compute the embeddings
            msg = f"<p>The workspace was created with an older tool version. Right now, no embeddings are stored in the database.</p>" \
                  f"<p>Do you want to proceed and calculate the embeddings?</p>" \
                  f"<p>These embeddings are less descriptive than the ones calculated for new workspaces using the Docker service.\n " \
                  f"However, they still can be helpful for similarity sorting.</p>"

            reply = QMessageBox.question(self.parent(), "Similarity Analysis", msg,
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.Yes:
                self.dispatch_embedding_calculation(fetch_num=2048, embedding_dim=128)
            else:
                self.update_glyph_model()
            return

        # Check if similarities were calculated and whether they are up-to-date
        conn_name = "similarity_check"
        db_handle = self.gsql_service.get_or_create_connection(conn_name)
        glyph_similarity_indexes = self.gsql_service.get_glyph_similarities(db_handle, label)
        if not len(glyph_similarity_indexes):
            return
        calc_status = max(glyph_similarity_indexes) >= 0
        db_handle.close()
        QSqlDatabase.removeDatabase(conn_name)

        if not force_calc:
            if calc_status:
                # If the calculcation is up-to-date and valid, just refresh the model with the similarity order
                self.update_glyph_model()
                return
            elif calc_status:
                msg = f"<p>The calculated glyph similarity for label <b>{label}</b> might not be up-to-date.</p>" \
                      f"<p>Do you want to start a re-caculation?</p>"
            else:
                msg = f"<p>Glyph similarity for label <b>{label}</b> has not been calculated yet. " \
                      f"This process might take up to several minutes, depending on the number of glyphs!</p>" \
                      f"<p>Do you want to proceed with the calculation?</p>"

            reply = QMessageBox.question(self.parent(), "Similarity Analysis", msg,
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)

            if reply != QMessageBox.StandardButton.Yes:
                self.update_glyph_model()
                return

        worker = self.injector.create_object(SimilarityCalcRunnable, {'label': label})
        self.wpbar.setWindowTitle("Similarity Calculation Progress")
        self.wpbar.setRange(min=0, max=SimilarityCalcRunnable.NUM_STAGES)
        self.wpbar.show()

        # Worker signals
        worker.signals.succeeded.connect(_on_calc_success)
        worker.signals.failed.connect(_on_calc_failure)

        worker.signals.finished.connect(self.wpbar.on_removed)
        worker.signals.finished.connect(self.wpbar.reset)
        worker.signals.progress.connect(self.wpbar.on_count_changed)
        worker.signals.status.connect(self.wpbar.on_status_changed)

        self.is_calc_similarity = True
        self.threadpool.start(worker)

    def dispatch_embedding_calculation(self, fetch_num: int = 512, embedding_dim: int = 128):
        @Slot()
        def _on_calc_success():
            logging.info("Embedding calculation finished")
            msg = "Embedding calculation finished!"
            QMessageBox.information(self, "Embedding calculation", msg)
            self.dispatch_similarity_calculation(self.glyph_model.current_label)
            return

        @Slot()
        def _on_calc_failure():
            logging.info("Embedding calculation failed")
            msg = "Embedding calculation failed. "
            QMessageBox.information(self, "Embedding calculation", msg)
            return

        @Slot()
        def _on_thread_dealloc():
            self.wthread = None
            self.worker = None

        class EmbeddingCalcRunner(QRunnable):

            def __init__(self, total_calc_num: int = None):
                super().__init__()
                self.total_calc_num = total_calc_num
                self.signals = WorkerSignals()
                self.conn_name = "embeddings"

            def run(self):
                progress_count = 0
                self.signals.progress.emit(progress_count)
                db_handle = self.gsql_service.get_or_create_connection(self.conn_name)
                try:
                    # Iterate over all labels
                    encodings = self.gsql_service.get_distinct_labels(db_handle)
                    for enc in encodings:
                        while True:
                            # Fetch glyph images from database
                            records, fields = self.gsql_service.fetch_nullemb_records(db_handle, enc, True, fetch_num)
                            if not len(records):
                                break

                            self.signals.status.emit(
                                f"Calculation embeddings for category <b>{enc}</b>: {progress_count}/{self.total_calc_num} ...")

                            file_id_idx = next(i for i, f in enumerate(fields) if f.name() == 'file_id')
                            glyph_id_idx = next(i for i, f in enumerate(fields) if f.name() == 'glyph_id')
                            img_idx = next(i for i, f in enumerate(fields) if f.name() == 'img')
                            X = []
                            for i in range(len(records)):
                                ba: QByteArray = records[i][img_idx]
                                if isinstance(ba, str):
                                    self.signals.failed.emit()
                                    self.signals.finished.emit()
                                    return

                                img: Image = Image.open(io.BytesIO(ba.data()))
                                X.append(np.array(img))

                            X_processed: List[np.ndarray] = SimilarityCalculationService.preprocess_images(X)
                            embeddings: List[np.ndarray] = SimilarityCalculationService.pca(X_processed,
                                                                                            num_comps=embedding_dim)

                            with Transaction(db_handle, name='dnd_update_glyph_similarity'):
                                for i in range(len(records)):
                                    pk = (records[i][file_id_idx], records[i][glyph_id_idx])
                                    self.gsql_service.update_glyph_embedding(db_handle, pk, QByteArray(
                                        embeddings[i].astype(np.float32).tobytes()))

                            progress_count += len(records)
                            self.signals.progress.emit(progress_count)

                    progress_count += 1
                    self.signals.progress.emit(progress_count)
                    self.signals.succeeded.emit()
                except Exception as e:
                    logging.error("EmbeddingCalcRunner: ", e)
                    self.signals.failed.emit()
                finally:
                    db_handle.close()
                    QSqlDatabase.removeDatabase(self.conn_name)
                    self.signals.finished.emit()

        self.glyph_model: GlyphsSQLModel

        conn_name = "embeddings_info"
        db_handle = self.gsql_service.get_or_create_connection(conn_name)
        # Check if ALL embeddings are calculated and return if nothing is missing
        glyph_embeddings = self.gsql_service.fetch_nullemb_records(db_handle, label=None, return_fields=False)
        db_handle.close()
        QSqlDatabase.removeDatabase(conn_name)

        worker = EmbeddingCalcRunner(total_calc_num=len(glyph_embeddings))
        self.wpbar.setWindowTitle("Embedding Calculcation Progress")
        self.wpbar.setRange(min=0, max=len(glyph_embeddings) + 1)
        self.wpbar.show()

        # Worker signals
        worker.signals.succeeded.connect(_on_calc_success, Qt.ConnectionType.BlockingQueuedConnection)
        worker.signals.failed.connect(_on_calc_failure)
        worker.signals.finished.connect(self.wpbar.on_removed)
        worker.signals.finished.connect(self.wpbar.reset)
        worker.signals.progress.connect(self.wpbar.on_count_changed)
        worker.signals.status.connect(self.wpbar.on_status_changed)

        self.threadpool.start(worker)

    @Slot(Any)
    def dispatch_autosave(self, num_pending_changes: Union[int, None] = None):
        @Slot()
        def _on_save_success():
            print("Autosave finished")
            self.is_autosaving = False
            return

        @Slot()
        def _on_save_failure():
            logging.error("Autosave failed")
            self.is_autosaving = False
            return

        if self.is_autosaving or not self.settings.autosave:
            return

        # set current bookmarks
        print(self.glyph_model.working)
        if not self.glyph_model.working:
            self.set_bookmarks(self.persistence.current_label, self.persistence.current_similarity)

        worker = self.injector.create_object(AutoSaveRunner, {'workspace_path': self.workspace})
        worker.signals.succeeded.connect(_on_save_success, Qt.ConnectionType.BlockingQueuedConnection)
        worker.signals.failed.connect(_on_save_failure)

        self.is_autosaving = True
        self.threadpool.start(worker)
