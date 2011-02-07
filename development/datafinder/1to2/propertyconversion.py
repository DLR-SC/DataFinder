# $Filename$$
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
# * Redistributions in binary form must reproduce the above copyright 
#   notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the 
#   distribution. 
#
# * Neither the name of the German Aerospace Center nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


""" 
Script to convert properties from a df 1.x repository to an df 2.x repository
"""

from datafinder.common.logger import getDefaultLogger
from datafinder.persistence import factory
from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.metadata.value_mapping import MetadataValue
from datafinder.persistence.adapters.webdav_.metadata import identifier_mapping
__version__ = "$Revision-Id:$" 

class PropertyConversion(object):
    #_log = getDefaultLogger()
    def __init__(self, repositoryuri, user, password):
        self.conversionTable ={
                          "DataFinderType" : u"____datatype____",
                          "DataFinderDataStore" : u"____datastorename____",
                          "DataFinderModificationDate": u"____contentmodificationdatetime____",
                          "DataFinderCreationDate" : u"____contentcreationdatetime____",
                          "DataFinderLength" : u"____content.size____",
                          "DataFinderArchiveIdentifier" : u"____contentidentifier____",
                          "DataFinderArchiveRetentionExeededDate": u"____archiveretentionexceededdatetime____",
                          "DataFinderArchiveRootCollection": u"____archiverootcollection____",
                          }
        fs = factory.createFileStorer(repositoryuri, BaseConfiguration(repositoryuri,username = user, password = password) )
        items = fs.getChildren()
        self.walkTheTree(items)
   
    def walkTheTree(self, treeItems):
        for item in treeItems:
            if item.isCollection:
                newProperties = self.workProperties(item)
                self.walkTheTree(item.getChildren())
                #item.updateMetaData(newProperties)
            elif item.isLeaf:
                newProperties = self.workProperties(item, "Leaf")
                #item.updateMetaData(newProperties)
            elif item.isLink:
                newProperties = self.workPropertiesLink(item.retrieveMetadata)
                #item.updateMetaData(newProperties)
                
    def workProperties(self, item, identifier = None):
        newProperties = {}
        conversionTable = self.conversionTable
        itemMetaData = item.retrieveMetadata()
        
        for k, v  in itemMetaData.iteritems():
            if k in conversionTable.keys():
                newProperties[conversionTable[k]] = v
                self.logToConsole(k, v, conversionTable[k])
            if k == "DataFinderType" and identifier == "Leaf":
                # implementation to find the correct dataformat
                newProperties[u"____dataformat____"] = v
                self.logToConsole(k, v,u"____dataformat____")
                
        return newProperties
    
    def workPropertiesLink(self, item):
        newProperties = {}
        itemMetaData = item.retrieveMetadata()
        #newProperties = self.workProperties(itemMetaData)
        
        for k,v in itemMetaData.iteritems():
            if k == "DataFinderOriginalResource":
                identifier_mapping._logicalToPersistenceIdMapping["linkTarget"] = ("http://dlr.de/system/","linkTarget")
                newProperties["linkTarget"] = v
                newProperties["____datatype____"]= "File"
                self.logToConsole(k, v, "linkTarget")
        
        return newProperties
    
    def logToConsole(self, oldkey, value, newkey):
        listValue = value.guessRepresentation()
        statement="OLDKEY:" + oldkey + " NEWKEY:" +newkey +" VALUE:" + str(listValue[0])
        #self._log.info(statement)
        print statement
       
username = "user"
password = "***"
repositoryurl = "test" #http://datafinder.dlr.de/repos/test/REL_1.2.1/data/
PropertyConversion(repositoryurl,  username, password)
