#CONFIGURATION DIRECTIVES
import logging
import mongoengine as odm

version=1.0
ip_address='10.100.45.123'
bind_port='8080'
temp_dir='/tmp'
data_dir='/tmp/prism_root'

def connect():
    odm.connect('prism')
    #odm.connect('prism', host='192.168.99.100', port=32768)
