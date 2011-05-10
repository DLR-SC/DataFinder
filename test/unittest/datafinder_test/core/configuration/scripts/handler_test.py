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
Implements tests for the script handler.
"""


import unittest

from datafinder.core.configuration.scripts import handler
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class ScripthandlerTestCase(unittest.TestCase):
    """ Implements tests for the script handler. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._createFileStorerMock = SimpleMock()
        handler.createFileStorer = self._createFileStorerMock
        self._createScriptMock = SimpleMock()
        handler.createScript = self._createScriptMock
        self._registryMock = SimpleMock()
        self._sourceFileStorerMock = SimpleMock()
        self._targetFileStorerMock = SimpleMock()
        self._handler = handler.ScriptHandler(self._registryMock, self._sourceFileStorerMock, self._targetFileStorerMock)

    def testLoad(self):
        """ Tests the initialization of the script handler. """
        
        # Success
        self._createScriptMock.value = SimpleMock(uri="uri")
        self._sourceFileStorerMock.methodNameResultMap = {"getChildren": ([SimpleMock(SimpleMock())], None)}
        self._targetFileStorerMock.methodNameResultMap = {"getChild": (SimpleMock(SimpleMock()), None),
                                                          "getChildren": ([SimpleMock(SimpleMock())], None)}
        self._handler._isUpdateRequired = SimpleMock(True)
        self._handler.load()

        # Cannot copy a certain script
        self._handler._copy = SimpleMock(error=PersistenceError(""))
        self._handler.load()
        
        # Cannot create target collection
        self._targetFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.load)

        # Cannot access scripts
        self._targetFileStorerMock.error = None
        self._sourceFileStorerMock.methodNameResultMap = None
        self._sourceFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.load)
        
    def testCreate(self):
        """ Tests the creation of the central script extension location. """
        
        self._handler.create()
         
        self._sourceFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.create)
        
    def testScriptAccess(self):
        """ Tests the access to scripts managed by the script handler. """
        
        self._targetFileStorerMock.value = SimpleMock(uri="uri")
        self.assertEquals(self._handler.getScript("test.py"), None)
        self.assertFalse(self._handler.hasScript("test.py"))
        
        self._registryMock.value = SimpleMock(uri="uri")
        self.assertNotEquals(self._handler.getScript("test.py"), None)
        self.assertTrue(self._handler.hasScript("test.py"))
        
        self._registryMock.value = list()
        self.assertEquals(len(self._handler.scripts), 0)
        self._registryMock.value = [SimpleMock(), SimpleMock()]
        self.assertEquals(len(self._handler.scripts), 2)
        
        self._registryMock.scripts = list()
        self.assertEquals(len(self._handler.allScripts), 0)
        self._registryMock.scripts = [SimpleMock(), SimpleMock()]
        self.assertEquals(len(self._handler.allScripts), 2)

    def testAddScript(self):
        """ Test the adding of a script extension. """
        
        self._createFileStorerMock.value = SimpleMock(True)
        self._sourceFileStorerMock.value = SimpleMock()
        self._targetFileStorerMock.value = SimpleMock(False)
        self._handler.addScript("file:///local/path/to/script.py")
        
        self._createFileStorerMock.value = SimpleMock(False)
        self.assertRaises(ConfigurationError, self._handler.addScript, "file:///local/path/to/script.py")
        
        self._createFileStorerMock.value = SimpleMock(error=PersistenceError(""))
        self.assertRaises(ConfigurationError, self._handler.addScript, "file:///local/path/to/script.py")
        
        self._createFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.addScript, "file:///local/path/to/script.py")
        
    def testRemoveScript(self):
        """ Tests the removal of a script extension. """
        
        self._sourceFileStorerMock.value = SimpleMock(True)
        self._targetFileStorerMock.value = SimpleMock(True)
        self._handler.removeScript(SimpleMock(name="scriptBaseFileName"))
        
        self._sourceFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.removeScript, SimpleMock(name="scriptBaseFileName"))
        
        self._sourceFileStorerMock.error = SimpleMock(True)
        self._targetFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.removeScript, SimpleMock(name="scriptBaseFileName"))
        
    def testExecuteStartupScripts(self):
        # Success
        self._handler.executeStartupScripts()
        
        # Error
        self._registryMock.error = ConfigurationError("")
        self.assertRaises(ConfigurationError, self._handler.executeStartupScripts)
