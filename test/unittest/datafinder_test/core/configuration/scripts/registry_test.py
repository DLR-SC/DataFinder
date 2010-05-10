#
# Created: 13.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: registry_test.py 4564 2010-03-25 22:30:55Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements tests for the script registry.
"""


import unittest

from datafinder.core.configuration.scripts import registry
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4564 $"


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
        
        self._createScriptMock.value = SimpleMock(uri="uri")
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
        
        firstScript = SimpleMock(uri="uri1")
        anotherScript = SimpleMock(uri="uri2")
        thirdScript = SimpleMock(uri="uri3")
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
        
        self._registry.unregister("test", SimpleMock(uri="unknown"))
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
