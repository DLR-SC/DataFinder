#
# Created: 06.11.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: model.py 3919 2009-04-07 15:52:01Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the model component of the create configuration dialog.
"""


__version__ = "$LastChangedRevision: 3919 $"


from datafinder.common import logger
from datafinder.core.error import ConfigurationError


_logger = logger.getDefaultLogger()


class CreateConfigurationModel(object):
    """ Implements the model component of the create configuration dialog. """
    
    def __init__(self, repositoryManager):
        """ Constructor. """
        
        self._repositoryManager = repositoryManager
        self._preferences = repositoryManager.preferences
        self._configurationUri = None
        self._dataPath = None
        self._repositoryConfiguration = None
        self._exists = None
        self._username = None
        self._password = None
        
    def reset(self):
        """ Resets the repository configuration. """
        
        self._configurationUri = None
        self._dataPath = None
        self._repositoryConfiguration = None
        self._exists = None
        
    def __exists(self):
        """ Getter of the existence flag. """
        
        if self._exists is None:
            raise ConfigurationError("Repository configuration is not initialized.")
        else:
            return self._exists
    exists = property(__exists)
        
    def prepareConfiguration(self, hostUri, configurationPath, dataPath, username, password):
        """ 
        Performs some basic checks of the paths. 
        
        @param configurationUri: URI of the configuration area.
        @type configurationUri: C{unicode}
        @param dataPath: Path of the data area.
        @type dataPath: C{unicode}
        
        @raise ConfigurationError: Indicating problems on repository initialization.
        """
        
        if not hostUri.endswith("/"):
            hostUri += "/"
        if configurationPath.startswith("/"):
            configurationPath = configurationPath[1:]
        if configurationPath.endswith("/"):
            configurationPath = configurationPath[:-1]
        if dataPath.startswith("/"):
            dataPath = dataPath[1:]
        if dataPath.endswith("/"):
            dataPath = dataPath[:-1]
        if dataPath == configurationPath:
            raise ConfigurationError("Configuration and data path should not be equal.")
        else:
            self._configurationUri = hostUri + configurationPath
            self._dataPath = dataPath
            self._username = username
            self._password = password
            
            self._repositoryConfiguration = self._repositoryManager.getRepositoryConfiguration(self._configurationUri,
                                                                                               username=self._username,
                                                                                               password=self._password,
                                                                                               baseUri=hostUri)
            self._exists = self._repositoryConfiguration.exists()
                    
    def createConfiguration(self, overwrite=True):
        """ 
        Creates the configuration or overwrites an existing.
        
        @param overwrite: Optional flag indicating whether an existing configuration is replaced. Default: C{True}
        @type overwrite: C{bool}
        """
        
        self._repositoryConfiguration.create(overwrite, self._dataPath)
        self._preferences.addConnection(self._configurationUri, self._username, self._password)
