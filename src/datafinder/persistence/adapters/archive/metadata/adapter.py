# $Filename$ 
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
This module implements a MetadataStorer that is able to write the
meta data of an item into separated property files. 
"""


__version__ = "$Revision-Id:$" 


import codecs
try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree
from zipfile import ZipInfo

from datafinder.persistence.metadata.metadatastorer import NullMetadataStorer
from datafinder.persistence.metadata.value_mapping import MetadataValue, \
                                                          getPersistenceRepresentation


_ZIP_FILENAME_CODEC = codecs.lookup("CP437")


class MetadataArchiveAdapter(NullMetadataStorer, object):
    """
    Implementation of the L{NullMetadataStorer} scheme for ZIP archives. This
    implementation keeps the meta data in a XML format in the comment associated
    with the respective item.
    """
    
    def __init__(self, identifier, archive, password=None):
        """ Constructor.
        
        @param identifier: The identifier of the associated item.
        @type identifier: C{unicode}
        @type archive: The zip archive that should be used for storage.
        @type archive: C{zipfile.ZipFile}
        @param password: If the archive is encrypted, the password should be given here.
        @type password: C{string}
        """
        
        super(MetadataArchiveAdapter, self).__init__(identifier)
        self._archive = archive
        self._password = password
        self._persistenceId = _ZIP_FILENAME_CODEC.encode(self.identifier, errors="ignore")[0] + ".xml"
        
    @staticmethod
    def _decodeMetadata(text):
        """ Decode meta data from a XML string.
        
        @param text: A string containing valid XML.
        @type text: C{string}
        @return: Deserialized meta data.
        @rtype: C{dict} mapping C{string} to
                L{MetadataValue<datafinder.persistence.metadata.value_mapping.MetadataValue>}
        """
        
        tree = etree.XML(text)
        result = dict()
        for propertyNode in tree.findall("property"):
            propertyName = propertyNode.attrib["name"]
            propertyValue = MetadataValue(propertyNode.text)
            result[propertyName] = propertyValue
        return result
    
    @staticmethod
    def _encodeMetadata(metadata):
        """ Encode meta data as XML document.
        
        @param metadata: The meta data
        @type metadata: C{dict}, mapping string to object 
        
        @return: A serialized XML document representing the meta data.
        @rtype: C{string}
        """
        
        tree = etree.Element("properties")
        for key in metadata:
            propertyNode = etree.Element("property", name=key)
            propertyNode.text = getPersistenceRepresentation(metadata[key])
            tree.append(propertyNode)
        return etree.tostring(tree)
    
    def retrieve(self, _=None):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>} """
        # fixme meinel: add propertyIds to filter retrieved properties
        
        try:
            return self._decodeMetadata(self._archive.open(self._persistenceId, "r", self._password).read())
        except KeyError:
            return dict()

    def _storeMetadata(self, encodedMetadata):
        """ This method stores back the given meta data.
        
        @param metadata: The dictionary with the metadata that should be stored.
        @type metadata: C{dict} mapping C{string} to
                        L{MetadataValue<datafinder.persistence.metadata.value_mapping.MetadataValue>}
        """
        
        try:
            info = self._archive.getinfo(self._persistenceId)
        except KeyError:
            info = ZipInfo(self._persistenceId)

        self._archive.writestr(info, encodedMetadata)

    def update(self, properties):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>} """

        metadata = self.retrieve()
        for key in metadata:
            if not key in properties:
                properties[key] = metadata[key].guessRepresentation()
            
        encodedMetadata = self._encodeMetadata(properties)
        self._storeMetadata(encodedMetadata)
    
    def delete(self, propertyIds):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>} """
    
        metadata = self.retrieve()
        properties = dict()
        for key in metadata:
            if not key in propertyIds:
                properties[key] = metadata[key].guessRepresentation()

        properties = self._encodeMetadata(properties)
        self._storeMetadata(properties)
