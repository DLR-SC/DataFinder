#
# Created: 28.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: identifier_mapping_test.py 3824 2009-03-01 13:56:03Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Test cases for the meta data identifier mapping.
"""


import unittest

from webdav.Constants import NS_DAV, PROP_CREATION_DATE, PROP_LAST_MODIFIED, PROP_CONTENT_LENGTH, \
                             PROP_CONTENT_TYPE, PROP_OWNER, PROP_DISPLAY_NAME

from datafinder.persistence.adapters.webdav_.metadata import identifier_mapping
from datafinder.persistence.metadata.constants import CREATION_DATETIME, MODIFICATION_DATETIME, \
                                                      OWNER, MIME_TYPE, SIZE


__version__ = "$LastChangedRevision: 3824 $"


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
