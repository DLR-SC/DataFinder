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
from datafinder.core.configuration.dataformats import registry
from datafinder.persistence import factory
from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.adapters.webdav_.metadata import identifier_mapping


__version__ = "$Revision-Id:$" 


class PropertyConversion(object):
    """ Module to convert properties"""   
    _log = getDefaultLogger()
    
    def __init__(self, repositoryUri, user, password):
        self._conversionMap = {
                          "DataFinderType": u"____datatype____",
                          "DataFinderDataStore": u"____datastorename____",
                          "DataFinderModificationDate": u"____contentmodificationdatetime____",
                          "DataFinderCreationDate": u"____contentcreationdatetime____",
                          "DataFinderLength": u"____content.size____",
                          "DataFinderArchiveIdentifier": u"____contentidentifier____",
                          "DataFinderArchiveRetentionExeededDate": u"____archiveretentionexceededdatetime____",
                          "DataFinderArchiveRootCollection": u"____archiverootcollection____",
                          }
        
        self._dataFormatRegistry = registry.DataFormatRegistry()
        # Little trick to correctly set the link target WebDAV property
        identifier_mapping._logicalToPersistenceIdMapping["linkTarget"] = ("http://dlr.de/system/", 
                                                                           "linkTarget")
                
        fs = factory.createFileStorer(repositoryUri, 
                                      BaseConfiguration(repositoryUri, username=user, password=password))
        items = fs.getChildren()
        self._walk(items)
   
    def _walk(self, items):
        """ walk trough each element in the specified file system"""
                
        for item in items:
            mappedProperties = self._handle(item)
            if item.isCollection:
                self._walk(item.getChildren())
            item.updateMetaData(mappedProperties) #AttributeError: 'FileStorer' object has no attribute 'updateMetaData'

                           
    def _handle(self, item):
        """ convert the properties to the updated constants"""
        properties = item.retrieveMetadata()
        mappedProperties = item.retrieveMetadata()
        
        for key, value in properties.iteritems():
            if key in self._conversionMap:
                mappedProperties[self._conversionMap[key]] = value.value
            elif key == "DataFinderType" and not item.isCollection: # in 1.X exists no data format
                dataFormat = self._dataFormatRegistry.determineDataFormat(baseName=item.name)
                mappedProperties[u"____dataformat____"] = dataFormat
            elif key == "DataFinderOriginalResource": # it is a link in 1.X
                mappedProperties["linkTarget"] = value.value
        
        # For log file
        self._log.info(item.uri)
        self._log.info(properties)
        self._log.info(mappedProperties)
        self._log.info("Successfully updated item.")
        self._log.info("")
        
        # For console
        print item.uri
        print properties
        print mappedProperties
        print "item success"
        print ""
        return mappedProperties
       

if __name__ == "__main__":
    import sys
              
    if len(sys.argv) != 4:
        print("Usage: repositoryurl = <string>, username = <string>, password = <string>")
    else:
        PropertyConversion(sys.argv[1], sys.argv[2],  sys.argv[3])
        print("Successfully mapped")       
