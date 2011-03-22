# pylint: disable=R0201
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
Tests the meta data adapter implementation.
"""


import unittest

from datafinder.persistence.adapters.svn.error import SubversionError
from datafinder.persistence.adapters.svn.metadata import adapter
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants
from datafinder.persistence.metadata.value_mapping import MetadataValue
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id$" 


class MetadataSubversionAdapterTestCase(unittest.TestCase):
    """ Tests the meta data adapter implementation. """
        
    def _initValidRetrieveResult(self):
        """ Creates the expected result. """
        
        mappedResult = dict()
        mappedResult[constants.MODIFICATION_DATETIME] = MetadataValue("")
        mappedResult[constants.CREATION_DATETIME] = MetadataValue("")
        mappedResult[constants.SIZE] = MetadataValue("")
        mappedResult[constants.OWNER] = MetadataValue("")
        mappedResult[constants.MIME_TYPE] = MetadataValue("{}")
        return mappedResult

    def testRetrieveSuccess(self):
        """ Tests successful meta data retrieval. """
        
        expectedResult = self._initValidRetrieveResult()
        
        connectionMock = SimpleMock(methodNameResultMap={"getProperty": ("{}", None), \
                                          "info": ({"lastChangedDate": "", "owner": "", "size": "", "creationDate": ""}, None)})
        defaultAdapter = adapter.MetadataSubversionAdapter("identifier", SimpleMock(connectionMock))
        self.assertEquals(defaultAdapter.retrieve(), expectedResult)
        self.assertEquals(defaultAdapter.retrieve(list()), dict())
        
        connectionMock = SimpleMock(methodNameResultMap={"getProperty": ("{\"1\": \"value\"}", None), \
                                          "info": ({"lastChangedDate": "", "owner": "", "size": "", "creationDate": ""}, None)})
        defaultAdapter = adapter.MetadataSubversionAdapter("identifier", SimpleMock(connectionMock))
        self.assertEquals(defaultAdapter.retrieve(["1"]), {"1": MetadataValue("value")})

    def testUpdateSuccess(self):
        """ Tests successful update of meta data. """
        
        connectionMock = SimpleMock(methodNameResultMap={"getProperty": ("{\"1\": \"value\"}", None), \
                                    "setProperty": (None, SubversionError)})
        defaultAdapter = adapter.MetadataSubversionAdapter("identifier", SimpleMock(connectionMock))
        self.assertRaises(PersistenceError, defaultAdapter.update, {"1":"", "2":"", "3":""})
    
    def testDeleteSuccess(self):
        """ Tests successful deletion of meta data. """

        connectionMock = SimpleMock(methodNameResultMap={"setProperty": (None, SubversionError), \
                                    "getProperty": ("{\"1\": \"value\"}", None)})
        defaultAdapter = adapter.MetadataSubversionAdapter("identifier", SimpleMock(connectionMock))
        self.assertRaises(PersistenceError, defaultAdapter.delete, ["1", "2"])
