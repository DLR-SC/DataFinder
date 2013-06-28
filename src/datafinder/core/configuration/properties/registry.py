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
This module provides a registration service for property definitions.
"""


from threading import RLock
from copy import copy
import mimetypes

from datafinder.core.configuration.properties import constants as const
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.properties import property_type
from datafinder.core.error import ConfigurationError


__version__ = "$Revision-Id:$" 


class PropertyDefinitionRegistry(object):
    """ Implements a registry for property definitions. """

    def __init__(self, propertyDefinitionFactory, isManagedRepository):
        """ 
        @param propertyDefinitionFactory: Factory instance allowing 
            creation of property definitions.
        @type propertyDefinitionFactory: L{PropertyDefinitionFactory
            <datafinder.core.configuration.properties.property_definition.
            PropertyDefinitionFactory>}
        @param isManagedRepository: Flag indicating whether the system-specific 
            properties which are only required for managed repositories are also
            loaded.
        @type isManagedRepository: C{bool}
        """

        self._systemPropertyDefinitions = list()
        self._registeredPropertyDefinitions = dict()
        self._defaultCollectionPropertyDefinitions = list()
        self._defaultResourcePropertyDefinitions = list()
        self._defaultArchivePropertyDefinitions = list()
        self._lock = RLock()
        self._propertyDefinitionFactory = propertyDefinitionFactory
        
        self._initUnmanagedSystemProperties()
        if isManagedRepository:
            self._initManagedSystemProperties()
        self.register(self._systemPropertyDefinitions)
        
    def _initUnmanagedSystemProperties(self):
        """ Defines the common system-specific properties. """
        
        options = [mimeType for mimeType in mimetypes.types_map.values()]
        mimeTypeValidator = property_type.StringType(options=options)
        mimeTypeProperty = PropertyDefinition(
            const.MIME_TYPE_ID, 
            const.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
            mimeTypeValidator,
            const.MIME_TYPE_DISPLAYNAME,
            const.MIME_TYPE_DESCRIPTION)
        self._systemPropertyDefinitions.append(mimeTypeProperty)
              
        resourceCreationProperty = PropertyDefinition(
            const.CREATION_DATETIME_ID,
            const.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.DatetimeType(),
            const.CREATION_DATETIME_DISPLAYNAME,
            const.CREATION_DATETIME_DESCRIPTION)
        self._systemPropertyDefinitions.append(resourceCreationProperty)
        
        resourceModificationProperty = PropertyDefinition(
            const.MODIFICATION_DATETIME_ID, 
            const.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.DatetimeType(),
            const.MODIFICATION_DATETIME_DISPLAYNAME, 
            const.MODIFICATION_DATETIME_DESCRIPTION)
        self._systemPropertyDefinitions.append(resourceModificationProperty)
        
        sizeProperty = PropertyDefinition(
            const.SIZE_ID, 
            const.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.NumberType(0, None),
            const.SIZE_DISPLAYNAME, 
            const.SIZE_DESCRIPTION)
        self._systemPropertyDefinitions.append(sizeProperty)
        
        ownerProperty = PropertyDefinition(
            const.OWNER_ID, 
            const.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.StringType(),
            const.OWNER_DISPLAYNAME,
            const.OWNER_DESCRIPTION)
        self._systemPropertyDefinitions.append(ownerProperty)
    
    def _initManagedSystemProperties(self):
        """ Defines the common system-specific properties. """
    
        dataTypeProperty = PropertyDefinition(
            const.DATATYPE_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.StringType(),
            const.DATATYPE_DISPLAYNAME,
            const.DATATYPE_DESCRIPTION)
        self._systemPropertyDefinitions.append(dataTypeProperty)
    
        datastoreProperty = PropertyDefinition(
            const.DATASTORE_NAME_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.StringType(),
            const.DATASTORE_DISPLAYNAME,
            const.DATASTORE_NAME_DESCRIPTION)
        self._systemPropertyDefinitions.append(datastoreProperty)
    
        fileSizeProperty = PropertyDefinition(
            const.CONTENT_SIZE_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.NumberType(0, None),
            const.CONTENT_SIZE_DISPLAYNAME,
            const.CONTENT_SIZE_DESCRIPTION)
        self._systemPropertyDefinitions.append(fileSizeProperty)
        
        fileCreationProperty = PropertyDefinition(
            const.CONTENT_CREATION_DATETIME_PROPERTY_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.DatetimeType(),
            const.CONTENT_CREATION_DISPLAYNAME,
            const.CONTENT_CREATION_DATETIME_DESCRIPTION)
        self._systemPropertyDefinitions.append(fileCreationProperty)
        
        fileModificationProperty = PropertyDefinition(
            const.CONTENT_MODIFICATION_DATETIME_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY, 
            property_type.DatetimeType(),
            const.CONTENT_MODIFICATION_DATETIME_DISPLAYNAME,
            const.CONTENT_MODIFICATION_DATETIME_DESCRIPTION)
        self._systemPropertyDefinitions.append(fileModificationProperty)
        
        archiveIdentifierProperty = PropertyDefinition(
            const.CONTENT_IDENTIFIER_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.StringType(),
            const.CONTENT_IDENTIFIER,
            const.CONTENT_IDENTIFIER_DESCRIPTION)
        self._systemPropertyDefinitions.append(archiveIdentifierProperty)
        
        archiveRetentionExceededProperty = PropertyDefinition(
            const.ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.DatetimeType(),
            const.ARCHIVE_RETENTION_EXCEEDED_DISPLAYNAME,
            const.ARCHIVE_RETENTION_EXCEEDED_DESCRIPTION)
        self._systemPropertyDefinitions.append(archiveRetentionExceededProperty)
        
        archiveRootCollectionProperty = PropertyDefinition(
            const.ARCHIVE_ROOT_COLLECTION_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.StringType(),
            const.ARCHIVE_ROOT_COLLECTION_DISPLAYNAME,
            const.ARCHIVE_ROOT_COLLECTION_DESCRIPTION)
        self._systemPropertyDefinitions.append(archiveRootCollectionProperty)
        
        archivePartIndexProperty = PropertyDefinition(
            const.ARCHIVE_PART_INDEX_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.NumberType(0, None),
            const.ARCHIVE_PART_INDEX_DISPLAYNAME,
            const.ARCHIVE_PART_INDEX_DESCRIPTION)
        self._systemPropertyDefinitions.append(archivePartIndexProperty)
        
        archivePartCount = PropertyDefinition(
            const.ARCHIVE_PART_COUNT_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.NumberType(0, None),
            const.ARCHIVE_PART_COUNT_DISPLAYNAME,
            const.ARCHIVE_PART_COUNT_DESCRIPTION)
        self._systemPropertyDefinitions.append(archivePartCount)

        dataFormatProperty = PropertyDefinition(
            const.DATA_FORMAT_ID, 
            const.MANAGED_SYSTEM_PROPERTY_CATEGORY,
            property_type.StringType(),
            const.DATA_FORMAT_DISPLAYNAME,
            const.DATA_FORMAT_DESCRIPTION)
        self._systemPropertyDefinitions.append(dataFormatProperty)
        
        # init default property definitions
        self._defaultCollectionPropertyDefinitions.append(dataTypeProperty)
        self._defaultResourcePropertyDefinitions.append(dataFormatProperty)
        self._defaultResourcePropertyDefinitions.append(datastoreProperty)
        self._defaultResourcePropertyDefinitions.append(fileCreationProperty)
        self._defaultResourcePropertyDefinitions.append(fileModificationProperty)
        self._defaultResourcePropertyDefinitions.append(fileSizeProperty)
        self._defaultArchivePropertyDefinitions.append(datastoreProperty)
        self._defaultArchivePropertyDefinitions.append(archiveRetentionExceededProperty)
        
    def register(self, propertyDefinitions):
        """ 
        Registers property definitions. A registered definition can 
        be updated by simply registering again.
        
        @param propertyDefinition: The property definitions to register.
        @type propertyDefinition: C{list} of L{PropertyDefinition}
        """
        
        self._lock.acquire()
        try:
            notRegPropDefs = list()
            for propDef in propertyDefinitions:
                try:
                    regPropDef = self._registeredPropertyDefinitions[(propDef.namespace, 
                        propDef.identifier)]    
                except KeyError:
                    self._registeredPropertyDefinitions[(propDef.namespace, 
                        propDef.identifier)] = propDef
                else:
                    if regPropDef.category == const.MANAGED_SYSTEM_PROPERTY_CATEGORY \
                       or regPropDef.category == const.UNMANAGED_SYSTEM_PROPERTY_CATEGORY:
                        notRegPropDefs.append(propDef)
                    else:
                        self._registeredPropertyDefinitions[(propDef.namespace, 
                            propDef.identifier)] = propDef
            if len(notRegPropDefs) > 0:
                propNames = [propDef.identifier + " " for propDef in notRegPropDefs]
                errorMessage = "The following properties were not registered because " \
                               + "system-specific property definitions already exist.\n '%s'" \
                               % propNames  
                raise ConfigurationError(errorMessage)
        finally:
            self._lock.release()
            
    def unregister(self, propertyDefinitions):
        """
        Removes the given property type definitions from the registration.
        
        @param propertyDefinitions: The property definition to unregister.
        @type propertyDefinitions: C{list} of C{PropertyDefinition}
        """
    
        self._lock.acquire()
        try:
            for propDef in propertyDefinitions:
                key = (propDef.namespace, propDef.identifier)
                if key in self._registeredPropertyDefinitions:
                    del self._registeredPropertyDefinitions[key]
        finally:
            self._lock.release()
    
    def clear(self):
        """ Clears the list of registered property definitions. """
        
        self._lock.acquire()
        try:
            self._registeredPropertyDefinitions.clear()
            self.register(self._systemPropertyDefinitions)
        finally:
            self._lock.release()
    
    def existsSystemPropertyDefinition(self, identifier):
        """ 
        Checks whether a system-specific property exists for the 
        given property identifier.
        
        @param identifier: Identifier of the property definition.
        @type identifier: C{unicode}
        
        @return: Flag indicating existence of a system-specfic property.
        @rtype: C{bool}
        """
    
        self._lock.acquire()
        try:
            return (None, identifier) in self._registeredPropertyDefinitions
        finally:
            self._lock.release()
            
    def isPropertyDefinitionRegistered(self, propertyDefinition):
        """ 
        Checks whether the given property is already registered. 
        
        @return: Flag indicating the existence of the property with 
            the given identifier and name space.
        @rtype: C{bool}
        """
            
        self._lock.acquire()
        try:
            key = (propertyDefinition.namespace, propertyDefinition.identifier)
            if key in self._registeredPropertyDefinitions:
                return True
            return False
        finally:
            self._lock.release()
        
    def getPropertyDefinition(self, propertyIdentifier, namespace=None):
        """
        Returns a property type definition for the given identifier.
        
        @param propertyIdentifier: Property identifier.
        @type propertyIdentifier: C{unicode}
        @param namespace: Name space of the property, i.e. the data type name 
            it is registered for.
        @type namespace: C{unicode}
        
        @return: Matching property definition.
        @rtype: L{PropertyDefinition}
        
        @raise ConfigurationError: Indicates problem on property definition creation.
        """
        
        self._lock.acquire()
        try:
            regPropDef = None
            if (namespace, propertyIdentifier) in self._registeredPropertyDefinitions:
                regPropDef = copy(
                    self._registeredPropertyDefinitions[(namespace, propertyIdentifier)])
            if (None, propertyIdentifier) in self._registeredPropertyDefinitions:
                regPropDef = copy(
                    self._registeredPropertyDefinitions[(None, propertyIdentifier)])
            if regPropDef is None:
                regPropDef = self._propertyDefinitionFactory.\
                    createPropertyDefinition(propertyIdentifier, 
                                             const.USER_PROPERTY_CATEGORY)
            return regPropDef
        finally:
            self._lock.release()

    @property
    def defaultCollectionPropertyDefinitions(self):
        """ Getter for the default properties of a collection. """
        
        return self._defaultCollectionPropertyDefinitions[:]
    
    @property
    def defaultResourcePropertyDefinitions(self):
        """ Getter for the default properties of a collection. """
        
        return self._defaultResourcePropertyDefinitions[:]
    
    @property
    def defaultArchivePropertyDefinitions(self):
        """ Returns the default properties of an archive. """
        
        return self._defaultArchivePropertyDefinitions[:]
    
    @property
    def registeredPropertyDefinitions(self):
        """
        Returns a mapping of property identifiers to existing property type definitions.
        
        @return: Mapping of property definition identifiers (namespace, property id) 
            to property type definitions.
        @rtype: C{dict}; keys: C{unicode}, C{unicode}; values: C{PropertyDefinition}
        """
        
        self._lock.acquire()
        try:
            return copy(self._registeredPropertyDefinitions)
        finally:
            self._lock.release()
    
    @property
    def systemPropertyDefinitions(self):
        """
        Returns a list of system-specific property type definitions.
        
        @return: Mapping of property definition identifiers 
            (namespace, property id) to property type definitions.
        @rtype: C{list} of C{PropertyDefinition}
        """
        
        self._lock.acquire()
        try:
            return self._systemPropertyDefinitions[:]
        finally:
            self._lock.release()

    @property
    def propertyNameValidationFunction(self):
        """ Getter for the property identifier validation function. 
        In addition to the pure name validation the function rejects IDs
        which have been already registered.
        
        The returned function expects a string as input and returns a boolean 
        value.
        """
        
        def _wrapperFunction(inputString):
            return self._propertyDefinitionFactory.isValidPropertyIdentifier(inputString) \
                   and not self.existsSystemPropertyDefinition(inputString)
        return _wrapperFunction
