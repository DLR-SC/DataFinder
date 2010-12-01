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

from webdav.Connection import WebdavError

from datafinder.persistence.adapters.webdav_.metadata.adapter import MetadataWebdavAdapter
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants
from datafinder.persistence.metadata.value_mapping import MetadataValue
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


_VALID_WEBDAV_PROPERTY_RESULT = {("1", "1"): SimpleMock("")}
_VALID_PROPERTY_RESULT = {constants.CREATION_DATETIME: MetadataValue(""), 
                          constants.MODIFICATION_DATETIME: MetadataValue(""),
                          constants.SIZE: MetadataValue("0"), 
                          constants.MIME_TYPE: MetadataValue(""), 
                          constants.OWNER: MetadataValue("")}

_VALID_WEBDAV_SEARCH_RESULT = {"http://server.de/Path": SimpleMock()}
_VALID_SEARCH_RESULT = ["/PATH"]


class MetadataWebdavAdapterTestCase(unittest.TestCase):
    """ Tests the meta data adapter implementation. """

    def setUp(self):
        """ Creates a default object under test. """
        
        self._defaultAdapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                                     SimpleMock(), SimpleMock(SimpleMock()))

    def testRetrieveSuccess(self):
        """ Tests successful meta data retrieval. """
        
        webdavStorerMock = SimpleMock(dict())
        adapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                        SimpleMock("1"), SimpleMock(webdavStorerMock))
        self.assertEquals(adapter.retrieve(), _VALID_PROPERTY_RESULT)
        self.assertEquals(adapter.retrieve(list()), dict())
        
        webdavStorerMock.value = {("1", "1"): SimpleMock("value")}
        self.assertEquals(adapter.retrieve(["1"]), {"1": MetadataValue("value")})

    def testUpdateSuccess(self):
        """ Tests successful update of meta data. """
        
        self._defaultAdapter.update({"1":"", "2":"", "3":""})
    
    def testDeleteSuccess(self):
        """ Tests successful deletion of meta data. """
        
        self._defaultAdapter.delete(["1", "2"])
    
    def testSearchSuccess(self):
        """ Tests successful deletion of meta data. """
        
        adapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock("/PATH"), 
                                        SimpleMock(), SimpleMock(SimpleMock(_VALID_WEBDAV_SEARCH_RESULT)))
        self.assertEquals(adapter.search([]), _VALID_SEARCH_RESULT)

    def testErrorHandlingOnLibraryInstanceCreation(self):
        """ Tests the error handling when creating concrete library instances. """

        adapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                        SimpleMock(), SimpleMock(error=PersistenceError("")))
        self.assertRaises(PersistenceError, adapter.retrieve)
        self.assertRaises(PersistenceError, adapter.update, dict())
        self.assertRaises(PersistenceError, adapter.delete, [])
        self.assertRaises(PersistenceError, adapter.search, [])

    def testErrorHandlingUsingLibraryInstances(self):
        """ Tests the error handling when using concrete library instances. """

        adapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                        SimpleMock(), SimpleMock(SimpleMock(error=WebdavError(""))))
        self.assertRaises(PersistenceError, adapter.retrieve)
        self.assertRaises(PersistenceError, adapter.update, dict())
        self.assertRaises(PersistenceError, adapter.delete, [])
        self.assertRaises(PersistenceError, adapter.search, [])
