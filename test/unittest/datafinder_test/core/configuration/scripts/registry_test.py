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
Implements tests for the script registry.
"""


import unittest

from datafinder.core.error import ConfigurationError
from datafinder.core.configuration.scripts.constants import LOCAL_SCRIPT_LOCATION
from datafinder.core.configuration.scripts import registry
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class ScriptRegistryTestCase(unittest.TestCase):
    """ Implements tests for the script registry. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._createFileStorerMock = SimpleMock()
        registry.createFileStorer = self._createFileStorerMock
        self._createScriptMock = SimpleMock()
        registry.createScript = self._createScriptMock
        self._registry = registry.ScriptRegistry(SimpleMock(scriptUris=["path1"]))
        
    def testLoad(self):
        """ Tests the initialization of the script registry. """
        
        self._createScriptMock.value = _ScriptMock(uri="uri")
        self._registry.load()
        self.assertEquals(len(self._registry.scripts), 1)
        
        self._createScriptMock.error = ConfigurationError("")
        self._registry.load()
        self.assertEquals(len(self._registry.scripts), 0)
        
        self._createFileStorerMock.error = PersistenceError("")
        self._registry.load()
        self.assertEquals(len(self._registry.scripts), 0)
        
    def testScriptHandling(self):
        """ Tests the management of script extensions. """
        
        firstScript = _ScriptMock(uri="uri1")
        anotherScript = _ScriptMock(uri="uri2")
        thirdScript = _ScriptMock(uri="uri3")
        self.assertFalse(self._registry.hasScript("test", "uri1"))
        self.assertEquals(self._registry.getScript("test", "uri1"), None)
        self._registry.register("anotherTest", [firstScript])
        self._registry.register("test", [firstScript, anotherScript, thirdScript])
        self.assertEquals(len(self._registry.getScripts("anotherTest")), 1)
        self.assertEquals(len(self._registry.getScripts("test")), 3)
        self.assertEquals(len(self._registry.scripts), 4)
        self.assertTrue(self._registry.hasScript("test", "uri1"))
        self.assertEquals(self._registry.getScript("test", "uri1").uri, "uri1")
        
        self._registry.unregister("test", firstScript)
        self.assertEquals(len(self._registry.getScripts("anotherTest")), 1)
        self.assertEquals(len(self._registry.getScripts("test")), 2)
        self.assertEquals(len(self._registry.scripts), 3)
        
        self._registry.unregister("test", _ScriptMock(uri="unknown"))
        self.assertEquals(len(self._registry.getScripts("anotherTest")), 1)
        self.assertEquals(len(self._registry.getScripts("test")), 2)
        self.assertEquals(len(self._registry.scripts), 3)
        
        self._registry.unregister("unknownLocation", anotherScript)
        self.assertEquals(len(self._registry.getScripts("anotherTest")), 1)
        self.assertEquals(len(self._registry.getScripts("test")), 2)
        self.assertEquals(len(self._registry.scripts), 3)
        
        self._registry.unregister("test", anotherScript)
        self._registry.unregister("test", thirdScript)
        self._registry.unregister("anotherTest", firstScript)
        self.assertEquals(len(self._registry.getScripts("anotherTest")), 0)
        self.assertEquals(len(self._registry.getScripts("test")), 0)
        self.assertEquals(len(self._registry.scripts), 0)
        
        # Register on local disk
        self._registry.register(LOCAL_SCRIPT_LOCATION, [firstScript])
        self._registry.unregister(LOCAL_SCRIPT_LOCATION, firstScript)
        
        
class _ScriptMock(object):
    def __init__(self, uri, error=False):
        self.uri = uri
        self.name = uri
        self.automatic = True
        self.error = error
        
    def execute(self):
        if self.error:
            raise ConfigurationError("")

class _ScriptCollectionMock(object):
    def __init__(self, uri):
        self.uri = uri
        self.name = uri
        self.scripts = [_ScriptMock("")]
