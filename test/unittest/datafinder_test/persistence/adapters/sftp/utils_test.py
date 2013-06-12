# -*- coding: utf-8 -*-
#
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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


""" Tests the ID mapper. """


import unittest

from datafinder.persistence.adapters.sftp import utils


__version__ = "$Revision-Id:$" 


class ItemIdMapperTest(unittest.TestCase):
    """ Tests the ID mapper. """
    # pylint: disable=R0904
    
    def setUp(self):
        self._mapper = utils.ItemIdentifierMapper(u"/basePäth")
        self._mapper2 = utils.ItemIdentifierMapper(u"/basePäth/")
        
        
    def testDeterminePersistenceIdSuccess(self):
        self.assertEquals(self._mapper.determinePeristenceId(u"/id"), "/basePäth/id")
        self.assertEquals(self._mapper.determinePeristenceId(u"/id/ä/ü"), "/basePäth/id/ä/ü")
        
        self.assertEquals(self._mapper2.determinePeristenceId(u"/id"), "/basePäth/id")
        self.assertEquals(self._mapper2.determinePeristenceId(u"/id/ä/ü"), "/basePäth/id/ä/ü")
        
    def testDeterminePersistenceIdEnsureItIsEncoded(self):
        pId = self._mapper.determinePeristenceId(u"/id")
        self.assertTrue(isinstance(pId, str))
        
    def testDetermineParentIdExamples(self):
        self.assertEquals(self._mapper.determineParentId(u""), u"")
        self.assertEquals(self._mapper.determineParentId(u"/"), u"")
        self.assertEquals(self._mapper.determineParentId(u"/a"), u"/")
        self.assertEquals(self._mapper.determineParentId(u"/id/ä"), u"/id")
        self.assertEquals(self._mapper.determineParentId(u"/id/ä/b"), u"/id/ä")
        self.assertEquals(self._mapper.determineParentId(u"/id/ä/b/"), u"/id/ä")
        self.assertEquals(self._mapper.determineParentId(u"/id/ä/b//"), u"/id/ä/b")
        
    def testDetermineChildIdExamples(self):
        self.assertEquals(self._mapper.determineChildId(u"", u""), u"")
        self.assertEquals(self._mapper.determineChildId(u"/", u""), u"/")
        self.assertEquals(self._mapper.determineChildId(u"/ä", u"ö"), u"/ä/ö")
        self.assertEquals(self._mapper.determineChildId(u"/ä/", u"ö"), u"/ä/ö")
        self.assertEquals(self._mapper.determineChildId(u"/ä//", u"ö"), u"/ä//ö")
