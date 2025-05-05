# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vieweditwidgetYbVqIi.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from widgets.imagescaleselector import ImageScaleSelector
from widgets.viewedit.labels.labels_view import LabelsTreeView
from widgets.viewedit.glyphs.glyphs_view import GlyphsListView


class Ui_EditWidget(object):
    def setupUi(self, EditWidget):
        if not EditWidget.objectName():
            EditWidget.setObjectName(u"EditWidget")
        EditWidget.resize(1232, 1036)
        self.verticalLayout = QVBoxLayout(EditWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolbarFrame = QFrame(EditWidget)
        self.toolbarFrame.setObjectName(u"toolbarFrame")
        self.toolbarFrame.setMaximumSize(QSize(16777215, 140))
        self.toolbarFrame.setFrameShape(QFrame.StyledPanel)
        self.toolbarFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.toolbarFrame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolsFrame = QFrame(self.toolbarFrame)
        self.toolsFrame.setObjectName(u"toolsFrame")
        self.toolsFrame.setMinimumSize(QSize(0, 140))
        self.toolsFrame.setFrameShape(QFrame.StyledPanel)
        self.toolsFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.toolsFrame)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox_2 = QGroupBox(self.toolsFrame)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QSize(158, 66))
        self.groupBox_2.setMaximumSize(QSize(158, 66))
        self.groupBox_2.setStyleSheet(u"QGroupBox\n"
"{\n"
"    font-size: 12px;\n"
"    font-weight: bold;\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButtonZoomIn = QPushButton(self.groupBox_2)
        self.pushButtonZoomIn.setObjectName(u"pushButtonZoomIn")
        self.pushButtonZoomIn.setMaximumSize(QSize(40, 28))
        icon = QIcon()
        icon.addFile(u":/icons/cil-zoom-in.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonZoomIn.setIcon(icon)
        self.pushButtonZoomIn.setIconSize(QSize(20, 20))

        self.horizontalLayout_3.addWidget(self.pushButtonZoomIn)

        self.pushButtonZoomOut = QPushButton(self.groupBox_2)
        self.pushButtonZoomOut.setObjectName(u"pushButtonZoomOut")
        self.pushButtonZoomOut.setMaximumSize(QSize(40, 28))
        icon1 = QIcon()
        icon1.addFile(u":/icons/cil-zoom-out.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonZoomOut.setIcon(icon1)
        self.pushButtonZoomOut.setIconSize(QSize(20, 20))

        self.horizontalLayout_3.addWidget(self.pushButtonZoomOut)

        self.comboBoxZoom = ImageScaleSelector(self.groupBox_2)
        self.comboBoxZoom.setObjectName(u"comboBoxZoom")
        self.comboBoxZoom.setMinimumSize(QSize(60, 28))
        self.comboBoxZoom.setMaximumSize(QSize(60, 28))

        self.horizontalLayout_3.addWidget(self.comboBoxZoom)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.verticalLayout_5.addWidget(self.groupBox_2)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)


        self.horizontalLayout_5.addLayout(self.verticalLayout_5)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_3 = QGroupBox(self.toolsFrame)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMinimumSize(QSize(81, 66))
        self.groupBox_3.setMaximumSize(QSize(81, 66))
        self.groupBox_3.setStyleSheet(u"QGroupBox\n"
"{\n"
"    font-size: 12px;\n"
"    font-weight: bold;\n"
"}")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEditImageCrop = QLineEdit(self.groupBox_3)
        self.lineEditImageCrop.setObjectName(u"lineEditImageCrop")
        self.lineEditImageCrop.setMinimumSize(QSize(40, 28))
        self.lineEditImageCrop.setMaximumSize(QSize(40, 28))
        self.lineEditImageCrop.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.lineEditImageCrop)

        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.verticalLayout_4.addWidget(self.groupBox_3)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)


        self.horizontalLayout_5.addLayout(self.verticalLayout_4)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBox = QGroupBox(self.toolsFrame)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(167, 110))
        self.groupBox.setMaximumSize(QSize(167, 110))
        self.groupBox.setStyleSheet(u"QGroupBox\n"
"{\n"
"    font-size: 12px;\n"
"    font-weight: bold;\n"
"}")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lineEditMinWidth = QLineEdit(self.groupBox)
        self.lineEditMinWidth.setObjectName(u"lineEditMinWidth")
        self.lineEditMinWidth.setMinimumSize(QSize(40, 28))
        self.lineEditMinWidth.setMaximumSize(QSize(40, 28))
        self.lineEditMinWidth.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.lineEditMinWidth, 2, 2, 1, 1)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMaximumSize(QSize(16777215, 28))
        self.label_6.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.label_6, 3, 2, 1, 1)

        self.lineEditMinHeight = QLineEdit(self.groupBox)
        self.lineEditMinHeight.setObjectName(u"lineEditMinHeight")
        self.lineEditMinHeight.setMinimumSize(QSize(40, 28))
        self.lineEditMinHeight.setMaximumSize(QSize(40, 28))
        self.lineEditMinHeight.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.lineEditMinHeight, 0, 2, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 2, 4, 1, 1)

        self.lineEditMaxWidth = QLineEdit(self.groupBox)
        self.lineEditMaxWidth.setObjectName(u"lineEditMaxWidth")
        self.lineEditMaxWidth.setMinimumSize(QSize(40, 28))
        self.lineEditMaxWidth.setMaximumSize(QSize(40, 28))
        self.lineEditMaxWidth.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.lineEditMaxWidth, 2, 3, 1, 1)

        self.lineEditMaxHeight = QLineEdit(self.groupBox)
        self.lineEditMaxHeight.setObjectName(u"lineEditMaxHeight")
        self.lineEditMaxHeight.setMinimumSize(QSize(40, 28))
        self.lineEditMaxHeight.setMaximumSize(QSize(40, 28))
        self.lineEditMaxHeight.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.lineEditMaxHeight, 0, 3, 1, 1)

        self.label_11 = QLabel(self.groupBox)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMaximumSize(QSize(16777215, 28))
        self.label_11.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.label_11, 3, 3, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 4, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 0, 1, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 2, 1, 1, 1)


        self.verticalLayout_6.addWidget(self.groupBox)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_3)


        self.horizontalLayout_5.addLayout(self.verticalLayout_6)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_5)


        self.horizontalLayout.addWidget(self.toolsFrame)


        self.verticalLayout.addWidget(self.toolbarFrame)

        self.workFrame = QFrame(EditWidget)
        self.workFrame.setObjectName(u"workFrame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.workFrame.sizePolicy().hasHeightForWidth())
        self.workFrame.setSizePolicy(sizePolicy1)
        self.workFrame.setFrameShape(QFrame.StyledPanel)
        self.workFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.workFrame)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.workSplitter = QSplitter(self.workFrame)
        self.workSplitter.setObjectName(u"workSplitter")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.workSplitter.sizePolicy().hasHeightForWidth())
        self.workSplitter.setSizePolicy(sizePolicy2)
        self.workSplitter.setMinimumSize(QSize(0, 407))
        self.workSplitter.setOrientation(Qt.Horizontal)
        self.workSplitter.setHandleWidth(5)
        self.verticalLayoutWidget = QWidget(self.workSplitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout_12 = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.treeViewLabels = LabelsTreeView(self.verticalLayoutWidget)
        self.treeViewLabels.setObjectName(u"treeViewLabels")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.treeViewLabels.sizePolicy().hasHeightForWidth())
        self.treeViewLabels.setSizePolicy(sizePolicy3)
        self.treeViewLabels.setFrameShadow(QFrame.Sunken)
        self.treeViewLabels.setLineWidth(1)

        self.verticalLayout_12.addWidget(self.treeViewLabels)

        self.treeViewLabelsToolbar = QFrame(self.verticalLayoutWidget)
        self.treeViewLabelsToolbar.setObjectName(u"treeViewLabelsToolbar")
        self.treeViewLabelsToolbar.setEnabled(True)
        self.treeViewLabelsToolbar.setFrameShape(QFrame.StyledPanel)
        self.treeViewLabelsToolbar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.treeViewLabelsToolbar)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(1, 1, 1, 1)
        self.pushButton = QPushButton(self.treeViewLabelsToolbar)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_6.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.treeViewLabelsToolbar)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_6.addWidget(self.pushButton_2)


        self.verticalLayout_12.addWidget(self.treeViewLabelsToolbar)

        self.workSplitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget_3 = QWidget(self.workSplitter)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayout_13 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.listViewGlyphs = GlyphsListView(self.verticalLayoutWidget_3)
        self.listViewGlyphs.setObjectName(u"listViewGlyphs")
        self.listViewGlyphs.setFrameShadow(QFrame.Sunken)
        self.listViewGlyphs.setLineWidth(1)

        self.verticalLayout_13.addWidget(self.listViewGlyphs)

        self.listViewGlyphsToolbar = QFrame(self.verticalLayoutWidget_3)
        self.listViewGlyphsToolbar.setObjectName(u"listViewGlyphsToolbar")
        self.listViewGlyphsToolbar.setFrameShape(QFrame.StyledPanel)
        self.listViewGlyphsToolbar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.listViewGlyphsToolbar)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(1, 1, 1, 1)
        self.label_7 = QLabel(self.listViewGlyphsToolbar)
        self.label_7.setObjectName(u"label_7")
        sizePolicy4 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy4)

        self.horizontalLayout_8.addWidget(self.label_7)

        self.comboBoxSortingStrategy = QComboBox(self.listViewGlyphsToolbar)
        self.comboBoxSortingStrategy.setObjectName(u"comboBoxSortingStrategy")

        self.horizontalLayout_8.addWidget(self.comboBoxSortingStrategy)

        self.checkBoxSortingStrategy = QCheckBox(self.listViewGlyphsToolbar)
        self.checkBoxSortingStrategy.setObjectName(u"checkBoxSortingStrategy")

        self.horizontalLayout_8.addWidget(self.checkBoxSortingStrategy)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_3)

        self.pushButtonCommitChanges = QPushButton(self.listViewGlyphsToolbar)
        self.pushButtonCommitChanges.setObjectName(u"pushButtonCommitChanges")
        self.pushButtonCommitChanges.setEnabled(True)
        self.pushButtonCommitChanges.setStyleSheet(u"QPushButton{ \n"
"	/*display: flex;*/\n"
"	height: 25px;\n"
"	padding: 2 8 2 8;\n"
"	background: #3373C4;\n"
"	border: 1px solid #03254c;\n"
"	outline: none;\n"
"	border-radius: 6px;\n"
"	/*overflow: hidden;*/\n"
"	/* font-family: \"Quicksand\", sans-serif;*/\n"
"	font-size: 14px;\n"
"	font-weight: 600;\n"
"	color: white;\n"
"	/*cursor: pointer;*/\n"
"	qproperty-icon: url(\":/icons/cil-data-transfer-down.svg\");\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background: #5494DA;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"background: #73B9EE;\n"
"}\n"
"\n"
"QPushButton:disabled\n"
"{\n"
"background-color: #d7d6d5;\n"
"border-color: #d7d6d5;\n"
"color: #5d5b59;\n"
"}\n"
"\n"
"\n"
"")

        self.horizontalLayout_8.addWidget(self.pushButtonCommitChanges)

        self.labelCommitChanges = QLabel(self.listViewGlyphsToolbar)
        self.labelCommitChanges.setObjectName(u"labelCommitChanges")

        self.horizontalLayout_8.addWidget(self.labelCommitChanges)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)

        self.listViewGlyphsInfo = QLabel(self.listViewGlyphsToolbar)
        self.listViewGlyphsInfo.setObjectName(u"listViewGlyphsInfo")

        self.horizontalLayout_8.addWidget(self.listViewGlyphsInfo)


        self.verticalLayout_13.addWidget(self.listViewGlyphsToolbar)

        self.workSplitter.addWidget(self.verticalLayoutWidget_3)

        self.horizontalLayout_7.addWidget(self.workSplitter)


        self.verticalLayout.addWidget(self.workFrame)


        self.retranslateUi(EditWidget)

        QMetaObject.connectSlotsByName(EditWidget)
    # setupUi

    def retranslateUi(self, EditWidget):
        EditWidget.setWindowTitle(QCoreApplication.translate("EditWidget", u"Test", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("EditWidget", u"Image scale", None))
        self.pushButtonZoomIn.setText("")
        self.pushButtonZoomOut.setText("")
#if QT_CONFIG(shortcut)
        self.pushButtonZoomOut.setShortcut("")
#endif // QT_CONFIG(shortcut)
        self.groupBox_3.setTitle(QCoreApplication.translate("EditWidget", u"Image crop", None))
        self.label.setText(QCoreApplication.translate("EditWidget", u"px", None))
        self.groupBox.setTitle(QCoreApplication.translate("EditWidget", u"Filter by size", None))
        self.label_6.setText(QCoreApplication.translate("EditWidget", u"min", None))
        self.label_4.setText(QCoreApplication.translate("EditWidget", u"px", None))
        self.label_11.setText(QCoreApplication.translate("EditWidget", u"max", None))
        self.label_2.setText(QCoreApplication.translate("EditWidget", u"px", None))
        self.label_3.setText(QCoreApplication.translate("EditWidget", u"Height", None))
        self.label_5.setText(QCoreApplication.translate("EditWidget", u"Width", None))
        self.pushButton.setText(QCoreApplication.translate("EditWidget", u"PushButton", None))
        self.pushButton_2.setText(QCoreApplication.translate("EditWidget", u"PushButton", None))
        self.label_7.setText(QCoreApplication.translate("EditWidget", u"Sort by", None))
        self.checkBoxSortingStrategy.setText(QCoreApplication.translate("EditWidget", u"Ascending", None))
        self.pushButtonCommitChanges.setText(QCoreApplication.translate("EditWidget", u"Commit Changes", None))
        self.labelCommitChanges.setText("")
        self.listViewGlyphsInfo.setText("")
    # retranslateUi

