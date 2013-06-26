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
Implements test cases for the WebDAV-specific file system factory.
"""


import unittest

from webdav.Connection import WebdavError

from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.adapters.webdav_.principal_search.adapter import PrincipalSearchWebdavAdapter
from datafinder.persistence.adapters.webdav_ import factory
from datafinder.persistence.adapters.webdav_.metadata.adapter import MetadataWebdavAdapter
from datafinder.persistence.adapters.webdav_.data.adapter import DataWebdavAdapter
from datafinder.persistence.adapters.webdav_.privileges.adapter import PrivilegeWebdavAdapter, SimplePrivilegeWebdavAdapter
from datafinder.persistence.adapters.webdav_.search.adapter import SearchWebdavAdapter
from datafinder.persistence.search.searcher import NullSearcher
from datafinder.persistence.principal_search.principalsearcher import NullPrincipalSearcher
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


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
        self.assertTrue(isinstance(self._factory.createPrivilegeStorer("identifier"), SimplePrivilegeWebdavAdapter))
        self.assertFalse(isinstance(self._factory.createPrivilegeStorer("identifier"), PrivilegeWebdavAdapter))
        
        self._factory._hasPrivilegeSupport = True
        self.assertFalse(isinstance(self._factory.createPrivilegeStorer("identifier"), SimplePrivilegeWebdavAdapter))
        self.assertTrue(isinstance(self._factory.createPrivilegeStorer("identifier"), PrivilegeWebdavAdapter))
        
    def testCreatePrincipalSearcher(self):
        """ Tests the creation of a WebDAV specific principal searcher. """
        
        self.assertTrue(isinstance(self._factory.createPrincipalSearcher(), NullPrincipalSearcher))
        
        self._factory._configuration.userCollectionUrl = "http://server.de/users"
        self._factory._configuration.groupCollectionUrl = "http://server.de/groups"
        self.assertTrue(isinstance(self._factory.createPrincipalSearcher(), PrincipalSearchWebdavAdapter))
        
    def testCreateSearcher(self):
        """ Tests the creation of a WebDAV specific searcher. """
        
        self.assertTrue(isinstance(self._factory.createSearcher(), NullSearcher))
        self.assertTrue(isinstance(self._factory.createSearcher(), SearchWebdavAdapter))
        
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
