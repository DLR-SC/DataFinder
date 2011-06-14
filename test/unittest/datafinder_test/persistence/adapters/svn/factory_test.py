# pylint: disable=W0212
# W0212: For test purposes it is fine to access protected members.
#
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
Implements test cases for the SVN-specific file system factory.
"""


import unittest


from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.common.connection.manager import ConnectionPoolManager
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.adapters.svn import connection_pool
from datafinder.persistence.adapters.svn import factory
from datafinder.persistence.adapters.svn.data.adapter import DataSubversionAdapter
from datafinder.persistence.adapters.svn.metadata.adapter import MetadataSubversionAdapter
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id$" 


class FileSystemTestCase(unittest.TestCase):

    def setUp(self):
        self._connectionMock = SimpleMock()
        self._createSvnConnectionMock = SimpleMock(self._connectionMock)
        connection_pool.util.createSubversionConnection = self._createSvnConnectionMock
        factory.FileSystem._connectionManager = ConnectionPoolManager(10) # Ensure it is empty
        self._factory = factory.FileSystem(BaseConfiguration("http://svn.test.de/svn"))
        self.assertTrue(self._factory.hasCustomMetadataSupport)

    def testCreateDataStorer(self):
        self.assertTrue(isinstance(self._factory.createDataStorer("identifier"), 
                                   DataSubversionAdapter))

    def testCreateMetadataStorer(self):
        self.assertTrue(isinstance(self._factory.createMetadataStorer("identifier"), 
                                   MetadataSubversionAdapter))
    
    def testUpdateCredentials(self):
        # Success
        self._factory.updateCredentials({"username": "me", "password": "secret"})
        self.assertEquals(self._factory._configuration.username, "me")
        self.assertEquals(self._factory._configuration.password, "secret")
        
        # Error
        self.assertRaises(PersistenceError, self._factory.updateCredentials, dict())
        
    def testPrepareUsage(self):
        # Success
        self._factory.prepareUsage()
        
        # Error
        self._connectionMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._factory.prepareUsage)
        
    def testRelease(self):
        # Success
        self.assertEquals(len(factory.FileSystem._connectionManager), 1)
        self._factory.release()
        self.assertEquals(len(factory.FileSystem._connectionManager), 0)
        
        # Trying to release it again
        self._factory.release()
        self.assertEquals(len(factory.FileSystem._connectionManager), 0)
        
    def testCanHandleLocation(self):
        # can handle it
        self.assertTrue(self._factory.canHandleLocation)
        
        # Cannot handle
        self._factory.release()
        self._createSvnConnectionMock.error = PersistenceError("")
        self.assertFalse(self._factory.canHandleLocation)
