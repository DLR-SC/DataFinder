# pylint: disable-msg=W0603
#
# Created: 29.01.2008 Heinrich Wendel
# Changed: $Id: repository_manager.py 4626 2010-04-20 20:57:02Z schlauch $
# 
# Version: $Revision: 4626 $
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


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


__version__ = "$LastChangedRevision: 4626 $"




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

    def getRepositoryConfiguration(self, configurationUri=None, username=None, password=None):
        """ 
        Returns a repository configuration for the given parameters.
        
        @return: Repository configuration.
        @rtype: L{RepositoryConfigurationy<datafinder.core.configuration.configuration.RepositoryConfiguration>}
        """

        repositoryConfiguration = self._createDefaultRepositoryConfiguration(not configurationUri is None)
        if not configurationUri is None:
            try:
                configurationCollection = createFileStorer(configurationUri, BaseConfiguration(configurationUri, username=username, password=password))
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
