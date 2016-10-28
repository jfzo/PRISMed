#import wsme
#from wsme.types import Enum, binary
#from wsme.types import UserType
import os
from wsme import WSRoot, expose, validate, signature
import prism_config as config
from prism_util import SubjectCaptureUnpacker
from prism_model import *
import time
from datetime import datetime
import logging
import hashlib

class PackageContent(object):
    id = unicode
    filename = unicode
    content = unicode

    def __repr__(self):
        return "PackageContent(%s, %s)" % (
            self.filename, self.content
        )


class RestStudy(object):
    id = unicode
    title = unicode
    #date_added = unicode
    metadata = unicode
    physiological_st = unicode
    data_type_in_study = unicode
    modalities = unicode # comma separated list of strings

    def __repr__(self):
        return "RestStudy(%s, %s, %s, %s, %s, %s)" % (
            self.id, self.title, self.metadata, self.physiological_st, self.data_type_in_study, self.modalities
        )
        
class RestAnonymizedSubject(object):
    id = unicode
    SID = unicode
    gender = unicode
    
    def __repr__(self):
        return "RestAnonymizedSubject(%s, %s, %s)" % (
            self.id, self.SID, self.gender
        )
 
class RestSDIS(object):
    id = unicode
    is_pacient = bool
    #in_study = unicode
    subject = unicode #SID
     
    def __repr__(self):
        return "RestAnonymizedSubject(%s, %s, %s)" % (
            self.id, self.is_pacient,  self.subject
        )
            
class RestData(object):
    id = unicode
    location = unicode
    filename = unicode
    size = int
    checksum = unicode
    datatype = unicode

    def __repr__(self):
        return "RestData(%s,%s,%s,%s,%s,%s)" % (
            self.id, self.location, self.filename, self.size, 
            self.checksum, self.datatype
        )




######################

#TODO: Change to SdisUploadController
class SDISController:
    def __init__(self):
        logging.debug("Initializing SDISController")


    def upload_packed_content(self, dir_path, file_name):
        #process the file
        logging.debug("File "+dir_path+"/"+file_name+" uploaded.")
        unpacker = SubjectCaptureUnpacker()
        st, sbj, sdis, lDataObjs, packedContentPath = unpacker.unpack_study(dir_path, file_name)

        logging.debug("Identifying repository path")
        # store data files... path is formed by 
        locpath = config.data_dir + os.sep + st.physiological_st 
        if not os.path.exists(locpath):
            os.makedirs(locpath)
        
        locpath += os.sep + st.data_type_in_study
        if not os.path.exists(locpath):
            os.makedirs(locpath)
        
        modalities = []
        for m in st.modalities:
            modalities.append( m.name )
        modalities.sort()
        
        locpath += os.sep + '+'.join( modalities ) + os.sep + str(st.id) + os.sep
        #check study directory
        if not os.path.exists(locpath):
            os.makedirs(locpath)

        if sdis.is_pacient:
            locpath += 'pacient' 
        else:
            locpath += 'subject'

        #check subject or pacient directory
        if not os.path.exists(locpath):
            os.makedirs(locpath)

        locpath += os.sep + sbj.SID
        #check specific subject  directory
        if not os.path.exists(locpath):
            os.makedirs(locpath)

        logging.debug('Saving data to DB and storing content files into folder '+locpath)
        # 
        # store SubjectDataInStudy and
        sdis.save()
        logging.debug("New SubjectDataInCapture stored ("+str(sdis.id)+")")
        # Data objects into DB and move the data
        for d in lDataObjs: # this block can easily be parallelized
            #logging.debug( "-_------>>" )
            #logging.debug( d )
            d.parent_sdis = sdis
            d.location = locpath
            # move file packedContentPath/filename to d.location/d.filename
            from_path = packedContentPath + os.sep + 'DATA' + os.sep + d.filename
            dest_path = d.location + os.sep + d.filename
            #logging.debug("Moving from "+ from_path +" to "+ dest_path)
            os.rename(from_path, dest_path) 
            d.checksum = self.md5(dest_path)
            d.save()
        return str(sdis.id)

    def get_SDIS_by_study(self, id):
        logging.debug("Searching for all the SDIS associated to study "+id)
        s = Study.objects(id=id)

        results = SubjectDataInStudy.objects(in_study=s.first().id)
        
        logging.debug("#results found:"+str(len(results)))
        #response = [(i.subject.SID, i.is_pacient) for i in results]
        response = []
        for i in results:
            o = RestSDIS()
            o.id = str(i.id)
            o.subject = i.subject.SID
            o.is_pacient = i.is_pacient
            response.append( o )
        return response

    def get_SDIS(self, id):
        results = SubjectDataInStudy.objects(id=id)
        
        response = []
        for i in results:
            o = RestSDIS()
            o.id = str(i.id)
            o.subject = i.subject.SID
            o.is_pacient = i.is_pacient
            response.append( o )
        return response[0]

    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_data_in_sdis(self, id):
        logging.debug("Searching for all the data in SDIS with id "+id)
        results = Data.objects(parent_sdis=id)
        logging.debug("#results found:"+str(len(results)))
        #response = [(i.subject.SID, i.is_pacient) for i in results]
        response = []
        for i in results:
            o = RestData()
            o.id = str(i.id)
            o.location = i.location
            o.filename = i.filename
            o.size = i.size
            o.checksum = i.checksum
            o.datatype = i.datatype
            response.append( o )
        return response

            
