#CONFIGURATION DIRECTIVES
import mongoengine as odm

# mongo
mongo_ip_address='localhost'
#mongo_port=32768
#mongo_ip_address='127.0.0.1'
mongo_port=27017

# app
bind_port=8080
bind_address='10.100.49.123'
version=1.0
temp_dir='/tmp'
data_dir='/home/prismed/prism_root'
rsakey='/home/prismed/prismed_key.pem'

def connect():
    #odm.connect('prism') # running as a localhost
    odm.connect('prism', host=mongo_ip_address, port=mongo_port)
