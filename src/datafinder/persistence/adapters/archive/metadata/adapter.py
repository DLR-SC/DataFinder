#
# Created: 29.06.2009 meinel <michael.meinel@dlr.de>
# Changed: $Id: adapter.py 4563 2010-03-24 13:19:14Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
This module implements a MetadataStorer that is able to write the
meta data of an item into separated property files. 
"""


__version__ = "$LastChangedRevision: 4563 $"


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
