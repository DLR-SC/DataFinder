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
Test cases of the preferences handler. 
"""


from StringIO import StringIO
import unittest
from xml.parsers.expat import ExpatError

from datafinder.core.configuration import preferences
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


_VALID_CONFIGURATION = \
"""<preferences>
    <useLdap>false</useLdap>
    <ldapServerUri>ldap://</ldapServerUri>
    <ldapBaseDn>OU=DLR,DC=intra,DC=dlr,DC=de</ldapBaseDn>
    <connections>
        <url>http://192.168.125.130/repos/config/test1</url>
    </connections>
    <connections>
        <url>http://192.168.125.130/repos/config/test2</url>
        <username>test</username>
        <password>dGVzdA==
</password>
        <defaultDataStore>ds1</defaultDataStore>
        <defaultArchiveStore>ds2</defaultArchiveStore>
    </connections>
    <scriptUris>path</scriptUris>
    <scriptUris>path2</scriptUris>
    <searchQueries>
        <name>query</name>
        <query>query</query>
    </searchQueries>
    <searchQueries>
        <name>query2</name>
        <query>query2</query>
    </searchQueries>
</preferences>
"""


class _WriteDataMock(object):
    """ Mocks the writeData method of the file storer. """
    
    def __init__(self):
        """ Constructor. """
        
        self.content = ""
    
    def __call__(self, stream):
        """ Mocks writeData method. """
        
        self.content = stream.read()


class PreferencesHandlerTestCase(unittest.TestCase):
    """ Test cases for the preferences handler. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._fileStorerMock = SimpleMock(isLeaf=False)
        self._handler = preferences.PreferencesHandler(SimpleMock(self._fileStorerMock))
        
    def testLoad(self):
        """ Tests the loading of the preferences. """
        
        self._fileStorerMock.isLeaf = True
        self._fileStorerMock.methodNameResultMap = {"readData": (StringIO(_VALID_CONFIGURATION), None)}
        self._handler.load()
        self.assertEquals(len(self._handler.connections), 2)
        
        self._fileStorerMock.methodNameResultMap = {"readData": (StringIO(""), None)}
        self._handler.load()
        self.assertEquals(len(self._handler.connections), 0)
        
        self._fileStorerMock.isLeaf = False
        self._fileStorerMock.methodNameResultMap = {"readData": (StringIO(""), None)}
        self._handler.load()
        self.assertEquals(len(self._handler.connections), 0)

        self._fileStorerMock.isLeaf = True
        self._fileStorerMock.methodNameResultMap = {"readData": (StringIO(""), None)}
        self._handler.load()
        self.assertEquals(len(self._handler.connections), 0)
        
        self._fileStorerMock.methodNameResultMap = {"readData": (StringIO(""), PersistenceError())}
        self._handler.load()
        self.assertEquals(len(self._handler.connections), 0)

    def testStore(self):
        """ Tests the storing of the preferences. """
        
        self._handler.load()
        writeDataMock = _WriteDataMock()
        self._fileStorerMock.writeData = writeDataMock
        self._handler.useLdap = False
        self._handler.ldapServerUri = "ldap://"
        self._handler.ldapbaseDn = "OU=d,DC=i,DC=d,DC=com"
        self._handler.showDottedFilesLocal = True
        self._handler.showDottedFilesRemote = False
        self._handler.addConnection("http://192.168.125.130/repos/config/test2", "test", "test", "ds1", "ds2")
        self._handler.addConnection("http://192.168.125.130/repos/config/test1", None, None)
        self._handler.addScriptUri("path")
        self._handler.addScriptUri("path2")
        self._handler.addSearchQuery("query", "query")
        self._handler.addSearchQuery("query2", "query2")
        self._handler.store()

        self.assertEquals(writeDataMock.content, _VALID_CONFIGURATION)
        del self._fileStorerMock.writeData
        self._handler.load()
        
        self._fileStorerMock.methodNameResultMap = {"exists": (None, PersistenceError())}
        self.assertRaises(ConfigurationError, self._handler.store)
        
        self._fileStorerMock.methodNameResultMap = {"exists": (False, None),
                                                    "createResource": (None, PersistenceError())}
        self.assertRaises(ConfigurationError, self._handler.store)
        
        self._fileStorerMock.methodNameResultMap = {"exists": (True, None),
                                                    "writeData": (None, PersistenceError())}
        self.assertRaises(ConfigurationError, self._handler.store)
        
        self._handler._preferences = SimpleMock(error=ExpatError())
        self._fileStorerMock.methodNameResultMap = {"exists": (True, None)}
        self.assertRaises(ConfigurationError, self._handler.store)
        
    def testConnectionHandling(self):
        """ Tests the management of connections. """
        
        self._handler.load()
        self._handler.addConnection("http://192.168.125.130/repos/config/test2", "test", "test", "defaultDs", "defaultADs")
        self.assertEquals(len(self._handler.connectionUris), 1)
        connection = self._handler.getConnection("http://192.168.125.130/repos/config/test2")
        self.assertEquals(connection.username, "test")
        self.assertEquals(connection.password, "test")
        self.assertEquals(connection.defaultDataStore, "defaultDs")
        self.assertEquals(connection.defaultArchiveStore, "defaultADs")
        # Test access to configuration with trailing slash
        connection = self._handler.getConnection("http://192.168.125.130/repos/config/test2/")
        self.assertEquals(connection.username, "test")
        self.assertEquals(connection.password, "test")
        self.assertEquals(connection.defaultDataStore, "defaultDs")
        self.assertEquals(connection.defaultArchiveStore, "defaultADs")
        
        
        self._handler.addConnection("http://192.168.125.130/repos/config/test2", None, "test")
        self.assertEquals(len(self._handler.connectionUris), 1)
        self._handler.addConnection("http://192.168.125.130/repos/config/test2", None, None)
        self.assertEquals(len(self._handler.connectionUris), 1)
        self.assertEquals(self._handler.getConnection("http://192.168.125.130/repos/config/test2").password, None)
        
        self._handler.removeConnection("http://192.168.125.130/repos/config/test2")
        self.assertEquals(len(self._handler.connectionUris), 0)
        self._handler.removeConnection("http://192.168.125.130/repos/config/test2")
        self.assertEquals(len(self._handler.connectionUris), 0)
        self.assertEquals(self._handler.getConnection("http://192.168.125.130/repos/config/test2"), None)
        
        self._handler.addConnection(None, None, None, None, None)
        self.assertEquals(len(self._handler.connectionUris), 0)
        
        self._handler.addConnection("http://192.168.125.130/repos/config/test2", "test", "test")
        self._handler.addConnection("http://192.168.125.130/repos/config/tes2", "test", "test")
        self.assertEquals(len(self._handler.connectionUris), 2)
        self._handler.clearConnections()
        self.assertEquals(len(self._handler.connectionUris), 0)
        
    def testEmptyConnectionsAreIgnored(self):
        """ Checks whether empty connections are ignored. """
        
        self._handler._preferences = SimpleMock(connections=[SimpleMock(url=None, username=None, password=None),
                                                             SimpleMock(url="uri", username=None, password=None)])
        self.assertEquals(len(self._handler.connectionUris), 1)
        
    def testScriptPathHandling(self):
        """ Tests the management of script paths. """
        
        self._handler.load()
        self._handler.addScriptUri("file:///repos/config/test2")
        self.assertEquals(len(self._handler.scriptUris), 1)
        self._handler.addScriptUri("file:///repos/config/test2")
        self.assertEquals(len(self._handler.scriptUris), 1)
        
        self._handler.removeScriptUri("file:///repos/config/test2")
        self.assertEquals(len(self._handler.scriptUris), 0)
        self._handler.removeScriptUri("file:///repos/config/test2")
        self.assertEquals(len(self._handler.scriptUris), 0)
        
        self._handler.addScriptUri("file:///repos/config/test2")
        self._handler.addScriptUri("file:///repos/config/test")
        self.assertEquals(len(self._handler.scriptUris), 2)
        self._handler.clearScriptUris()
        self.assertEquals(len(self._handler.scriptUris), 0)
        
    def testSearchQueryHandling(self):
        """ Tests the management of search queries. """
        
        self._handler.load()
        self._handler.addSearchQuery("query", "query")
        self.assertEquals(len(self._handler.searchQueries), 1)
        self._handler.addSearchQuery("query", "query")
        self.assertEquals(len(self._handler.searchQueries), 1)
        
        self._handler.removeSearchQuery("query")
        self.assertEquals(len(self._handler.searchQueries), 0)
        self._handler.removeSearchQuery("query")
        self.assertEquals(len(self._handler.searchQueries), 0)
        
        self._handler.addSearchQuery("query", "query")
        self._handler.addSearchQuery("query2", "query2")
        self.assertEquals(len(self._handler.searchQueries), 2)
        self._handler.clearSearchQueries()
        self.assertEquals(len(self._handler.searchQueries), 0)
        