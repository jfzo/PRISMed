import sys
from PyQt4 import QtCore, QtGui
import prism_search_ui as prismui


try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class PrismGUI(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = prismui.Ui_Form()
        self.ui.setupUi(self)

        QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.search_studies)
        #QtCore.QMetaObject.connectSlotsByName(Form)

        item = self.ui.listWidget.item(0)
        item.setText(_translate("Form", "item AA", None))
        item = self.ui.listWidget.item(1)
        item.setText(_translate("Form", "item BB", None))
        item = self.ui.listWidget.item(2)
        item.setText(_translate("Form", "item CC", None))
    
    def search_studies(self):
        print "BUSCANDO ESTUIDIOS "+self.ui.lineEdit.text()


if __name__ == "__main__":
    app = QtGui.QApplication( sys.argv )
    myapp = PrismGUI()
    myapp.show()
    sys.exit(app.exec_())
