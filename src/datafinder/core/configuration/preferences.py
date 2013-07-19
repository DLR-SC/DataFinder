# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
#met:
#
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


""" Handler for the generated preferences stuff. """


import base64
import codecs
import logging
from StringIO import StringIO
from xml.parsers.expat import ExpatError

from datafinder.core.configuration.gen import preferences
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


_DEFAULT_ENCODING = "UTF-8"
preferences.ExternalEncoding = _DEFAULT_ENCODING


class PreferencesHandler(object):
    """ Handles the local preferences information. """
   
    _streamWriterClass = codecs.getwriter(_DEFAULT_ENCODING)
    _preferencesFileName = "preferences.xml"
    _log = logging.getLogger()
    
    def __init__(self, fileStorer):
        """ 
        Constructor.
        
        @param fileStorer: Points to the parent directory of the preferences file.
        @type fileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>} 
        
        @note: Call C{load} to initialize the handler.
        """
        
        self._fileStorer = fileStorer.getChild(self._preferencesFileName)
        self._connections = None
        self._connectionOrder = list()
        self._preferences = None
        
    def _reset(self):
        """ Resets current configuration. """
        
        self._connections = None
        self._connectionOrder = list()
        self._preferences = None
        
    def load(self):
        """ 
        Loads the preferences. 
        
        @note: When a problem occurs a new default preferences configuration is created.
        """
        
        self._reset()
        try:
            if self._fileStorer.isLeaf:
                data = self._fileStorer.readData()
                content = data.read()
                data.close()
                try:
                    self._preferences = preferences.parseString(unicode(content, _DEFAULT_ENCODING))
                except (ValueError, ExpatError, UnicodeDecodeError, SyntaxError):
                    self._log.error("Problem occurred during parsing preferences. Default preferences used.", exc_info=True)
                    self._preferences = self._getDefaultPreferences()
            else:
                self._preferences = self._getDefaultPreferences()
        except PersistenceError:
            self._preferences = self._getDefaultPreferences()
        self._getConnections()
    
    @staticmethod
    def _getDefaultPreferences():
        """ Creates the default preferences. """
        
        return preferences.preferences(scriptUris=list(), searchQueries=list())
    
    def store(self):
        """ 
        Stores the preferences. 
        
        @raise ConfigurationError: Indicating problems on storage.
        """
        
        try:
            if not self._fileStorer.exists():
                self._fileStorer.createResource()
            stream = self._streamWriterClass(StringIO())
            self._preferences.connections = list()
            for connectionUri in self._connectionOrder:
                connection = self._connections[connectionUri]
                if connection.password is None:
                    encryptedPassword = None
                else:
                    encryptedPassword = base64.encodestring(connection.password)
                copiedConnection = preferences.connection(connection.url, connection.username, encryptedPassword,
                                                          connection.useLdap, connection.ldapServerUri, connection.ldapBaseDn,
                                                          connection.useLucene, connection.luceneIndexUri, 
                                                          connection.defaultDataStore, connection.defaultArchiveStore,
                                                          connection.defaultOfflineStore)

                if not copiedConnection.url is None:
                    self._preferences.addConnections(copiedConnection)
            self._preferences.__dict__.update(self.__dict__)
            try:
                self._preferences.export(stream, 0)
            except ExpatError:
                raise ConfigurationError("Cannot persist preferences configuration.")
            stream.seek(0)
            self._fileStorer.writeData(stream)
        except PersistenceError, error:
            raise ConfigurationError("Unable to store preferences file.\nReason: '%s'" % error.message)
    
    def getConnection(self, configurationUri):
        """
        Returns the connection information for the given URI. 
        
        @param configurationUri: URI of the configuration.
        @type configurationUri: C{unicode}
        
        @return: Object containing the configuration parameters.
        @rtype: C{object}
        """
        
        result = None
        if not configurationUri is None:
            configurationUri = self._normalizeConfigurationUri(configurationUri)
            if configurationUri in self._connections:
                result = self._connections[configurationUri]
        return result

    def addScriptUri(self, scriptUri):
        """ 
        Adds a script URI to the preferences.
        
        @param scriptUri: URI identifying the script extension.
        @type scriptUri: C{unicode}
        """
        
        if not scriptUri in self._preferences.scriptUris:
            self._preferences.scriptUris.append(scriptUri)
        
    def removeScriptUri(self, scriptUri):
        """ 
        Removes a script URI from the preferences.
        
        @param scriptPath: URI identifying the script extension.
        @type scriptPath: C{unicode}
        """
        
        if scriptUri in self._preferences.scriptUris:
            self._preferences.scriptUris.remove(scriptUri)
            
    def clearScriptUris(self):
        """
        Removes all existing script URIs from preferences.
        """
        
        self._preferences.scriptUris = list()
        
    def addSearchQuery(self, name, query):
        """ 
        Adds a search query to the preferences.
        
        @param name: Name of the search query.
        @type name: C{unicode}
        @param query: A search query string.
        @type query: C{unicode}
        """
        
        if not name is None and not query is None:
            searchQuery = self._getSearchQuery(name)
            if searchQuery is None:
                searchQuery = preferences.searchQuery(name, query)
                self._preferences.searchQueries.append(searchQuery)
            else:
                searchQuery.query = query

    def _getSearchQuery(self, name):
        """ Returns the query under the given name or C{None} if it does not exist. """
        
        for searchQuery in self._preferences.searchQueries:
            if searchQuery.name == name:
                return searchQuery
        return None
        
    def removeSearchQuery(self, name):
        """ 
        Removes a search query from the preferences.
        
        @param name: Name of the search query.
        @type name: C{unicode}
        """
        
        searchQuery = self._getSearchQuery(name)
        if not searchQuery is None:
            self._preferences.searchQueries.remove(searchQuery)
            
    def clearSearchQueries(self):
        """
        Removes all existing search queries from preferences.
        """
        
        self._preferences.searchQueries = list()
    
    def addConnection(self, configurationUri, username=None, password=None,
                      useLdap=None, ldapServerUri=None, ldapBaseDn=None, 
                      useLucene=None, luceneIndexUri=None,
                      defaultDataStore=None, defaultArchiveStore=None, defaultOfflineStore=None):
        """ 
        Adds a connection. 
        
        @param configurationUri: URI of the configuration.
        @type configurationUri: C{unicode}
        @param username: Username for authentication.
        @type username: C{unicode}
        @param password: Not encrypted password.
        @type password: C{unicode}
        """
        
        if not configurationUri is None:
            configurationUri = self._normalizeConfigurationUri(configurationUri)
            if configurationUri in self._connectionOrder:
                connection = self.getConnection(configurationUri)
                self._connectionOrder.remove(configurationUri)
            else:
                connection = preferences.connection(configurationUri, username, password, useLdap,
                                                    ldapServerUri, ldapBaseDn, useLucene, luceneIndexUri,
                                                    defaultDataStore, defaultArchiveStore)

            connection.username = username
            connection.password = password
            connection.useLdap = useLdap
            connection.ldapServerUri = ldapServerUri
            connection.ldapBaseDn = ldapBaseDn
            connection.useLucene = useLucene
            connection.luceneIndexUri = luceneIndexUri
            connection.defaultDataStore = defaultDataStore
            connection.defaultArchiveStore = defaultArchiveStore
            connection.defaultOfflineStore = defaultOfflineStore

            self._connections[configurationUri] = connection
            self._connectionOrder.insert(0, configurationUri)

    @staticmethod
    def _normalizeConfigurationUri(configurationUri):
        """ Ensures that the path component of the URI is in the correct format,
        i.e. without trailing slash. """
        
        if configurationUri.endswith("/"):
            configurationUri = configurationUri[:-1]
        return configurationUri
    
    def removeConnection(self, configurationUri):
        """ 
        Removes a connection.
         
        @param configurationUri: URI of the configuration.
        @type configurationUri: C{unicode}
        """
        
        if not configurationUri is None:
            configurationUri = self._normalizeConfigurationUri(configurationUri)
            if configurationUri in self._connections:
                del self._connections[configurationUri]
            if configurationUri in self._connectionOrder:
                self._connectionOrder.remove(configurationUri)
            
    def clearConnections(self):
        """ Clears all connections. """
        
        self._connections.clear()
        self._connectionOrder = list()
        
    def _getConnections(self):
        """ Getter for the connections. """
        
        if self._connections is None or self._connectionOrder is None:
            self._connections = dict()
            for connection in self._preferences.connections:
                if not connection.url is None:
                    self._connectionOrder.append(connection.url)
                    decryptedPassword = connection.password
                    if not decryptedPassword is None:
                        decryptedPassword = base64.decodestring(connection.password)
                    copiedConnection = preferences.connection(connection.url, connection.username, decryptedPassword,
                                                              connection.useLdap, connection.ldapServerUri, connection.ldapBaseDn,
                                                              connection.useLucene, connection.luceneIndexUri, 
                                                              connection.defaultDataStore, connection.defaultArchiveStore,
                                                              connection.defaultOfflineStore)
                    self._connections[copiedConnection.url] = copiedConnection
        return self._connectionOrder[:]
    connectionUris = property(_getConnections)
    
    
    def __getattr__(self, name):
        """ Automatically redirects property calls to the generated class. """
        
        return getattr(self._preferences, name)
