#
# Created: 28.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory.py 4626 2010-04-20 20:57:02Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
This module provides access to a generic file system interface.
A file system - in dependence to the used interface - provides
a certain feature set (e.g. custom meta data, meta data search,
ACL).
"""


from urlparse import urlsplit
        
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.filestorer import FileStorer


__version__ = "$LastChangedRevision: 4626 $"


def createFileStorer(itemUri, additionalParameters=BaseConfiguration()):
    """ 
    Creates a file storer object for the given URI. 

    @param itemUri:This is the URI of file storer item. 
    @type itemUri: C{unicode}
    @param additionalParameters: Defines additional parameters, e.g. credentials.
    @type additionalParameters: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
    
    @note: When setting C{itemUri} to C{None} a null pattern conform file storer 
           implementation is returned. 
    """
    
    if itemUri is None:
        return FileSystem(None).createFileStorer("/")
    else:
        parsedUri = urlsplit(itemUri)
        baseUri = parsedUri.scheme + "://" + parsedUri.netloc + "/"
        additionalParameters.baseUri = baseUri
        return FileSystem(additionalParameters).createFileStorer(parsedUri.path)
    

class FileSystem(object):
    """ Implements a generic file system interface. """
    
    _uriSchemeAdapterMap = {"http": "webdav_",
                            "https": "webdav_",
                            "file": "filesystem",
                            "ldap": "ldap_",
                            "tsm": "tsm",
                            "arch": "archive",
                            "s3": "amazonS3"}
    
    _BASE_IMPL_PACKAGE_PATTERN = "datafinder.persistence.adapters.%s.factory"
    
    def __init__(self, baseConfiguration=None, basePrincipalSearchConfiguration=None):
        """ 
        Initializes the generic file system. 
        
        @param baseConfiguration: Specifies configuration of the generic file system.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        @param basePrincipalSearchConfiguration: Specifies configuration properties of the principal search.
        @type basePrincipalSearchConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}

        @raise PersistenceError: Indicates an unsupported interface or wrong configuration.
        """

        self._baseConfiguration = baseConfiguration
        if not baseConfiguration is None:
            self._factory = self._getFactory(baseConfiguration.uriScheme)(baseConfiguration)
            if basePrincipalSearchConfiguration is None:
                self._principalSearchFactory = self._factory
            else:
                self._principalSearchFactory = self._getFactory(baseConfiguration.uriScheme)(basePrincipalSearchConfiguration)
        else:
            self._factory = BaseFileSystem()
            self._principalSearchFactory = BaseFileSystem()
            
    def _getFactory(self, uriScheme):
        """ Determines dynamically the concrete factory implementation. """
        
        try:
            adapterPackageName = self._uriSchemeAdapterMap[uriScheme]
        except KeyError:
            raise PersistenceError("The URI scheme '%s' is unsupported." % uriScheme)
        else:
            fullDottedModuleName = self._BASE_IMPL_PACKAGE_PATTERN % adapterPackageName
            try:
                moduleInstance = __import__(fullDottedModuleName, globals(), dict(), [""])
                return getattr(moduleInstance, self.__class__.__name__)
            except (ImportError, AttributeError):
                errorMessage = "The specified interface '%s' is not supported." % adapterPackageName
                raise PersistenceError(errorMessage)

    def createFileStorer(self, identifier):
        """ 
        Creates a C{FileStorer} which represents a concrete item in the file system.
        
        @param identifier: Path of the item within the file system.
        @type identifier: C{unicode}
        
        @return: Representation of the item in the file system.
        @rtype: L{FileStorer<datafinder.persistence.factory.FileStorer>} 
        """
        
        self._factory.prepareUsage()
        dataStorer = self._factory.createDataStorer(identifier)
        metadataStorer = self._factory.createMetadataStorer(identifier)
        privilegeStorer = self._factory.createPrivilegeStorer(identifier)
        return FileStorer(self, identifier, dataStorer, metadataStorer, privilegeStorer)

    def searchPrincipal(self, pattern, searchMode):
        """ 
        Retrieves principals matching the given restrictions.
        
        @param pattern: Principal name pattern.
        @type pattern: C{unicode}
        @param searchMode: Distinguishes search for users / groups or both.
        @type searchMode: C{unicode} @see L{Constants<definition<datafinder.persistence.constants>} 
        
        @return: Matched principals described by dictionary (unique name => {displayName, isUser, [memberOf])}.
        @rtype: C{dict} keys: C{unicode} values: C{tuple} of C{unicode}, C{bool}, C{list} of C{unicode}
        """
        
        principalSearcher = self._principalSearchFactory.createPrincipalSearcher()
        return principalSearcher.searchPrincipal(pattern, searchMode)
    
    def updateCredentials(self, credentials):
        """ 
        Updates the authentication information used for general file system access. 
        
        @param credentials: Dictionary containing the specific authentication information, e.g. user name, password.
        @type credentials: C{dict} 
        """
        
        self._factory.updateCredentials(credentials)
            
    def updatePrincipalSearchCredentials(self, credentials):
        """ 
        Updates the authentication information used for principal search.
        
        @param credentials: Dictionary containing the specific authentication information, e.g. user name, password.
        @type credentials: C{dict} 
        """
        
        self._principalSearchFactory.updateCredentials(credentials)
    
    def release(self):
        """ Releases the file system. """
        
        self._factory.release()

    @property
    def baseConfiguration(self):
        """ Returns the configuration parameters. """
        
        return self._baseConfiguration
            
    @property
    def baseUri(self):
        """ Getter for the base URI. """
        
        result = None
        if not self._baseConfiguration is None:
            result = self._baseConfiguration.baseUri
        return result
    
    @property
    def isAccessible(self):
        """ Flag indicating whether the file system is accessible. """
            
        isAccessible = True
        try:
            self._factory.prepareUsage()
        except PersistenceError:
            isAccessible = False
        else:
            try:
                isAccessible = self.createFileStorer("/").exists()
            except PersistenceError:
                isAccessible = False
        return isAccessible

    @property
    def hasCustomMetadataSupport(self):
        """ 
        Checks whether file system supports the annotation of custom meta data. 
        
        @return: Flag indicating whether custom meta data is supported.
        @rtype: C{bool}
        """
        
        return self._factory.hasCustomMetadataSupport

    def isValidIdentifier(self, name):
        """ 
        Checks whether the given string can be used as a file storer identifier.
        
        @param name: Name to check.
        @type name: C{unicode}
        
        @return: Tuple indicating whether it is valid or not and 
                 - when available - the error position. C{None} identifies
                 the empty error position.
        @rtype: C{tuple} of C{bool}, C{int}
        """
        
        return self._factory.isValidIdentifier(name)

    def isValidMetadataIdentifier(self, name):
        """ 
        Checks whether the given string can be used as a meta data identifier.
        
        @param name: Name to check.
        @type name: C{unicode}
        
        @return: Tuple indicating whether it is valid or not and 
                 - when available - the error position. C{None} identifies
                 the empty error position.
        @rtype: C{tuple} of C{bool}, C{int}
        """
        
        return self._factory.isValidMetadataIdentifier(name)

    @property
    def hasMetadataSearchSupport(self):
        """ 
        Checks whether file system supports a search in meta data. 
        
        @return: Flag indicating whether meta data search is supported.
        @rtype: C{bool}
        """
        
        return self._factory.hasMetadataSearchSupport

    @property
    def hasPrivilegeSupport(self):
        """ 
        Checks whether the file system supports the setting of privileges. 
        
        @return: Flag indicating whether setting of privileges is supported.
        @rtype: C{bool}
        """
    
        return self._factory.hasPrivilegeSupport
