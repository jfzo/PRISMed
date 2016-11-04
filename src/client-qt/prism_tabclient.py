#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append( os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))) )

from suds.client import Client
from suds import TypeNotFound
import base64

from prism_model import *
#import prism_config as config
import time
from datetime import datetime
from pymongo import MongoClient
import zipfile

import logging

class PRISMTabClient(QTabWidget):
    client = None
    lResultStudies = None #used to keep the returned results.
    lResultSDIS = None #used to keep the returned results.
    lResultData = None #used to keep the returned results.



    def __init__(self, parent = None):  

        super(PRISMTabClient, self).__init__(parent)

        self.bind_address = ""
        self.bind_port = ""
        self.client = None
        self.connected_ok = False
        
        self.tab_connection = QWidget()
        self.tab_new_study = QWidget()
        self.tab_search_study = QWidget()
        self.tab_sdis = QWidget()
        self.tab_load_data = QWidget()
        
          
        self.addTab(self.tab_connection,"Conexion al servidor")
        self.index_tab_connection = 0
        
        self.addTab(self.tab_new_study,"Nuevo estudio")
        self.index_tab_new_study = 1    
        self.tab_new_study.setDisabled(True)
        
        self.addTab(self.tab_search_study,"Buscar estudios")
        self.index_tab_search_study = 2
        self.tab_search_study.setDisabled(True)
        
        self.addTab(self.tab_sdis,"Sujeto en estudio")
        self.index_tab_sdis = 3
        self.tab_sdis.setDisabled(True)
        
        self.addTab(self.tab_load_data,"Carga de datos")
        self.index_tab_load_data = 4
        self.tab_load_data.setDisabled(True)
        ##
        self.draw_tab_connection()
        self.draw_tab_new_study()
        self.draw_tab_search_study()
        self.draw_tab_sdis()
        self.draw_tab_load_data()
        self.setWindowTitle("Cliente PRISM vAlfa")
		
        self.connect(self, SIGNAL('currentChanged(int)'), self.selector)
        
    def selector(self, selected_index):
        if self.connected_ok:
            if selected_index == self.index_tab_connection:
                logging.debug("Se selecciono la primera")
            elif selected_index == self.index_tab_new_study:
                logging.debug("Se selecciono la segunda")
                self.update_modality_list()
            elif selected_index == self.index_tab_search_study:
                logging.debug("Se selecciono la tercera")
            elif selected_index == self.index_tab_sdis:
                logging.debug("Se selecciono la cuarta")
            elif selected_index == self.index_tab_load_data:
                logging.debug("Se selecciono la quinta")
 
            
        
    def connect_to_server(self):
        '''
        CONNECT TO THE SERVER
        '''
        self.connected_ok = False
        self.bind_address = str(self.lnEdtServerAddress.text())
        self.bind_port = str(self.lnEdtServerPort.text())
        
        url = 'http://'+self.bind_address+':'+str(self.bind_port)+'/prism/api.wsdl'
        logging.debug("Connecting to URL:"+ url)
        try:
            self.client = Client(url, cache=None)
            self.connected_ok = True
        except TypeNotFound:
            self.client = Client(url, cache=None)
            self.connected_ok = True
        except URLError:
            logging.error("Error al conectar")

        if self.connected_ok:
            self.btnServerConnect.setDisabled(True)
            
            self.tab_new_study.setDisabled(False)
            self.tab_search_study.setDisabled(False)
            self.tab_sdis.setDisabled(False)
            self.tab_load_data.setDisabled(False)

        
    def draw_tab_connection(self):
        layout = QFormLayout()
        #layout.addRow("Name",QLineEdit())
        #layout.addRow("Address",QLineEdit())
        #self.setTabText(0,"Contact Details")
        #self.tab_search_study.setLayout(layout)
        
        self.lnEdtServerAddress = QLineEdit("127.0.0.1")
        self.lnEdtServerPort = QLineEdit("8080")
        self.btnServerConnect = QPushButton("Conectar")
        
        layout.addRow("IP Servidor", self.lnEdtServerAddress)
        layout.addRow("Puerto", self.lnEdtServerPort)
        layout.addRow("", self.btnServerConnect)

        self.tab_connection.setLayout(layout)
        self.setTabText(self.index_tab_connection,"Conexion")

        QObject.connect(self.btnServerConnect, SIGNAL("clicked()"), self.connect_to_server)        
       
        
    def draw_tab_new_study(self):
        layout = QFormLayout()
        #layout.addRow("Name",QLineEdit())
        #layout.addRow("Address",QLineEdit())
        #self.setTabText(0,"Contact Details")
        #self.tab_search_study.setLayout(layout)
        
        self.lnEdtStudyTitle = QLineEdit()
        self.txtEdtStudyMetadata = QTextEdit() #.toPlainText()
        self.lnEdtStudyPhySt = QLineEdit()
        self.cmbStudyDatatype = QComboBox() # self.cb.currentText()
        self.cmbStudyDatatype.addItem("image")
        self.cmbStudyDatatype.addItem("signal")
        self.cmbStudyDatatype.addItem("image+signal")
        self.btnStudyNewModality = QPushButton("Nueva modalidad")
        self.lstStudyModality = QListView()
        #self.update_modality_list()

            
        layout.addRow("Titulo", self.lnEdtStudyTitle)
        layout.addRow("Metadatos", self.txtEdtStudyMetadata)
        layout.addRow("Estructura fisiologica", self.lnEdtStudyPhySt)
        layout.addRow("Tipo(s) de dato(s) en el estudio", self.cmbStudyDatatype )
        hbox = QHBoxLayout()
        hbox.addWidget(self.lstStudyModality)
        hbox.addWidget(self.btnStudyNewModality)
        layout.addRow("Modalidad(es)", hbox)

        
        self.btnStudySave = QPushButton("Guardar estudio")
        layout.addRow("", self.btnStudySave)
        QObject.connect(self.btnStudySave, SIGNAL("clicked()"), self.save_new_study)
        QObject.connect(self.btnStudyNewModality, SIGNAL("clicked()"), self.create_new_modality_dialog)


        self.tab_new_study.setLayout(layout)
        self.setTabText(self.index_tab_new_study,"Nuevo Estudio")

    def draw_tab_search_study(self):
        layout = QFormLayout()
        #layout.addRow("Name",QLineEdit())
        #layout.addRow("Address",QLineEdit())
        #self.setTabText(0,"Contact Details")
        #self.tab_search_study.setLayout(layout)

        hbox = QHBoxLayout()
        self.searchLnEdt = QLineEdit()
        self.btnSearchStudies = QPushButton("Buscar")
        hbox.addWidget(self.searchLnEdt)
        hbox.addWidget(self.btnSearchStudies)
        hbox.addStretch()
        layout.addRow(QLabel("Palabra clave del estudio:"),hbox)
          
        layout.addRow("Resultados :",QLabel(""))
        header_labels = ['ID', 'Titulo', 'Estructura']
        self.listStudy = QTableWidget(0,len(header_labels))
        self.listStudy.setHorizontalHeaderLabels(header_labels)
        self.listStudy.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.listStudy.horizontalHeader()
        #header.setStretchLastSection(True)
        header.setResizeMode(QHeaderView.Stretch)
        layout.addRow( self.listStudy)

        self.btnToUpload = QPushButton("Cargar datos de nuevo sujeto al estudio seleccionado")
        layout.addRow("", self.btnToUpload)
        QObject.connect(self.btnToUpload, SIGNAL("clicked()"), self.switch_to_upload_tab)
        
        self.btnGetSDIS = QPushButton("Explorar datos en el estudio")
        layout.addRow("", self.btnGetSDIS)

        layout.addRow("Datos de sujetos en estudio seleccionado :",QLabel(""))

        # SubjectDataInStudy display list:
        header_labels = ['ID', 'ID de sujeto', 'Es paciente?']
        self.listSDIS = QTableWidget(0,len(header_labels))
        self.listSDIS.setHorizontalHeaderLabels(header_labels)

        self.listSDIS.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.listSDIS.horizontalHeader()
        #header.setStretchLastSection(True)
        header.setResizeMode(QHeaderView.Stretch)
        layout.addRow( self.listSDIS)



        #
        self.setTabText(self.index_tab_search_study,"Buscar Estudios")
        self.tab_search_study.setLayout(layout)

        
        self.btnToSDIS = QPushButton("Explorar datos de sujeto seleccionado en el estudio")
        layout.addRow("", self.btnToSDIS)
        QObject.connect(self.btnToSDIS, SIGNAL("clicked()"), self.switch_to_sdis_tab)



        # ACTIONS
        QObject.connect(self.btnSearchStudies, SIGNAL("clicked()"), self.search_studies)
        QObject.connect(self.btnGetSDIS, SIGNAL("clicked()"), self.get_sdis_from_study)



    def draw_tab_sdis(self):
        layout = QFormLayout()
        self.btnClearForm = QPushButton("Limpiar")
        self.btnClearForm.setDisabled(True)
        self.tab2_lnEdtSubject = QLineEdit()
        self.lnEdtSDIS = QLineEdit()
        self.btnSearchData = QPushButton("Buscar") # search data in sdis
        #self.btnSearchData.setDisabled(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.tab2_lnEdtSubject)
        hbox.addWidget(self.btnClearForm)
        layout.addRow("ID Sujeto: ", hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.lnEdtSDIS)
        hbox.addWidget(self.btnSearchData)
        layout.addRow("ID datos en el estudio: ", hbox)
        
        # results

        header_labels = ['ID', 'Nombre archivo', 'Tipo']
        self.listData = QTableWidget(0,len(header_labels))
        self.listData.setHorizontalHeaderLabels(header_labels)
        self.listData.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addRow("Datos del sujeto en el estudio:", QLabel(""))
        header = self.listData.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)

        layout.addRow(self.listData)
    
        self.setTabText(self.index_tab_sdis,"Sujeto en el estudio")
        self.tab_sdis.setLayout(layout)

        QObject.connect(self.btnSearchData, SIGNAL("clicked()"), self.get_data_from_sdis)
        QObject.connect(self.listData, SIGNAL("doubleClicked(QModelIndex)"), self.show_selection_in_sdis)
        
        
    def draw_tab_load_data(self):
        layout = QFormLayout()
        self.lnEdtStudyId = QLineEdit()
        self.lnEdtStudyId.setFixedWidth(250)
        layout.addRow("ID Estudio:", self.lnEdtStudyId)


        hbox = QHBoxLayout()
        self.lnEdtSubjectId = QLineEdit()
        self.lnEdtSubjectId.setFixedWidth(280)

        self.btnCheckSubject = QPushButton("Agregar sujeto")
        hbox.addWidget(self.lnEdtSubjectId)
        hbox.addWidget(self.btnCheckSubject)
        layout.addRow("ID de Sujeto:", hbox)
        
        self.chkIsPacient = QCheckBox()
        layout.addRow("Es paciente?",  self.chkIsPacient)  

        hbox = QHBoxLayout()
        self.lnEdtFolderPath = QLineEdit()
        self.btnSelectFolder = QPushButton("Seleccionar carpeta")
        hbox.addWidget(self.lnEdtFolderPath)
        hbox.addWidget(self.btnSelectFolder)
        
        layout.addRow("Ubicacion de carpeta de datos:", hbox)

        self.lnEdtPackageName = QLineEdit()
        self.lnEdtPackageName.setFixedWidth(400)
        self.lnEdtPackageName.setText(str(datetime.fromtimestamp(time.time()) ).replace(" ","_").replace(":","_"))
        layout.addRow("Nombre del paquete a enviar:", self.lnEdtPackageName)

        self.btnNewSDIS = QPushButton("Cargar datos")
        layout.addRow(self.btnNewSDIS )

        self.setTabText(self.index_tab_load_data, "Carga de Datos")
        self.tab_load_data.setLayout(layout)

        QObject.connect(self.btnSelectFolder, SIGNAL("clicked()"), self.get_folder)
        #QObject.connect(self.btnCheckSubject, SIGNAL("clicked()"), self.check_subject)self.create_new_subject_dialog()
        QObject.connect(self.btnCheckSubject, SIGNAL("clicked()"), self.create_new_subject_dialog)
        QObject.connect(self.btnNewSDIS, SIGNAL("clicked()"), self.upload_sdis)

    '''
    Functions
    '''
    def update_modality_list(self):
        # Filling the modality list
        self.lstStudyModality.reset()
        model = QStandardItemModel(self.lstStudyModality)


        logging.debug("Listando modalidades")
        results = self.client.service.handle_list_modalities()
        #print "***",results

        modalities = []
        for r in results[0]:
            modality = r
            logging.debug("Found: "+modality.name)
            modalities.append( modality.name )

        ####
        for modl in modalities:
            item = QStandardItem(modl)
            item.setCheckable(True)
            model.appendRow(item)
        self.lstStudyModality.setModel(model)
        #


    def create_new_modality_dialog(self):
        logging.debug("Opening a new popup window...")
        self.new_mod = QWidget()
        self.new_mod.setGeometry(QRect(100, 100, 400, 200))
        layout = QFormLayout()

        self.new_mod.lnEdtModalityName = QLineEdit()
        self.new_mod.txtEdtModalityInfo = QTextEdit()
        self.new_mod.btnModalitySave = QPushButton("Guardar modalidad")

        layout.addRow("Nombre de modalidad:", self.new_mod.lnEdtModalityName)
        layout.addRow("Informacion general:", self.new_mod.txtEdtModalityInfo)
        layout.addRow(self.new_mod.btnModalitySave)

        self.new_mod.setLayout(layout)
        self.new_mod.show()

        QObject.connect(self.new_mod.btnModalitySave, SIGNAL("clicked()"), self.save_modality)
        
    def save_modality(self):
        modalityName = str(self.new_mod.lnEdtModalityName.text())
        modalityInfo = str(self.new_mod.txtEdtModalityInfo.toPlainText())
        logging.debug("SAVING..."+modalityName+" with info "+modalityInfo)
        #todo: Store to platform.
        asub = self.client.factory.create('ns0:RestModality')
        asub.name = modalityName
        asub.information = modalityInfo
        asub = self.client.service.handle_save_modality(asub)

        if len(asub.id) > 0:
            msgAlert = QMessageBox.information(self, 'Creacion de modalidad',"Modalidad creada exitosamente.",QMessageBox.Ok)
        else:
            msgAlert = QMessageBox.information(self, 'Creacion de modalidad',"Modalidad no pudo ser creada.",QMessageBox.Ok)
        self.new_mod.close()
        self.update_modality_list()
        self.new_mod.close()
    
    def save_new_study(self):
        logging.debug("ALMACENANDO ESTUDIO (TODO)")

        
        model = self.lstStudyModality.model()
        modalities = []
        i = 0
        while model.item(i):
            if model.item(i).checkState():
                modalities.append( str(model.item(i).text()) )
            i += 1
        modalities = ','.join(modalities)

        p = self.client.factory.create('ns0:RestStudy')
        p.title = str(self.lnEdtStudyTitle.text())
        p.metadata = str(self.txtEdtStudyMetadata.toPlainText())
        p.physiological_st = str(self.lnEdtStudyPhySt.text())
        p.data_type_in_study = str(self.cmbStudyDatatype.currentText() )
        p.modalities=modalities

        p = self.client.service.handle_save_study(p) # updated with the ID
        study_id = p.id
    
        if len(study_id ) > 0:
            msgAlert = QMessageBox.information(self, 'Creacion de estudio',"Estudio almacenado exitosamente.",QMessageBox.Ok)
        else:
            msgAlert = QMessageBox.warning(self, 'Creacion de estudio',"Estudio no pudo ser almacenado.",QMessageBox.Ok)


    def upload_sdis(self):
        logging.debug("UPLOAD DATA")
        self.btnNewSDIS.setDisabled(True)
        
        if not self.check_subject():
            self.btnNewSDIS.setDisabled(False)
            msgAlert = QMessageBox.warning(self, 'Carga de datos',"Sujeto debe ser agregado previamente.",QMessageBox.Ok)
            return None
        
        study_id = str(self.lnEdtStudyId.text())
        subject_id = str(self.lnEdtSubjectId.text())
        is_pacient = False
        if self.chkIsPacient.isChecked():
            is_pacient = True
        data_source_dir = str(self.lnEdtFolderPath.text())
        package_fname=str(self.lnEdtPackageName.text())

        #logging.debug("from",data_source_dir,"for study",study_id,"and subject",subject_id,"(",is_pacient,")")
        # get all the data inside
        zipf = zipfile.ZipFile("/tmp/"+package_fname, "w", zipfile.ZIP_DEFLATED)
        lfiles = []
        for root, dirs, files in os.walk(data_source_dir):
            for file in files:
                fsize=os.path.getsize(os.path.join(root, file))
                lfiles.append( (file,fsize) )
                zipf.write(os.path.join(root, file), 'DATA'+os.sep+file)

        metainfo = open('/tmp/META.INFO','w')
        metainfo.write('1.0')
        metainfo.write('\nSTUDY,'+study_id)
        metainfo.write('\nSUBJECT,'+subject_id)
        if is_pacient:
            metainfo.write('\nP')
        else:
            metainfo.write('\nNO_P')
        metainfo.write('\nDATA:\n')
        for f,s in lfiles:
            datatype=''
            extension = f.split(".")[-1]
            if extension in ['dcm']:
                datatype='image'
            else:
                datatype='signal'
            metainfo.write('{0},{1},DATA,{2}\n'.format(datatype, s,f) )
        metainfo.close()
        zipf.write('/tmp/META.INFO', 'META.INFO')
        zipf.close()


        '''
        CREATE A PACKAGE, OPEN THE ZIP FILE AND SEND IT 
        '''
        with open("/tmp/"+package_fname)  as zip_file:
            encoded_string = base64.b64encode(zip_file.read())

        pc = self.client.service.newPackageContent()
        pc.filename = package_fname
        pc.content = encoded_string
        pc = self.client.service.handle_capture_upload( pc )

        if len(pc.id) > 0:
            logging.debug("A new Subject capture has been created ("+pc.id+")")
            msgAlert = QMessageBox.information(self, 'Carga de datos',"Se registraron exitosamente los datos del sujeto en el estudio.",QMessageBox.Ok)
            #clear lineedits
            self.lnEdtStudyId.clear()
            self.lnEdtSubjectId.clear()
            self.lnEdtFolderPath.clear()
        
        self.btnNewSDIS.setDisabled(False)

    def check_subject(self):
        study_id = self.lnEdtStudyId.text()
        id = self.lnEdtSubjectId.text()
        if len(id) == 0 or len(study_id) == 0:
            return None
        logging.debug(id)
        # check if subject exists
        result = self.client.service.handle_get_anonymized_subject(id)
        logging.debug(result)
        logging.debug(len(result))

        if len(result) ==  0:
            return False
        return True
        # if it exists, show a message 
        '''
        if len(result) ==  0:
        # otherwise ask if the user wants to create a new sibject register.
            choice = QMessageBox.question(self, 'Verificacion de sujeto',"Desea crear un nuevo registro de sujeto?",QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                logging.debug("desplegando dialogo de creacion")
                self.create_new_subject_dialog()
                #sys.exit()
            else:
                pass
        else:
            logging.debug("OK, subject exists!")
            msgAlert = QMessageBox.information(self, 'Verificacion de sujeto',"Sujeto ya existe.",QMessageBox.Ok)
        '''



    def create_new_subject_dialog(self):
        logging.debug("Opening a new popup window...")
        self.w = QWidget()
        self.w.setGeometry(QRect(100, 100, 400, 200))
        layout = QFormLayout()
        self.w.lnEdtSID = QLabel(self.lnEdtSubjectId.text())
        layout.addRow("ID de Sujeto anonimizado:", self.w.lnEdtSID)
        self.w.bg = QButtonGroup()
        self.w.b1 = QCheckBox("H")
        self.w.b2 = QCheckBox("M")
        self.w.bg.addButton(self.w.b1,1)
        self.w.bg.addButton(self.w.b2,2)
        self.w.selectedGenre = ''
        hbox = QHBoxLayout()
        hbox.addWidget(self.w.b1)
        hbox.addWidget(self.w.b2)
        layout.addRow("Genero:", hbox)
        
        self.w.btnSaveSubject = QPushButton("Registrar sujeto")
        layout.addRow(self.w.btnSaveSubject)
        self.w.setLayout(layout)
        self.w.show()
        self.w.bg.buttonClicked[QAbstractButton].connect(self.btngroup)
        QObject.connect(self.w.btnSaveSubject, SIGNAL("clicked()"), self.save_subject)
        
    def save_subject(self):
        logging.debug("SAVING...",self.w.lnEdtSID.text())
        #todo: Store to platform.
        asub = self.client.factory.create('ns0:RestAnonymizedSubject')
        asub.SID = str(self.w.lnEdtSID.text())
        asub.gender = str(self.w.selectedGenre)
        asub = self.client.service.handle_save_anonymizedSubject(asub)

        if len(asub.SID) > 0:
            msgAlert = QMessageBox.information(self, 'Creacion de sujeto',"Sujeto creado exitosamente.",QMessageBox.Ok)
        else:
            msgAlert = QMessageBox.information(self, 'Creacion de sujeto',"Sujeto no pudo ser creado.",QMessageBox.Ok)
        self.w.close()


    def btngroup(self,btn):
        logging.debug(btn.text()+" is selected")
        self.w.selectedGenre = btn.text()


    def get_folder(self):
        #fname = QFileDialog.getOpenFileName(self, 'Abrir', '/',"Carpetas")
        fname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.lnEdtFolderPath.setText(fname)

    def switch_to_sdis_tab(self):
        self.setCurrentIndex(self.index_tab_sdis)

        sdis_id = str(self.listSDIS.item(self.listSDIS.currentRow(), 0).text())
        sdis_subject = str(self.listSDIS.item(self.listSDIS.currentRow(), 1).text())

        self.tab2_lnEdtSubject.setText(sdis_subject)
        self.lnEdtSDIS.setText(sdis_id)
        self.btnSearchData.setDisabled(False)

    def switch_to_upload_tab(self):
        self.setCurrentIndex(self.index_tab_load_data)
        id = self.lResultStudies[int(self.listStudy.currentRow())]
        self.lnEdtStudyId.setText(id)

    def search_studies(self):
        logging.debug("BUSCANDO ESTUIDIOS "+self.searchLnEdt.text())
        logging.debug(self.client)
        results = self.client.service.handle_search_study_by_title(self.searchLnEdt.text())
        #print "***",results

        self.lResultStudies = []

        self.listStudy.clearContents()
        self.listStudy.setRowCount(0)
        inx = 0
        for r in results[0]:
            study = r
            self.lResultStudies.append(study.id)
            self.listStudy.insertRow(inx)
            self.listStudy.setItem(inx,0,QTableWidgetItem(study.id))
            self.listStudy.setItem(inx,1,QTableWidgetItem(study.title))
            self.listStudy.setItem(inx,2,QTableWidgetItem(study.physiological_st))
            inx+=1

    def get_sdis_from_study(self):
        id = self.lResultStudies[int(self.listStudy.currentRow())]
        #print "****",self.client

        results = self.client.service.handle_get_SDIS_by_study(id) # list of RestSDIS
        #print results

        self.lResultSDIS = []
        
        self.listSDIS.clearContents()
        self.listSDIS.setRowCount(0)
        inx = 0
        for r in results[0]:
            sdis = r
            self.lResultSDIS.append(sdis.subject)
            self.listSDIS.insertRow(inx)
            self.listSDIS.setItem(inx,0,QTableWidgetItem(sdis.id))
            self.listSDIS.setItem(inx,1,QTableWidgetItem(sdis.subject))
            self.listSDIS.setItem(inx,2,QTableWidgetItem(str(sdis.is_pacient).replace("False","No").replace("True","Yes") ))
            inx+=1
        #print self.ui.listStudy.currentItem().text()

    def get_data_from_sdis(self):
        self.listData.clearContents()
        self.listData.setRowCount(0)
        id = self.lnEdtSDIS.text()


        oSDIS = self.client.service.handle_get_SDIS(id)
        self.tab2_lnEdtSubject.setText(oSDIS.subject)

        results = self.client.service.handle_get_data_by_sdis(id) # list of RestSDIS
        #print results

        self.lResultData = []
        
        self.listData.clearContents()
        inx = 0
        logging.debug("#Resultados:"+str(len(results[0])))
        #print results[0]
        for r in results[0]:
            data = r
            #print "#### Result", inx,"\n",data
            self.lResultData.append(data.id)
            self.listData.insertRow(inx)
            self.listData.setItem(inx,0,QTableWidgetItem(data.id))
            self.listData.setItem(inx,1,QTableWidgetItem(data.filename))
            self.listData.setItem(inx,2,QTableWidgetItem(data.datatype))
            inx+=1

    def show_selection_in_sdis(self, index):
        id = str(self.listData.item(index.row(), 0).text())
        #msgAlert = QMessageBox.information(self, 'Dato de sujeto',"Mostrando item "+str(index.row())+" - "+ id,QMessageBox.Ok)
        data = self.client.service.handle_get_SDIS_data(id)
        
        temp_output = '/tmp/_'+data.filename+'.png'
        logging.debug("Decoding received file :"+temp_output)
        with open(temp_output, "wb") as fh:
            fh.write(data.content.decode('base64'))


        dialog = QDialog()
        dialog.setWindowTitle("Visualizacion de dato:"+id)
        layout = QVBoxLayout()

        lbl = QLabel()
        lbl.setPixmap(QPixmap(temp_output))
        layout.addWidget( lbl)


        dialog.setLayout(layout)
        dialog.exec_()
        
        

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='/tmp/prism_client.log',level=logging.DEBUG)    
    app = QApplication(sys.argv)
    ex = PRISMTabClient()
    ex.resize(800, 500)
    ex.show()
    sys.exit(app.exec_())
	
if __name__ == '__main__':
    main()

