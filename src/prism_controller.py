#import wsme
#from wsme.types import Enum, binary
#from wsme.types import UserType
from wsme import WSRoot, expose, validate
import prism_config as config
from prism_util import SubjectCaptureUnpacker
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
#### WSDL Service Interface

class PackageContent(object):
    filename = unicode
    content = unicode

    def __repr__(self):
        return "PackageContent(%s, %s)" % (
            self.filename, self.content
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
    
    def init(self):
        if self.captureController == None:
            logging.debug('Creating subjectCaptureController')
            self.captureController = SubjectCaptureUploadController()



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







