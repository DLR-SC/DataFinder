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
Implements test cases for the icon handler.
"""


import unittest

from datafinder.core.configuration.icons import handler
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class IconHandlerTestCase(unittest.TestCase):
    """ Implements icon handler test. """
    
    
    def setUp(self):
        """ Creates object under test. """
        
        handler.parseIconDirectory = SimpleMock(list())
        self._createFileStorerMock = SimpleMock()
        handler.createFileStorer = self._createFileStorerMock
        self._sourceFileStorer = SimpleMock()
        self._targetFileStorer = SimpleMock()
        self._iconRegistry = SimpleMock()
        self._handler = handler.IconHandler(self._iconRegistry, self._sourceFileStorer, self._targetFileStorer)
        
    def testLoad(self):
        """ Tests the loading of the icon handler. """
        
        self._sourceFileStorer.methodNameResultMap = {"getChildren": ([SimpleMock(SimpleMock())], None)}
        self._targetFileStorer.methodNameResultMap = {"getChild": (SimpleMock(SimpleMock()), None)}
        self._handler._isUpdateRequired = SimpleMock(True)
        self._handler.load()

        self._targetFileStorer.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.load)

        self._targetFileStorer.error = None
        self._sourceFileStorer.methodNameResultMap = None
        self._sourceFileStorer.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.load)

    def testCreate(self):
        """ Tests the creation of the central icon location. """
        
        self._handler.create()
         
        self._sourceFileStorer.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.create)

    def testGetIcon(self):
        """ Tests the retrieval of an icon. """
        
        self.assertEquals(self._handler.getIcon("test"), None)
        
        iconMock = SimpleMock()
        self._iconRegistry.value = iconMock
        self.assertEquals(self._handler.getIcon("test2"), iconMock)
        
    def testHasIcon(self):
        """ Tests icon existence check. """
        
        self._iconRegistry.value = False
        self.assertFalse(self._handler.hasIcon("test"))
        
        self._iconRegistry.value = True
        self.assertTrue(self._handler.getIcon("test2"))
        
    def testAllIcons(self):
        """ Tests the retrieval of all icons managed by the handler. """
        
        self._iconRegistry.icons = list()
        self.assertEquals(len(self._handler.allIcons), 0)
        
        self._iconRegistry.icons = [SimpleMock()]
        self.assertEquals(len(self._handler.allIcons), 1)
        
        self._iconRegistry.icons = [SimpleMock(), SimpleMock(), SimpleMock(), SimpleMock()]
        self.assertEquals(len(self._handler.allIcons), 4)
    
    def testAddIcon(self):
        """ Tests the adding of an icon. """
        
        self._sourceFileStorer.value = SimpleMock()
        self._targetFileStorer.value = SimpleMock()
        localIconFileStorerMock = SimpleMock()
        localIconFileStorerMock.methodNameResultMap = {"exists": (True, None), "readData": (SimpleMock(), None)}
        self._createFileStorerMock.value = SimpleMock(localIconFileStorerMock)
        self._handler.addIcon("test", "/test/zzz/testPath")
        
        localIconFileStorerMock.methodNameResultMap = {"exists": (False, None)}
        self.assertRaises(ConfigurationError, self._handler.addIcon, "test", "/test/zzz/testPath")
        
        localIconFileStorerMock.methodNameResultMap = {"exists": (True, None), "readData": (None, PersistenceError(""))}
        self.assertRaises(ConfigurationError, self._handler.addIcon, "test", "/test/zzz/testPath")
        
        self._createFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.addIcon, "test", "/test/zzz/testPath")
        
    def testRemoveIcon(self):
        """ Tests the removal of an icon. """
        
        self._sourceFileStorer.value = SimpleMock(True)
        self._targetFileStorer.value = SimpleMock(True)
        self._handler.removeIcon(SimpleMock())
        
        self._sourceFileStorer.value = SimpleMock(error=PersistenceError(""))
        self.assertRaises(ConfigurationError, self._handler.removeIcon, SimpleMock())
        
        self._targetFileStorer.value = SimpleMock(error=PersistenceError(""))
        self._sourceFileStorer.value = SimpleMock(True)
        self.assertRaises(ConfigurationError, self._handler.removeIcon, SimpleMock())
