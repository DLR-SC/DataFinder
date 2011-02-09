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


from datafinder.persistence.adapters.svn.metadata.adapter import MetadataSVNAdapter
from datafinder.persistence.metadata import constants
from datafinder.persistence.metadata.value_mapping import MetadataValue
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


_VALID_SVN_PROPERTY_RESULT = {("1", "1"): SimpleMock("")}
_VALID_PROPERTY_RESULT = {constants.CREATION_DATETIME: MetadataValue(""), 
                          constants.MODIFICATION_DATETIME: MetadataValue(""),
                          constants.SIZE: MetadataValue("0"), 
                          constants.MIME_TYPE: MetadataValue(""), 
                          constants.OWNER: MetadataValue("")}


class MetadataSVNAdapterTestCase(unittest.TestCase):
    """ Tests the meta data adapter implementation. """

    def setUp(self):
        """ Creates a default object under test. """
        
        #self._defaultAdapter = MetadataSVNAdapter("identifier", SimpleMock())
        pass

    def testRetrieveSuccess(self):
        """ Tests successful meta data retrieval. """
        
        pass

    def testUpdateSuccess(self):
        """ Tests successful update of meta data. """
        
       #self._defaultAdapter.update({"1":"", "2":"", "3":""})
    
    def testDeleteSuccess(self):
        """ Tests successful deletion of meta data. """
        
        #self._defaultAdapter.delete(["1", "2"])
    
