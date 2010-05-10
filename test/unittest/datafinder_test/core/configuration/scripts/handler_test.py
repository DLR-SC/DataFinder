#
# Created: 13.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: handler_test.py 4564 2010-03-25 22:30:55Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements tests for the script handler.
"""


import unittest

from datafinder.core.configuration.scripts import handler
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4564 $"


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
        
        self._createScriptMock.value = SimpleMock(uri="uri")
        self._sourceFileStorerMock.methodNameResultMap = {"getChildren": ([SimpleMock(SimpleMock())], None)}
        self._targetFileStorerMock.methodNameResultMap = {"getChild": (SimpleMock(SimpleMock()), None),
                                                          "getChildren": ([SimpleMock(SimpleMock())], None)}
        self._handler._isUpdateRequired = SimpleMock(True)
        self._handler.load()

        self._targetFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._handler.load)

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
