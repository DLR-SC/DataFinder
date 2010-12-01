# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
Implements the model component of the create configuration dialog.
"""


__version__ = "$Revision-Id:$" 


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
