# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'prism_search_ui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(674, 549)
        self.gridLayoutWidget = QtGui.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 10, 631, 51))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pushButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 0, 1, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.gridLayoutWidget_2 = QtGui.QWidget(Form)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(20, 90, 631, 231))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.listWidget = QtGui.QListWidget(self.gridLayoutWidget_2)
        self.listWidget.setEnabled(False)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.gridLayout_2.addWidget(self.listWidget, 1, 0, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.gridLayout_2.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 70, 71, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayoutWidget_3 = QtGui.QWidget(Form)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(20, 360, 501, 181))
        self.gridLayoutWidget_3.setObjectName(_fromUtf8("gridLayoutWidget_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.listWidget_2 = QtGui.QListWidget(self.gridLayoutWidget_3)
        self.listWidget_2.setObjectName(_fromUtf8("listWidget_2"))
        self.gridLayout_3.addWidget(self.listWidget_2, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(20, 330, 211, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayoutWidget = QtGui.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(520, 360, 133, 111))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.pushButton_3 = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.pushButton_4 = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.verticalLayout_2.addWidget(self.pushButton_4)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton.setText(_translate("Form", "Buscar estudio", None))
        self.pushButton_2.setText(_translate("Form", "Revisar estudio", None))
        self.label.setText(_translate("Form", "Resultados", None))
        self.label_2.setText(_translate("Form", "Capturas en estudio seleccionado", None))
        self.pushButton_3.setText(_translate("Form", "Nueva captura", None))
        self.pushButton_4.setText(_translate("Form", "Agregar a la captura", None))

