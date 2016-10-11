#!/usr/bin/python
#-*- coding: utf-8 -*-

import mongoengine as odm

#odm.connect('prism')
#odm.connect('prism', host='192.168.99.100', port=32768) # for DOCKER




class AnonymizedSubject(odm.Document):
    SID = odm.StringField(max_length=20,  required=True, unique=True)
    gender = odm.StringField(max_length=50)


class Source(odm.Document):
    name = odm.StringField(max_length=50,  required=True, unique=True)
    information = odm.StringField(max_length=100)


class Data(odm.EmbeddedDocument):
    annotations = odm.StringField(max_length=200)
    location = odm.StringField(max_length=100, required=True)
    filename = odm.StringField(max_length=50, required=True)
    size = odm.IntField(required=True)
    checksum = odm.StringField(required=True)
    datatype = odm.StringField(choices=('Image','Signal'), max_length=20, required=True) #set by the inherited class.
    source = odm.ReferenceField(Source, required=True)

    #meta = {'allow_inheritance':True}
    #meta = {'abstract':True}

    #def associate_to_capture(self, c):
    #    self.capture = c



class Study(odm.Document):
    title = odm.StringField(max_length=50, required=True)
    date_added = odm.DateTimeField(required=True)
    metadata = odm.StringField(max_length=100)
    physiological_st = odm.StringField(max_length=50, required=True)#eventually isolate
    #captures = odm.ListField(odm.EmbeddedDocumentField(SubjectCapture), default=list)

    def init(self, ):
        pass

    def add_capture(self, c):
        self.captures.append(c)

class SubjectCapture(odm.Document):
    is_pacient = odm.BooleanField(default=False)
    in_study = odm.ReferenceField(Study, required=True)
    data = odm.ListField(odm.EmbeddedDocumentField(Data), default=list)
    subject = odm.ReferenceField(AnonymizedSubject, required=True)

    def init(self, ):
        pass



class User(odm.Document):
    pass

