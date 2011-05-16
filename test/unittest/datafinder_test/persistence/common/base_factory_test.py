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
Tests the base factory implementation.
"""


import unittest

from datafinder.persistence.common.base_factory import BaseFileSystem


__version__ = "$Revision-Id:$" 


class BaseFileSystemTestCase(unittest.TestCase):

    def setUp(self):
        self._baseFactory = BaseFileSystem()
        
    def testIsValidIdentifier(self):
        # Success cases
        self.assertEquals(self._baseFactory.isValidIdentifier("name12"), (True, None))
        self.assertEquals(self._baseFactory.isValidIdentifier("name__"), (True, None))
        
        # Error cases
        self.assertEquals(self._baseFactory.isValidIdentifier(None), (False, None))
        self.assertEquals(self._baseFactory.isValidIdentifier(""), (False, None))
        self.assertEquals(self._baseFactory.isValidIdentifier("  "), (False, None))
        self.assertEquals(self._baseFactory.isValidIdentifier(" !#"), (False, 0))
        self.assertEquals(self._baseFactory.isValidIdentifier("asd;asd"), (False, 3))
        
    def testIsValidMetadataIdentifier(self):
        # Success cases
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier("name12"), (True, None))
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier("name__"), (True, None))
        
        # Error cases
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier(None), (False, None))
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier(""), (False, None))
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier("  "), (False, None))
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier(" !#"), (False, 0))
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier("asd;asd"), (False, 3))
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier("12asdasd"), (False, 0))
        self.assertEquals(self._baseFactory.isValidMetadataIdentifier("!asdasd"), (False, 0))