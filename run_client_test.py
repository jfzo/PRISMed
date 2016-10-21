import sys, os
sys.path.append( os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))) )

from suds.client import Client
from suds import TypeNotFound
import base64

from prism_model import *
import prism_config as config
import time
from datetime import datetime
from pymongo import MongoClient
import zipfile

'''
CLEAR THE DATABASE FIRST
'''
#client = MongoClient()
client = MongoClient("mongodb://"+config.mongo_ip_address+":"+str(config.mongo_port))
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
url = 'http://'+config.bind_address+':'+str(config.bind_port)+'/prism/api.wsdl'
try:
    client = Client(url, cache=None)
except TypeNotFound:
    client = Client(url, cache=None)

'''
CREATE A SUBJECT AND A STUDY
'''
p = client.factory.create('ns0:RestStudy')
p.title="This is the first study"
p.metadata="This study is related to aneurism images."
p.physiological_st = "brain"
p.data_type_in_study='image'
p.modalities="MR,FMRI"

p = client.service.handle_save_study(p) # updated with the ID
study_id = p.id


asub = client.factory.create('ns0:RestAnonymizedSubject')
asub.SID = '4e8e2b6c6328502764b1857e7d925dd6'
asub.gender = 'M'
asub = client.service.handle_save_anonymizedSubject(asub)
subject_id = asub.SID

'''
CREATE A META.INFO WITH THE INFORMATION ABOVE AND PACK IT INTO A ZIP FILE
'''
is_pacient=False
data_source_dir="/home/juan/Descargas/Ax_FSPGR_3D_7/DATA/"
#data_source_dir="/Volumes/SSDII/Users/juan/Downloads/Ax_FSPGR_3D_7/DATA"

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
    metainfo.write('image,{0},DATA,{1}\n'.format(s,f) )
metainfo.close()
zipf.write('/tmp/META.INFO', 'META.INFO')
zipf.close()


'''
CREATE A PACKAGE, OPEN THE ZIP FILE AND SEND IT 
'''
with open("/tmp/Ax_FSPGR_3D_7.zip")  as zip_file:
    encoded_string = base64.b64encode(zip_file.read())




pc = client.service.newPackageContent()
pc.filename = 'Ax_FSPGR_3D_7.zip'
pc.content = encoded_string
pc = client.service.handle_capture_upload( pc )
print "A new Subject capture has been created ("+pc.id+")"

