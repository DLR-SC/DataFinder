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
from datafinder.persistence.metadata import constants as const
from datafinder.persistence.metadata.value_mapping import MetadataValue
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id$" 


class MetadataSubversionAdapterTestCase(unittest.TestCase):
        
    def testRetrieve(self):
        # Success
        expectedResult = self._initValidRetrieveResult()
        connectionMock = SimpleMock(methodNameResultMap=\
            {"getProperty": ('{"name": "me"}', None),
            "info": ({"lastChangedDate": "", "owner": "", "size": "10", "creationDate": ""}, None)})
        defaultAdapter = adapter.MetadataSubversionAdapter("identifier", SimpleMock(connectionMock))
        self.assertEquals(defaultAdapter.retrieve(), expectedResult) # Filter nothing
        self.assertEquals(defaultAdapter.retrieve(list()), expectedResult) # Filter nothing
        self.assertEquals(defaultAdapter.retrieve([const.SIZE]), 
                          {const.SIZE: MetadataValue("10")}) # Filter size

        # Error access system properties
        connectionMock.methodNameResultMap = {"info": (None, SubversionError(""))}
        self.assertRaises(PersistenceError, defaultAdapter.retrieve)

        # Error accessing custom properties
        connectionMock.methodNameResultMap = {"getProperty": (None, SubversionError(""))}
        self.assertRaises(PersistenceError, defaultAdapter.retrieve)

    @staticmethod
    def _initValidRetrieveResult():
        mappedResult = dict()
        mappedResult[const.MODIFICATION_DATETIME] = MetadataValue("")
        mappedResult[const.CREATION_DATETIME] = MetadataValue("")
        mappedResult[const.SIZE] = MetadataValue("10")
        mappedResult[const.OWNER] = MetadataValue("")
        mappedResult[const.MIME_TYPE] = MetadataValue("")
        mappedResult["name"] = MetadataValue("me")
        return mappedResult
    
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
