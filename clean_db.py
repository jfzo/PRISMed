import sys, os

sys.path.append( os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))) )

from pymongo import MongoClient
client = MongoClient()
#client = MongoClient("mongodb://192.168.99.100:32768")
db = client.prism

db.data.drop()
db.anonymized_subject.drop()
db.study.drop()
db.modality.drop()
db.subject_data_in_study.drop()


