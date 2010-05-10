# pylint: disable-msg=W0212
#
# Created: 04.02.2010 Patrick Schaefer <patrick.schaefer@dlr.de>
# Changed: $Id: repository.py 4554 2010-03-21 11:58:03Z schlauch $ 
# 
# Copyright (c) 2010, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
Module for a simple repository interface.
"""


from datafinder.core.error import ConfigurationError, ItemError
from datafinder.core.repository_manager import repositoryManagerInstance
from datafinder.script_api.error import ScriptApiError, ItemSupportError


__version__ = "$LastChangedRevision: 4554 $"


def connectRepository(dataUri, configUri=None, username=None, password=None):
    """
    Connect to a remote repository.
        
    @type connection: L{<datafinder.core.configuration.preferences.connection>} 
    
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
    
    @param repositoryDesrciption: Repository to set.
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
