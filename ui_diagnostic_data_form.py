# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'diagnostic_data_form.ui'
#
# Created: Mon Mar 11 16:47:29 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DiagnosticDataForm(object):
    def setupUi(self, DiagnosticDataForm):
        DiagnosticDataForm.setObjectName(_fromUtf8("DiagnosticDataForm"))
        DiagnosticDataForm.resize(380, 335)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/meta.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DiagnosticDataForm.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(DiagnosticDataForm)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.two_by_two_table = QtGui.QTableWidget(DiagnosticDataForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.two_by_two_table.sizePolicy().hasHeightForWidth())
        self.two_by_two_table.setSizePolicy(sizePolicy)
        self.two_by_two_table.setMinimumSize(QtCore.QSize(356, 111))
        self.two_by_two_table.setMaximumSize(QtCore.QSize(356, 111))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        self.two_by_two_table.setFont(font)
        self.two_by_two_table.setFrameShape(QtGui.QFrame.NoFrame)
        self.two_by_two_table.setFrameShadow(QtGui.QFrame.Plain)
        self.two_by_two_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.two_by_two_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.two_by_two_table.setAlternatingRowColors(True)
        self.two_by_two_table.setGridStyle(QtCore.Qt.DashLine)
        self.two_by_two_table.setRowCount(3)
        self.two_by_two_table.setColumnCount(3)
        self.two_by_two_table.setObjectName(_fromUtf8("two_by_two_table"))
        item = QtGui.QTableWidgetItem()
        self.two_by_two_table.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.two_by_two_table.setVerticalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.two_by_two_table.setVerticalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.two_by_two_table.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.two_by_two_table.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.two_by_two_table.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.two_by_two_table)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.prevalence_lbl = QtGui.QLabel(DiagnosticDataForm)
        self.prevalence_lbl.setObjectName(_fromUtf8("prevalence_lbl"))
        self.horizontalLayout_3.addWidget(self.prevalence_lbl)
        self.prevalence_txt_box = QtGui.QLineEdit(DiagnosticDataForm)
        self.prevalence_txt_box.setMinimumSize(QtCore.QSize(75, 0))
        self.prevalence_txt_box.setMaximumSize(QtCore.QSize(75, 16777215))
        self.prevalence_txt_box.setObjectName(_fromUtf8("prevalence_txt_box"))
        self.horizontalLayout_3.addWidget(self.prevalence_txt_box)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.startover_Btn = QtGui.QPushButton(DiagnosticDataForm)
        self.startover_Btn.setObjectName(_fromUtf8("startover_Btn"))
        self.horizontalLayout_3.addWidget(self.startover_Btn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_13 = QtGui.QLabel(DiagnosticDataForm)
        self.label_13.setMinimumSize(QtCore.QSize(50, 0))
        self.label_13.setMaximumSize(QtCore.QSize(50, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        self.label_13.setFont(font)
        self.label_13.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_2.addWidget(self.label_13)
        self.effect_cbo_box = QtGui.QComboBox(DiagnosticDataForm)
        self.effect_cbo_box.setMinimumSize(QtCore.QSize(100, 20))
        self.effect_cbo_box.setMaximumSize(QtCore.QSize(76, 20))
        self.effect_cbo_box.setObjectName(_fromUtf8("effect_cbo_box"))
        self.horizontalLayout_2.addWidget(self.effect_cbo_box)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_14 = QtGui.QLabel(DiagnosticDataForm)
        self.label_14.setMinimumSize(QtCore.QSize(0, 20))
        self.label_14.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        self.label_14.setFont(font)
        self.label_14.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout.addWidget(self.label_14, 0, 0, 1, 1)
        self.effect_txt_box = QtGui.QLineEdit(DiagnosticDataForm)
        self.effect_txt_box.setMinimumSize(QtCore.QSize(50, 22))
        self.effect_txt_box.setMaximumSize(QtCore.QSize(50, 22))
        self.effect_txt_box.setObjectName(_fromUtf8("effect_txt_box"))
        self.gridLayout.addWidget(self.effect_txt_box, 0, 1, 1, 1)
        self.label_15 = QtGui.QLabel(DiagnosticDataForm)
        self.label_15.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        self.label_15.setFont(font)
        self.label_15.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout.addWidget(self.label_15, 0, 2, 1, 1)
        self.low_txt_box = QtGui.QLineEdit(DiagnosticDataForm)
        self.low_txt_box.setMinimumSize(QtCore.QSize(50, 22))
        self.low_txt_box.setMaximumSize(QtCore.QSize(50, 22))
        self.low_txt_box.setObjectName(_fromUtf8("low_txt_box"))
        self.gridLayout.addWidget(self.low_txt_box, 0, 3, 1, 1)
        self.label_16 = QtGui.QLabel(DiagnosticDataForm)
        self.label_16.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        self.label_16.setFont(font)
        self.label_16.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout.addWidget(self.label_16, 0, 4, 1, 1)
        self.high_txt_box = QtGui.QLineEdit(DiagnosticDataForm)
        self.high_txt_box.setMinimumSize(QtCore.QSize(50, 22))
        self.high_txt_box.setMaximumSize(QtCore.QSize(50, 22))
        self.high_txt_box.setObjectName(_fromUtf8("high_txt_box"))
        self.gridLayout.addWidget(self.high_txt_box, 0, 5, 1, 1)
        self.se_lbl = QtGui.QLabel(DiagnosticDataForm)
        self.se_lbl.setObjectName(_fromUtf8("se_lbl"))
        self.gridLayout.addWidget(self.se_lbl, 0, 6, 1, 1)
        self.se_txt_box = QtGui.QLineEdit(DiagnosticDataForm)
        self.se_txt_box.setMinimumSize(QtCore.QSize(50, 22))
        self.se_txt_box.setMaximumSize(QtCore.QSize(50, 22))
        self.se_txt_box.setObjectName(_fromUtf8("se_txt_box"))
        self.gridLayout.addWidget(self.se_txt_box, 0, 7, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(DiagnosticDataForm)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.alpha_edit = QtGui.QLineEdit(DiagnosticDataForm)
        self.alpha_edit.setMaximumSize(QtCore.QSize(30, 16777215))
        self.alpha_edit.setText(_fromUtf8(""))
        self.alpha_edit.setObjectName(_fromUtf8("alpha_edit"))
        self.horizontalLayout.addWidget(self.alpha_edit)
        self.ci_label = QtGui.QLabel(DiagnosticDataForm)
        self.ci_label.setObjectName(_fromUtf8("ci_label"))
        self.horizontalLayout.addWidget(self.ci_label)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.inconsistencyLabel = QtGui.QLabel(DiagnosticDataForm)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.inconsistencyLabel.setFont(font)
        self.inconsistencyLabel.setObjectName(_fromUtf8("inconsistencyLabel"))
        self.horizontalLayout_4.addWidget(self.inconsistencyLabel)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem4)
        self.buttonBox = QtGui.QDialogButtonBox(DiagnosticDataForm)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_4.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.prevalence_lbl.setBuddy(self.prevalence_txt_box)

        self.retranslateUi(DiagnosticDataForm)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DiagnosticDataForm.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DiagnosticDataForm.reject)
        QtCore.QMetaObject.connectSlotsByName(DiagnosticDataForm)

    def retranslateUi(self, DiagnosticDataForm):
        DiagnosticDataForm.setWindowTitle(_translate("DiagnosticDataForm", "Dialog", None))
        item = self.two_by_two_table.verticalHeaderItem(0)
        item.setText(_translate("DiagnosticDataForm", "(test) +", None))
        item = self.two_by_two_table.verticalHeaderItem(1)
        item.setText(_translate("DiagnosticDataForm", "(test) -", None))
        item = self.two_by_two_table.verticalHeaderItem(2)
        item.setText(_translate("DiagnosticDataForm", "total", None))
        item = self.two_by_two_table.horizontalHeaderItem(0)
        item.setText(_translate("DiagnosticDataForm", "(disease) +", None))
        item = self.two_by_two_table.horizontalHeaderItem(1)
        item.setText(_translate("DiagnosticDataForm", "(disease) -", None))
        item = self.two_by_two_table.horizontalHeaderItem(2)
        item.setText(_translate("DiagnosticDataForm", "total", None))
        self.prevalence_lbl.setText(_translate("DiagnosticDataForm", "Prevalence", None))
        self.startover_Btn.setText(_translate("DiagnosticDataForm", "Start Over", None))
        self.label_13.setText(_translate("DiagnosticDataForm", "metric", None))
        self.label_14.setText(_translate("DiagnosticDataForm", "est.", None))
        self.label_15.setText(_translate("DiagnosticDataForm", "low", None))
        self.label_16.setText(_translate("DiagnosticDataForm", "high", None))
        self.se_lbl.setText(_translate("DiagnosticDataForm", "se", None))
        self.label_2.setText(_translate("DiagnosticDataForm", "α:", None))
        self.ci_label.setText(_translate("DiagnosticDataForm", "(95% confidence interval)", None))
        self.inconsistencyLabel.setText(_translate("DiagnosticDataForm", "INCONSISTENT FORM", None))

import icons_rc
