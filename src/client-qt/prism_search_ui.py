# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'prism_search_ui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import sys

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

class Ui_Form(QtGui.QWidget):
    def __init__(self):
        super(Ui_Form, self).__init__()
        self.setupUi()

    def setupUi(self):
        #Form.setObjectName(_fromUtf8("Form"))
        #Form.resize(702, 547)
        self.gridLayoutWidget = QtGui.QWidget()
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 10, 661, 66))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnSearchStudies = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnSearchStudies.setObjectName(_fromUtf8("btnSearchStudies"))
        self.gridLayout.addWidget(self.btnSearchStudies, 0, 2, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.gridLayoutWidget_2 = QtGui.QWidget()
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(20, 90, 661, 231))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.listStudy = QtGui.QListWidget(self.gridLayoutWidget_2)
        self.listStudy.setEnabled(True)
        self.listStudy.setObjectName(_fromUtf8("listStudy"))
        self.gridLayout_2.addWidget(self.listStudy, 1, 0, 1, 1)
        self.btnGetSDIS = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.btnGetSDIS.setEnabled(False)
        self.btnGetSDIS.setObjectName(_fromUtf8("btnGetSDIS"))
        self.gridLayout_2.addWidget(self.btnGetSDIS, 1, 1, 1, 1)
        self.label = QtGui.QLabel()
        self.label.setGeometry(QtCore.QRect(20, 70, 71, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayoutWidget_3 = QtGui.QWidget()
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(20, 360, 501, 181))
        self.gridLayoutWidget_3.setObjectName(_fromUtf8("gridLayoutWidget_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.listSDIS = QtGui.QListWidget(self.gridLayoutWidget_3)
        self.listSDIS.setObjectName(_fromUtf8("listSDIS"))
        self.gridLayout_3.addWidget(self.listSDIS, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel()
        self.label_2.setGeometry(QtCore.QRect(20, 330, 331, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayoutWidget = QtGui.QWidget()
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(520, 360, 176, 111))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.btnNewSDIS = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnNewSDIS.setObjectName(_fromUtf8("btnNewSDIS"))
        self.verticalLayout_2.addWidget(self.btnNewSDIS)
        self.pushButton_4 = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton_4.setEnabled(False)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.verticalLayout_2.addWidget(self.pushButton_4)

        self.retranslateUi()
        #QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self):
        #Form.setWindowTitle(_translate("Form", "Form", None))
        self.btnSearchStudies.setText(_translate("Form", "Buscar", None))
        self.label_3.setText(_translate("Form", "Titulo del estudio:", None))
        self.btnGetSDIS.setText(_translate("Form", "Listar registros", None))
        self.label.setText(_translate("Form", "Resultados", None))
        self.label_2.setText(_translate("Form", "Registros de sujetos en estudio seleccionado", None))
        self.btnNewSDIS.setText(_translate("Form", "Nuevo registro de sujeto", None))
        self.pushButton_4.setText(_translate("Form", "Agregar a la captura", None))


def main():
   app = QtGui.QApplication(sys.argv)
   ex = Ui_Form()
   ex.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()
