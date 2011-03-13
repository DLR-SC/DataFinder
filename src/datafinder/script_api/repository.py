# pylint: disable=W0212
# W0212: We can need to access the _repository attribute of the
# repository description only for internal usage.
#
# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Module for a simple repository interface.
"""


from datafinder.core.error import ConfigurationError, ItemError
from datafinder.core.repository_manager import repositoryManagerInstance
from datafinder.script_api.error import ScriptApiError, ItemSupportError


__version__ = "$Revision-Id:$" 


def connectRepository(dataUri, configUri=None, username=None, password=None):
    """
    Connect to a remote repository.
        
    @param dataUri: URI identifying the root item of repository which has to be connected.
    @type dataUri: C{unicode}
    @param configUri: Optional repository configuration URI. Default: C{None}
    @type configUri: C{unicode}
    @param username: Optional user name. Default: C{None}
    @type username: C{unicode}
    @param password: Optional password. Default: C{None}
    @type password: C{unicode}
    
    @raise ScriptApiError: Raised when an error occurred.
    """

    try:        
        configuration = repositoryManagerInstance.getRepositoryConfiguration(configUri, username, password)
        configuration.load()
        repository = repositoryManagerInstance.connectRepository(dataUri, configuration, username, password)
        repositoryDescription = RepositoryDescription(repository)
    except ConfigurationError:
        raise ScriptApiError("Unable to initialize configuration.")
    else:     
        return repositoryDescription


def disconnectRepository(repositoryDescription):        
    """
    Disconnects the given repository.
        
    @param repositoryDescription: Repository to disconnect.
    @type repositoryDescription: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    
    @raise ScriptApiError: Raised when an error occurred.
    """  

    try:
        repositoryManagerInstance.disconnectRepository(repositoryDescription._repository)
    except ConfigurationError, error:
        raise ScriptApiError("Unable to disconnect repository. Reason: %s" % error.message)


def getWorkingRepository():
    """
    Get the current working repository.
    """
    
    return RepositoryDescription(repositoryManagerInstance.workingRepository)


def setWorkingRepository(repositoryDescription):
    """
    Set the current working repository.
    
    @param repositoryDescription: Repository to set.
    @type repositoryDescription: L{RepositoryDescription<datafinder.script_api.repository.RepositoryDescription>}
    """
    
    repositoryManagerInstance.workingRepository = repositoryDescription._repository


class RepositoryDescription(object):
    """
    The repository represents the container for the items.
    """
    
    def __init__(self, repository):
        """
        Constructor.
        
        @param repository: The repository.
        @type repository: L{Repository<datafinder.core.repository.Repository>}
        """
        
        self._repository = repository
    
    def determineUniqueItemName(self, proposedName, targetParentPath):
        """ Determines a unique name. """
        
        try:
            targetParentItem = self._repository.getItem(targetParentPath)
        except ItemError:
            raise ItemSupportError("Item cannot be found.")
        else:
            return self._repository.determineUniqueItemName(proposedName, targetParentItem)
    
    def isValidIdentifier(self, identifier):
        """ 
        Checks whether the given string describes a valid identifier.
        
        @param identifier: String describing the identifier.
        @type identifier: C{unicode}
        
        @return: C{True},C{None} if it is valid, otherwise C{False}, position
        @rtype: C{tuple} of C{bool}, C{int}
        """
        
        return self._repository.isValidIdentifier(identifier)
        
    def isValidPropertyIdentifier(self, identifier):
        """ 
        Checks whether the given string describes a valid property identifier.
        
        @param identifier: String describing the property identifier.
        @type identifier: C{unicode}
        
        @return: C{True} if it is valid, otherwise C{False}
        @rtype: C{bool}
        """
        
        return self._repository.isValidPropertyIdentifier(identifier)

    @property
    def isManagedRepository(self):
        """ Checks whether the repository is a managed or an unmanaged repository. """
        
        return self._repository.repositoryConfiguration.isManagedRepository
    
    @property
    def hasCustomMetadataSupport(self):
        """
        Checks whether it is allowed to store custom meta data or not.
        """
        
        return self._repository.hasCustomMetadataSupport
    
    @property
    def hasMetadataSearchSupport(self):
        """
        Checks whether a meta data search is supported.
        """
        
        return self._repository.hasMetadataSearchSupport
    
    @property
    def hasPrivilegeSupport(self):
        """
        Checks whether privilege setting is supported.
        """
        
        return self._repository.hasPrivilegeSupport

    def __cmp__(self, other):
        """ Implements comparison. """
        
        return cmp(self._repository, other._repository)
