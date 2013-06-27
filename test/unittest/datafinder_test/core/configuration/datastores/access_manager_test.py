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
Provides test of the access manager.
"""


import unittest

from datafinder.core.configuration.datastores import access_manager
from datafinder.core.configuration.datastores import datastore
from datafinder.core.error import AuthenticationError
from datafinder.persistence.error import PersistenceError
from datafinder_test import mocks


__version__ = "$Revision-Id$" 


class DataStoreAccessManagerTest(unittest.TestCase):
    """ Tests of the data store access manager. """ # pylint: disable=R0904
    
    def setUp(self):
        # Fine for testing: pylint: disable=W0212
        self._datastore = datastore.DefaultDataStore()
        self._fileSystemMock = mocks.SimpleMock(isAccessible=True)
        self._createFileSystemMock = mocks.SimpleMock(self._fileSystemMock)
        
        self._accessManager = access_manager.DataStoreAccessManager()
        self._accessManager._createFileSystem = self._createFileSystemMock
        
    def testIsAccessible(self):
        isAccessible = self._accessManager.isAccessible(self._datastore)
        fileSystem = self._accessManager.getFileSystem(self._datastore)

        self.assertTrue(isAccessible)
        self.assertTrue(not fileSystem is None)
        
    def testNotAccessible(self):
        self._fileSystemMock.isAccessible = False
        
        isAccessible = self._accessManager.isAccessible(self._datastore)
        fileSystem = self._accessManager.getFileSystem(self._datastore)
        
        self.assertFalse(isAccessible)
        self.assertTrue(not fileSystem is None)
        
    def testInvalidFileSystem(self):
        self._createFileSystemMock.error = PersistenceError("Invalid interface.")
        
        isAccessible = self._accessManager.isAccessible(self._datastore)
        fileSystem =  self._accessManager.getFileSystem(self._datastore)
        
        self.assertFalse(isAccessible)
        self.assertTrue(fileSystem is None)
        
    def testAccessibleAfterExplicitCheck(self):
        self._fileSystemMock.isAccessible = False
        self.assertFalse(self._accessManager.isAccessible(self._datastore))
        
        self._fileSystemMock.isAccessible = True
        self._accessManager.checkAccessibility(self._datastore)
        self.assertTrue(self._accessManager.isAccessible(self._datastore))
        
    def testAuthenticationCallback(self):
        self._fileSystemMock.isAccessible = False
        self.assertFalse(self._accessManager.isAccessible(self._datastore))
        
        try:
            self._accessManager.checkAccessibility(self._datastore)
        except AuthenticationError, error:
            callback = error.updateCredentialsCallback 
            
            # First try
            self.assertFalse(callback({"username": "me", "password": "secret"}))
            self.assertFalse(self._accessManager.isAccessible(self._datastore))
            
            # Successful retry
            self._fileSystemMock.isAccessible = True
            self.assertTrue(callback({"username": "me", "password": "right_secret"}))
            self.assertTrue(self._accessManager.isAccessible(self._datastore))
            
            # Problems on credential update
            self._fileSystemMock.error = PersistenceError("Cannot update credentials.")
            self.assertTrue(callback({"username": "me", "password__": "secret"}))
            self.assertTrue(self._accessManager.isAccessible(self._datastore))
        
    def testRelease(self):
        fileSystem = self._accessManager.getFileSystem(self._datastore)
        def _release():
            fileSystem.release.called = True
        fileSystem.release = _release
        
        self._accessManager.release()
        self.assertTrue(fileSystem.release.called)
