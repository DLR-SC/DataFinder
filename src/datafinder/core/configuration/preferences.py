#
# Handler for the generated preferences stuff.
#
# Created: Heinrich Wendel (heinrich.wendel@dlr.de)
#
# Version: $Id: preferences.py 4615 2010-04-16 15:50:04Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


""" Handler for the generated preferences stuff. """


import base64
import codecs
from StringIO import StringIO
from xml.parsers.expat import ExpatError

from datafinder.core.configuration.gen import preferences
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4615 $"


_DEFAULT_ENCODING = "UTF-8"
preferences.ExternalEncoding = _DEFAULT_ENCODING


class PreferencesHandler(object):
    """ Handles the local preferences information. """
   
    _streamWriterClass = codecs.getwriter(_DEFAULT_ENCODING)
    _preferencesFileName = "preferences.xml"
    
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
                except (ValueError, ExpatError, UnicodeDecodeError):
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
                connection = preferences.connection(configurationUri, username, password, defaultDataStore, defaultArchiveStore)

            connection.username = username
            connection.password = password
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
                                                              connection.defaultDataStore, connection.defaultArchiveStore,
                                                              connection.defaultOfflineStore)
                    self._connections[copiedConnection.url] = copiedConnection
        return self._connectionOrder[:]
    connectionUris = property(_getConnections)
    
    
    def __getattr__(self, name):
        """ Automatically redirects property calls to the generated class. """
        
        return getattr(self._preferences, name)
