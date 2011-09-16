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
Test cases of the meta data adapter.
"""


import unittest

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants
from datafinder.persistence.metadata.value_mapping import MetadataValue
from datafinder.persistence.adapters.filesystem.metadata import adapter
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class _OsModuleMock(SimpleMock):
    """ Mocks the relevant functions of the os module. """
    
    def __init__(self, returnValue=None, error=None):
        """ Constructor. """
        
        self.returnValue = returnValue
        self.error = error
        SimpleMock.__init__(self, returnValue, error)
        
    @staticmethod
    def strerror(errorNumber):
        """ Explicitly mocking the error interpretation function. """
        
        return str(errorNumber)


class MetadataFileSystemAdapterTestCase(unittest.TestCase):
    """ Test cases of the meta data adapter. """

    def setUp(self):
        """ Creates the test setup. """

        # Mocks os module
        self._osStatResult = SimpleMock()
        self._osStatResult.st_ctime = 788999998.0
        self._osStatResult.st_mtime = 788999998.0
        self._osStatResult.st_size = 788999998.0
        self._osModuleMock = _OsModuleMock(self._osStatResult)
        adapter.os = self._osModuleMock
        
        # Mocks mimetypes module
        self._mimetypesModuleMock = SimpleMock((None, None))
        adapter.mimetypes = self._mimetypesModuleMock
        
        self._adapter = adapter.MetadataFileSystemAdapter("/identifier", SimpleMock("/identifier"))

    def _initValidRetrieveResult(self, mimeType):
        """ Creates the expected result. """
        
        mappedResult = dict()
        mappedResult[constants.CREATION_DATETIME] = MetadataValue(str(self._osStatResult.st_ctime))
        mappedResult[constants.MODIFICATION_DATETIME] = MetadataValue(str(self._osStatResult.st_mtime))
        mappedResult[constants.SIZE] = MetadataValue(str(self._osStatResult.st_size))
        mappedResult[constants.MIME_TYPE] = MetadataValue(mimeType)
        mappedResult[constants.OWNER] = MetadataValue("")
        return mappedResult
                                                                    
    def testRetrieve(self):
        """ Tests the retrieve behavior. """
        
        expectedResult = self._initValidRetrieveResult("")
        self.assertEquals(self._adapter.retrieve(), expectedResult)
        
        result = self._adapter.retrieve([constants.OWNER])
        self.assertTrue(len(result) == 1)
        self.assertTrue(constants.OWNER in result)
        
        result = self._adapter.retrieve([constants.OWNER, constants.CREATION_DATETIME])
        self.assertTrue(len(result) == 2)
        self.assertTrue(constants.OWNER in result)
        self.assertTrue(constants.CREATION_DATETIME in result)
        
        self.assertEquals(self._adapter.retrieve([]), expectedResult)
        self.assertEquals(self._adapter.retrieve(None), expectedResult)
        
        self._mimetypesModuleMock.value = ("application/pdf", None)
        expectedResult = self._initValidRetrieveResult("application/pdf")
        self.assertEquals(self._adapter.retrieve(), expectedResult)
        
        self._osModuleMock.error = OSError()
        self.assertRaises(PersistenceError, self._adapter.retrieve)
        
    def testUpdate(self):
        """ Tests the update behavior. """
        
        self._adapter.update(dict())

    def testDelete(self):
        """ Tests the delete behavior. """
        
        self._adapter.delete(list())
        
