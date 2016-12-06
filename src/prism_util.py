import zipfile as zf
import datetime
import prism_config as config
import os
from prism_model import *

import logging

class SubjectCaptureUnpacker:
    def __init__(self):
        config.connect()

    def unpack_study(self, dir_path, packed_filename):
        '''
        Returns the Study obj, AnonymizedSubject obj, Capture obj, a list with Data objs and the full path where the package were extracted.
        '''
        logging.debug("Extracting received content")
        packedContentPath = self.extract_to_temporary_dir(dir_path, packed_filename)
        # open META.INFO and check content
        logging.debug("Checking META.INFO file")
        metainfo = open(packedContentPath + os.sep + 'META.INFO')

        pversion = metainfo.readline().strip()
        studyid = metainfo.readline().strip().split(',')[1]
        sbjid = metainfo.readline().strip().split(',')[1]
        
        logging.debug("Locating study with "+studyid+" with subject "+sbjid)
        
        is_pacient = False
        if metainfo.readline().strip() == 'P':
            is_pacient = True


        dtcapture_date = map(int, metainfo.readline().strip().split(",")[1].split("-") )
        dtcapture_date = datetime.datetime(dtcapture_date[0], dtcapture_date[1], dtcapture_date[2])

        labels = metainfo.readline().strip().split(",")[1:]

        assert( 'DATA:' == metainfo.readline().strip()) # DATA LINE

        logging.debug("File looks ok. Verifying packed content...")
        # check content
        # ...
        lNotFound = []
        lData = []
        for c in metainfo:
            logging.debug("Fields found:"+str(len(c.strip().split(','))))
            ftype, fsize, fpath, fname, meta = c.strip().split(',')
            if not os.path.exists(packedContentPath + os.sep + fpath + os.sep + fname):
                lNotFound.append( fname )
            else:
                enc_fields = {}
                fields = meta.split(" ") #pares llave valor
                for f in  fields:
                    k,v = f.split(':')
                    #v = odm.fields.BinaryField( v.replace("JUMP", "\n").replace("COMMA", ",").replace("SPACE", " ").replace("2DOTS", ":") )
                    enc_fields[k] = v
                lData.append( (ftype, fsize, fname, enc_fields))

        assert( len(lNotFound) == 0 ) #check that all files were added.
        metainfo.close()
    
        logging.debug("Declared data match the contained file list.")
        # get objects
        logging.debug("Getting Study and Subject info")
        st = Study.objects(id=studyid)
        assert( st.count() > 0 )
        st = st.first()

        sbj = AnonymizedSubject.objects(SID=sbjid)
        assert( sbj.count() > 0)
        sbj = sbj.first()
        # create capture and data objects
        logging.debug("Creating SubjectDataInStudy")
        sc = SubjectDataInStudy(in_study=st, subject=sbj, is_pacient=is_pacient, capture_date=dtcapture_date, labels=labels)
        logging.debug("With tags..."+str(sc.labels) )

        lDataObjs = []
        for dtype, dsize, dname, enc_fields in lData:
            dt = Data(datatype=dtype, filename=dname, size=dsize, capture_date = dtcapture_date, labels=labels, deidentified_fields = enc_fields)
            lDataObjs.append( dt )
        # returns the Study obj, AnonymizedSubject obj, Capture obj, a list with Data objs and the full path where the package were extracted.
        return st, sbj, sc, lDataObjs, packedContentPath

    def extract_to_temporary_dir(self, dir_path, packed_filename):
        '''
        Extracts all files to a temporary directory and returns its full path
        '''
        filepath = dir_path + os.sep + packed_filename
        packedFile = zf.ZipFile(filepath)
        if 'META.INFO' not in packedFile.namelist():
            logging.error("The file "+packed_filename+" is not well formed. META.INFO file is missing")
            return none
        fldname = config.temp_dir + os.sep + self.get_new_folder_name()
        assert( not os.path.exists(fldname) )
        os.makedirs( fldname )
        logging.debug("Extracting files to directory "+fldname)
        packedFile.extractall( fldname ) 
        packedFile.close()
        return fldname



    def get_new_folder_name(self):
        '''
        Creates a new folder name based on current datetime.
        '''
        dt = datetime.datetime.now()
        folder_name = '{0}{1}{2}_{3}{4}{5}_{6}'.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        return folder_name
