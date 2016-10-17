from wsme import WSRoot, expose, validate
import logging

from suds.client import Client
import base64

import sys, os

# "/Volumes/SSDII/Users/juan/Downloads/Ax_FSPGR_3D_7.zip"

if len(sys.argv) < 3:
    print("Not enough parameters")
    print("Usage:"+sys.argv[0]+" path_to_zip_file name_of_the_zip_file")
    sys.exit()

f_path = sys.argv[1]+os.sep+sys.argv[2]

logging.debug("Opening file "+f_path)

with open(f_path,'rb') as zip_file:
    encoded_string = base64.b64encode(zip_file.read())

url = 'http://127.0.0.1:8080/prism/api.wsdl'
logging.debug("Opening connection to server at "+url)

client = Client(url, cache=None)
client = Client(url, cache=None)
pc = client.service.newPackageContent()

pc.filename = sys.argv[2]
pc.content = encoded_string
client.service.handle_capture_upload( pc )
logging.debug("Transfer done!")
