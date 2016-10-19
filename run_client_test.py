import sys, os
sys.path.append( os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))) )

from suds.client import Client
from suds import TypeNotFound
import base64

from prism_model import *
import time
from datetime import datetime
from pymongo import MongoClient
import zipfile

'''
CLEAR THE DATABASE FIRST
'''
client = MongoClient()
#client = MongoClient("mongodb://192.168.99.100:27017")
db = client.prism

db.data.drop()
db.anonymized_subject.drop()
db.study.drop()
db.modality.drop()
db.subject_data_in_study.drop()


# ####################################
# CLIENT ROUTINE


'''
CONNECT TO THE SERVER
'''
try:
    client = Client(url, cache=None)
except TypeNotFound:
    client = Client(url, cache=None)

'''
CREATE A SUBJECT AND A STUDY
'''



'''
CREATE A META.INFO WITH THE INFORMATION ABOVE AND PACK IT INTO A ZIP FILE
'''
data_source_dir="/home/juan/Descargas/Ax_FSPGR_3D_7/DATA/"
package_fname="Ax_FSPGR_3D_7.zip"
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
    metainfo.write('IM,{0},DATA,{1}\n'.(s,f) )
metainfo.close()
zipf.write('/tmp/META.INFO', 'META.INFO')
zipf.close()


'''
CREATE A PACKAGE, OPEN THE ZIP FILE AND SEND IT 
'''
with open("/home/juan/Descargas/Ax_FSPGR_3D_7.zip")  as zip_file:
    encoded_string = base64.b64encode(zip_file.read())
url = 'http://127.0.0.1:8080/prism/api.wsdl'



pc = client.service.newPackageContent()
pc.filename = 'Ax_FSPGR_3D_7.zip'
pc.content = encoded_string
client.service.handle_capture_upload( pc )

