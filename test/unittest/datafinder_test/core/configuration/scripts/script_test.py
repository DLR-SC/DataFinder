#
# Created: 13.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: script_test.py 4569 2010-03-26 19:42:22Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements tests of the script representations.
"""


from StringIO import StringIO
import unittest

from datafinder.core.configuration.scripts import script
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4569 $"


class CreateScriptTestCase(unittest.TestCase):
    """ Implements tests of the script factory method. """
    
    def setUp(self):
        """ Creates test environment. """
        
        self._scriptInitMock = SimpleMock()
        self._scriptCollectionInitMock = SimpleMock()
        self._initScriptInitPointer = script.Script.__init__
        self._initScriptCollectionPointer = script.ScriptCollection.__init__
        script.Script.__init__ = self._scriptInitMock
        script.ScriptCollection.__init__ = self._scriptCollectionInitMock

    def tearDown(self):
        """ Restores changed environment. """
        
        script.Script.__init__ = self._initScriptInitPointer
        script.ScriptCollection.__init__ = self._initScriptCollectionPointer

    def testCreateScript(self):
        """ Tests the script factory method. """
        
        fileStorerMock = SimpleMock()
        
        fileStorerMock.name = "/path/test.py"
        self.assertNotEquals(script.createScript(fileStorerMock), None)

        fileStorerMock.name = "/path/test.tar"
        self.assertNotEquals(script.createScript(fileStorerMock), None)
        
        fileStorerMock.name = "/path/test"
        self.assertRaises(ConfigurationError, script.createScript, fileStorerMock)
        
        self._scriptInitMock.error = PersistenceError("")
        fileStorerMock.name = "/path/test.py"
        self.assertRaises(ConfigurationError, script.createScript, fileStorerMock)

        self._scriptCollectionInitMock.error = PersistenceError("")
        fileStorerMock.name = "/path/test.tar"
        self.assertRaises(ConfigurationError, script.createScript, fileStorerMock)


class ScriptTestCase(unittest.TestCase):
    """ Implements tests of the script representation. """
    
    _VALID_SCRIPT_HEADER = \
    """
    # @title:  Title  
    #     @description:   Description goes here...  
    #   @datatypes: DataTypeName1, DataTypeName2,  ,  DataTypeName3
     # @dataformats: MimeType1,  MimeType2,   , MimeType3
        # @icon:   AnIconName   
     # @version:   1.2.0  
    """
                        
    def setUp(self):
        """ Creates object under test. """

        self._fileStorerMock = SimpleMock(name="name", uri="file:///name")
        self._fileStorerMock.methodNameResultMap = {"readData": (StringIO(self._VALID_SCRIPT_HEADER), None)}
        self._script = script.Script(self._fileStorerMock)
        
    def testCreatedScriptInstance(self):
        """ Tests the created script. """
        
        self.assertEquals(self._script.name, self._fileStorerMock.name)
        self.assertEquals(self._script.uri, self._fileStorerMock.uri)
        self.assertEquals(self._script.title, "Title")
        self.assertEquals(self._script.description, "Description goes here...")
        self.assertEquals(self._script.datatypes, ["DataTypeName1", "DataTypeName2", "DataTypeName3"])
        self.assertEquals(self._script.dataformats, ["MimeType1", "MimeType2", "MimeType3"])
        self.assertEquals(self._script.iconName, "AnIconName")
        self.assertEquals(self._script.version, "1.2.0")
        self.assertTrue(self._script.isBound)
        
    def testScriptCreationErrorHandling(self):
        """ Tests the error handling when creating a script. """

        self._fileStorerMock.methodNameResultMap = {"readData": (None, PersistenceError(""))}
        self.assertRaises(PersistenceError, script.Script, self._fileStorerMock)
        
        self._fileStorerMock.methodNameResultMap = {"readData": (SimpleMock(error=IOError), None)}
        self.assertRaises(ConfigurationError, script.Script, self._fileStorerMock)
        
    def testExecute(self):
        """ Tests the execution of a script. """

        self._fileStorerMock.methodNameResultMap = {"readData": (StringIO(""), None)}
        self._script.execute()
        
        self._fileStorerMock.methodNameResultMap = {"readData": (None, PersistenceError(""))}
        self.assertRaises(ConfigurationError, self._script.execute)
        
        self._fileStorerMock.methodNameResultMap = {"readData": (StringIO(" jjj"), None)}
        self.assertRaises(ConfigurationError, self._script.execute)
        

class ScriptCollectionTestCase(unittest.TestCase):
    """ Implements tests for script collections. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._tarFileOpenMock = SimpleMock(SimpleMock([SimpleMock()]))
        script.tarfile.open = self._tarFileOpenMock
        self._configFileStorerMock = SimpleMock(methodNameResultMap={"readData": (StringIO(""), None), "exists": (True, None)})
        self._createFileStorerMock = SimpleMock(SimpleMock(self._configFileStorerMock))
        script.createFileStorer = self._createFileStorerMock
        script.atexit = SimpleMock()
        self._fileStorerMock = SimpleMock(name="name", uri="file:///name")
        self._fileStorerMock.value = SimpleMock()
        self._scriptCollection = script.ScriptCollection(self._fileStorerMock)
        
    def testCreatedScriptInstance(self):
        """ Tests the created script collection. """
    
        self.assertEquals(self._scriptCollection.name, self._fileStorerMock.name)
        self.assertEquals(self._scriptCollection.uri, self._fileStorerMock.uri)
        self.assertEquals(self._scriptCollection.title, self._scriptCollection.name[:-4])
        self.assertTrue(self._scriptCollection.hasPreferences)
        
    def testExecutePreferencesPage(self):
        """ Tests the execution of the preferences page dialog. """
        
        self._scriptCollection.hasPreferences = False
        self._scriptCollection.executePreferences()
        
        self._scriptCollection.hasPreferences = True
        self._configFileStorerMock.methodNameResultMap = {"readData": (StringIO(""), None)}
        self._scriptCollection.executePreferences()
        
        self._scriptCollection.hasPreferences = True
        self._configFileStorerMock.methodNameResultMap = {"readData": (StringIO(" jjj"), None)}
        self.assertRaises(ConfigurationError, self._scriptCollection.executePreferences)
        