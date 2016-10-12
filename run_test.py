import sys, os

sys.path.append( os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))) )

from pymongo import MongoClient
client = MongoClient()
db = client.prism

db.data.drop()
db.anonymized_subject.drop()
db.study.drop()
db.source.drop()
db.subject_capture.drop()


#odm.connect('prism', host='192.168.99.100', port=32768) # for DOCKER

from prism_model import *
import time
from datetime import datetime

odm.connect('prism')

src1 = Source(name='EEG').save()
src2 = Source(name='TAC').save()


# define subjects
sbj1 = AnonymizedSubject(SID='6d4f105c1b68b13', gender='male').save()
sbj2 = AnonymizedSubject(SID='622dfeecf34075f', gender='female').save()
sbj3 = AnonymizedSubject(SID='be6eacf31198674', gender='female').save()
sbj4 = AnonymizedSubject(SID='c99ba9ec0203c87', gender='male').save()


today = datetime.fromtimestamp(time.time())
st1 = Study(title='Estudio numero 1', date_added=today, physiological_st='EEG').save()
# take the study id --> str(st1.id)

#Create capture for subject 1 in study 1
sc1 = SubjectCapture(in_study=st1, subject=sbj1)
sc1.save()
sc2 = SubjectCapture(in_study=st1, subject=sbj2)
sc2.save()
sc3 = SubjectCapture(in_study=st1, subject=sbj3)
sc3.save()
sc4 = SubjectCapture(in_study=st1, subject=sbj4)
sc4.save()
#create all the data  within the capture 1:
dt = Data(source=src1, datatype='Image', checksum='4dc8e0d8411fa6d4f105c1b68b1375d1', size=66, filename='image001.dcm', location='brain/image/eeg/'+str(st1.id)+'/subject/'+sc1.subject.SID, parent_capture=sc1).save()
#sc1.data.append(dt1)
dt = Data(source=src1, datatype='Image', checksum='3ac8e0d8411fa1a4t105c1b68b1375t9', size=66, filename='image002.dcm', location='brain/image/eeg/'+str(st1.id)+'/subject/'+sc1.subject.SID, parent_capture=sc1).save()
#sc1.data.append(dt2)

dt = Data(source=src2, datatype='Image', checksum='9ac8e0d8411fa1p4t105c1b68b7375t9', size=66, filename='image001.dcm', location='brain/image/eeg/'+str(st1.id)+'/subject/'+sc2.subject.SID, parent_capture=sc2).save()


dt = Data(source=src1, datatype='Image', checksum='4ac8e0d8411fa1o4t105c1b68b1375t9', size=66, filename='image001.dcm', location='brain/image/eeg/'+str(st1.id)+'/subject/'+sc3.subject.SID, parent_capture=sc3).save()

dt = Data(source=src2, datatype='Image', checksum='1ac8e0d8411fa1l4t105c1b68b1375t9', size=66, filename='image002.dcm', location='brain/image/eeg/'+str(st1.id)+'/subject/'+sc3.subject.SID, parent_capture=sc3).save()


dt = Data(source=src2, datatype='Image', checksum='3ac2e0d8411fanm4t105c1b68b1375t9', size=66, filename='image001.dcm', location='brain/image/eeg/'+str(st1.id)+'/subject/'+sc4.subject.SID, parent_capture=sc4).save()


