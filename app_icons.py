from PySide6.QtWidgets import QStyle, QMainWindow
from enum import Enum
import qdarktheme
import json

### qdarktheme DUCKTYPING
# icon svgs from google fonts
resources = json.loads(qdarktheme._resources.svg.SVG_RESOURCES)
resources['processing'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M160-160v-80h110l-16-14q-52-46-73-105t-21-119q0-111 66.5-197.5T400-790v84q-72 26-116 88.5T240-478q0 45 17 87.5t53 78.5l10 10v-98h80v240H160Zm400-10v-84q72-26 116-88.5T720-482q0-45-17-87.5T650-648l-10-10v98h-80v-240h240v80H690l16 14q49 49 71.5 106.5T800-482q0 111-66.5 197.5T560-170Z"/></svg>'
resources['edit'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M200-200h56l345-345-56-56-345 345v56Zm572-403L602-771l56-56q23-23 56.5-23t56.5 23l56 56q23 23 24 55.5T829-660l-57 57Zm-58 59L290-120H120v-170l424-424 170 170Zm-141-29-28-28 56 56-28-28Z"/></svg>'
resources['add'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/></svg>'
resources['undo'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M280-200v-80h284q63 0 109.5-40T720-420q0-60-46.5-100T564-560H312l104 104-56 56-200-200 200-200 56 56-104 104h252q97 0 166.5 63T800-420q0 94-69.5 157T564-200H280Z"/></svg>'
resources['settings'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm112-260q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Zm0-80q-25 0-42.5-17.5T422-480q0-25 17.5-42.5T482-540q25 0 42.5 17.5T542-480q0 25-17.5 42.5T482-420Zm-2-60Zm-40 320h79l14-106q31-8 57.5-23.5T639-327l99 41 39-68-86-65q5-14 7-29.5t2-31.5q0-16-2-31.5t-7-29.5l86-65-39-68-99 42q-22-23-48.5-38.5T533-694l-13-106h-79l-14 106q-31 8-57.5 23.5T321-633l-99-41-39 68 86 64q-5 15-7 30t-2 32q0 16 2 31t7 30l-86 65 39 68 99-42q22 23 48.5 38.5T427-266l13 106Z"/></svg>'
resources['extract'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M480-120q-75 0-140.5-28.5t-114-77q-48.5-48.5-77-114T120-480q0-75 28.5-140.5t77-114q48.5-48.5 114-77T480-840v80q-117 0-198.5 81.5T200-480q0 117 81.5 198.5T480-200v80Zm160-160-56-57 103-103H360v-80h327L584-624l56-56 200 200-200 200Z"/></svg>'
resources['import_book'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M260-320q47 0 91.5 10.5T440-278v-394q-41-24-87-36t-93-12q-36 0-71.5 7T120-692v396q35-12 69.5-18t70.5-6Zm260 42q44-21 88.5-31.5T700-320q36 0 70.5 6t69.5 18v-396q-33-14-68.5-21t-71.5-7q-47 0-93 12t-87 36v394Zm-40 118q-48-38-104-59t-116-21q-42 0-82.5 11T100-198q-21 11-40.5-1T40-234v-482q0-11 5.5-21T62-752q46-24 96-36t102-12q58 0 113.5 15T480-740q51-30 106.5-45T700-800q52 0 102 12t96 36q11 5 16.5 15t5.5 21v482q0 23-19.5 35t-40.5 1q-37-20-77.5-31T700-240q-60 0-116 21t-104 59ZM280-494Z"/></svg>'
resources['install'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M320-120v-80H160q-33 0-56.5-23.5T80-280v-480q0-33 23.5-56.5T160-840h320v80H160v480h640v-120h80v120q0 33-23.5 56.5T800-200H640v80H320Zm360-280L480-600l56-56 104 103v-287h80v287l104-103 56 56-200 200Z"/></svg>'
resources['transfer'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M280-120 80-320l200-200 57 56-104 104h607v80H233l104 104-57 56Zm400-320-57-56 104-104H120v-80h607L623-784l57-56 200 200-200 200Z"/></svg>'
resources['export'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M240-40q-33 0-56.5-23.5T160-120v-440q0-33 23.5-56.5T240-640h120v80H240v440h480v-440H600v-80h120q33 0 56.5 23.5T800-560v440q0 33-23.5 56.5T720-40H240Zm200-280v-447l-64 64-56-57 160-160 160 160-56 57-64-64v447h-80Z"/></svg>'
resources['file'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M320-240h320v-80H320v80Zm0-160h320v-80H320v80ZM240-80q-33 0-56.5-23.5T160-160v-640q0-33 23.5-56.5T240-880h320l240 240v480q0 33-23.5 56.5T720-80H240Zm280-520v-200H240v640h480v-440H520ZM240-800v200-200 640-640Z"/></svg>'
resources['pending'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M280-420q25 0 42.5-17.5T340-480q0-25-17.5-42.5T280-540q-25 0-42.5 17.5T220-480q0 25 17.5 42.5T280-420Zm200 0q25 0 42.5-17.5T540-480q0-25-17.5-42.5T480-540q-25 0-42.5 17.5T420-480q0 25 17.5 42.5T480-420Zm200 0q25 0 42.5-17.5T740-480q0-25-17.5-42.5T680-540q-25 0-42.5 17.5T620-480q0 25 17.5 42.5T680-420ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>'
resources['workspace'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M240-120q-66 0-113-47T80-280q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47Zm480 0q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47Zm-480-80q33 0 56.5-23.5T320-280q0-33-23.5-56.5T240-360q-33 0-56.5 23.5T160-280q0 33 23.5 56.5T240-200Zm480 0q33 0 56.5-23.5T800-280q0-33-23.5-56.5T720-360q-33 0-56.5 23.5T640-280q0 33 23.5 56.5T720-200ZM480-520q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47Zm0-80q33 0 56.5-23.5T560-680q0-33-23.5-56.5T480-760q-33 0-56.5 23.5T400-680q0 33 23.5 56.5T480-600Zm0-80Zm240 400Zm-480 0Z"/></svg>'
resources['zoom_in'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M784-120 532-372q-30 24-69 38t-83 14q-109 0-184.5-75.5T120-580q0-109 75.5-184.5T380-840q109 0 184.5 75.5T640-580q0 44-14 83t-38 69l252 252-56 56ZM380-400q75 0 127.5-52.5T560-580q0-75-52.5-127.5T380-760q-75 0-127.5 52.5T200-580q0 75 52.5 127.5T380-400Zm-40-60v-80h-80v-80h80v-80h80v80h80v80h-80v80h-80Z"/></svg>'
resources['zoom_out'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M784-120 532-372q-30 24-69 38t-83 14q-109 0-184.5-75.5T120-580q0-109 75.5-184.5T380-840q109 0 184.5 75.5T640-580q0 44-14 83t-38 69l252 252-56 56ZM380-400q75 0 127.5-52.5T560-580q0-75-52.5-127.5T380-760q-75 0-127.5 52.5T200-580q0 75 52.5 127.5T380-400ZM280-540v-80h200v80H280Z"/></svg>'
resources['bookmark'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M120-40v-640q0-33 23.5-56.5T200-760h400q33 0 56.5 23.5T680-680v640L400-160 120-40Zm640-120v-680H240v-80h520q33 0 56.5 23.5T840-840v680h-80Z"/></svg>'
resources['bookmark_jump'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M440-440v-160h80v80h80v80H440Zm280 0v-80h80v-80h80v160H720ZM440-720v-160h160v80h-80v80h-80Zm360 0v-80h-80v-80h160v160h-80ZM136-80l-56-56 224-224H120v-80h320v320h-80v-184L136-80Z"/></svg>'
resources['glyph_locate'] = '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368"><path d="M480-400q-33 0-56.5-23.5T400-480q0-33 23.5-56.5T480-560q33 0 56.5 23.5T560-480q0 33-23.5 56.5T480-400Zm-40-240v-200h80v200h-80Zm0 520v-200h80v200h-80Zm200-320v-80h200v80H640Zm-520 0v-80h200v80H120Z"/></svg>'
qdarktheme._resources.svg.SVG_RESOURCES = json.dumps(resources)

# icon lookup
icon_map = qdarktheme._resources.standard_icons.NEW_STANDARD_ICON_MAP
icon_map[QStyle.StandardPixmap.SP_MediaPlay] = {"id": "processing"}
icon_map[QStyle.StandardPixmap.SP_MediaStop] = {"id": "edit"}
icon_map[QStyle.StandardPixmap.SP_MediaPause] = {"id": "add"}
icon_map[QStyle.StandardPixmap.SP_MediaVolume] = {"id": "undo"}
icon_map[QStyle.StandardPixmap.SP_MediaSeekBackward] = {"id": "settings"}
icon_map[QStyle.StandardPixmap.SP_MediaSeekForward] = {"id": "extract"}
icon_map[QStyle.StandardPixmap.SP_MediaSkipBackward] = {"id": "import_book"}
icon_map[QStyle.StandardPixmap.SP_MediaSkipForward] = {"id": "install"}
icon_map[QStyle.StandardPixmap.SP_CommandLink] = {"id": "transfer"}
icon_map[QStyle.StandardPixmap.SP_ComputerIcon] = {"id": "export"}
icon_map[QStyle.StandardPixmap.SP_DriveCDIcon] = {"id": "file"}
icon_map[QStyle.StandardPixmap.SP_DriveFDIcon] = {"id": "pending"}
icon_map[QStyle.StandardPixmap.SP_DriveHDIcon] = {"id": "workspace"}
icon_map[QStyle.StandardPixmap.SP_TitleBarMinButton] = {"id": "zoom_in"}
icon_map[QStyle.StandardPixmap.SP_TitleBarMaxButton] = {"id": "zoom_out"}
icon_map[QStyle.StandardPixmap.SP_BrowserReload] = {"id": "bookmark"}
icon_map[QStyle.StandardPixmap.SP_BrowserStop] = {"id": "bookmark_jump"}
icon_map[QStyle.StandardPixmap.SP_VistaShield] = {"id": "glyph_locate"}
qdarktheme._resources.standard_icons.NEW_STANDARD_ICON_MAP = icon_map


class AppIcons(object):
    ICON_FAIL = QStyle.StandardPixmap.SP_DialogCancelButton
    ICON_SUCCESS = QStyle.StandardPixmap.SP_DialogApplyButton
    ICON_PROCESSING = QStyle.StandardPixmap.SP_MediaPlay

    ICON_DELETE = QStyle.StandardPixmap.SP_DialogDiscardButton
    ICON_DELETE_ALL = QStyle.StandardPixmap.SP_DialogCancelButton
    ICON_EDIT = QStyle.StandardPixmap.SP_MediaStop
    ICON_NEW = QStyle.StandardPixmap.SP_MediaPause
    ICON_TRANSFER = QStyle.StandardPixmap.SP_CommandLink
    ICON_IMPORT = QStyle.StandardPixmap.SP_MediaSkipBackward
    ICON_EXPORT = QStyle.StandardPixmap.SP_ComputerIcon
    ICON_TEXT = QStyle.StandardPixmap.SP_DriveCDIcon
    ICON_REVERT = QStyle.StandardPixmap.SP_MediaVolume
    ICON_SETUP = QStyle.StandardPixmap.SP_MediaSkipForward
    ICON_EXTRACT = QStyle.StandardPixmap.SP_MediaSeekForward
    ICON_SETTINGS = QStyle.StandardPixmap.SP_MediaSeekBackward
    ICON_VIEWEDIT = QStyle.StandardPixmap.SP_DriveHDIcon
    ICON_ZOOMIN = QStyle.StandardPixmap.SP_TitleBarMinButton
    ICON_ZOOMOUT = QStyle.StandardPixmap.SP_TitleBarMaxButton
    ICON_BOOKMARK = QStyle.StandardPixmap.SP_BrowserReload
    ICON_BOOKMARK_JUMP = QStyle.StandardPixmap.SP_BrowserStop
    ICON_GLYPH_LOCATE = QStyle.StandardPixmap.SP_VistaShield

    ICON_UNPROCESSED = ICON_CROSS = QStyle.StandardPixmap.SP_DialogCancelButton
    ICON_PENDING = QStyle.StandardPixmap.SP_DriveFDIcon
    ICON_DONE = ICON_CHECK = QStyle.StandardPixmap.SP_DialogApplyButton

    def as_icon(self, style: QStyle):
        ico = style.standardIcon(self)
        return ico

    @classmethod
    def get_icon(cls, ico: QStyle.StandardPixmap, style: QStyle):
        ico = style.standardIcon(ico, None, None)
        return ico

    @classmethod
    def get_pixmap(cls, ico: QStyle.StandardPixmap, style: QStyle, extent=32):
        ico = style.standardIcon(ico, None, None)
        return ico.pixmap(extent)



