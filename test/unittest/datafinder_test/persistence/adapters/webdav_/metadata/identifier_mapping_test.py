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
Test cases for the meta data identifier mapping.
"""


import unittest

from webdav.Constants import NS_DAV, PROP_CREATION_DATE, PROP_LAST_MODIFIED, PROP_CONTENT_LENGTH, \
                             PROP_CONTENT_TYPE, PROP_OWNER, PROP_DISPLAY_NAME

from datafinder.persistence.adapters.webdav_.metadata import identifier_mapping
from datafinder.persistence.metadata.constants import CREATION_DATETIME, MODIFICATION_DATETIME, \
                                                      OWNER, MIME_TYPE, SIZE


__version__ = "$Revision-Id:$" 


_davNamespace = NS_DAV
_datafinderNamespace = "http://dlr.de/"


class IdentfierMappingTestCase(unittest.TestCase):
    """ Tests cases for meta data identifier mapping. """

    def testMapMetadataId(self):
        """ Demonstrates the behavior of the mapMetadataId function. """
        
        self.assertEquals(identifier_mapping.mapMetadataId("logicalId"), (_datafinderNamespace, "logicalId"))
        self.assertEquals(identifier_mapping.mapMetadataId(None), (_datafinderNamespace, None))
        
        self.assertEquals(identifier_mapping.mapMetadataId(CREATION_DATETIME), (_davNamespace, PROP_CREATION_DATE))
        self.assertEquals(identifier_mapping.mapMetadataId(MODIFICATION_DATETIME), (_davNamespace, PROP_LAST_MODIFIED))
        self.assertEquals(identifier_mapping.mapMetadataId(MIME_TYPE), (_davNamespace, PROP_CONTENT_TYPE))
        self.assertEquals(identifier_mapping.mapMetadataId(OWNER), (_davNamespace, PROP_OWNER))
        self.assertEquals(identifier_mapping.mapMetadataId(SIZE), (_davNamespace, PROP_CONTENT_LENGTH))
        
    def testMapPersistenceMetadataId(self):
        """ Demonstrates the behavior of the mapPersistenceMetadataId function. """
      
        self.assertEquals(identifier_mapping.mapPersistenceMetadataId((_datafinderNamespace, "logicalId")), "logicalId")
        self.assertEquals(identifier_mapping.mapPersistenceMetadataId((_datafinderNamespace, None)), None)
        
        self.assertEquals(identifier_mapping.mapPersistenceMetadataId((_davNamespace, PROP_CREATION_DATE)), CREATION_DATETIME)
        self.assertEquals(identifier_mapping.mapPersistenceMetadataId((_davNamespace, PROP_LAST_MODIFIED)), MODIFICATION_DATETIME)
        self.assertEquals(identifier_mapping.mapPersistenceMetadataId((_davNamespace, PROP_CONTENT_TYPE)), MIME_TYPE)
        self.assertEquals(identifier_mapping.mapPersistenceMetadataId((_davNamespace, PROP_OWNER)), OWNER)
        self.assertEquals(identifier_mapping.mapPersistenceMetadataId((_davNamespace, PROP_CONTENT_LENGTH)), SIZE)
        
        self.assertEquals(identifier_mapping.mapPersistenceMetadataId((_davNamespace, PROP_DISPLAY_NAME)), None)
