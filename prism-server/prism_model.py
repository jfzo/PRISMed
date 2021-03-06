#!/usr/bin/python
#-*- coding: utf-8 -*-

import mongoengine as odm

#odm.connect('prism')
#odm.connect('prism', host='192.168.99.100', port=32768) # for DOCKER




class AnonymizedSubject(odm.Document):
    SID = odm.StringField(max_length=100,  unique=True)
    gender = odm.StringField(max_length=50)


class PhysiologicalStructure(odm.Document):
    name = odm.StringField(max_length=50,  required=True, unique=True)

    
class Modality(odm.Document):
    name = odm.StringField(max_length=50,  required=True, unique=True)
    information = odm.StringField(max_length=100)

class Study(odm.Document):
    title = odm.StringField(max_length=100, required=True)
    date_added = odm.DateTimeField(required=True)
    description = odm.StringField(max_length=1000)    
    physiological_st = odm.ReferenceField(PhysiologicalStructure)
    data_type_in_study = odm.StringField(max_length=50, required=True)#eventually isolate
    modalities = odm.ListField(odm.ReferenceField(Modality), default=list)
    #captures = odm.ListField(odm.EmbeddedDocumentField(SubjectDataInStudy), default=list)

    def init(self, ):
        pass

class SubjectDataInStudy(odm.Document):
    is_pacient = odm.BooleanField(default=False)
    in_study = odm.ReferenceField(Study, required=True)
    subject = odm.ReferenceField(AnonymizedSubject, required=True)
    capture_date = odm.DateTimeField(required=True)
    labels = odm.ListField(odm.StringField(), default=list)

    def init(self, ):
        pass


class Data(odm.Document):
    annotations = odm.StringField(max_length=200)
    location = odm.StringField(max_length=500, required=True)
    filename = odm.StringField(max_length=50, required=True)
    size = odm.IntField(required=True)
    checksum = odm.StringField(required=True, unique=True)
    datatype = odm.StringField(choices=('image','signal'), max_length=20, required=True) #set by the inherited class.
    parent_sdis = odm.ReferenceField(SubjectDataInStudy, required=True)
    labels = odm.ListField(odm.StringField(), default=list)
    capture_date = odm.DateTimeField(required=True)   #meta = {'allow_inheritance':True}
    deidentified_fields = odm.DictField(default=dict())
    #meta = {'abstract':True}

    #def associate_to_capture(self, c):
    #    self.capture = c

class User(odm.Document):
    pass

