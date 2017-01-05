#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append( os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))) )

from suds.client import Client
from suds import TypeNotFound
import base64

#from prism_model import *
#import prism_config as config
import time
from datetime import datetime
#from pymongo import MongoClient
import zipfile

import logging
import dicom as dcm

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP



class PRISMTabClient(QTabWidget):
    client = None
    lResultStudies = None #used to keep the returned results.
    lResultSDIS = None #used to keep the returned results.
    lResultData = None #used to keep the returned results.

    logger = None

    def __init__(self, parent = None):  

        super(PRISMTabClient, self).__init__(parent)

        """
        logging configuration
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        fh = logging.FileHandler('prism_client.log')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s %(module)s[%(lineno)d] - %(message)s')

        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # add the handlers to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)
        """
        """

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
                self.logger.debug("Tab de conexion")
            elif selected_index == self.index_tab_new_study:
                self.logger.debug("Tab de estudio")
                self.update_modality_list()
            elif selected_index == self.index_tab_search_study:
                self.logger.debug("Tab de busqueda")
            elif selected_index == self.index_tab_sdis:
                self.logger.debug("Tab de SubjectDataInStudy")
            elif selected_index == self.index_tab_load_data:
                self.logger.debug("Tab de carga de datos")
                self.captureDate = self.calCaptureDate.selectedDate().toString(Qt.ISODate)
                self.logger.debug("Fecha seleccionada inicialmente: " + self.captureDate)
 
            
        
    def connect_to_server(self):
        '''
        CONNECT TO THE SERVER
        '''
        self.connected_ok = False
        self.bind_address = str(self.lnEdtServerAddress.text().toUtf8())
        self.bind_port = str(self.lnEdtServerPort.text().toUtf8())
        
        url = 'http://'+self.bind_address+':'+str(self.bind_port)+'/prism/api.wsdl'
        self.logger.debug("Connecting to URL:"+ url)
        try:
            self.client = Client(url, cache=None)
            self.connected_ok = True
        except TypeNotFound:
            self.client = Client(url, cache=None)
            self.connected_ok = True
        except URLError:
            self.logger.error("Error al conectar")

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
        self.txtEdtStudyDescription = QTextEdit() #.toPlainText()

        self.cmbStudyPhySt = QComboBox()
        self.cmbStudyPhySt.addItem("cerebro".decode("UTF-8"))
        self.cmbStudyPhySt.addItem("corazón".decode("UTF-8"))
        self.cmbStudyPhySt.addItem("columna lumbar".decode("UTF-8"))

        self.cmbStudyDatatype = QComboBox() # self.cb.currentText()
        self.cmbStudyDatatype.addItem("imagen".decode("UTF-8"))
        self.cmbStudyDatatype.addItem("señal".decode("UTF-8"))
        self.cmbStudyDatatype.addItem("imágen+señal".decode("UTF-8"))
        self.btnStudyNewModality = QPushButton("Nueva modalidad")
        self.lstStudyModality = QListView()
        #self.update_modality_list()

            
        layout.addRow("Título".decode("UTF-8"), self.lnEdtStudyTitle)
        layout.addRow("Descripción".decode("UTF-8"), self.txtEdtStudyDescription)
        layout.addRow("Estructura fisiológica".decode("UTF-8"), self.cmbStudyPhySt)

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
        header_labels = ['ID', 'ID de sujeto', 'Es paciente?', 'Fecha captura', 'Etiquetas']
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

        self.btnToLoadSDIS = QPushButton("Cargar datos de sujeto seleccionado en el estudio")
        layout.addRow("", self.btnToLoadSDIS)
        QObject.connect(self.btnToLoadSDIS, SIGNAL("clicked()"), self.switch_to_loadsdis_tab)


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
        self.lnEdtSubjectId.setDisabled(True)

        self.btnCheckSubject = QPushButton("Agregar sujeto")
        hbox.addWidget(self.lnEdtSubjectId)
        hbox.addWidget(self.btnCheckSubject)
        layout.addRow("ID de Sujeto:", hbox)
        
        self.chkIsPacient = QCheckBox()
        layout.addRow("Es paciente?",  self.chkIsPacient)

        self.calCaptureDate = QCalendarWidget(self)
        self.calCaptureDate.setGridVisible(True)
        self.calCaptureDate.clicked[QDate].connect(self.showDate)

        layout.addRow("Fecha de captura", self.calCaptureDate)


        #self.captureDate = self.calCaptureDate.selectedDate().toString(Qt.ISODate)
        #self.logger.debug("Fecha seleccionada inicialmente: "+self.captureDate)

        #self.lblLabels = QLineEdit()
        #layout.addRow("Etiquetas", self.lblLabels)


        #hbox = QHBoxLayout()
        #self.lnEdtFolderPath = QLineEdit()
        #self.btnSelectFolder = QPushButton("Seleccionar carpeta")
        #hbox.addWidget(self.lnEdtFolderPath)
        #hbox.addWidget(self.btnSelectFolder)
        
        #layout.addRow("Ubicacion de carpeta de datos:", hbox)

        #self.lnEdtPackageName = QLineEdit()
        #self.lnEdtPackageName.setFixedWidth(400)
        #self.lnEdtPackageName.setText(str(datetime.fromtimestamp(time.time()) ).replace(" ","_").replace(":","_"))
        #layout.addRow("Nombre del paquete a enviar:", self.lnEdtPackageName) # INNECESARIO


        self.setTabText(self.index_tab_load_data, "Carga de Datos")
        self.tab_load_data.setLayout(layout)

        ####
        self.inputWidgetArray = []
        self.dynamicGrid = QGridLayout()

        self.btnNewInput = QPushButton("+")
        layout.addRow(self.btnNewInput)

        # adding new component
        '''
        self.inputWidgetArray.append( {'lnEdtFolderPath':QLineEdit(), 'btnSelectFolder':QPushButton("Seleccionar carpeta"), 'lblLabels':QLineEdit()} )
        self.dynamicGrid.addWidget(QLabel("Ubicacion de carpeta de datos:"), 0, 0)
        self.dynamicGrid.addWidget(self.inputWidgetArray[0]['lnEdtFolderPath'], 0, 1)
        self.dynamicGrid.addWidget(self.inputWidgetArray[0]['btnSelectFolder'], 0, 2)
        self.dynamicGrid.addWidget(QLabel("Etiquetas:"), 1, 0)
        self.dynamicGrid.addWidget(self.inputWidgetArray[0]['lblLabels'], 1, 1)
        '''
        layout.addRow(self.dynamicGrid)

        self.btnNewSDIS = QPushButton("Cargar datos")
        layout.addRow(self.btnNewSDIS)


        #QObject.connect(self.btnSelectFolder, SIGNAL("clicked()"), self.get_folder)
        #QObject.connect(self.btnCheckSubject, SIGNAL("clicked()"), self.check_subject)self.create_new_subject_dialog()
        QObject.connect(self.btnCheckSubject, SIGNAL("clicked()"), self.create_new_subject_dialog)
        QObject.connect(self.btnNewSDIS, SIGNAL("clicked()"), self.upload_sdis)
        QObject.connect(self.btnNewInput, SIGNAL("clicked()"), self.add_new_folder_input)


    '''
    Functions
    '''

    def add_new_folder_input(self):
        n = len(self.inputWidgetArray)
        N = n * 2

        self.inputWidgetArray.append(
            {'lnEdtFolderPath': QLineEdit(), 'btnSelectFolder': QPushButton("Seleccionar carpeta"),
             'lblLabels': QLineEdit(), 'lnEdtPackageName': QLineEdit()})
        package_name = str(datetime.fromtimestamp(time.time())).replace(" ", "_").replace(":", "_")
        self.inputWidgetArray[n]['lnEdtPackageName'].setText(package_name)

        self.logger.debug("Nuevo package name: "+package_name)

        self.dynamicGrid.addWidget(QLabel("Ubicacion de carpeta de datos:"), N, 0)
        self.dynamicGrid.addWidget(self.inputWidgetArray[n]['lnEdtFolderPath'], N, 1)
        self.dynamicGrid.addWidget(self.inputWidgetArray[n]['btnSelectFolder'], N, 2)
        self.dynamicGrid.addWidget(QLabel("Etiquetas:"), N+1, 0)
        self.dynamicGrid.addWidget(self.inputWidgetArray[n]['lblLabels'], N+1, 1)

        QObject.connect(self.inputWidgetArray[n]['btnSelectFolder'], SIGNAL("clicked()"), lambda index=n: self.get_folder(index))


    def showDate(self, date):
        self.captureDate = date.toString(Qt.ISODate) # formato YYYY-MM-DD
        self.logger.debug("Se selecciono "+self.captureDate)

    def update_modality_list(self):
        # Filling the modality list
        self.lstStudyModality.reset()
        model = QStandardItemModel(self.lstStudyModality)


        self.logger.debug("Listando modalidades")
        results = self.client.service.handle_list_modalities()
        #print "***",results

        modalities = []
        for r in results[0]:
            modality = r
            self.logger.debug("Found: "+modality.name)
            modalities.append( modality.name )

        ####
        for modl in modalities:
            item = QStandardItem(modl)
            item.setCheckable(True)
            model.appendRow(item)
        self.lstStudyModality.setModel(model)
        #


    def create_new_modality_dialog(self):
        self.logger.debug("Opening a new popup window...")
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
        modalityName = str(self.new_mod.lnEdtModalityName.text().toUtf8())
        modalityInfo = str(self.new_mod.txtEdtModalityInfo.toPlainText().toUtf8())
        self.logger.debug("SAVING..."+modalityName+" with info "+modalityInfo)
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
        self.logger.debug("ALMACENANDO ESTUDIO (TODO)")

        
        model = self.lstStudyModality.model()
        modalities = []
        i = 0
        while model.item(i):
            if model.item(i).checkState():
                modalities.append( str(model.item(i).text().toUtf8()) )
            i += 1
        modalities = ','.join(modalities)

        p = self.client.factory.create('ns0:RestStudy')
        p.title = str(self.lnEdtStudyTitle.text().toUtf8()).decode("UTF-8").lower()
        p.description = str(self.txtEdtStudyDescription.toPlainText().toUtf8()).decode("UTF-8").lower()
        p.physiological_st = str(self.cmbStudyPhySt.currentText().toUtf8() ).decode("UTF-8").lower()
        p.data_type_in_study = str(self.cmbStudyDatatype.currentText().toUtf8() ).decode("UTF-8").lower()


        ### Reocrdar que estos campos tienen impact en el nombre de las carpetas y no siempre el sistema de archivos acepta caracteres 'raros'
        self.logger.debug("Cambiando "+p.data_type_in_study)
        p.data_type_in_study = p.data_type_in_study.replace('imágen'.decode("UTF-8"),'image').replace('señal'.decode("UTF-8"),'signal')
        self.logger.debug("... por " + p.data_type_in_study)
        ###

        p.modalities=modalities

        p = self.client.service.handle_save_study(p) # updated with the ID
        study_id = p.id
    
        if len(study_id ) > 0:
            msgAlert = QMessageBox.information(self, 'Creacion de estudio',"Estudio almacenado exitosamente.",QMessageBox.Ok)
            self.lnEdtStudyTitle.clear()
            self.txtEdtStudyDescription.clear()
            #self.cmbStudyPhySt.clear()
            self.update_modality_list()

        else:
            msgAlert = QMessageBox.warning(self, 'Creacion de estudio',"Estudio no pudo ser almacenado.",QMessageBox.Ok)


    def upload_sdis(self):
        '''
        Creates the Package together with its METAinfo.
        Then, uploads it to the server.
        :return:
        '''
        self.logger.debug("UPLOAD DATA")
        self.btnNewSDIS.setDisabled(True)
        
        if not self.check_subject():
            self.btnNewSDIS.setDisabled(False)
            msgAlert = QMessageBox.warning(self, 'Carga de datos',"Sujeto debe ser agregado previamente.",QMessageBox.Ok)
            return None

        pubkeystr = self.client.service.handle_obtain_encryption_key()
        if len(pubkeystr) == 0:
            self.btnNewSDIS.setDisabled(False)
            msgAlert = QMessageBox.warning(self, 'Carga de datos',"No se pudo obtener clave de encriptacion desde el servidor.",QMessageBox.Ok)
            return None

        self.logger.debug("Key received:"+pubkeystr)
        newpubkey = RSA.importKey(pubkeystr)
        cipher = PKCS1_OAEP.new(newpubkey)# ciphertext = cipher.encrypt("15340959-5")

        study_id = str(self.lnEdtStudyId.text().toUtf8())
        subject_id = str(self.lnEdtSubjectId.text().toUtf8())
        is_pacient = False
        capture_date = self.captureDate # formato YYYY-MM-DD


        # Traverse the list of input boxes
        packages_to_upload = list()
        for package_input in self.inputWidgetArray:

            #each item is a dict with keys: 'lnEdtFolderPath': QLineEdit(), 'btnSelectFolder': QPushButton, 'lblLabels': QLineEdit(), 'lnEdtPackageName': QLineEdit()}

            labels = str(package_input['lblLabels'].text().toUtf8())

            if self.chkIsPacient.isChecked():
                is_pacient = True
            data_source_dir = str(package_input['lnEdtFolderPath'].text().toUtf8())
            package_fname = str(package_input['lnEdtPackageName'].text().toUtf8())

            #self.logger.debug("from",data_source_dir,"for study",study_id,"and subject",subject_id,"(",is_pacient,")")
            # get all the data inside
            #create a temp dir to store the encrypted data

            local_temp_package = "/tmp/.enc_" + package_fname
            os.makedirs(local_temp_package)

            zipf = zipfile.ZipFile("/tmp/"+package_fname, "w", zipfile.ZIP_DEFLATED)
            lfiles = []
            for root, dirs, files in os.walk(data_source_dir):
                for file in files:
                    if not file.endswith('.dcm') and file.startswith('.'):
                        continue

                    if file.endswith('.dcm'):
                        fsize=os.path.getsize(os.path.join(root, file))
                        #self.logger.debug("Adding file "+os.path.join(root, file))

                        self.logger.debug("Storing "+root+" "+file)
                        # For signals...
                        #lfiles.append((file, fsize, ()))
                        # read and de-identify dicom
                        imgObj = dcm.read_file(os.path.join(root, file))

                        #Only for images
                        #lfiles.append((file,fsize,{'PatientName':cipher.encrypt(imgObj.PatientName).replace("\n","JUMP").replace(",","COMMA").replace(" ","SPACE").replace(":","2DOTS"),
                        #                           'PatientID':cipher.encrypt(imgObj.PatientID).replace("\n","JUMP").replace(",","COMMA").replace(" ","SPACE").replace(":","2DOTS"),
                        #                           'PatientBirthDate':cipher.encrypt(imgObj.PatientBirthDate).replace("\n","JUMP").replace(",","COMMA").replace(" ","SPACE").replace(":","2DOTS")}))

                        lfiles.append((file, fsize, {'PatientName'     : base64.b64encode(cipher.encrypt(imgObj.PatientName)),
                                                     'PatientID'       : base64.b64encode(cipher.encrypt(imgObj.PatientID)),
                                                     'PatientBirthDate': base64.b64encode(cipher.encrypt(imgObj.PatientBirthDate))}))


                        imgObj.PatientName = "Anonym" #cipher.encrypt(imgObj.PatientName)
                        imgObj.PatientID = "Anonym" #cipher.encrypt(imgObj.PatientID)
                        imgObj.PatientBirthDate = "Anonym" #cipher.encrypt(imgObj.PatientBirthDate)
                        imgObj.save_as(local_temp_package + os.sep + file)

                    zipf.write(local_temp_package + os.sep + file, 'DATA' + os.sep + file)
                    ##zipf.write(os.path.join(root, file), 'DATA'+os.sep+file)
                    #self.logger.debug("Copying file "+"/tmp/"+package_fname+os.sep+'DATA'+os.sep+file)

            metainfo = open('/tmp/META.INFO','w')
            metainfo.write('1.0') # version
            metainfo.write('\nSTUDY,'+study_id) # study id
            metainfo.write('\nSUBJECT,'+subject_id) # anonymized_subject id
            if is_pacient: # Writes if it's pacient or just subject.
                metainfo.write('\nP')
            else:
                metainfo.write('\nNO_P')
            metainfo.write('\nCAPTURE_DATE,'+capture_date)
            metainfo.write('\nLABELS,'+labels)
            metainfo.write('\nDATA:\n')
            for f,s, meta in lfiles:
                datatype=''
                extension = f.split(".")[-1]
                if extension in ['dcm']:
                    datatype='image'
                else:
                    datatype='signal'
                metainfo.write('{0},{1},DATA,{2},'.format(datatype, s,f))

                for field, enc_value in meta.items(): #ENCRYPTED FIELDS
                    metainfo.write('{0}:{1} '.format(field, enc_value))

                metainfo.write('\n')
            metainfo.close()
            zipf.write('/tmp/META.INFO', 'META.INFO')
            zipf.close()


            '''
            CREATE A PACKAGE, OPEN THE ZIP FILE AND SEND IT
            '''
            with open("/tmp/"+package_fname)  as zip_file:
                encoded_string = base64.b64encode(zip_file.read())

            packages_to_upload.append( {'package_fname':package_fname,'encoded_string':encoded_string} )



        successful_upload = True
        for pkg in packages_to_upload:
            self.logger.debug("Package uploaded: "+pkg['package_fname'])

            pc = self.client.service.newPackageContent()
            pc.filename = pkg['package_fname']
            pc.content = pkg['encoded_string']
            pc = self.client.service.handle_capture_upload( pc )

            if len(pc.id) > 0:
                self.logger.debug("A new Subject capture has been created ("+pc.id+")")
                msgAlert = QMessageBox.information(self, 'Carga de datos',"Se registraron exitosamente los datos del sujeto en el estudio.",QMessageBox.Ok)
            else:
                successful_upload = False


        if successful_upload:
            #self.logger.debug("A new Subject capture has been created (" + pc.id + ")")
            msgAlert = QMessageBox.information(self, 'Carga de datos',
                                               "Se registraron exitosamente los datos del sujeto en el estudio.",
                                               QMessageBox.Ok)
            # clear lineedits
            self.lnEdtStudyId.clear()
            self.lnEdtSubjectId.clear()
            self.chkIsPacient.setChecked(False)

            for i in reversed(range(self.dynamicGrid.count())):
                widget = self.dynamicGrid.takeAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

            self.inputWidgetArray = []


            # self.lnEdtFolderPath.clear()

        self.btnNewSDIS.setDisabled(False)



    def check_subject(self):
        study_id = self.lnEdtStudyId.text().toUtf8()
        id = self.lnEdtSubjectId.text().toUtf8()
        if len(id) == 0 or len(study_id) == 0:
            return None
        self.logger.debug(id)
        # check if subject exists
        result = self.client.service.handle_get_anonymized_subject(id)
        self.logger.debug(result)
        self.logger.debug(len(result))

        if len(result) ==  0:
            return False
        return True
        # if it exists, show a message 
        '''
        if len(result) ==  0:
        # otherwise ask if the user wants to create a new sibject register.
            choice = QMessageBox.question(self, 'Verificacion de sujeto',"Desea crear un nuevo registro de sujeto?",QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.logger.debug("desplegando dialogo de creacion")
                self.create_new_subject_dialog()
                #sys.exit()
            else:
                pass
        else:
            self.logger.debug("OK, subject exists!")
            msgAlert = QMessageBox.information(self, 'Verificacion de sujeto',"Sujeto ya existe.",QMessageBox.Ok)
        '''



    def create_new_subject_dialog(self):
        self.logger.debug("Opening a new popup window...")
        self.w = QWidget()
        self.w.setGeometry(QRect(100, 100, 400, 200))
        layout = QFormLayout()
        #self.w.lnEdtSID = QLabel(self.lnEdtSubjectId.text())
        #self.w.lnEdtSID = QLabel()
        #layout.addRow("ID de Sujeto anonimizado:", self.w.lnEdtSID)
        self.w.bg = QButtonGroup()
        self.w.b1 = QCheckBox("M")
        self.w.b2 = QCheckBox("F")
        self.w.bg.addButton(self.w.b1,1)
        self.w.bg.addButton(self.w.b2,2)
        self.w.selectedGenre = ''
        hbox = QHBoxLayout()
        hbox.addWidget(self.w.b1)
        hbox.addWidget(self.w.b2)
        layout.addRow("Género:".decode("UTF-8"), hbox)
        
        self.w.btnSaveSubject = QPushButton("Registrar sujeto")
        layout.addRow(self.w.btnSaveSubject)
        self.w.setLayout(layout)
        self.w.show()
        self.w.bg.buttonClicked[QAbstractButton].connect(self.btngroup)
        QObject.connect(self.w.btnSaveSubject, SIGNAL("clicked()"), self.save_subject)

        
    def save_subject(self):
        #self.logger.debug("SAVING...",self.w.lnEdtSID.text().toUtf8())
        #todo: Store to platform.
        asub = self.client.factory.create('ns0:RestAnonymizedSubject')
        #asub.SID = str(self.w.lnEdtSID.text().toUtf8())
        asub.SID = ''
        asub.gender = str(self.w.selectedGenre)
        asub = self.client.service.handle_save_anonymizedSubject(asub)


        if len(asub.SID) > 0:
            msgAlert = QMessageBox.information(self, 'Creacion de sujeto',"Sujeto creado exitosamente (SID:"+asub.SID+").",QMessageBox.Ok)
        else:
            msgAlert = QMessageBox.information(self, 'Creacion de sujeto',"Sujeto no pudo ser creado.",QMessageBox.Ok)
        self.w.close()
        self.lnEdtSubjectId.setText(asub.SID)


    def btngroup(self,btn):
        self.logger.debug(btn.text().toUtf8()+" is selected")
        self.w.selectedGenre = btn.text().toUtf8()


    def get_folder(self, index_btn=-1):
        #fname = QFileDialog.getOpenFileName(self, 'Abrir', '/',"Carpetas")
        print "Se escogio el numero ",index_btn
        fname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.inputWidgetArray[index_btn]['lnEdtFolderPath'].setText(fname)
        #self.lnEdtFolderPath.setText(fname)

    def switch_to_sdis_tab(self):
        self.setCurrentIndex(self.index_tab_sdis)

        sdis_id = str(self.listSDIS.item(self.listSDIS.currentRow(), 0).text().toUtf8())
        sdis_subject = str(self.listSDIS.item(self.listSDIS.currentRow(), 1).text().toUtf8())

        self.tab2_lnEdtSubject.setText(sdis_subject)
        self.lnEdtSDIS.setText(sdis_id)
        self.btnSearchData.setDisabled(False)

    def switch_to_loadsdis_tab(self):
        self.setCurrentIndex(self.index_tab_load_data)

        sdis_subject = str(self.listSDIS.item(self.listSDIS.currentRow(), 1).text().toUtf8())
        self.lnEdtSubjectId.setText(sdis_subject)

        id = self.lResultStudies[int(self.listStudy.currentRow())]
        self.lnEdtStudyId.setText(id)

        self.logger.debug("Sujeto son ID:" + sdis_subject + " seleccionado en estudio:"+id)

    def switch_to_upload_tab(self):
        self.setCurrentIndex(self.index_tab_load_data)
        id = self.lResultStudies[int(self.listStudy.currentRow())]
        self.lnEdtStudyId.setText(id)

    def search_studies(self):
        self.logger.debug("BUSCANDO ESTUDIOS "+self.searchLnEdt.text().toUtf8())
        self.logger.debug(self.client)
        results = self.client.service.handle_search_study_by_query(str(self.searchLnEdt.text().toUtf8()).decode("UTF-8") )
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
            self.listSDIS.setItem(inx, 0, QTableWidgetItem(sdis.id))
            self.listSDIS.setItem(inx, 1, QTableWidgetItem(sdis.subject))
            self.listSDIS.setItem(inx, 2, QTableWidgetItem(str(sdis.is_pacient).replace("False","No").replace("True","Yes") ))
            self.listSDIS.setItem(inx, 3, QTableWidgetItem(sdis.capture_date))
            self.listSDIS.setItem(inx, 4, QTableWidgetItem(sdis.labels))
            inx+=1
        #print self.ui.listStudy.currentItem().text()

    def get_data_from_sdis(self):
        self.listData.clearContents()
        self.listData.setRowCount(0)
        id = self.lnEdtSDIS.text().toUtf8()


        oSDIS = self.client.service.handle_get_SDIS(id)
        self.tab2_lnEdtSubject.setText(oSDIS.subject)

        results = self.client.service.handle_get_data_by_sdis(id) # list of RestSDIS
        #print results

        self.lResultData = []
        
        self.listData.clearContents()
        inx = 0
        self.logger.debug("#Resultados:"+str(len(results[0])))
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
        id = str(self.listData.item(index.row(), 0).text().toUtf8())
        #msgAlert = QMessageBox.information(self, 'Dato de sujeto',"Mostrando item "+str(index.row())+" - "+ id,QMessageBox.Ok)
        data = self.client.service.handle_get_SDIS_data(id)
        
        temp_output = '/tmp/_'+data.filename+'.png'
        self.logger.debug("Decoding received file :"+temp_output)
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
    #logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='/tmp/prism_client.log',level=self.logger.DEBUG)
    logging.basicConfig(     datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.root.addFilter(logging.Filter(__name__))
    app = QApplication(sys.argv)
    ex = PRISMTabClient()
    ex.resize(800, 500)
    ex.show()
    sys.exit(app.exec_())
	
if __name__ == '__main__':
    main()

