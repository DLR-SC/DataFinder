#
# Created: 28.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory_test.py 4333 2009-11-10 16:33:34Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements test cases for the WebDAV-specific file system factory.
"""


import unittest

from webdav.Connection import WebdavError

from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.privileges.privilegestorer import NullPrivilegeStorer
from datafinder.persistence.adapters.webdav_ import factory
from datafinder.persistence.adapters.webdav_.metadata.adapter import MetadataWebdavAdapter
from datafinder.persistence.adapters.webdav_.data.adapter import DataWebdavAdapter
from datafinder.persistence.adapters.webdav_.privileges.adapter import PrivilegeWebdavAdapter
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4333 $"


class _CollectionStorerMock(object):
    """ Mocks a collection storer. """

    def __init__(self):
        """ Constructor. """
        
        self.result = True
        self.raiseError = False
    
    def _getterMock(self):
        """ Raises a WebDAV-error. """
    
        if self.raiseError:
            raise WebdavError("")
        else:
            return self.result
    
    daslBasicsearchSupportAvailable = property(_getterMock)
    aclSupportAvailable = property(_getterMock)


class FileSystemTestCase(unittest.TestCase):
    """ Test cases for WebDAV file system factory. """ 

    def setUp(self):
        """ Mocks an utility functionality. """
        
        self._collectionStorerMock = _CollectionStorerMock()
        factory.createCollectionStorer = self._createCollectionStorerMock
        factory.FileSystem._getConnectionPool = SimpleMock(SimpleMock())
        self._factory = factory.FileSystem(BaseConfiguration("http://test.de/mypath/"))
    
    def _createCollectionStorerMock(self, *_, **__):
        """ Mocks utility function for creation of collection storer. """
        
        return self._collectionStorerMock
 
    def testCreateDataStorer(self):
        """ Tests the creation of a WebDAV specific data storer. """
        
        self.assertTrue(isinstance(self._factory.createDataStorer("identifier"), DataWebdavAdapter))
    
    def testCreateMetadataStorer(self):
        """ Tests the creation of a WebDAV specific meta data storer. """
        
        self.assertTrue(isinstance(self._factory.createMetadataStorer("identifier"), MetadataWebdavAdapter))
    
    def testCreatePrivilegeStorer(self):
        """ Tests the creation of a WebDAV specific privilege data storer. """
        
        self._factory._hasPrivilegeSupport = False
        self.assertTrue(isinstance(self._factory.createPrivilegeStorer("identifier"), NullPrivilegeStorer))
        self.assertFalse(isinstance(self._factory.createPrivilegeStorer("identifier"), PrivilegeWebdavAdapter))
        
        self._factory._hasPrivilegeSupport = True
        self.assertTrue(isinstance(self._factory.createPrivilegeStorer("identifier"), NullPrivilegeStorer))
        self.assertTrue(isinstance(self._factory.createPrivilegeStorer("identifier"), PrivilegeWebdavAdapter))
        
    def testHasMetadataSearchSupport(self):
        """ Tests the default behavior of the hasMetadataSearchSupport method. """
        
        self._collectionStorerMock.raiseError = False
        self._collectionStorerMock.result = True
        self.assertTrue(self._factory.hasMetadataSearchSupport)
       
    def testHasMetadataSearchSupportAndCaching(self):
        """ Tests the default behavior of the hasMetadataSearchSupport method and demonstrates the caching. """
        
        self._collectionStorerMock.raiseError = False
        self._collectionStorerMock.result = False
        self.assertFalse(self._factory.hasMetadataSearchSupport)
        
        self._collectionStorerMock.result = True
        self.assertFalse(self._factory.hasMetadataSearchSupport)
    
    def testHasMetadataSearchSupportError(self):
        """ Tests the error handling of the hasMetadataSearchSupport method. """
        
        self._collectionStorerMock.raiseError = True
        self.assertFalse(self._factory.hasMetadataSearchSupport)
    
    def testHasPrivilegeSupport(self):
        """ Tests the default behavior of the hasMetadataSearchSupport method. """
        
        self._collectionStorerMock.raiseError = False
        self._collectionStorerMock.result = True
        self.assertTrue(self._factory.hasPrivilegeSupport)
        
    def testHasPrivilegeSupportAndCaching(self):
        """ Tests the default behavior of the hasMetadataSearchSupport method and demonstrates the caching. """
        
        self._collectionStorerMock.raiseError = False
        self._collectionStorerMock.result = False
        self.assertFalse(self._factory.hasPrivilegeSupport)
        
        self._collectionStorerMock.result = True
        self.assertFalse(self._factory.hasPrivilegeSupport)

    def testHasPrivilegeSupportError(self):
        """ Tests the error handling of the hasMetadataSearchSupport method. """
        
        self._collectionStorerMock.raiseError = True
        self.assertFalse(self._factory.hasPrivilegeSupport)
