# pylint: disable-msg=W0511, W0201
#
# Created: 28.11.2009 ney <Miriam.Ney@dlr.de>
# Changed: $Id: factory_test.py 4559 2010-03-23 15:20:18Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements test cases for the AmazonS3-specific file system factory.
"""


import unittest


from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.adapters.amazonS3 import factory
from datafinder.persistence.adapters.amazonS3.data.adapter import DataS3Adapter
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4559 $"


class FileSystemTestCase(unittest.TestCase):
    """ Test cases for Amazon S3 file system factory."""
    
    def setUp(self):
        """ Mocks an utility functionality. """
        
        factory.FileSystem._getConnection = SimpleMock(SimpleMock())
        factory.FileSystem._getConnectionPool = SimpleMock(SimpleMock())
        self._factory = factory.FileSystem(BaseConfiguration("http://s3.amazonaws.de/bucketname/keyname"))
       
    def testCreateDataStorer(self):
        """ Tests the creation of a AmazonS3 specific data storer. """
        
        self.assertTrue(isinstance(self._factory.createDataStorer("identifier"), DataS3Adapter))
