# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'glyphlocatorwidgetMInLOP.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from widgets.viewedit.glyph_locator.zoomablegraphicsview import ZoomableGraphicsView

import resources_rc

class Ui_GlyphLocatorWidget(object):
    def setupUi(self, GlyphLocatorWidget):
        if not GlyphLocatorWidget.objectName():
            GlyphLocatorWidget.setObjectName(u"GlyphLocatorWidget")
        GlyphLocatorWidget.resize(640, 480)
        GlyphLocatorWidget.setMinimumSize(QSize(640, 480))
        icon = QIcon()
        icon.addFile(u":/resources/icons/cil-search.svg", QSize(), QIcon.Normal, QIcon.Off)
        GlyphLocatorWidget.setWindowIcon(icon)
        self.verticalLayout_2 = QVBoxLayout(GlyphLocatorWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(GlyphLocatorWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.groupBox_2 = QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setStyleSheet(u"QGroupBox {\n"
"    font: bold;\n"
"    border: 1px solid silver;\n"
"    border-radius: 6px;\n"
"    margin-top: 10px;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 7px;\n"
"    padding: 0px 5px 0px 5px;\n"
"}")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.overviewGraphicsView = ZoomableGraphicsView(self.groupBox_2)
        self.overviewGraphicsView.setObjectName(u"overviewGraphicsView")
        self.overviewGraphicsView.setMinimumSize(QSize(300, 0))

        self.verticalLayout_3.addWidget(self.overviewGraphicsView)

        self.splitter.addWidget(self.groupBox_2)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_3 = QGroupBox(self.widget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setStyleSheet(u"QGroupBox {\n"
"    font: bold;\n"
"    border: 1px solid silver;\n"
"    border-radius: 6px;\n"
"    margin-top: 10px;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 7px;\n"
"    padding: 0px 5px 0px 5px;\n"
"}")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.roiGraphicsView = ZoomableGraphicsView(self.groupBox_3)
        self.roiGraphicsView.setObjectName(u"roiGraphicsView")

        self.verticalLayout_4.addWidget(self.roiGraphicsView)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.groupBox = QGroupBox(self.widget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet(u"QGroupBox {\n"
"    font: bold;\n"
"    border: 1px solid silver;\n"
"    border-radius: 6px;\n"
"    margin-top: 10px;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 7px;\n"
"    padding: 0px 5px 0px 5px;\n"
"}")
        self.formLayout_2 = QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setBold(False)
        font.setUnderline(True)
        font.setKerning(True)
        self.label.setFont(font)

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label)

        self.label_imageDir = QLabel(self.groupBox)
        self.label_imageDir.setObjectName(u"label_imageDir")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.label_imageDir)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        font1 = QFont()
        font1.setBold(False)
        font1.setUnderline(True)
        self.label_4.setFont(font1)
        self.label_4.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.label_filename = QLabel(self.groupBox)
        self.label_filename.setObjectName(u"label_filename")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.label_filename)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font1)

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_5)

        self.label_glyphID = QLabel(self.groupBox)
        self.label_glyphID.setObjectName(u"label_glyphID")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.label_glyphID)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        font2 = QFont()
        font2.setUnderline(True)
        self.label_7.setFont(font2)

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_7)

        self.label_glyphLabel = QLabel(self.groupBox)
        self.label_glyphLabel.setObjectName(u"label_glyphLabel")

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.label_glyphLabel)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font2)

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_9)

        self.label_BBox = QLabel(self.groupBox)
        self.label_BBox.setObjectName(u"label_BBox")

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.label_BBox)

        self.label_11 = QLabel(self.groupBox)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font2)
        self.label_11.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.label_11)

        self.label_heightWidth = QLabel(self.groupBox)
        self.label_heightWidth.setObjectName(u"label_heightWidth")

        self.formLayout_2.setWidget(5, QFormLayout.FieldRole, self.label_heightWidth)


        self.verticalLayout.addWidget(self.groupBox)

        self.splitter.addWidget(self.widget)

        self.verticalLayout_2.addWidget(self.splitter)


        self.retranslateUi(GlyphLocatorWidget)

        QMetaObject.connectSlotsByName(GlyphLocatorWidget)
    # setupUi

    def retranslateUi(self, GlyphLocatorWidget):
        GlyphLocatorWidget.setWindowTitle(QCoreApplication.translate("GlyphLocatorWidget", u"Form", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("GlyphLocatorWidget", u"Overview", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("GlyphLocatorWidget", u"Region of Interest", None))
        self.groupBox.setTitle(QCoreApplication.translate("GlyphLocatorWidget", u"Glyph Details", None))
        self.label.setText(QCoreApplication.translate("GlyphLocatorWidget", u"Image folder", None))
        self.label_imageDir.setText(QCoreApplication.translate("GlyphLocatorWidget", u"TextLabel", None))
        self.label_4.setText(QCoreApplication.translate("GlyphLocatorWidget", u"File name", None))
        self.label_filename.setText(QCoreApplication.translate("GlyphLocatorWidget", u"TextLabel", None))
        self.label_5.setText(QCoreApplication.translate("GlyphLocatorWidget", u"Glyph ID", None))
        self.label_glyphID.setText(QCoreApplication.translate("GlyphLocatorWidget", u"TextLabel", None))
        self.label_7.setText(QCoreApplication.translate("GlyphLocatorWidget", u"Glyph label", None))
        self.label_glyphLabel.setText(QCoreApplication.translate("GlyphLocatorWidget", u"TextLabel", None))
        self.label_9.setText(QCoreApplication.translate("GlyphLocatorWidget", u"Bounding box", None))
        self.label_BBox.setText(QCoreApplication.translate("GlyphLocatorWidget", u"TextLabel", None))
        self.label_11.setText(QCoreApplication.translate("GlyphLocatorWidget", u"Height / Width", None))
        self.label_heightWidth.setText(QCoreApplication.translate("GlyphLocatorWidget", u"TextLabel", None))
    # retranslateUi

