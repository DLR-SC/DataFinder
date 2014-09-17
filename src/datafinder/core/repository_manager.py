#
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
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


"""
Central entry point into the repository handling.

@note: There should be only ONE repository manager for every "DataFinder application".
       For that reason just use the module variable C{repositoryManagerInstance} 
       instead of creating your own instance.
"""


from hashlib import sha1

from datafinder.core.configuration import constants
from datafinder.core.configuration.configuration import RepositoryConfiguration
from datafinder.core.configuration.dataformats.registry import DataFormatRegistry
from datafinder.core.configuration.datamodel import DataModelHandler
from datafinder.core.configuration.datastores import DataStoreAccessManager, DataStoreHandler
from datafinder.core.configuration.icons import IconRegistry, IconHandler
from datafinder.core.configuration.preferences import PreferencesHandler
from datafinder.core.configuration.properties import PropertyDefinitionRegistry, PropertyDefinitionFactory
from datafinder.core.configuration.scripts import ScriptRegistry, ScriptHandler
from datafinder.core.error import ConfigurationError, CoreError
from datafinder.core.repository import Repository
from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import FileSystem, createFileStorer


__version__ = "$Revision-Id:$" 


class RepositoryManager(object):
    """ Manages the available repositories. 
    
    In detail it:
     * Loads global configuration data
     * Allows initialization of repositories and their configuration
     * Centrally manages the available repositories
     
    Repositories are distinguished into managed and unmanaged repositories. 
     * A managed repository has DataFinder-specific configuration (e.g., data model, data stores, etc.).
     * A unmanaged repository is just a "plain file system" without any specific configuration.
    """
    
    def __init__(self):
        self.managedRepositories = list()
        self.unmanagedRepositories = list()
        self.iconRegistry = IconRegistry()
        self.dataFormatRegistry = DataFormatRegistry()
        self.workingRepository = None
        # Is required in the persistence layer to have a "persistent" working directory => See SVN adapter
        BaseConfiguration.baseWorkingDirectory = constants.WORKING_PATH
        
        try:
            self._localBaseConfigurationCollection = createFileStorer("file:///" + constants.WORKING_PATH)
        except PersistenceError, error:
            raise CoreError("Cannot access local configuration directory '%s'. Reason: '%s'" \
                            % (constants.WORKING_PATH, error.message))
        else:
            self.preferences = PreferencesHandler(self._localBaseConfigurationCollection)
            self.scriptRegistry = ScriptRegistry(self.preferences)
        
    def load(self):
        """
        Loads basic configuration data like global preferences.
        
        @raise ConfigurationError: Indicating problems loading the base configuration.
        """
        
        self.preferences.load()
        self.scriptRegistry.load()
        self.iconRegistry.load()
        self.dataFormatRegistry.load()

    def getRepositoryConfiguration(self, configurationUri=None, username=None, password=None, baseUri=None):
        """ 
        Returns a repository configuration for the given parameters.
        
        @param configurationUri: URI which identifies the configuration collection. If C{None} a default configuration is used.
        @type configurationUri: C{unicode}
        @param username: An optional user name used for authentication.
        @param username: C{unicode}
        @param password: An optional password used for authentication.
        @param password: C{unicode}
        @param baseUri: Optional base URI of the underlying file system containing the configuration.
                        This can be used to identify the root collection of this file system.
                        E.g. configuration URI is: http://myserver.de/test/config and base URI should be: http://myserver.de/test
                        when http://myserver.de/test is the base WebDAV-enabled root collection.
        @type baseUri: C{unicode}
        
        @return: Repository configuration.
        @rtype: L{RepositoryConfigurationy<datafinder.core.configuration.configuration.RepositoryConfiguration>}
        """

        authenticationParameters = {"username": username, "password": password}
        isManaged = not configurationUri is None
        baseConfiguration = self._createBaseRepositoryConfiguration(isManaged)
        if isManaged:
            configurationCollection = self._createConfigurationCollection(configurationUri, username, password, baseUri)
            localConfigurationCollection = self._createLocalConfigurationCollection(configurationUri)
            self._setManagedRepositoryParameters(
                baseConfiguration, configurationCollection, localConfigurationCollection, authenticationParameters)
        return baseConfiguration
            
    def _createBaseRepositoryConfiguration(self, isManagedRepository=False):
        propertyDefinitionFactory = PropertyDefinitionFactory()
        propertyDefinitionRegistry = PropertyDefinitionRegistry(propertyDefinitionFactory, isManagedRepository)
        return RepositoryConfiguration(
            propertyDefinitionFactory, propertyDefinitionRegistry, self.iconRegistry, self.dataFormatRegistry)
      
    @staticmethod
    def _createConfigurationCollection(configurationUri, username, password, baseUri):
        if baseUri is None:
            baseUri = configurationUri
        baseConfiguration = BaseConfiguration(baseUri, username=username, password=password)
        try:
            return createFileStorer(configurationUri, baseConfiguration)
        except PersistenceError, error:
            raise ConfigurationError("Unable to initialize configuration.\nReason: '%s'" % error.message)
        
    def _createLocalConfigurationCollection(self, configurationUri):
        try:
            repositoryHash = sha1(configurationUri).hexdigest()
        except TypeError, error:
            raise ConfigurationError("Cannot determine unique repository hash. Reason: '%s'" % error.message)
        return self._localBaseConfigurationCollection.getChild(repositoryHash)
            
    def _setManagedRepositoryParameters(self, baseConfiguration, configurationCollection, 
        localConfigurationCollection, authenticationParameters):
        
        baseConfiguration.propertyDefinitionFactory.propertyIdValidator = configurationCollection.fileSystem.isValidMetadataIdentifier
        
        dataModelHandler = DataModelHandler(
            configurationCollection.getChild(constants.DATAMODEL_FILENAME), baseConfiguration.propertyDefinitionRegistry)
        
        dataStoreHandler = DataStoreHandler(configurationCollection.getChild(constants.DATASTORE_FILENAME))
        
        dataStoreAccessManager = DataStoreAccessManager(authenticationParameters)
    
        sourceIconCollection = configurationCollection.getChild(constants.ICON_DIRECTORYNAME)
        targetIconCollection = localConfigurationCollection.getChild(constants.ICON_DIRECTORYNAME)
        iconHandler = IconHandler(self.iconRegistry, sourceIconCollection, targetIconCollection)
    
        sourceScriptCollection = configurationCollection.getChild(constants.SCRIPT_DIRECTORYNAME)
        targetScriptCollection = localConfigurationCollection.getChild(constants.SCRIPT_DIRECTORYNAME)
        scriptHandler = ScriptHandler(self.scriptRegistry, sourceScriptCollection, targetScriptCollection)
        
        baseConfiguration.setManagedRepositoryParameters(
            configurationCollection, dataModelHandler, dataStoreHandler, 
            dataStoreAccessManager, iconHandler, scriptHandler, self.preferences)
    
    def connectRepository(self, dataUri, repositoryConfiguration=None, username=None, password=None):
        """
        Connect to a repository.
        
        @param dataUri: URI identifying the root item of repository which has to be connected.
        @type dataUri: C{unicode}
        @param repositoryConfiguration: Optional repository configuration. Default: C{None}
        @type repositoryConfiguration: L{RepositoryConfiguration<datafinder.core.configuration.configuration.RepositoryConfiguration>}
        @param username: Optional user name. Default: C{None}
        @type username: C{unicode}
        @param password: Optional password. Default: C{None}
        @type password: C{unicode}
        """
        
        if repositoryConfiguration is None:
            repositoryConfiguration = self._createBaseRepositoryConfiguration()
        try:
            fileSystem = self._createRepositoryFileSystem(
                repositoryConfiguration.repositoryConfigurationUri, dataUri, username, password)
        except PersistenceError, error:
            raise ConfigurationError("Unable to initialize the repository.\nReason: '%s'" % error.message)
        else:
            return self._createRepository(fileSystem, repositoryConfiguration)
        
    def _createRepositoryFileSystem(self, configurationUri, dataUri, username, password):
        baseConfiguration = BaseConfiguration(dataUri, username=username, password=password)
        # make this accessible for data stores => 
        principalSearchConfiguration = None
        searchConfiguration = None
        connection = self.preferences.getConnection(configurationUri)
        if not connection is None:
            if connection.useLdap and connection.ldapServerUri:
                principalSearchConfiguration = BaseConfiguration(
                    connection.ldapServerUri, baseDn=connection.ldapBaseDn, 
                    username=username, password=password, domain="dlr") # Hard-code domain should be put into preferences
            if connection.useLucene and connection.luceneIndexUri:
                searchConfiguration = BaseConfiguration(connection.luceneIndexUri, username=username, password=password)
        
        return FileSystem(baseConfiguration, principalSearchConfiguration, searchConfiguration)
    
    def _createRepository(self, fileSystem, repositoryConfiguration):
        repository = Repository(fileSystem, repositoryConfiguration, self)

        if repositoryConfiguration.isManagedRepository:
            self.managedRepositories.append(repository)
        else:
            self.unmanagedRepositories.append(repository)
        self.workingRepository = repository
        return repository
    
    def disconnectRepository(self, repository):
        """
        Disconnects the given repository.
        
        @param repository: Repository to disconnect.
        @type repository: L{Repository<datafinder.core.repository.Repository>}
        """
        
        repository.release()
        repository.configuration.release()
        if repository in self.managedRepositories:
            self.managedRepositories.remove(repository)
        if repository in self.unmanagedRepositories:
            self.unmanagedRepositories.remove(repository)
            
        if self.workingRepository == repository:
            self.workingRepository = None

    def savePreferences(self):
        """ 
        Stores the preferences. 
        
        @raise ConfigurationError: Indicating problem on preferences storage.
        """
        
        self.preferences.store()
        

# Central single instance for script API and clients
repositoryManagerInstance = RepositoryManager()
