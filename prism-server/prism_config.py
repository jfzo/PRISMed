#CONFIGURATION DIRECTIVES
import mongoengine as odm

# mongo
mongo_ip_address='192.168.99.100'
mongo_port=32768
#mongo_ip_address='127.0.0.1'
#mongo_port=27017

# app
bind_port=8080
#bind_address='10.0.2.15'
bind_address='127.0.0.1'
version=1.0
temp_dir='/tmp'
#data_dir='/home/juan/prism_root'
data_dir='/tmp/prism_root'
rsakey='/tmp/prismed_key.pem'

def connect():
    #odm.connect('prism')
    odm.connect('prism', host=mongo_ip_address, port=mongo_port)
