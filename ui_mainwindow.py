# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindowetrQHQ.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from widgets.viewedit.vieweditwidget import ViewEditWidget

from injector import Injector
from modules import WorkspaceModule

import resources_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1080, 960)
        MainWindow.setMinimumSize(QSize(1080, 960))
        icon = QIcon()
        icon.addFile(u":/app.ico", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QSize(0, 52))
        self.tabWidget.setCursor(QCursor(Qt.ArrowCursor))
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tabWidget.setIconSize(QSize(16, 16))
        self.tabWidget.setElideMode(Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.setupTab = QWidget()
        self.setupTab.setObjectName(u"setupTab")
        self.horizontalLayout_10 = QHBoxLayout(self.setupTab)
        self.horizontalLayout_10.setSpacing(6)
        self.horizontalLayout_10.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.setupWidgets = QWidget(self.setupTab)
        self.setupWidgets.setObjectName(u"setupWidgets")
        self.verticalLayout_10 = QVBoxLayout(self.setupWidgets)
        self.verticalLayout_10.setSpacing(6)
        self.verticalLayout_10.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.setup1 = QFrame(self.setupWidgets)
        self.setup1.setObjectName(u"setup1")
        self.setup1.setFrameShape(QFrame.StyledPanel)
        self.setup1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.setup1)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.setup1_title = QFrame(self.setup1)
        self.setup1_title.setObjectName(u"setup1_title")
        self.setup1_title.setFrameShape(QFrame.StyledPanel)
        self.setup1_title.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.setup1_title)
        self.verticalLayout_12.setSpacing(6)
        self.verticalLayout_12.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.labelSetupDescription = QLabel(self.setup1_title)
        self.labelSetupDescription.setObjectName(u"labelSetupDescription")
        self.labelSetupDescription.setOpenExternalLinks(True)

        self.verticalLayout_12.addWidget(self.labelSetupDescription)

        self.verticalLayout_11.addWidget(self.setup1_title)

        self.setup1_content = QFrame(self.setup1)
        self.setup1_content.setObjectName(u"setup1_content")
        self.setup1_content.setFrameShape(QFrame.StyledPanel)
        self.setup1_content.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.setup1_content)
        self.verticalLayout_13.setSpacing(6)
        self.verticalLayout_13.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setSpacing(6)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.labelDockerStatusMessage = QLabel(self.setup1_content)
        self.labelDockerStatusMessage.setObjectName(u"labelDockerStatusMessage")

        self.gridLayout_5.addWidget(self.labelDockerStatusMessage, 0, 1, 1, 1)

        self.labelDockerStatusImage = QLabel(self.setup1_content)
        self.labelDockerStatusImage.setObjectName(u"labelDockerStatusImage")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.labelDockerStatusImage.sizePolicy().hasHeightForWidth())
        self.labelDockerStatusImage.setSizePolicy(sizePolicy1)
        self.labelDockerStatusImage.setMinimumSize(QSize(25, 25))
        self.labelDockerStatusImage.setMaximumSize(QSize(25, 25))
        self.labelDockerStatusImage.setPixmap(QPixmap(u":/icons/cil-x-circle.svg"))
        self.labelDockerStatusImage.setScaledContents(True)

        self.gridLayout_5.addWidget(self.labelDockerStatusImage, 0, 0, 1, 1)

        self.verticalLayout_13.addLayout(self.gridLayout_5)

        self.verticalLayout_11.addWidget(self.setup1_content)

        self.verticalLayout_10.addWidget(self.setup1)

        self.setup2 = QFrame(self.setupWidgets)
        self.setup2.setObjectName(u"setup2")
        self.setup2.setEnabled(True)
        self.setup2.setFrameShape(QFrame.StyledPanel)
        self.setup2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.setup2)
        self.verticalLayout_14.setSpacing(0)
        self.verticalLayout_14.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.setup2_title = QFrame(self.setup2)
        self.setup2_title.setObjectName(u"setup2_title")
        self.setup2_title.setFrameShape(QFrame.StyledPanel)
        self.setup2_title.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.setup2_title)
        self.verticalLayout_15.setSpacing(6)
        self.verticalLayout_15.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.labelImagePullDescription = QLabel(self.setup2_title)
        self.labelImagePullDescription.setObjectName(u"labelImagePullDescription")
        self.labelImagePullDescription.setWordWrap(True)

        self.verticalLayout_15.addWidget(self.labelImagePullDescription)

        self.verticalLayout_14.addWidget(self.setup2_title)

        self.setup2_content = QFrame(self.setup2)
        self.setup2_content.setObjectName(u"setup2_content")
        self.setup2_content.setFrameShape(QFrame.StyledPanel)
        self.setup2_content.setFrameShadow(QFrame.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.setup2_content)
        self.verticalLayout_16.setSpacing(6)
        self.verticalLayout_16.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setSpacing(6)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.labelDockerEBM = QLabel(self.setup2_content)
        self.labelDockerEBM.setObjectName(u"labelDockerEBM")
        self.labelDockerEBM.setEnabled(True)

        self.gridLayout_4.addWidget(self.labelDockerEBM, 1, 0, 1, 1)

        self.labelDockerOCRD = QLabel(self.setup2_content)
        self.labelDockerOCRD.setObjectName(u"labelDockerOCRD")

        self.gridLayout_4.addWidget(self.labelDockerOCRD, 0, 0, 1, 1)

        self.progressBarDockerEBM = QProgressBar(self.setup2_content)
        self.progressBarDockerEBM.setObjectName(u"progressBarDockerEBM")
        self.progressBarDockerEBM.setEnabled(True)
        self.progressBarDockerEBM.setMaximum(100)
        self.progressBarDockerEBM.setValue(-1)

        self.gridLayout_4.addWidget(self.progressBarDockerEBM, 1, 5, 1, 1)

        self.pushButtonDockerOCRDRemote = QPushButton(self.setup2_content)
        self.pushButtonDockerOCRDRemote.setObjectName(u"pushButtonDockerOCRDRemote")
        sizePolicy1.setHeightForWidth(self.pushButtonDockerOCRDRemote.sizePolicy().hasHeightForWidth())
        self.pushButtonDockerOCRDRemote.setSizePolicy(sizePolicy1)
        self.pushButtonDockerOCRDRemote.setMinimumSize(QSize(100, 30))

        self.gridLayout_4.addWidget(self.pushButtonDockerOCRDRemote, 0, 3, 1, 1)

        self.progressBarDockerOCRD = QProgressBar(self.setup2_content)
        self.progressBarDockerOCRD.setObjectName(u"progressBarDockerOCRD")
        self.progressBarDockerOCRD.setMaximum(100)
        self.progressBarDockerOCRD.setValue(-1)

        self.gridLayout_4.addWidget(self.progressBarDockerOCRD, 0, 5, 1, 1)

        self.pushButtonDockerEBMRemote = QPushButton(self.setup2_content)
        self.pushButtonDockerEBMRemote.setObjectName(u"pushButtonDockerEBMRemote")
        self.pushButtonDockerEBMRemote.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.pushButtonDockerEBMRemote.sizePolicy().hasHeightForWidth())
        self.pushButtonDockerEBMRemote.setSizePolicy(sizePolicy1)
        self.pushButtonDockerEBMRemote.setMinimumSize(QSize(100, 30))

        self.gridLayout_4.addWidget(self.pushButtonDockerEBMRemote, 1, 3, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_3, 1, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.labelDockerOCRDStatus = QLabel(self.setup2_content)
        self.labelDockerOCRDStatus.setObjectName(u"labelDockerOCRDStatus")
        sizePolicy1.setHeightForWidth(self.labelDockerOCRDStatus.sizePolicy().hasHeightForWidth())
        self.labelDockerOCRDStatus.setSizePolicy(sizePolicy1)
        self.labelDockerOCRDStatus.setMinimumSize(QSize(25, 25))
        self.labelDockerOCRDStatus.setMaximumSize(QSize(25, 25))
        self.labelDockerOCRDStatus.setPixmap(QPixmap(u":/icons/cil-x-circle.svg"))
        self.labelDockerOCRDStatus.setScaledContents(True)
        self.labelDockerOCRDStatus.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.labelDockerOCRDStatus, 0, 1, 1, 1, Qt.AlignHCenter | Qt.AlignVCenter)

        self.labelDockerEBMStatus = QLabel(self.setup2_content)
        self.labelDockerEBMStatus.setObjectName(u"labelDockerEBMStatus")
        self.labelDockerEBMStatus.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.labelDockerEBMStatus.sizePolicy().hasHeightForWidth())
        self.labelDockerEBMStatus.setSizePolicy(sizePolicy1)
        self.labelDockerEBMStatus.setMinimumSize(QSize(25, 25))
        self.labelDockerEBMStatus.setMaximumSize(QSize(25, 25))
        self.labelDockerEBMStatus.setPixmap(QPixmap(u":/icons/cil-x-circle.svg"))
        self.labelDockerEBMStatus.setScaledContents(True)

        self.gridLayout_4.addWidget(self.labelDockerEBMStatus, 1, 1, 1, 1)

        self.pushButtonDockerOCRDLocal = QPushButton(self.setup2_content)
        self.pushButtonDockerOCRDLocal.setObjectName(u"pushButtonDockerOCRDLocal")
        sizePolicy1.setHeightForWidth(self.pushButtonDockerOCRDLocal.sizePolicy().hasHeightForWidth())
        self.pushButtonDockerOCRDLocal.setSizePolicy(sizePolicy1)
        self.pushButtonDockerOCRDLocal.setMinimumSize(QSize(100, 30))

        self.gridLayout_4.addWidget(self.pushButtonDockerOCRDLocal, 0, 4, 1, 1)

        self.pushButtonDockerEBMLocal = QPushButton(self.setup2_content)
        self.pushButtonDockerEBMLocal.setObjectName(u"pushButtonDockerEBMLocal")
        self.pushButtonDockerEBMLocal.setEnabled(True)
        self.pushButtonDockerEBMLocal.setMinimumSize(QSize(100, 30))

        self.gridLayout_4.addWidget(self.pushButtonDockerEBMLocal, 1, 4, 1, 1)

        self.verticalLayout_16.addLayout(self.gridLayout_4)

        self.verticalLayout_14.addWidget(self.setup2_content)

        self.verticalLayout_10.addWidget(self.setup2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer)

        self.horizontalLayout_10.addWidget(self.setupWidgets)

        icon1 = QIcon()
        icon1.addFile(u":/icons/cil-bolt-circle.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.tabWidget.addTab(self.setupTab, icon1, "")
        self.importTab = QWidget()
        self.importTab.setObjectName(u"importTab")
        self.horizontalLayout_2 = QHBoxLayout(self.importTab)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.dataWidgets = QWidget(self.importTab)
        self.dataWidgets.setObjectName(u"dataWidgets")
        self.dataWidgets.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.dataWidgets)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.row1 = QFrame(self.dataWidgets)
        self.row1.setObjectName(u"row1")
        sizePolicy.setHeightForWidth(self.row1.sizePolicy().hasHeightForWidth())
        self.row1.setSizePolicy(sizePolicy)
        self.row1.setStyleSheet(u"")
        self.row1.setFrameShape(QFrame.StyledPanel)
        self.row1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.row1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.row1_title = QFrame(self.row1)
        self.row1_title.setObjectName(u"row1_title")
        self.row1_title.setFrameShape(QFrame.StyledPanel)
        self.row1_title.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.row1_title)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.labelDataSel = QLabel(self.row1_title)
        self.labelDataSel.setObjectName(u"labelDataSel")

        self.verticalLayout_4.addWidget(self.labelDataSel)

        self.verticalLayout_2.addWidget(self.row1_title)

        self.row1_content = QFrame(self.row1)
        self.row1_content.setObjectName(u"row1_content")
        self.row1_content.setMinimumSize(QSize(876, 50))
        self.row1_content.setFrameShape(QFrame.StyledPanel)
        self.row1_content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.row1_content)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(9, 9, 9, 9)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lineEditDataSel = QLineEdit(self.row1_content)
        self.lineEditDataSel.setObjectName(u"lineEditDataSel")
        self.lineEditDataSel.setMinimumSize(QSize(0, 30))
        font = QFont()
        font.setItalic(False)
        self.lineEditDataSel.setFont(font)
        self.lineEditDataSel.setAutoFillBackground(False)
        self.lineEditDataSel.setDragEnabled(False)
        self.lineEditDataSel.setCursorMoveStyle(Qt.LogicalMoveStyle)
        self.lineEditDataSel.setClearButtonEnabled(True)

        self.gridLayout_2.addWidget(self.lineEditDataSel, 0, 1, 1, 1)

        self.pushButtonDataSel = QPushButton(self.row1_content)
        self.pushButtonDataSel.setObjectName(u"pushButtonDataSel")
        sizePolicy1.setHeightForWidth(self.pushButtonDataSel.sizePolicy().hasHeightForWidth())
        self.pushButtonDataSel.setSizePolicy(sizePolicy1)
        self.pushButtonDataSel.setMinimumSize(QSize(100, 30))
        self.pushButtonDataSel.setMaximumSize(QSize(100, 30))
        icon2 = QIcon()
        icon2.addFile(u":/icons/images/icons/cil-folder-open.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonDataSel.setIcon(icon2)

        self.gridLayout_2.addWidget(self.pushButtonDataSel, 0, 0, 1, 1)

        self.horizontalLayout.addLayout(self.gridLayout_2)

        self.verticalLayout_2.addWidget(self.row1_content)

        self.verticalLayout_5.addWidget(self.row1)

        self.line = QFrame(self.dataWidgets)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_5.addWidget(self.line)

        self.row2 = QFrame(self.dataWidgets)
        self.row2.setObjectName(u"row2")
        self.row2.setEnabled(True)
        self.row2.setFrameShape(QFrame.StyledPanel)
        self.row2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.row2)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.row2_title = QFrame(self.row2)
        self.row2_title.setObjectName(u"row2_title")
        self.row2_title.setEnabled(True)
        self.row2_title.setFrameShape(QFrame.StyledPanel)
        self.row2_title.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.row2_title)
        self.verticalLayout_7.setSpacing(6)
        self.verticalLayout_7.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.labelWSPrep = QLabel(self.row2_title)
        self.labelWSPrep.setObjectName(u"labelWSPrep")
        self.labelWSPrep.setEnabled(True)

        self.verticalLayout_7.addWidget(self.labelWSPrep)

        self.verticalLayout_6.addWidget(self.row2_title)

        self.row2_content = QFrame(self.row2)
        self.row2_content.setObjectName(u"row2_content")
        self.row2_content.setFrameShape(QFrame.StyledPanel)
        self.row2_content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.row2_content)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.groupBoxWSSep = QGroupBox(self.row2_content)
        self.groupBoxWSSep.setObjectName(u"groupBoxWSSep")
        self.groupBoxWSSep.setMinimumSize(QSize(0, 0))
        self.groupBoxWSSep.setStyleSheet(u"QGroupBox\n"
                                         "{\n"
                                         "    font-size: 12px;\n"
                                         "    font-weight: bold;\n"
                                         "}")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBoxWSSep)
        self.horizontalLayout_7.setSpacing(6)
        self.horizontalLayout_7.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.radioButtonImportNone = QRadioButton(self.groupBoxWSSep)
        self.radioButtonImportNone.setObjectName(u"radioButtonImportNone")
        self.radioButtonImportNone.setChecked(True)

        self.horizontalLayout_7.addWidget(self.radioButtonImportNone, 0, Qt.AlignLeft)

        self.radioButtonImportBatchSize = QRadioButton(self.groupBoxWSSep)
        self.radioButtonImportBatchSize.setObjectName(u"radioButtonImportBatchSize")

        self.horizontalLayout_7.addWidget(self.radioButtonImportBatchSize, 0, Qt.AlignRight)

        self.lineEditBatchSize = QLineEdit(self.groupBoxWSSep)
        self.lineEditBatchSize.setObjectName(u"lineEditBatchSize")
        sizePolicy1.setHeightForWidth(self.lineEditBatchSize.sizePolicy().hasHeightForWidth())
        self.lineEditBatchSize.setSizePolicy(sizePolicy1)
        self.lineEditBatchSize.setMinimumSize(QSize(100, 25))
        self.lineEditBatchSize.setMaximumSize(QSize(100, 25))

        self.horizontalLayout_7.addWidget(self.lineEditBatchSize)

        self.horizontalLayout_6.addWidget(self.groupBoxWSSep)

        self.horizontalSpacer_11 = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_11)

        self.groupBoxWSOpts = QGroupBox(self.row2_content)
        self.groupBoxWSOpts.setObjectName(u"groupBoxWSOpts")
        self.groupBoxWSOpts.setStyleSheet(u"QGroupBox\n"
                                          "{\n"
                                          "    font-size: 12px;\n"
                                          "    font-weight: bold;\n"
                                          "}")
        self.groupBoxWSOpts.setFlat(False)
        self.groupBoxWSOpts.setCheckable(False)
        self.horizontalLayout_8 = QHBoxLayout(self.groupBoxWSOpts)
        self.horizontalLayout_8.setSpacing(6)
        self.horizontalLayout_8.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.checkBoxNoNumIDs = QCheckBox(self.groupBoxWSOpts)
        self.checkBoxNoNumIDs.setObjectName(u"checkBoxNoNumIDs")

        self.horizontalLayout_8.addWidget(self.checkBoxNoNumIDs, 0, Qt.AlignLeft)

        self.checkBoxConvert = QCheckBox(self.groupBoxWSOpts)
        self.checkBoxConvert.setObjectName(u"checkBoxConvert")

        self.horizontalLayout_8.addWidget(self.checkBoxConvert, 0, Qt.AlignHCenter)

        self.label_8 = QLabel(self.groupBoxWSOpts)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_8.addWidget(self.label_8)

        self.lineEditDPI = QLineEdit(self.groupBoxWSOpts)
        self.lineEditDPI.setObjectName(u"lineEditDPI")
        sizePolicy1.setHeightForWidth(self.lineEditDPI.sizePolicy().hasHeightForWidth())
        self.lineEditDPI.setSizePolicy(sizePolicy1)
        self.lineEditDPI.setMinimumSize(QSize(100, 25))
        self.lineEditDPI.setMaximumSize(QSize(100, 25))

        self.horizontalLayout_8.addWidget(self.lineEditDPI)

        self.horizontalLayout_6.addWidget(self.groupBoxWSOpts)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)

        self.verticalLayout_6.addWidget(self.row2_content)

        self.verticalLayout_5.addWidget(self.row2)

        self.line_3 = QFrame(self.dataWidgets)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_5.addWidget(self.line_3)

        self.row3 = QFrame(self.dataWidgets)
        self.row3.setObjectName(u"row3")
        self.row3.setEnabled(True)
        self.row3.setFrameShape(QFrame.StyledPanel)
        self.row3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.row3)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.row3_title = QFrame(self.row3)
        self.row3_title.setObjectName(u"row3_title")
        self.row3_title.setFrameShape(QFrame.StyledPanel)
        self.row3_title.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.row3_title)
        self.verticalLayout_9.setSpacing(6)
        self.verticalLayout_9.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label = QLabel(self.row3_title)
        self.label.setObjectName(u"label")

        self.verticalLayout_9.addWidget(self.label)

        self.verticalLayout_8.addWidget(self.row3_title)

        self.row3_content = QFrame(self.row3)
        self.row3_content.setObjectName(u"row3_content")
        self.row3_content.setFrameShape(QFrame.StyledPanel)
        self.row3_content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.row3_content)
        self.horizontalLayout_9.setSpacing(6)
        self.horizontalLayout_9.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName(u"gridLayout")
        self.progressBarImport = QProgressBar(self.row3_content)
        self.progressBarImport.setObjectName(u"progressBarImport")
        self.progressBarImport.setEnabled(False)
        self.progressBarImport.setMinimum(0)
        self.progressBarImport.setMaximum(100)
        self.progressBarImport.setValue(-1)
        self.progressBarImport.setInvertedAppearance(False)

        self.gridLayout.addWidget(self.progressBarImport, 1, 3, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 1, 2, 1, 1)

        self.plainTextEditCreateWorkspace = QPlainTextEdit(self.row3_content)
        self.plainTextEditCreateWorkspace.setObjectName(u"plainTextEditCreateWorkspace")

        self.gridLayout.addWidget(self.plainTextEditCreateWorkspace, 4, 0, 1, 4)

        self.labelImportDescription = QLabel(self.row3_content)
        self.labelImportDescription.setObjectName(u"labelImportDescription")
        self.labelImportDescription.setScaledContents(False)

        self.gridLayout.addWidget(self.labelImportDescription, 2, 3, 1, 1)

        self.labelIconImport = QLabel(self.row3_content)
        self.labelIconImport.setObjectName(u"labelIconImport")
        sizePolicy1.setHeightForWidth(self.labelIconImport.sizePolicy().hasHeightForWidth())
        self.labelIconImport.setSizePolicy(sizePolicy1)
        self.labelIconImport.setMinimumSize(QSize(25, 25))
        self.labelIconImport.setMaximumSize(QSize(25, 25))
        self.labelIconImport.setPixmap(QPixmap(u":/icons/cil-x-circle.svg"))
        self.labelIconImport.setScaledContents(True)

        self.gridLayout.addWidget(self.labelIconImport, 1, 1, 1, 1)

        self.pushButtonImport = QPushButton(self.row3_content)
        self.pushButtonImport.setObjectName(u"pushButtonImport")
        self.pushButtonImport.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.pushButtonImport.sizePolicy().hasHeightForWidth())
        self.pushButtonImport.setSizePolicy(sizePolicy1)
        self.pushButtonImport.setMinimumSize(QSize(130, 30))
        icon3 = QIcon()
        icon3.addFile(u":/icons/images/icons/cil-data-transfer-down.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonImport.setIcon(icon3)

        self.gridLayout.addWidget(self.pushButtonImport, 1, 0, 1, 1)

        self.label_7 = QLabel(self.row3_content)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)

        self.horizontalLayout_9.addLayout(self.gridLayout)

        self.verticalLayout_8.addWidget(self.row3_content)

        self.verticalLayout_5.addWidget(self.row3)

        self.horizontalLayout_2.addWidget(self.dataWidgets)

        icon4 = QIcon()
        icon4.addFile(u":/icons/cil-note-add.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.tabWidget.addTab(self.importTab, icon4, "")
        self.extractTab = QWidget()
        self.extractTab.setObjectName(u"extractTab")
        self.horizontalLayout_11 = QHBoxLayout(self.extractTab)
        self.horizontalLayout_11.setSpacing(6)
        self.horizontalLayout_11.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.extractWidgets = QWidget(self.extractTab)
        self.extractWidgets.setObjectName(u"extractWidgets")
        self.verticalLayout_17 = QVBoxLayout(self.extractWidgets)
        self.verticalLayout_17.setSpacing(6)
        self.verticalLayout_17.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.extract1 = QFrame(self.extractWidgets)
        self.extract1.setObjectName(u"extract1")
        self.extract1.setFrameShape(QFrame.StyledPanel)
        self.extract1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_18 = QVBoxLayout(self.extract1)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.extract1_title = QFrame(self.extract1)
        self.extract1_title.setObjectName(u"extract1_title")
        self.extract1_title.setFrameShape(QFrame.StyledPanel)
        self.extract1_title.setFrameShadow(QFrame.Raised)
        self.verticalLayout_19 = QVBoxLayout(self.extract1_title)
        self.verticalLayout_19.setSpacing(6)
        self.verticalLayout_19.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.labelWorkspaceSel = QLabel(self.extract1_title)
        self.labelWorkspaceSel.setObjectName(u"labelWorkspaceSel")

        self.verticalLayout_19.addWidget(self.labelWorkspaceSel)

        self.verticalLayout_18.addWidget(self.extract1_title)

        self.extract1_content = QFrame(self.extract1)
        self.extract1_content.setObjectName(u"extract1_content")
        self.extract1_content.setMinimumSize(QSize(876, 50))
        self.extract1_content.setFrameShape(QFrame.StyledPanel)
        self.extract1_content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.extract1_content)
        self.horizontalLayout_12.setSpacing(6)
        self.horizontalLayout_12.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setSpacing(6)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.pushButtonWorkspaceSel = QPushButton(self.extract1_content)
        self.pushButtonWorkspaceSel.setObjectName(u"pushButtonWorkspaceSel")
        sizePolicy1.setHeightForWidth(self.pushButtonWorkspaceSel.sizePolicy().hasHeightForWidth())
        self.pushButtonWorkspaceSel.setSizePolicy(sizePolicy1)
        self.pushButtonWorkspaceSel.setMinimumSize(QSize(100, 30))
        self.pushButtonWorkspaceSel.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_19.addWidget(self.pushButtonWorkspaceSel)

        self.lineEditWorkspaceSel = QLineEdit(self.extract1_content)
        self.lineEditWorkspaceSel.setObjectName(u"lineEditWorkspaceSel")
        self.lineEditWorkspaceSel.setMinimumSize(QSize(0, 30))
        self.lineEditWorkspaceSel.setFont(font)
        self.lineEditWorkspaceSel.setReadOnly(False)
        self.lineEditWorkspaceSel.setClearButtonEnabled(True)

        self.horizontalLayout_19.addWidget(self.lineEditWorkspaceSel)

        self.horizontalLayout_12.addLayout(self.horizontalLayout_19)

        self.verticalLayout_18.addWidget(self.extract1_content)

        self.verticalLayout_17.addWidget(self.extract1)

        self.line_4 = QFrame(self.extractWidgets)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_17.addWidget(self.line_4)

        self.extract2 = QFrame(self.extractWidgets)
        self.extract2.setObjectName(u"extract2")
        self.extract2.setFrameShape(QFrame.StyledPanel)
        self.extract2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_20 = QVBoxLayout(self.extract2)
        self.verticalLayout_20.setSpacing(0)
        self.verticalLayout_20.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.extract2_title = QFrame(self.extract2)
        self.extract2_title.setObjectName(u"extract2_title")
        self.extract2_title.setFrameShape(QFrame.StyledPanel)
        self.extract2_title.setFrameShadow(QFrame.Raised)
        self.verticalLayout_21 = QVBoxLayout(self.extract2_title)
        self.verticalLayout_21.setSpacing(6)
        self.verticalLayout_21.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.labelWorkflowSelection = QLabel(self.extract2_title)
        self.labelWorkflowSelection.setObjectName(u"labelWorkflowSelection")

        self.verticalLayout_21.addWidget(self.labelWorkflowSelection)

        self.verticalLayout_20.addWidget(self.extract2_title)

        self.extract2_content = QFrame(self.extract2)
        self.extract2_content.setObjectName(u"extract2_content")
        self.extract2_content.setFrameShape(QFrame.StyledPanel)
        self.extract2_content.setFrameShadow(QFrame.Raised)
        self.verticalLayout_22 = QVBoxLayout(self.extract2_content)
        self.verticalLayout_22.setSpacing(6)
        self.verticalLayout_22.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.groupBox = QGroupBox(self.extract2_content)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy2)
        font1 = QFont()
        font1.setBold(True)
        self.groupBox.setFont(font1)
        self.groupBox.setStyleSheet(u"QGroupBox\n"
                                    "{\n"
                                    "    font-size: 12px;\n"
                                    "    font-weight: bold;\n"
                                    "}")
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(120, 20))
        self.label_4.setMaximumSize(QSize(120, 25))

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_14, 0, 3, 1, 1)

        self.comboBoxWorkflowSel = QComboBox(self.groupBox)
        self.comboBoxWorkflowSel.setObjectName(u"comboBoxWorkflowSel")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.comboBoxWorkflowSel.sizePolicy().hasHeightForWidth())
        self.comboBoxWorkflowSel.setSizePolicy(sizePolicy3)
        self.comboBoxWorkflowSel.setMinimumSize(QSize(250, 25))
        self.comboBoxWorkflowSel.setMaximumSize(QSize(100, 25))

        self.gridLayout_3.addWidget(self.comboBoxWorkflowSel, 0, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(120, 0))
        self.label_2.setMaximumSize(QSize(120, 16777215))

        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)

        self.lineEditPadding = QLineEdit(self.groupBox)
        self.lineEditPadding.setObjectName(u"lineEditPadding")
        self.lineEditPadding.setMinimumSize(QSize(50, 25))
        self.lineEditPadding.setMaximumSize(QSize(50, 25))

        self.gridLayout_3.addWidget(self.lineEditPadding, 2, 1, 1, 1)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSliderParalellization = QSlider(self.groupBox)
        self.horizontalSliderParalellization.setObjectName(u"horizontalSliderParalellization")
        self.horizontalSliderParalellization.setEnabled(True)
        self.horizontalSliderParalellization.setMinimumSize(QSize(120, 0))
        self.horizontalSliderParalellization.setMaximumSize(QSize(150, 16777215))
        self.horizontalSliderParalellization.setMinimum(1)
        self.horizontalSliderParalellization.setMaximum(6)
        self.horizontalSliderParalellization.setOrientation(Qt.Horizontal)
        self.horizontalSliderParalellization.setInvertedAppearance(False)
        self.horizontalSliderParalellization.setInvertedControls(False)
        self.horizontalSliderParalellization.setTickPosition(QSlider.TicksBelow)
        self.horizontalSliderParalellization.setTickInterval(1)

        self.horizontalLayout_3.addWidget(self.horizontalSliderParalellization)

        self.horizontalSpacer_10 = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_10)

        self.spinBoxParallelization = QSpinBox(self.groupBox)
        self.spinBoxParallelization.setObjectName(u"spinBoxParallelization")
        self.spinBoxParallelization.setMinimum(1)
        self.spinBoxParallelization.setMaximum(6)
        self.spinBoxParallelization.setValue(1)

        self.horizontalLayout_3.addWidget(self.spinBoxParallelization)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_8)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setSpacing(6)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy4)

        self.horizontalLayout_14.addWidget(self.label_6, 0, Qt.AlignHCenter)

        self.horizontalSpacer_7 = QSpacerItem(100, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_7)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setEnabled(True)

        self.horizontalLayout_14.addWidget(self.label_5, 0, Qt.AlignHCenter)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_9)

        self.verticalLayout_3.addLayout(self.horizontalLayout_14)

        self.gridLayout_3.addLayout(self.verticalLayout_3, 0, 5, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(80, 20))
        self.label_3.setMaximumSize(QSize(80, 100))

        self.gridLayout_3.addWidget(self.label_3, 0, 4, 1, 1)

        self.verticalLayout_22.addWidget(self.groupBox, 0, Qt.AlignLeft)

        self.groupBox_2 = QGroupBox(self.extract2_content)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setStyleSheet(u"QGroupBox\n"
                                      "{\n"
                                      "    font-size: 12px;\n"
                                      "    font-weight: bold;\n"
                                      "}")
        self.horizontalLayout_13 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_13.setSpacing(6)
        self.horizontalLayout_13.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setSpacing(6)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_8.addItem(self.horizontalSpacer_5, 0, 2, 1, 1)

        self.labelIconRunWorkflow = QLabel(self.groupBox_2)
        self.labelIconRunWorkflow.setObjectName(u"labelIconRunWorkflow")
        sizePolicy1.setHeightForWidth(self.labelIconRunWorkflow.sizePolicy().hasHeightForWidth())
        self.labelIconRunWorkflow.setSizePolicy(sizePolicy1)
        self.labelIconRunWorkflow.setMinimumSize(QSize(25, 25))
        self.labelIconRunWorkflow.setMaximumSize(QSize(25, 25))
        self.labelIconRunWorkflow.setPixmap(QPixmap(u":/icons/cil-x-circle.svg"))
        self.labelIconRunWorkflow.setScaledContents(True)

        self.gridLayout_8.addWidget(self.labelIconRunWorkflow, 0, 1, 1, 1)

        self.pushButtonRunWorkflow = QPushButton(self.groupBox_2)
        self.pushButtonRunWorkflow.setObjectName(u"pushButtonRunWorkflow")
        sizePolicy1.setHeightForWidth(self.pushButtonRunWorkflow.sizePolicy().hasHeightForWidth())
        self.pushButtonRunWorkflow.setSizePolicy(sizePolicy1)
        self.pushButtonRunWorkflow.setMinimumSize(QSize(130, 30))

        self.gridLayout_8.addWidget(self.pushButtonRunWorkflow, 0, 0, 1, 1)

        self.progressBarRunWorkflow = QProgressBar(self.groupBox_2)
        self.progressBarRunWorkflow.setObjectName(u"progressBarRunWorkflow")
        self.progressBarRunWorkflow.setMaximum(100)
        self.progressBarRunWorkflow.setValue(-1)

        self.gridLayout_8.addWidget(self.progressBarRunWorkflow, 0, 3, 1, 1)

        self.logsLabel = QLabel(self.groupBox_2)
        self.logsLabel.setObjectName(u"logsLabel")

        self.gridLayout_8.addWidget(self.logsLabel, 1, 0, 1, 1)

        self.plainTextEditWorkflowLogs = QPlainTextEdit(self.groupBox_2)
        self.plainTextEditWorkflowLogs.setObjectName(u"plainTextEditWorkflowLogs")
        self.plainTextEditWorkflowLogs.setReadOnly(True)

        self.gridLayout_8.addWidget(self.plainTextEditWorkflowLogs, 2, 0, 1, 4)

        self.horizontalLayout_13.addLayout(self.gridLayout_8)

        self.verticalLayout_22.addWidget(self.groupBox_2)

        self.verticalLayout_20.addWidget(self.extract2_content)

        self.verticalLayout_17.addWidget(self.extract2)

        self.horizontalLayout_11.addWidget(self.extractWidgets)

        icon5 = QIcon()
        icon5.addFile(u":/icons/cil-satelite.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.tabWidget.addTab(self.extractTab, icon5, "")
        self.editTab = QWidget()
        self.editTab.setObjectName(u"editTab")
        self.horizontalLayout_4 = QHBoxLayout(self.editTab)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.editWidgets = QWidget(self.editTab)
        self.editWidgets.setObjectName(u"editWidgets")
        sizePolicy.setHeightForWidth(self.editWidgets.sizePolicy().hasHeightForWidth())
        self.editWidgets.setSizePolicy(sizePolicy)
        self.verticalLayout_24 = QVBoxLayout(self.editWidgets)
        self.verticalLayout_24.setSpacing(6)
        self.verticalLayout_24.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.edit1 = QFrame(self.editWidgets)
        self.edit1.setObjectName(u"edit1")
        self.edit1.setFrameShape(QFrame.StyledPanel)
        self.edit1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_25 = QVBoxLayout(self.edit1)
        self.verticalLayout_25.setSpacing(0)
        self.verticalLayout_25.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.edit1_title = QFrame(self.edit1)
        self.edit1_title.setObjectName(u"edit1_title")
        self.edit1_title.setFrameShape(QFrame.StyledPanel)
        self.edit1_title.setFrameShadow(QFrame.Raised)
        self.verticalLayout_26 = QVBoxLayout(self.edit1_title)
        self.verticalLayout_26.setSpacing(6)
        self.verticalLayout_26.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.labelEditDescription = QLabel(self.edit1_title)
        self.labelEditDescription.setObjectName(u"labelEditDescription")

        self.verticalLayout_26.addWidget(self.labelEditDescription)

        self.verticalLayout_25.addWidget(self.edit1_title)

        self.edit1_content = QFrame(self.edit1)
        self.edit1_content.setObjectName(u"edit1_content")
        self.edit1_content.setMinimumSize(QSize(876, 50))
        self.edit1_content.setFrameShape(QFrame.StyledPanel)
        self.edit1_content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.edit1_content)
        self.horizontalLayout_15.setSpacing(6)
        self.horizontalLayout_15.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setSpacing(6)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.pushButtonViewEdit = QPushButton(self.edit1_content)
        self.pushButtonViewEdit.setObjectName(u"pushButtonViewEdit")
        sizePolicy1.setHeightForWidth(self.pushButtonViewEdit.sizePolicy().hasHeightForWidth())
        self.pushButtonViewEdit.setSizePolicy(sizePolicy1)
        self.pushButtonViewEdit.setMinimumSize(QSize(100, 30))

        self.horizontalLayout_16.addWidget(self.pushButtonViewEdit)

        self.lineEditViewEdit = QLineEdit(self.edit1_content)
        self.lineEditViewEdit.setObjectName(u"lineEditViewEdit")
        self.lineEditViewEdit.setMinimumSize(QSize(0, 30))

        self.horizontalLayout_16.addWidget(self.lineEditViewEdit)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_6)

        self.pushButtonViewEditImport = QPushButton(self.edit1_content)
        self.pushButtonViewEditImport.setObjectName(u"pushButtonViewEditImport")
        sizePolicy1.setHeightForWidth(self.pushButtonViewEditImport.sizePolicy().hasHeightForWidth())
        self.pushButtonViewEditImport.setSizePolicy(sizePolicy1)
        self.pushButtonViewEditImport.setMinimumSize(QSize(100, 30))

        self.horizontalLayout_16.addWidget(self.pushButtonViewEditImport)

        self.labelDBImport = QLabel(self.edit1_content)
        self.labelDBImport.setObjectName(u"labelDBImport")
        sizePolicy1.setHeightForWidth(self.labelDBImport.sizePolicy().hasHeightForWidth())
        self.labelDBImport.setSizePolicy(sizePolicy1)
        self.labelDBImport.setMinimumSize(QSize(25, 25))
        self.labelDBImport.setMaximumSize(QSize(25, 25))
        self.labelDBImport.setPixmap(QPixmap(u":/icons/cil-x-circle.svg"))
        self.labelDBImport.setScaledContents(True)

        self.horizontalLayout_16.addWidget(self.labelDBImport)

        self.horizontalLayout_15.addLayout(self.horizontalLayout_16)

        self.verticalLayout_25.addWidget(self.edit1_content)

        self.verticalLayout_24.addWidget(self.edit1)

        self.line_2 = QFrame(self.editWidgets)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_24.addWidget(self.line_2)

        # def setup_parent(binder):
        #     binder.bind(QWidget, to=self.editWidgets)

        # injector = Injector([setup_parent, WorkspaceModule])
        # self.viewEditDynFrame = injector.get(ViewEditWidget)
        self.viewEditDynFrame = ViewEditWidget(self.editWidgets)
        self.viewEditDynFrame.setObjectName(u"viewEditDynFrame")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.viewEditDynFrame.sizePolicy().hasHeightForWidth())
        self.viewEditDynFrame.setSizePolicy(sizePolicy5)
        self.horizontalLayout_5 = QHBoxLayout(self.viewEditDynFrame)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_24.addWidget(self.viewEditDynFrame)

        self.horizontalLayout_4.addWidget(self.editWidgets)

        icon6 = QIcon()
        icon6.addFile(u":/icons/cil-swap-horizontal.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.tabWidget.addTab(self.editTab, icon6, "")
        self.exportTab = QWidget()
        self.exportTab.setObjectName(u"exportTab")
        icon7 = QIcon()
        icon7.addFile(u":/icons/cil-save.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.tabWidget.addTab(self.exportTab, icon7, "")
        self.settingsTab = QWidget()
        self.settingsTab.setObjectName(u"settingsTab")
        self.horizontalLayout_17 = QHBoxLayout(self.settingsTab)
        self.horizontalLayout_17.setSpacing(6)
        self.horizontalLayout_17.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.settingsWidgets = QVBoxLayout()
        self.settingsWidgets.setSpacing(6)
        self.settingsWidgets.setObjectName(u"settingsWidgets")
        self.groupBox_4 = QGroupBox(self.settingsTab)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setStyleSheet(u"QGroupBox\n"
                                      "{\n"
                                      "    font-size: 12px;\n"
                                      "    font-weight: bold;\n"
                                      "}")
        self.horizontalLayout_20 = QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_20.setSpacing(6)
        self.horizontalLayout_20.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setSpacing(6)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.appThemeLabel = QLabel(self.groupBox_4)
        self.appThemeLabel.setObjectName(u"appThemeLabel")
        self.appThemeLabel.setMinimumSize(QSize(200, 0))

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.appThemeLabel)

        self.appThemeComboBox = QComboBox(self.groupBox_4)
        self.appThemeComboBox.setObjectName(u"appThemeComboBox")
        self.appThemeComboBox.setMinimumSize(QSize(200, 0))

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.appThemeComboBox)

        self.horizontalLayout_20.addLayout(self.formLayout_2)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_13)

        self.settingsWidgets.addWidget(self.groupBox_4)

        self.groupBox_3 = QGroupBox(self.settingsTab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setStyleSheet(u"QGroupBox\n"
                                      "{\n"
                                      "    font-size: 12px;\n"
                                      "    font-weight: bold;\n"
                                      "}")
        self.horizontalLayout_18 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_18.setSpacing(6)
        self.horizontalLayout_18.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.formLayout = QFormLayout()
        self.formLayout.setSpacing(6)
        self.formLayout.setObjectName(u"formLayout")
        self.similaritySortAlgorithmLabel = QLabel(self.groupBox_3)
        self.similaritySortAlgorithmLabel.setObjectName(u"similaritySortAlgorithmLabel")
        self.similaritySortAlgorithmLabel.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.similaritySortAlgorithmLabel)

        self.similaritySortAlgorithmComboBox = QComboBox(self.groupBox_3)
        self.similaritySortAlgorithmComboBox.setObjectName(u"similaritySortAlgorithmComboBox")
        self.similaritySortAlgorithmComboBox.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.similaritySortAlgorithmComboBox)

        self.autosaveLabel = QLabel(self.groupBox_3)
        self.autosaveLabel.setObjectName(u"autosaveLabel")
        self.autosaveLabel.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.autosaveLabel)

        self.autosaveCheckBox = QCheckBox(self.groupBox_3)
        self.autosaveCheckBox.setObjectName(u"autosaveCheckBox")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.autosaveCheckBox)

        self.tempStoreLabel = QLabel(self.groupBox_3)
        self.tempStoreLabel.setObjectName(u"tempStoreLabel")
        self.tempStoreLabel.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.tempStoreLabel)

        self.tempStoreComboBox = QComboBox(self.groupBox_3)
        self.tempStoreComboBox.setObjectName(u"tempStoreComboBox")
        self.tempStoreComboBox.setMinimumSize(QSize(200, 0))

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.tempStoreComboBox)

        self.horizontalLayout_18.addLayout(self.formLayout)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_12)

        self.settingsWidgets.addWidget(self.groupBox_3)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.settingsWidgets.addItem(self.verticalSpacer_2)

        self.horizontalLayout_17.addLayout(self.settingsWidgets)

        icon8 = QIcon()
        icon8.addFile(u":/icons/cil-settings.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.tabWidget.addTab(self.settingsTab, icon8, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(5)
        self.pushButtonWorkspaceSel.setDefault(False)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"WdB Glyph Extractor", None))
        self.labelSetupDescription.setText(QCoreApplication.translate("MainWindow",
                                                                      u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(1) Setup Docker </span></p><p><span style=\" font-size:10pt;\">Please install Docker on your system. This can be either done using:</span></p><p><span style=\" font-size:10pt;\">i. (recommended) Docker Desktop: </span><a href=\"https://docs.docker.com/desktop/install/windows-install/\"><span style=\" text-decoration: underline; color:#0000ff;\">Install Docker Desktop on Windows</span></a></p><p><span style=\" font-size:10pt;\">ii. Server and client binaries: </span><a href=\"https://docs.docker.com/engine/install/binaries/\"><span style=\" text-decoration: underline; color:#0000ff;\">Install server and client binaries on Windows</span></a></p></body></html>",
                                                                      None))
        self.labelDockerStatusMessage.setText(
            QCoreApplication.translate("MainWindow", u"No docker installation found!", None))
        self.labelDockerStatusImage.setText("")
        self.labelImagePullDescription.setText(QCoreApplication.translate("MainWindow",
                                                                          u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(2) Pull/Load Docker images</span></p><p><span style=\" font-size:10pt;\">The processing workflow for glyph extraction depends on services that are 'dockerized'. These services include (i) </span><span style=\" font-size:10pt; font-style:italic;\">OCR-D</span><span style=\" font-size:10pt;\"> and (ii) </span><span style=\" font-size:10pt; font-style:italic;\">Glyph classification and Out-of-Distribution detection using energy-based models. </span></p><p><span style=\" font-size:10pt;\">Please 'pull' (download) the service images from DockerHub or install them on your system using exported image files.</span></p></body></html>",
                                                                          None))
        self.labelDockerEBM.setText(
            QCoreApplication.translate("MainWindow", u"Classifier/Pruner (flojoko/glyphclassifier)", None))
        self.labelDockerOCRD.setText(QCoreApplication.translate("MainWindow", u"OCR-D (flojoko/ocrd)", None))
        self.pushButtonDockerOCRDRemote.setText(QCoreApplication.translate("MainWindow", u"Pull Remote", None))
        self.pushButtonDockerEBMRemote.setText(QCoreApplication.translate("MainWindow", u"Pull Remote", None))
        self.labelDockerOCRDStatus.setText("")
        self.labelDockerEBMStatus.setText("")
        self.pushButtonDockerOCRDLocal.setText(QCoreApplication.translate("MainWindow", u"Open Local", None))
        self.pushButtonDockerEBMLocal.setText(QCoreApplication.translate("MainWindow", u"Open Local", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.setupTab),
                                  QCoreApplication.translate("MainWindow", u"Setup", None))
        self.labelDataSel.setText(QCoreApplication.translate("MainWindow",
                                                             u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(1) Select data directory</span></p><p><span style=\" font-size:10pt;\">Please choose a local directory on your machine with image material that you want to process.</span></p></body></html>",
                                                             None))
        # if QT_CONFIG(tooltip)
        self.lineEditDataSel.setToolTip(QCoreApplication.translate("MainWindow",
                                                                   u"<html><head/><body><p><span style=\" font-size:10pt;\">- The directory is allowed to have nested folders and will be searched recursively. </span></p><p><span style=\" font-size:10pt;\">- All data within the directory will be assigned to a dedicated workspace. Please structure your image material accordingly.</span></p></body></html>",
                                                                   None))
        # endif // QT_CONFIG(tooltip)
        self.lineEditDataSel.setPlaceholderText(
            QCoreApplication.translate("MainWindow", u"Select data directory", None))
        self.pushButtonDataSel.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.labelWSPrep.setText(QCoreApplication.translate("MainWindow",
                                                            u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(2) Import settings</span></p></body></html>",
                                                            None))
        # if QT_CONFIG(tooltip)
        self.groupBoxWSSep.setToolTip(QCoreApplication.translate("MainWindow",
                                                                 u"<html><head/><body><p><span style=\" font-weight:400;\"><br/>Some steps in the processing workflow might fail if your local resources do not meet the hardware requirements. </span></p><p><span style=\" font-weight:400;\">Some problems can be alleviated by workflow parallelization where the data is separate into several chunks each processed individually. </span></p></body></html>",
                                                                 None))
        # endif // QT_CONFIG(tooltip)
        self.groupBoxWSSep.setTitle(QCoreApplication.translate("MainWindow", u"Workspace parallelization", None))
        # if QT_CONFIG(tooltip)
        self.radioButtonImportNone.setToolTip(QCoreApplication.translate("MainWindow",
                                                                         u"<html><head/><body><p>The workspace is initiated at the root level with no parallelization options during the subsequent extraction steps. </p></body></html>",
                                                                         None))
        # endif // QT_CONFIG(tooltip)
        self.radioButtonImportNone.setText(QCoreApplication.translate("MainWindow", u"None", None))
        # if QT_CONFIG(tooltip)
        self.radioButtonImportBatchSize.setToolTip(QCoreApplication.translate("MainWindow",
                                                                              u"<html><head/><body><p>The numer of images that are assigned to each sub-workspace/subset. This does NOT copy the data but uses symlinks (soft references) to the data. </p></body></html>",
                                                                              None))
        # endif // QT_CONFIG(tooltip)
        self.radioButtonImportBatchSize.setText(QCoreApplication.translate("MainWindow", u"Subset size", None))
        self.groupBoxWSOpts.setTitle(QCoreApplication.translate("MainWindow", u"Data format", None))
        # if QT_CONFIG(tooltip)
        self.checkBoxNoNumIDs.setToolTip(QCoreApplication.translate("MainWindow",
                                                                    u"<html><head/><body><p>Rename the files in ascending numerical order.</p></body></html>",
                                                                    None))
        # endif // QT_CONFIG(tooltip)
        self.checkBoxNoNumIDs.setText(QCoreApplication.translate("MainWindow", u"Numerical IDs", None))
        # if QT_CONFIG(tooltip)
        self.checkBoxConvert.setToolTip(QCoreApplication.translate("MainWindow",
                                                                   u"<html><head/><body><p>Automatically convert PDF data.</p></body></html>",
                                                                   None))
        # endif // QT_CONFIG(tooltip)
        self.checkBoxConvert.setText(QCoreApplication.translate("MainWindow", u"Auto Convert", None))
        # if QT_CONFIG(tooltip)
        self.label_8.setToolTip(
            QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Specify the import DPI</p></body></html>",
                                       None))
        # endif // QT_CONFIG(tooltip)
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"DPI", None))
        self.lineEditDPI.setText("")
        self.lineEditDPI.setPlaceholderText(QCoreApplication.translate("MainWindow", u"300", None))
        self.label.setText(QCoreApplication.translate("MainWindow",
                                                      u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(3) Create workspace</span></p><p>Create the workspace which populates a .mets file which keeps tracks of all data, its location, and the processing. </p></body></html>",
                                                      None))
        self.labelImportDescription.setText("")
        self.labelIconImport.setText("")
        self.pushButtonImport.setText(QCoreApplication.translate("MainWindow", u"Create Workspace", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Logs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.importTab),
                                  QCoreApplication.translate("MainWindow", u"Import", None))
        self.labelWorkspaceSel.setText(QCoreApplication.translate("MainWindow",
                                                                  u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(1) Select workspace</span></p><p><span style=\" font-size:10pt;\">Please select the workspace you would like to process.</span></p></body></html>",
                                                                  None))
        self.pushButtonWorkspaceSel.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        # if QT_CONFIG(tooltip)
        self.lineEditWorkspaceSel.setToolTip(QCoreApplication.translate("MainWindow",
                                                                        u"<html><head/><body><p>The workspace must contain a valid .mets file comptabile with the OCR-D ecosystem.</p></body></html>",
                                                                        None))
        # endif // QT_CONFIG(tooltip)
        self.lineEditWorkspaceSel.setText("")
        self.lineEditWorkspaceSel.setPlaceholderText(
            QCoreApplication.translate("MainWindow", u"Select workspace directory", None))
        self.labelWorkflowSelection.setText(QCoreApplication.translate("MainWindow",
                                                                       u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(2) Run workflow and classify/prune glyph images</span></p><p><span style=\" font-size:10pt;\">Please select a processing workflow you would like to apply to all images in the current workspace. </span></p><p><span style=\" font-size:10pt;\">If the workflow contains a glyph extraction step, the glyphs are automatically categorized and outliers are marked.</span></p></body></html>",
                                                                       None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Extraction workflow ", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Glyph padding [px]", None))
        self.lineEditPadding.setText(QCoreApplication.translate("MainWindow", u"10", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"6", None))
        # if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("MainWindow",
                                                           u"<html><head/><body><p>Specify the number of workers that process the task concurrently. </p><p><br/></p><p>This has no effect if the workspace was not parallelized during the import stage.</p></body></html>",
                                                           None))
        # endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Parallelization", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Execution", None))
        self.labelIconRunWorkflow.setText("")
        self.pushButtonRunWorkflow.setText(QCoreApplication.translate("MainWindow", u"Run extraction", None))
        self.logsLabel.setText(QCoreApplication.translate("MainWindow", u"Logs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.extractTab),
                                  QCoreApplication.translate("MainWindow", u"Extract/Prune", None))
        self.labelEditDescription.setText(QCoreApplication.translate("MainWindow",
                                                                     u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(1) Select workspace</span></p><p><span style=\" font-size:10pt;\">Please select the workspace you would like to view and edit.</span></p></body></html>",
                                                                     None))
        self.pushButtonViewEdit.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.lineEditViewEdit.setPlaceholderText(
            QCoreApplication.translate("MainWindow", u"Select workspace directory", None))
        self.pushButtonViewEditImport.setText(QCoreApplication.translate("MainWindow", u"Load/Reload", None))
        self.labelDBImport.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.editTab),
                                  QCoreApplication.translate("MainWindow", u"View/Edit", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.exportTab),
                                  QCoreApplication.translate("MainWindow", u"Export", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"General Options", None))
        self.appThemeLabel.setText(QCoreApplication.translate("MainWindow", u"App theme", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"View/Edit Options", None))
        self.similaritySortAlgorithmLabel.setText(
            QCoreApplication.translate("MainWindow", u"Similarity sorting algorithm", None))
        self.autosaveLabel.setText(QCoreApplication.translate("MainWindow", u"Autosave workspace", None))
        self.tempStoreLabel.setText(QCoreApplication.translate("MainWindow", u"Database temporary storage", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab),
                                  QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi
