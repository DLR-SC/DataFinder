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
Implements the repository configuration.
"""


from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


class RepositoryConfiguration(object):
    """ Represents the configuration of repository. """

    def __init__(self, propertyDefinitionFactory, propertyDefinitionRegistry, iconRegistry, dataFormatRegistry):
        """
        Constructor.
        
        @param propertyDefinitionFactory: The property definition factory.
        @type propertyDefinitionFactory: L{PropertyDefinitionFactory<datafinder.core.configuration.properties.
                                           property_definition.PropertyDefinitionFactory>} 
        @param propertyDefinitionFactory: The property definition factory.
        @type propertyDefinitionFactory: L{PropertyDefinitionRegistry<datafinder.core.configuration.properties.
                                           registry.PropertyDefinitionRegistry>} 
        @param iconRegistry: Global icon registry.
        @type iconRegistry: L{IconRegistry<datafinder.core.configuration.icons.registry.IconRegistry>}
        @param dataFormatRegistry: Global data format registry.
        @type dataFormatRegistry: L{DataFormatRegistry<datafinder.core.configuration.dataformats.registry.DataFormatRegistry>}
        """
        
        self._propertyDefinitionFactory = propertyDefinitionFactory
        self._propertyDefinitionRegistry = propertyDefinitionRegistry
        self._iconRegistry = iconRegistry
        self._dataFormatRegistry = dataFormatRegistry
        self._configurationCollection = None
        self._dataModelHandler = None
        self._dataStoreHandler = None
        self._iconHandler = None
        self._scriptHandler = None
        self._preferences = None

    def setManagedRepositoryParameters(self, configurationCollection, dataModelHandler, dataStoreHandler,
                                       iconHandler, scriptHandler, preferences):
        """
        Sets the additional parameters required accessing a managed repository.
        
        @param configurationCollection: Represents the central configuration collection/directory of the repository.
        @type configurationCollection: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        @param dataModelHandler: The data model handler.
        @type dataModelHandler: L{DataModelHandler<datafinder.core.configuration.datamodel.handler.DataModelHandler>}
        @param dataStoreHandler: The data store configuration handler.
        @type dataStoreHandler: L{DataStoreHandler<datafinder.core.configuration.datastores.handler.DataStoreHandler>}
        @param iconHandler: The icon handler.
        @type iconHandler: L{IconHandler<datafinder.core.configuration.icons.handler.IconHandler>}
        @param scriptHandler: The script handler.
        @type scriptHandler: L{ScriptHandler<datafinder.core.configuration.scripts.handler.ScriptHandler>}
        @param preferences: Local preferences.
        @type preferences: L{PreferencesHandler<datafinder.core.configuration.preferences.PreferencesHandler>}
        """
        
        self._configurationCollection = configurationCollection
        self._dataModelHandler = dataModelHandler
        self._dataStoreHandler = dataStoreHandler
        self._iconHandler = iconHandler
        self._scriptHandler = scriptHandler
        self._preferences = preferences

    def create(self, overwrite=False, defaultDataPath=None):
        """ 
        Creates the repository configuration. 
        
        @param overwrite: Flag indicating that an existing configuration can be removed before creating the new one.
                          The default is C{False}.
        @type overwrite: C{bool}
        @param defaultDataPath: Optional path to a data root collection which is created as well. The path is located
                                on the same file system as the configuration. An existing data root collection is not 
                                replaced.
        @type defaultDataPath: C{unicode}
        
        @raise ConfigurationError: Indicating problem on repository configuration creation.
        """
        
        if self.isManagedRepository:
            try:
                if self._configurationCollection.exists():
                    if not overwrite:
                        errorMessage = "The repository configuration '%s' "  % self.repositoryConfigurationUri \
                                       + "already exists and is not replaced by default."
                        raise ConfigurationError(errorMessage)
                    self._configurationCollection.delete()
                self._configurationCollection.createCollection(True)
                dataFileStorer = self._configurationCollection.fileSystem.createFileStorer(defaultDataPath)
                if not dataFileStorer.exists():
                    dataFileStorer.createCollection(True)
            except PersistenceError, error:
                raise ConfigurationError(error.message)
            else:
                self._dataModelHandler.create()
                self._dataStoreHandler.create(dataFileStorer.uri)
                self._iconHandler.create()
                self._scriptHandler.create()
                
    def load(self):
        """ 
        Initializes configuration. 
        
        @raise ConfigurationError: Indicating problem on configuration loading.
        """
        
        if self.isManagedRepository:
            try:
                exists = self._configurationCollection.exists()
            except PersistenceError, error:
                raise ConfigurationError("Cannot determine repository configuration existence.\nReason: '%s'" % error.message)
            else:
                if not exists:
                    errorMessage = "The repository configuration '%s' does not exist." % self.repositoryConfigurationUri
                    raise ConfigurationError(errorMessage)
                else:
                    self._dataModelHandler.load()
                    self._dataStoreHandler.load()
                    self._scriptHandler.load()
                    self._iconHandler.load()
        
    def store(self):
        """ 
        Stores the current configuration state (data model, data store configurations). 
        
        @raise ConfigurationError: Indicating problem on storing.
        """
        
        if self.isManagedRepository:
            self._dataModelHandler.store()
            self._dataStoreHandler.store()
        
    def exists(self):
        """ 
        Checks whether the configuration does already exist.
        In case of an unmanaged repository it is always returned C{False}
    
        @return: Flag indicating existence of the configuration.
        @rtype: C{bool}
        
        @raise ConfigurationError: Indicating problem on existence check.
        """
        
        if self.isManagedRepository:
            try:
                return self._configurationCollection.exists()
            except PersistenceError, error:
                raise ConfigurationError(error.message)
        else:
            return False
            
    def delete(self):
        """ 
        Deletes the repository configuration. 
        
        @raise ConfigurationError: Indicating problem on deletion.
        """

        if self.isManagedRepository:
            try:
                if self._configurationCollection.exists():
                    self._configurationCollection.delete()
            except PersistenceError, error:
                errorMessage = "Cannot delete the repository configuration.\nReason: '%s'" % error.message
                raise ConfigurationError(errorMessage)

    def release(self):
        """ 
        Releases acquired resources. 
        
        @raise ConfigurationError: Indicating problem on resource release.
        """
        
        if self.isManagedRepository:
            try:
                self._configurationCollection.fileSystem.release()
            except PersistenceError, error:
                raise ConfigurationError("Problem on releasing acquired configuration resources. Reason: '%s'" % error.message)
    
    def getIcon(self, iconBaseName):
        """
        Retrieves an icon for the specified icon base name.
        If a specific icon handler instance is available its C{getIcon}
        implementation is used. Otherwise the implementation of the general
        icon registry is used.
        
        @param iconBaseName: Base name of the icon.
        @type iconBaseName: C{unicode}
        
        @return: Icon instance.
        @rtype: L{Icon<datafinder.core.configuration.icons.icon.Icon>}
        """
        
        if self.isManagedRepository:
            return self._iconHandler.getIcon(iconBaseName)
        else:
            return self._iconRegistry.getIcon(iconBaseName)
    
    @property
    def isManagedRepository(self):
        """ Determines whether it is a managed repository. """
        
        return not self._configurationCollection is None
    
    @property
    def repositoryConfigurationUri(self):
        """ Returns the repository URI. """
        
        uri = None
        if self.isManagedRepository:
            uri = self._configurationCollection.uri
        return uri
    
    @property
    def preferences(self):
        """ 
        Get for the local preferences defined for this configuration. 
        @see: L{getConnection<datafinder.core.configuration.preferences.PreferencesHandler.getConnection>}
        """
        
        if self.isManagedRepository:
            return self._preferences.getConnection(self.repositoryConfigurationUri)
    
    @property
    def dataModelHandler(self):
        """ Getter for the data model handler. """
        
        return self._dataModelHandler
    
    @property
    def dataStoreHandler(self):
        """ Getter for the data store configuration handler. """
        
        return self._dataStoreHandler
    
    @property
    def scriptHandler(self):
        """ Getter for the script handler. """
        
        return self._scriptHandler
    
    @property
    def iconHandler(self):
        """ Getter for the icon handler. """
        
        return self._iconHandler
    
    @property
    def propertyDefinitionRegistry(self):
        """ Getter for the property definition registry. """
        
        return self._propertyDefinitionRegistry
    
    @property
    def propertyDefinitionFactory(self):
        """ Getter for the property definition factory. """
        
        return self._propertyDefinitionFactory
    
    @property
    def dataFormatRegistry(self):
        """ Getter of the data format registry. """
        
        return self._dataFormatRegistry
    
    @property
    def defaultDataUris(self):
        """ Returns a list of default data URIs. """
        
        defaultDataUris = list()
        if self.isManagedRepository:
            defaultDataUris = self._dataStoreHandler.defaultDataUris
        return defaultDataUris
    
    def __getattr__(self, name):
        """ Delegates calls to encapsulated configuration handlers. """
        
        result = None
        if hasattr(self._dataModelHandler, name):
            result = getattr(self._dataModelHandler, name)
        if hasattr(self._dataStoreHandler, name):
            result = getattr(self._dataStoreHandler, name)
        if hasattr(self._iconHandler, name):
            result = getattr(self._iconHandler, name)
        if hasattr(self._scriptHandler, name):
            result = getattr(self._scriptHandler, name)
        if hasattr(self._propertyDefinitionFactory, name):
            result = getattr(self._propertyDefinitionFactory, name)
        if hasattr(self._propertyDefinitionRegistry, name):
            result = getattr(self._propertyDefinitionRegistry, name)
        if hasattr(self._dataFormatRegistry, name):
            result = getattr(self._dataFormatRegistry, name)
        if result is None:
            raise AttributeError("Unknown interface '%s'." % name)
        else:
            return result