class StudyController:
    def __init__(self):
        logging.debug("Initializing StudyController")
        config.connect()
        
    def search_study_by_title(self, titleq):
        logging.debug("Searching for all the studies matching title: "+titleq)
        results = Study.objects(title__icontains=titleq)
        lResult = []
        for s in results:
            news = RestStudy()
            news.id = str(s.id)
            news.title = s.title
            #news.date_added = 
            news.metadata = s.metadata
            news.physiological_st = s.physiological_st
            news.data_type_in_study = s.data_type_in_study
            news.modalities = '/'.join( x.name for x in s.modalities)
            lResult.append( news )
        return lResult



    def store_study(self, s):
        #create model object, save and return id
        logging.debug("Creating Study object")
        mods = s.modalities.lower().split(',')
        lMods = []
        for m in mods:
            #search modality or create a new one
            qmod = Modality.objects(name=m)
            if qmod.count() > 0:
                lMods.append( qmod.first() )
            else:
                newmod = Modality(name=m).save()
                lMods.append( newmod )
        logging.debug("...storing Study object")
        today = datetime.fromtimestamp(time.time()) 
        st = Study(title=s.title, date_added=today, metadata=s.metadata, physiological_st=s.physiological_st, data_type_in_study=s.data_type_in_study, modalities=lMods).save()
        logging.debug("...id assigned "+str(st.id))
        
        return str(st.id)
        
class AnonymizedSubjectController:
    def __init__(self):
        logging.debug("Initializing AnonymizedSubjectController")
        config.connect()

    def store_subject(self, o):
        sbj = AnonymizedSubject(SID=o.SID, gender=o.gender).save()
        return str(sbj.id)

    def get_subject(self, sid):
        sbj = AnonymizedSubject.objects(SID=sid)
        o = RestAnonymizedSubject()
        if sbj.count() > 0:
            o.id = str(sbj.first().id)
            o.SID = sbj.first().SID
            o.gender = sbj.first().gender

        return o
            
            
        
        
        
            
#### WSDL Service Interface



class FrontController(WSRoot):
    '''
    --HOW TO USE THIS WSDL INTERFACE--
    from suds.client import Client
    import base64
    with open("/Volumes/SSDII/Users/juan/Downloads/Ax_FSPGR_3D_7.zip",'rb') as zip_file:
        encoded_string = base64.b64encode(zip_file.read())

    url = 'http://127.0.0.1:8080/prism/api.wsdl'
    client = Client(url, cache=None)
    pc = client.service.newPackageContent()

    pc.filename = 'Ax_FSPGR_3D_7.zip'
    pc.content = encoded_string
    client.service.handle_capture_upload( pc )
    '''
    
    sdisController = None
    studyController = None
    anonymizedSubjectController = None
    
    def init(self):
        if self.sdisController == None:
            logging.debug('Creating sdisController')
            self.sdisController = SDISController()
            logging.debug('Creating studyController')
            self.studyController = StudyController()
            logging.debug('Creating anonymizedSubjectController')
            self.anonymizedSubjectController = AnonymizedSubjectController()

    '''
    @expose(RestStudy)
    def newStudy(self):
        s = RestStudy()
        s.title = ''
        s.date_added = ''
        s.metadata = ''
        s.physiological_st = ''
        s.data_type_in_study = ''
        s.modalities = ''
        return s
    '''

    #@expose([RestStudy])
    #@validate([RestStudy])
    @signature([RestStudy], unicode)
    def handle_search_study_by_title(self, title):
        logging.debug( "Querying db for studies matching "+title )
        self.init()
        return self.studyController.search_study_by_title(title)
            
    @expose(RestStudy)
    @validate(RestStudy)
    def handle_save_study(self, o):
        logging.debug( "received new study"+o.title )
        self.init()
        id = self.studyController.store_study(o)
        o.id = id
        return o


    @expose(RestAnonymizedSubject)
    @validate(RestAnonymizedSubject)
    def handle_save_anonymizedSubject(self, o):
        logging.debug( "received new anonymized subject"+o.SID )
        self.init()
        id = self.anonymizedSubjectController.store_subject(o)
        o.id = id
        return o

    @signature(RestAnonymizedSubject, unicode)
    def handle_get_anonymized_subject(self, sid):
        self.init()
        return self.anonymizedSubjectController.get_subject(sid)

    @signature(RestSDIS, unicode)
    def handle_get_SDIS(self, sdisid):
        logging.debug( "Querying db for sdis with id "+ sdisid)
        self.init()
        return self.sdisController.get_SDIS(sdisid)

    @signature([RestSDIS], unicode)
    def handle_get_SDIS_by_study(self, studyid):
        logging.debug( "Querying db for studies matching "+ studyid)
        self.init()
        return self.sdisController.get_SDIS_by_study(studyid)

    @signature([RestData], unicode)
    def handle_get_data_by_sdis(self, sdisid):
        logging.debug( "Querying db for data in sdis with id "+ sdisid)
        self.init()
        return self.sdisController.get_data_in_sdis(sdisid)
    




    @expose(PackageContent)
    def newPackageContent(self):
        p = PackageContent()
        p.filename = ''
        p.content = ''
        return p



    @expose(PackageContent)
    @validate(PackageContent)
    def handle_capture_upload(self, o):
        logging.debug( "received "+o.filename )     

        with open(config.temp_dir+'/'+o.filename, "wb") as fh:
            fh.write(o.content.decode('base64'))

            o.content = '' # empty because it can be huge on the response.
        # delegate the content processing to the corresponding controller.
        self.init()
        id = self.sdisController.upload_packed_content(config.temp_dir, o.filename)
        logging.debug("Successful upload ("+id+")")
        o.id = id
        return o







