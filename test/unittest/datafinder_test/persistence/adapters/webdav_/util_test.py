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
Tests utility functionality.
"""


__version__ = "$Revision-Id:$" 


import unittest

from datafinder.persistence.adapters.webdav_ import util


_PERSISTENCE_ID = "http://test.de:80/hhh/j/c:/lll/"
_INTERFACE_ID = "/c:/lll"


class ItemIdentifierMapperTestCase(unittest.TestCase):
    """ Tests the identifier mapping. """
    
    def testMapIdentifier(self):
        """ Tests the normal behavior of the identifier mapping. """
        
        mapper = util.ItemIdentifierMapper("http://test.de:80/hhh/j")
        self.assertEquals(mapper.mapIdentifier("/c:/lll/"), _PERSISTENCE_ID)
        self.assertEquals(mapper.mapIdentifier("c:/lll/"), _PERSISTENCE_ID)
        mapper = util.ItemIdentifierMapper("http://test.de:80/hhh/j/")
        self.assertEquals(mapper.mapIdentifier("/c:/lll/"), _PERSISTENCE_ID)
        self.assertEquals(mapper.mapIdentifier("c:/lll/"), _PERSISTENCE_ID)
        
    def testMapPersistenceIdentifier(self):
        """ Tests the normal behavior of the persistence ID mapping. """
        
        mapper = util.ItemIdentifierMapper("http://test.de:80/hhh/j")
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test.de:80/hhh/j/c:/lll/"), _INTERFACE_ID)
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test.de:80/hhh/j/c:/lll"), _INTERFACE_ID)
        mapper = util.ItemIdentifierMapper("http://test.de:80/hhh/j/")
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test.de:80/hhh/j/c:/lll/"), _INTERFACE_ID)
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test.de:80/hhh/j/c:/lll"), _INTERFACE_ID)
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test:80/kkk/j/c:/lll"), "/kkk/j/c:/lll")
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test:80/kkk/j/c:/lll/"), "/kkk/j/c:/lll")

    def testDetermineBaseName(self):
        """ Tests the determine base name functionality. """
        
        self.assertEquals(util.ItemIdentifierMapper.determineBaseName("/kkjh/aa/hh"), "hh")
        self.assertEquals(util.ItemIdentifierMapper.determineBaseName("/"), "")
        self.assertEquals(util.ItemIdentifierMapper.determineBaseName("jjj"), "jjj")
        self.assertEquals(util.ItemIdentifierMapper.determineBaseName(""), "")
        self.assertRaises(AttributeError, util.ItemIdentifierMapper.determineBaseName, None)
        
    def testDetermineParentPath(self):
        """ Tests the determine parent functionality. """
        
        self.assertEquals(util.ItemIdentifierMapper.determineParentPath("/kkjh/aa/hh"), "/kkjh/aa")
        self.assertEquals(util.ItemIdentifierMapper.determineParentPath("/"), "")
        self.assertEquals(util.ItemIdentifierMapper.determineParentPath("jjj"), "")
        self.assertEquals(util.ItemIdentifierMapper.determineParentPath(""), "")
        self.assertRaises(AttributeError, util.ItemIdentifierMapper.determineBaseName, None)
    
    def testInvalidUrl(self):
        """ Tests invalid base URL. """
        
        self.assertRaises(AttributeError, util.ItemIdentifierMapper, None)
        util.ItemIdentifierMapper("invalidURL")
