#CONFIGURATION DIRECTIVES
import logging
import mongoengine as odm

# mongo
#mongo_ip_address='192.168.99.100'
#mongo_port=32768
mongo_ip_address='127.0.0.1'
mongo_port=27017

# app
bind_port=8080
bind_address='10.0.2.15'
version=1.0
temp_dir='/tmp'
data_dir='/home/juan/prism_root'

def connect():
    #odm.connect('prism')
    odm.connect('prism', host=mongo_ip_address, port=mongo_port)
