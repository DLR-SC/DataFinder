#
# Created: 09.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: util.py 4460 2010-02-12 09:04:16Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements mapping of logical identifiers to WebDAV-specific identifiers.
"""


import urlparse

from webdav.Connection import WebdavError
from webdav.WebdavClient import ResourceStorer, CollectionStorer
from webdav.WebdavRequests import createFindBody

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.adapters.webdav_.constants import RESOURCE_TYPE_PROPERTY, LINK_TARGET_PROPERTY


__version__ = "$LastChangedRevision: 4460 $"


class ItemIdentifierMapper(object):
    """ Utility class mapping identifiers. """
    
    def __init__(self, baseUrl):
        """ 
        Constructor.
        
        @param baseUrl: WebDAV base URL.
        @type baseUrl: C{unicode}
        """
        
        self.__baseUrl = baseUrl
        if self.__baseUrl.endswith("/"):
            self.__baseUrl = self.__baseUrl[:-1]
        self.__basePath = urlparse.urlsplit(self.__baseUrl).path
        
    def mapIdentifier(self, identifier):
        """ 
        Maps the logical identifier to the persistence representation.
        
        @param identifier: Path relative to the configured base URL.
                           Base URL is implicitly represented by '/'.
        @type identifier: C{unicode}
        
        @return: URL identifying the resource.
        @rtype: C{unicode}
        """
        
        if identifier.startswith("/"):
            persistenceId = self.__baseUrl + identifier
        else:
            persistenceId = self.__baseUrl + "/" + identifier
        return persistenceId

    @staticmethod
    def determineBaseName(identifier):
        """ 
        Determines the last component of the logical path - the base name. 
        
        @param identifier: The interface identifier.
        @type identifier: C{unicode}
        
        @return: Last part of the identifier.
        @rtype: C{unicode}
        """
        
        return identifier.rsplit("/")[-1]
            
    @staticmethod
    def determineParentPath(identifier):
        """ 
        Determines the parent path of the logical path. 
        
        @param identifier: The interface identifier.
        @type identifier: C{unicode}
        
        @return: The parent path of the identifier.
        @rtype: C{unicode}
        """
        
        parentPath = "/".join(identifier.rsplit("/")[:-1])
        if parentPath == "" and identifier.startswith("/") and identifier != "/":
            parentPath = "/"
        return parentPath
    
    def mapPersistenceIdentifier(self, identifier):
        """ 
        Maps the persistence identifier to the logical representation. 
        
        @param identifier: URL identifying the resource.
        @type identifier: C{unicode}
        
        @return: Path relative to the configured base URL.
        @rtype: C{unicode}
        """
        
        parsedUrl = urlparse.urlsplit(identifier)
        result = parsedUrl.path
        if result.startswith(self.__basePath):
            result = result[len(self.__basePath):]
        if result.endswith("/"):
            result = result[:-1]
        if not result.startswith("/"):
            result = "/" + result
        return result


def createResourceStorer(persistenceIdentifier, connection, validate=False):
    """
    Creates a C{ResourceStorer} object to manage a WebDAV resource.
    
    @param persistenceIdentifier: URL identifying the collection.
    @type persistenceIdentifier: C{unicode}
    @param connection: Connection used to perform WebDAV server requests.
    @type connection: L{Connection<webdav.Connection.Connection>}
    @param validate: Flag indicating automatic existence validation. Default is C{False}.
    @type validate: C{bool}
    
    @return: Object representing the WebDAV resource.
    @rtype: instance of L{ResourceStorer<webdav.WebdavClient.ResourceStorer>}
    
    @raise PersistenceError - Indicating problems with WebDAV connection. 
    """
    
    webdavStorer = ResourceStorer(persistenceIdentifier, connection)
    if validate:
        _checkWebdavConnection(webdavStorer)
    return webdavStorer


def createCollectionStorer(persistenceIdentifier, connection, validate=False):
    """
    Creates a C{CollectionStorer} object to manage a WebDAV resource.
    
    @param persistenceIdentifier: URL identifying the collection.
    @type persistenceIdentifier: C{unicode}
    @param connection: Connection used to perform WebDAV server requests.
    @type connection: L{Connection<webdav.Connection.Connection>}
    @param validate: Flag indicating automatic existence validation. Default is C{False}.
    @type validate: C{bool}
    
    @return: Object representing the WebDAV resource.
    @rtype: instance of L{CollectionStorer<webdav.WebdavClient.CollectionStorer>}
    
    @raise PersistenceError - Indicating problems with WebDAV connection.
    """

    webdavStorer = CollectionStorer(persistenceIdentifier, connection)
    if validate:
        _checkWebdavConnection(webdavStorer)
    return webdavStorer    


def _checkWebdavConnection(webdavStorer):
    """ Checks the connection of the given resource. """
    
    try:
        webdavStorer.validate()
    except WebdavError, error:
        errorMessage = "Cannot connect to WebDAV server. Reason '%s'." % error.reason
        raise PersistenceError(errorMessage)


def determineResourceType(resourceStorer, includeChildren=False):
    """ 
    Helper method to determine resource type (link, resource, collection) 
    of the given WebDAV resource (including or excluding its children).
    
    @param resourceStorer: 
    @type resourceStorer: instance of L{ResourceStorer<webdav.WebdavClient.ResourceStorer>}
    @param includeChildren: Flag indicating that the resource type of the children is determined as well.
    @type includeChildren: C{bool}
    """
    
    depth = 0
    if includeChildren:
        depth = 1
    body = createFindBody([LINK_TARGET_PROPERTY, RESOURCE_TYPE_PROPERTY])
    response = resourceStorer.connection.propfind(resourceStorer.path, body, depth=depth)
    result = dict()
    for path, properties in response.msr.items():
        isCollection = None
        linkTargetPath = None
        if RESOURCE_TYPE_PROPERTY in properties:
            isCollection = len(properties[RESOURCE_TYPE_PROPERTY].children) > 0
        if LINK_TARGET_PROPERTY in properties:
            linkTargetPath = properties[LINK_TARGET_PROPERTY].textof()
        result[path] = isCollection, linkTargetPath
    return result
