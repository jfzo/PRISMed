import sys, os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
import prism_search_ui as study_ui
import prism_new_sdis as sdis_ui
import prism_main as main_ui

sys.path.append( os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))) )

from suds.client import Client
from suds import TypeNotFound
import base64

from prism_model import *
import prism_config as config
import time
from datetime import datetime
from pymongo import MongoClient
import zipfile


try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)



class PrismGUI(QtGui.QMainWindow):
    client = None
    lResultStudies = None #used to keep the returned results.
    lResultSDIS = None #used to keep the returned results.

    def __init__(self, parent=None):


        '''
        CONNECT TO THE SERVER
        '''
        url = 'http://'+config.bind_address+':'+str(config.bind_port)+'/prism/api.wsdl'
        try:
            self.client = Client(url, cache=None)
        except TypeNotFound:
            self.client = Client(url, cache=None)



        QtGui.QWidget.__init__(self, parent)
        #self.ui = study_ui.Ui_Form()
        self.ui = main_ui.Ui_MainWindow()
        self.ui.setupUi(self)


        self.search_ui = study_ui.Ui_Form()
        self.search_ui.setupUi(self)

        QtCore.QObject.connect(self.search_ui.btnSearchStudies, QtCore.SIGNAL("clicked()"), self.search_studies)
        QtCore.QObject.connect(self.search_ui.btnGetSDIS, QtCore.SIGNAL("clicked()"), self.get_sdis_from_study)
        QtCore.QObject.connect(self.search_ui.btnNewSDIS, QtCore.SIGNAL("clicked()"), self.open_sdis_dialog)
        #QtCore.QMetaObject.connectSlotsByName(Form)
        QtCore.QObject.connect(self.search_ui.listStudy,  QtCore.SIGNAL("clicked(QModelIndex)"), self.activate_SDISBtn)

        # Main WIndo menu connection
        QtCore.QObject.connect(self.ui.menubar, QtCore.SIGNAL("triggered(QAction*)"), self.show_search_ui)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def show_search_ui(self):
        print "MOSTRAR VENTANA DE BUSQUEDA"
        self.search_ui.exec_()

    def open_sdis_dialog(self):
        sdisdialog = sdis_ui.Ui_NewSDIS()
        sdisdialog.exec_()
        #self.dialogTextBrowser = MyDialog(self)
        #self.dialogTextBrowser.exec_()

    def activate_SDISBtn(self):
        self.search_ui.btnGetSDIS.setEnabled(True)
        
    def search_studies(self):
        print "BUSCANDO ESTUIDIOS "+self.search_ui.lineEdit.text()
        print self.client
        results = self.client.service.handle_search_study_by_title(self.search_ui.lineEdit.text())
        print "***",results
        
        self.lResultStudies = []

        for r in results:            
            print "****",r[1][0]
            study = r[1][0]    
            self.lResultStudies.append(study.id)
            item = QListWidgetItem("Title: %s" % study.title)
            self.search_ui.listStudy.addItem(item)

    def get_sdis_from_study(self):
        id = self.lResultStudies[int(self.search_ui.listStudy.currentRow())]

        print "****",self.client

        results = self.client.service.handle_get_SDIS_by_study(id) # list of RestSDIS
        print results

        self.lResultSDIS = []

        for r in results:
            sdis = r[1][0]
            self.lResultSDIS.append(sdis.subject)
            item = QListWidgetItem("Subject: %s" % sdis.subject)
            self.search_ui.listSDIS.addItem(item)
        
        #print self.ui.listStudy.currentItem().text()


'''
if __name__ == "__main__":
    app = QtGui.QApplication( sys.argv )
    myapp = PrismGUI()
    #myapp = main_ui.Ui_MainWindow()
    myapp.show()
    sys.exit(app.exec_())
'''

def main():
    
    app 	= QtGui.QApplication(sys.argv)
    tabs	= QtGui.QTabWidget()
    pushButton1 = QtGui.QPushButton("QPushButton 1")
    pushButton2 = QtGui.QPushButton("QPushButton 2")
    
    tab1	= study_ui.Ui_Form()
    tab2	= QtGui.QWidget()
    tab3	= QtGui.QWidget()
    
    vBoxlayout	= QtGui.QVBoxLayout()
    vBoxlayout.addWidget(pushButton1)
    vBoxlayout.addWidget(pushButton2)

    #Resize width and height
    tabs.resize(250, 150)
    
    #Move QTabWidget to x:300,y:300
    tabs.move(300, 300)
    
    #Set Layout for Third Tab Page
    tab3.setLayout(vBoxlayout)   
    
    tabs.addTab(tab1,"Tab 1")
    #tabs.addTab(tab2,"Tab 2")
    #tabs.addTab(tab3,"Tab 3")
    
    tabs.setWindowTitle('PyQt QTabWidget Add Tabs and Widgets Inside Tab')
    tabs.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


