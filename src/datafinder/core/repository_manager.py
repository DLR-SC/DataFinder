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
Main application class of the datafinder.
"""


from hashlib import sha1

from datafinder.core.configuration import constants
from datafinder.core.configuration.configuration import RepositoryConfiguration
from datafinder.core.configuration.dataformats.registry import DataFormatRegistry
from datafinder.core.configuration.datamodel import DataModelHandler
from datafinder.core.configuration.datastores import DataStoreHandler
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
    """ Init point. """
    
    def __init__(self):
        """
        Constructor.
        """
        
        self.managedRepositories = list()
        self.unmanagedRepositories = list()
        self.iconRegistry = IconRegistry()
        self.dataFormatRegistry = DataFormatRegistry()
        self.workingRepository = None
        
        try:
            self._localBaseConfigurationCollection = createFileStorer("file:///" + constants.USER_HOME)
        except PersistenceError, error:
            raise CoreError("Cannot access local configuration directory '%s'. Reason: '%s'" % (constants.USER_HOME, error.message))
        else:
            self.preferences = PreferencesHandler(self._localBaseConfigurationCollection)
            self.scriptRegistry = ScriptRegistry(self.preferences)
        
    def load(self):
        """
        Initializes global data structures.
        
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

        repositoryConfiguration = self._createDefaultRepositoryConfiguration(not configurationUri is None)
        if not configurationUri is None:
            if baseUri is None:
                baseUri = configurationUri
            try:
                configurationCollection = createFileStorer(configurationUri, 
                                                           BaseConfiguration(baseUri, username=username, password=password))
            except PersistenceError, error:
                raise ConfigurationError("Unable to initialize configuration.\nReason: '%s'" % error.message)
            else:
                repositoryHash = self._determineRepositoryHash(configurationUri)
                localConfigurationCollection = self._localBaseConfigurationCollection.getChild(repositoryHash)
                
                repositoryConfiguration.propertyDefinitionFactory.propertyIdValidator = \
                                                                          configurationCollection.fileSystem.isValidMetadataIdentifier
                dataModelHandler = DataModelHandler(configurationCollection.getChild(constants.DATAMODEL_FILENAME), 
                                                    repositoryConfiguration.propertyDefinitionRegistry)
                dataStoreHandler = DataStoreHandler(configurationCollection.getChild(constants.DATASTORE_FILENAME))
            
                sourceFileStorer = configurationCollection.getChild(constants.ICON_DIRECTORYNAME)
                targetFileStorer = localConfigurationCollection.getChild(constants.ICON_DIRECTORYNAME)
                iconHandler = IconHandler(self.iconRegistry, sourceFileStorer, targetFileStorer)
            
                sourceFileStorer = configurationCollection.getChild(constants.SCRIPT_DIRECTORYNAME)
                targetFileStorer = localConfigurationCollection.getChild(constants.SCRIPT_DIRECTORYNAME)
                scriptHandler = ScriptHandler(self.scriptRegistry, sourceFileStorer, targetFileStorer)
                
                repositoryConfiguration.setManagedRepositoryParameters(configurationCollection, dataModelHandler, dataStoreHandler, 
                                                                       iconHandler, scriptHandler, self.preferences)
        return repositoryConfiguration
        
    def _createDefaultRepositoryConfiguration(self, isManagedRepository=False):
        """ Creates a new repository configurations initialized with the basic parameters. """
        
        propertyDefinitionFactory = PropertyDefinitionFactory()
        propertyDefinitionRegistry = PropertyDefinitionRegistry(propertyDefinitionFactory, isManagedRepository)
        repositoryConfiguration = RepositoryConfiguration(propertyDefinitionFactory, propertyDefinitionRegistry,
                                                          self.iconRegistry, self.dataFormatRegistry)
        return repositoryConfiguration
        
    @staticmethod
    def _determineRepositoryHash(configurationUri):
        """ Helper function to determine the repository has by the configuration URI of the repository. """
        
        try:
            return sha1(configurationUri).hexdigest()
        except TypeError, error:
            raise ConfigurationError("Cannot determine unique repository hash. Reason: '%s'" % error.message)
        
    def connectRepository(self, dataUri, repositoryConfiguration=None, username=None, password=None):
        """
        Connect to a remote repository.
        
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
            repositoryConfiguration = self._createDefaultRepositoryConfiguration()
        try:
            fileSystem = FileSystem(BaseConfiguration(dataUri, username=username, password=password))
        except PersistenceError, error:
            raise ConfigurationError("Unable to initialize configuration.\nReason: '%s'" % error.message)
        else:
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
        

repositoryManagerInstance = RepositoryManager()
