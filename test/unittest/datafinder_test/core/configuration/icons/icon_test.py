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
Tests for the icon module.
"""


import unittest

from datafinder.core.configuration.icons import icon
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class IconTestCase(unittest.TestCase):
    """ Tests the parsing of a specific directory for suitable icon files. """
    
    def setUp(self):
        """ Creates test setup. """
        
        self._directoryFileStorer = SimpleMock(identifier="/test")
    
    def testParsingSuccess(self):
        """  Tests the successful parsing of a directory for icon files. """
        
        self._directoryFileStorer.value = [SimpleMock(name="a16.png"), SimpleMock(name="a24.png"),
                                           SimpleMock(name="b16.png"), SimpleMock(name="b24.png")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 2)
        
        self._directoryFileStorer.value = [SimpleMock(name="a6.png"), SimpleMock(name="a24.png"),
                                           SimpleMock(name="b16.png"), SimpleMock(name="b24.png")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 1)
        
        self._directoryFileStorer.value = [SimpleMock(name="a6.png"), SimpleMock(name="a24.png"),
                                           SimpleMock(name="b16.png"), SimpleMock(name="b24.ng")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 1)
        
        self._directoryFileStorer.value = [SimpleMock(name="a6.png"), SimpleMock(name="a24.png"),
                                           SimpleMock(name="b6.png"), SimpleMock(name="b24.ng")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 0)
        
    def testErrorHandling(self):
        """ Tests the error handling when parsing a directory for icon files. """
        
        self._directoryFileStorer.value = [SimpleMock(name=""), SimpleMock(name="a24.png")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 0)
        
        self._directoryFileStorer.error = PersistenceError("")
        self.assertRaises(ConfigurationError, icon.parseIconDirectory, self._directoryFileStorer)
        
    def testIconComparison(self):
        """ Tests the comparison of icons. """
        
        anIcon = icon.Icon("a", "b", "c", "d")
        self.assertEquals(anIcon, anIcon)
        
        anotherIcon = icon.Icon("a", "b", "c", "d")
        self.assertEquals(anIcon, anotherIcon)
        
        anotherIcon.baseName = "d"
        self.assertNotEquals(anIcon, anotherIcon)
        
        self.assertNotEquals(anIcon, None)
    