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
Implements tests of the script representations.
"""


from StringIO import StringIO
from tempfile import NamedTemporaryFile
import unittest

from datafinder.core.configuration.scripts import script
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


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
     # @automatic
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
        self.assertEquals(self._script.automatic, True)
        self.assertTrue(self._script.isBound)
        
    def testScriptCreationErrorHandling(self):
        """ Tests the error handling when creating a script. """

        self._fileStorerMock.methodNameResultMap = {"readData": (None, PersistenceError(""))}
        self.assertRaises(PersistenceError, script.Script, self._fileStorerMock)
        
        self._fileStorerMock.methodNameResultMap = {"readData": (SimpleMock(error=IOError), None)}
        self.assertRaises(ConfigurationError, script.Script, self._fileStorerMock)
        
    def testExecute(self):
        """ Tests the execution of a script. """
                
        self._fileStorerMock.methodNameResultMap = {"readData": (NamedTemporaryFile().file, None)}
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
        self._configFileStorerMock.methodNameResultMap = {"readData": (NamedTemporaryFile().file, None)}
        self._scriptCollection.executePreferences()
        
        self._scriptCollection.hasPreferences = True
        self._configFileStorerMock.methodNameResultMap = {"readData": (StringIO(" jjj"), None)}
        self.assertRaises(ConfigurationError, self._scriptCollection.executePreferences)
        