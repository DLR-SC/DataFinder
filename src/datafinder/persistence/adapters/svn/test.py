'''
Created on 02.02.2011

@author: scha_pt
'''
from datafinder.persistence.adapters.svn.factory import FileSystem

import json

class BaseConfig(object):
    
    def __init__(self, baseUri, uriScheme, username, password, workingCopyPath):
        self.baseUri = baseUri
        self.uriScheme = uriScheme
        self.username = username
        self.password = password
        self.workingCopyPath = workingCopyPath
        
if __name__ == "__main__":
    
    baseUri = "https://svn-dmz.sistec.dlr.de/svn/students/patrick-schaefer/"
    workingCopyPath = "C:\Dokumente und Einstellungen\scha_pt\.datafinder"
    #baseUri = "https://svn.sistec.dlr.de/svn/xps-data-ppt/trunk/as-rpt/70_student%20research/1998/"
    #username = "f_xps4cf"
    #password = "newPW765"
    username = "scha_pt" 
    password = "k@trin1534"
    modelIdentifier = "datafinder.persistence.adapters.svn.author.AuthorProperty"

    baseConfig = BaseConfig(baseUri, "svn", username, password, workingCopyPath)
    fileSystem = FileSystem(baseConfig)
    #datastore = fileSystem.createDataStorer("/datafinder/test.pdf")
    #datastore.createResource()
    metadata = fileSystem.createMetadataStorer("/datafinder/test.pdf")
    
    #properties = {u'title': u'Other', u'filePath': u'trunk/as-rpt/99_other', u'summary': u'', u'nasaCategories': None, u'authors': [{u'lastName': u'Melber-Wilkending', u'uid': u'ea5i', u'firstName': u'Stefan', u'eMail': u'Stefan.Melber@dlr.de'}, {u'lastName': u'Ronzheimer', u'uid': u'ea07', u'firstName': u'Arno', u'eMail': u'Arno.Ronzheimer@dlr.de'}, {u'lastName': u'Rudnik', u'uid': u'ea1g', u'firstName': u'Ralf', u'eMail': u'Ralf.Rudnik@dlr.de'}], u'version': u'', u'documentType': u'', u'keywords': [], u'tauCategories': []}
    properties = {u'title': u'Other', u'filePath': u'trunk/as-rpt/99_other', u'summary': u'', u'nasaCategories': None, u'authors': {u'lastName': u'Melber-Wilkending', u'uid': u'ea5i', u'firstName': u'Stefan', u'eMail': u'Stefan.Melber@dlr.de'}, u'version': u'', u'documentType': u'', u'keywords': [], u'tauCategories': []}


    #metadata.update(properties)
     
    #print metadata
    property =  metadata.retrieve()
    print property
    #print metadata.retrieve()
    value = property["authors"]
    print value
    print value.persistedValue
    print value.value
    
    #print json.loads("{\"version\" : \"\", \"summary\" : \"\", \"filePath\" : \"trunk/as-rpt/99_other\", \"title\" : \"Other\", \"keywords\" : [ ], \"documentType\" : \"\", \"authors\" : [ {\"uid\" : \"ea5i\", \"eMail\": \"Stefan.Melber@dlr.de\", \"lastName\" : \"Melber-Wilkending\", \"firstName\" : \"Stefan\"}, {\"uid\" : \"ea07\", \"eMail\" : \"Arno.Ronzheimer@dlr.de\", \"lastName\" : \"Ronzheimer\", \"firstName\" : \"Arno\"}, {\"uid\" : \"ea1g\", \"eMail\" : \"Ralf.Rudnik@dlr.de\", \"lastName\" : \"Rudnik\", \"firstName\" : \"Ralf\"}], \"tauCategories\" : [ ], \"nasaCategories\" : null}")
    
    
