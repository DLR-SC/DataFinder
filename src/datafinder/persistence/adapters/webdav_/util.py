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
Implements mapping of logical identifiers to WebDAV-specific identifiers.
"""


import urlparse

from webdav.Connection import WebdavError
from webdav.WebdavClient import ResourceStorer, CollectionStorer
from webdav.WebdavRequests import createFindBody

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.adapters.webdav_.constants import RESOURCE_TYPE_PROPERTY, LINK_TARGET_PROPERTY


__version__ = "$Revision-Id:$" 


class ItemIdentifierMapper(object):
    """ Utility class mapping identifiers. """
    
    def __init__(self, baseUrl):
        """ 
        Constructor.
        
        @param baseUrl: WebDAV base URL.
        @type baseUrl: C{unicode}
        """
        # pylint: disable=E1103
        # E1103: urlsplit produces the required results but Pylint
        # cannot correctly determine it.

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
        # pylint: disable=E1103
        # E1103: urlsplit produces the required results but Pylint
        # cannot correctly determine it.

        parsedUrl = urlparse.urlsplit(identifier, allow_fragments=False)
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
