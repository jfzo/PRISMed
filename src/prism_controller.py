#import wsme
#from wsme.types import Enum, binary
#from wsme.types import UserType
from wsme import WSRoot, expose, validate
import prism_config as config
from prism_util import SubjectCaptureUnpacker
from prism_model import *
import time
from datetime import datetime
import logging


class SubjectCaptureUploadController:
    def __init__(self):
        logging.debug("Initializing SubjectCaptureUploadController")


    def upload_packed_content(self, dir_path, file_name):
        #process the file
        logging.debug("File "+dir_path+"/"+file_name+" uploaded.")
        unpacker = SubjectCaptureUnpacker()
        st, sbj, sdis, lDataObjs, packedContentPath = unpacker.unpack_study(dir_path, file_name)

        logging.debug("Identifying repository path")
        # store data files... path is formed by 
        locpath = st.physiological_st + os.sep + st.data_type_in_study + os.sep
        modalities = []
        for m in st.modalities:
            modalities.append( m.name )
        modalities.sort()
        locpath += '+'.join( modalities ) + os.sep + str(st.id) + os.sep
        #check study directory
        if not os.path.exists(locpath):
            os.makedirs(locpath)

        if sbj.is_pacient:
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
        # Data objects into DB and move the data
        for d in lDataObjs: # this block can easily be parallelized
            d.parent_sdis = sdis
            d.location = locpath
            # move file packedContentPath/filename to d.location/d.filename
            os.rename(packedContentPath + os.sep + filename, config.data_dir + os.sep + d.location + os.sep + d.filename) 
            d.checksum = mf5(config.data_dir + os.sep + d.location + os.sep + d.filename)
            d.save()


        def md5(self, fname):
            hash_md5 = hashlib.md5()
            with open(fname, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
class StudyController:
    def __init__(self):
        logging.debug("Initializing SubjectCaptureUploadController")
        config.connect()
        
    def store_study(self, s):
        #create model object, save and return id
        today = datetime.fromtimestamp(time.time())
        metadata = unicode
        physiological_st = unicode
        data_type_in_study = unicode
        modalities = unicode # comma separated list of strings
        
        mods = s.modalities.lower().split(',')
        lMods = []
        for m in mods:
            #search modality or create a new one
            qmod = Modality.objects()
            if qmod.count() > 0:
                lMods.append( qmod.first() )
            else:
                newmod = Modality(name=m).save()
                lMods.append( newmod )
        
        st = Study(title=s.title, date_added=today, metadata=s.metadata, physiological_st=s.physiological_st, 
        data_type_in_study=s.data_type_in_study, modalities=lMods).save()
        
        return st.id
        
class AnonymizedSubjectController:
        
            
#### WSDL Service Interface

class PackageContent(object):
    filename = unicode
    content = unicode

    def __repr__(self):
        return "PackageContent(%s, %s)" % (
            self.filename, self.content
        )


class RestStudy:
    title = unicode
    #date_added = unicode
    metadata = unicode
    physiological_st = unicode
    data_type_in_study = unicode
    modalities = unicode # comma separated list of strings

    def __repr__(self):
        return "RestStudy(%s, %s, %s, %s, %s)" % (
            self.title, self.metadata, self.physiological_st, self.data_type_in_study, self.modalities
        )
        
class RestAnonymizedSubject:
    SID = unicode
    gender = unicode
    
    def __repr__(self):
        return "RestAnonymizedSubject(%s, %s)" % (
            self.SID, self.gender
        )
    
            

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
    
    captureController = None
    studyController = None
    anonymizedSubjectController = None
    
    def init(self):
        if self.captureController == None:
            logging.debug('Creating subjectCaptureController')
            self.captureController = SubjectCaptureUploadController()
            logging.debug('Creating studyController')
            self.studyController = StudyController()
            logging.debug('Creating anonymizedSubjectController')
            self.anonymizedSubjectController = AnonymizedSubjectController()


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
    
    @expose()
    @validate(RestStudy)
    def handle_save_study(self, o):
        logging.debug( "received new study"+o.title )
        self.init()
        self.anonymizedSubjectController.store_study(o)

    @expose(RestAnonymizedSubject)
    def newRestAnonymizedSubject(self):
        aSub = RestAnonymizedSubject()
        aSub.SID = ''
        aSub.gender = ''
        return aSub



    @expose(PackageContent)
    def newPackageContent(self):
        p = PackageContent()
        p.filename = ''
        p.content = ''
        return p



    @expose()
    @validate(PackageContent)
    def handle_capture_upload(self, o):
        logging.debug( "received "+o.filename )     

        with open(config.temp_dir+'/'+o.filename, "wb") as fh:
            fh.write(o.content.decode('base64'))

        # delegate the content processing to the corresponding controller.
        logging.debug("HANDLE_CAPTURE_UPLOAD")
        self.init()
        self.captureController.upload_packed_content(config.temp_dir, o.filename)

        return len(o.content)







