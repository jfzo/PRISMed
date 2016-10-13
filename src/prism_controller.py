import wsme
from wsme import WSRoot
from wsme.types import Enum, binary
from wsme.types import UserType
from wsme import WSRoot, expose, validate, signature


#CONFIGURATION DIRECTIVES
ip_address='10.100.45.123'
bind_port='8080'
temp_dir='/tmp'


class SubjectCaptureUploadController:
    def __init__(self):
        pass

    def upload_packed_content(self, ):
        pass

    def save_model(self, ):
        pass



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

    import base64
    with open("<PATH_TO_THE_CAPTURE_ZIP_FILE>/Ax_FSPGR_3D_7.zip",'rb') as zip_file:
        encoded_string = base64.b64encode(zip_file.read())

    url = 'http://10.100.45.123:8080/ws/api.wsdl'
    client = Client(url, cache=None)
    pc = client.service.create()

    pc.filename = 'Ax_FSPGR_3D_7.zip'
    pc.content = encoded_string
    client.service.upload_packed_content( pc )
    '''
    
    captureController = SubjectCaptureUploadController = None
    
    def init(self):
        if self.captureController == None:
            self.captureController = SubjectCaptureUploadController()



    @expose(PackageContent)
    def create(self):
        p = PackageContent()
        p.filename = ''
        p.content = ''
        return p

    @expose()
    @validate(PackageContent)
    def handle_capture_upload(self, o):
        logging.debug( "received "+o.filename )     

        with open(temp_dir+'/'+o.filename, "wb") as fh:
            fh.write(o.content.decode('base64'))

        # delegate the content processing to the corresponding controller.
        self.init()
        captureController.upload_packed_content(temp_dir+'/'+o.filename)

        return len(o.content)







