#
# Created: 09.06.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: registry.py 4524 2010-03-05 14:09:59Z schlauch $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" 
This module provides a registration service for property definitions.
"""


from threading import RLock
from copy import copy
import mimetypes

from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.properties import property_type
from datafinder.core.error import ConfigurationError


__version__ = "$LastChangedRevision: 4524 $"


class PropertyDefinitionRegistry(object):
    """ Implements a registry for property types. """

    def __init__(self, propertyDefinitionFactory, isManagedRepository):
        """ 
        Constructor. 
        
        @param propertyDefinitionFactory: Factory instance allowing creation of property definitions.
        @type propertyDefinitionFactory: L{PropertyDefinitionFactory<datafinder.core.configuration.
        properties.property_definition.PropertyDefinitionFactory>}
        @param isManagedRepository: Flag indicating whether the system-specific properties
                                    which are only required for managed repositories are also
                                    loaded.
        @type isManagedRepository: C{bool}
        """

        self._systemProperties = list()
        self._registeredProperties = dict()
        self._defaultCollectionPropertyDefinitions = list()
        self._defaultResourcePropertyDefinitions = list()
        self._defaultArchivePropertyDefinitions = list()
        self._lock = RLock()
        self._propertyDefinitionFactory = propertyDefinitionFactory

        self._initUnmanagedSystemProperties()
        if isManagedRepository:
            self._initManagedSystemProperties()
        self.register(self._systemProperties)

    def _initUnmanagedSystemProperties(self):
        """ Defines the common system-specific properties. """
        
        options = [mimeType for mimeType in mimetypes.types_map.values()]
        mimeTypeValidator = property_type.StringType(options=options)
        mimeTypeProperty = PropertyDefinition(constants.MIME_TYPE_ID, 
                                              constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
                                              mimeTypeValidator,
                                              constants.MIME_TYPE_DISPLAYNAME,
                                              constants.MIME_TYPE_DESCRIPTION)
        self._systemProperties.append(mimeTypeProperty)
              
        resourceCreationProperty = PropertyDefinition(constants.CREATION_DATETIME_ID,
                                                      constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
                                                      property_type.DatetimeType(),
                                                      constants.CREATION_DATETIME_DISPLAYNAME,
                                                      constants.CREATION_DATETIME_DESCRIPTION)
        self._systemProperties.append(resourceCreationProperty)
        
        resourceModificationProperty = PropertyDefinition(constants.MODIFICATION_DATETIME_ID, 
                                                          constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
                                                          property_type.DatetimeType(),
                                                          constants.MODIFICATION_DATETIME_DISPLAYNAME, 
                                                          constants.MODIFICATION_DATETIME_DESCRIPTION)
        self._systemProperties.append(resourceModificationProperty)
        
        sizeProperty = PropertyDefinition(constants.SIZE_ID, 
                                          constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
                                          property_type.NumberType(0, None),
                                          constants.SIZE_DISPLAYNAME, 
                                          constants.SIZE_DESCRIPTION)
        self._systemProperties.append(sizeProperty)
        
        ownerProperty = PropertyDefinition(constants.OWNER_ID, 
                                           constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY,
                                           property_type.StringType(),
                                           constants.OWNER_DISPLAYNAME,
                                           constants.OWNER_DESCRIPTION)
        self._systemProperties.append(ownerProperty)
    
    def _initManagedSystemProperties(self):
        """ Defines the common system-specific properties. """
    
        dataTypeProperty = PropertyDefinition(constants.DATATYPE_ID, 
                                              constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                              property_type.StringType(),
                                              constants.DATATYPE_DISPLAYNAME,
                                              constants.DATATYPE_DESCRIPTION)
        self._systemProperties.append(dataTypeProperty)
    
        datastoreProperty = PropertyDefinition(constants.DATASTORE_NAME_ID, 
                                               constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                               property_type.StringType(),
                                               constants.DATASTORE_DISPLAYNAME,
                                               constants.DATASTORE_NAME_DESCRIPTION)
        self._systemProperties.append(datastoreProperty)
    
        fileSizeProperty = PropertyDefinition(constants.CONTENT_SIZE_ID, 
                                              constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                              property_type.NumberType(0, None),
                                              constants.CONTENT_SIZE_DISPLAYNAME,
                                              constants.CONTENT_SIZE_DESCRIPTION)
        self._systemProperties.append(fileSizeProperty)
        
        fileCreationProperty = PropertyDefinition(constants.CONTENT_CREATION_DATETIME_PROPERTY_ID, 
                                                  constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                                  property_type.DatetimeType(),
                                                  constants.CONTENT_CREATION_DISPLAYNAME,
                                                  constants.CONTENT_CREATION_DATETIME_DESCRIPTION)
        self._systemProperties.append(fileCreationProperty)
        
        fileModificationProperty = PropertyDefinition(constants.CONTENT_MODIFICATION_DATETIME_ID, 
                                                      constants.MANAGED_SYSTEM_PROPERTY_CATEGORY, 
                                                      property_type.DatetimeType(),
                                                      constants.CONTENT_MODIFICATION_DATETIME_DISPLAYNAME,
                                                      constants.CONTENT_MODIFICATION_DATETIME_DESCRIPTION)
        self._systemProperties.append(fileModificationProperty)
        
        archiveIdentifierProperty = PropertyDefinition(constants.CONTENT_IDENTIFIER_ID, 
                                                       constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                                       property_type.StringType(),
                                                       constants.CONTENT_IDENTIFIER,
                                                       constants.CONTENT_IDENTIFIER_DESCRIPTION)
        self._systemProperties.append(archiveIdentifierProperty)
        
        archiveRetentionExceededProperty = PropertyDefinition(constants.ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID, 
                                                              constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                                              property_type.DatetimeType(),
                                                              constants.ARCHIVE_RETENTION_EXCEEDED_DISPLAYNAME,
                                                              constants.ARCHIVE_RETENTION_EXCEEDED_DESCRIPTION)
        self._systemProperties.append(archiveRetentionExceededProperty)
        
        archiveRootCollectionProperty = PropertyDefinition(constants.ARCHIVE_ROOT_COLLECTION_ID, 
                                                           constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                                           property_type.StringType(),
                                                           constants.ARCHIVE_ROOT_COLLECTION_DISPLAYNAME,
                                                           constants.ARCHIVE_ROOT_COLLECTION_DESCRIPTION)
        self._systemProperties.append(archiveRootCollectionProperty)
        
        archivePartIndexProperty = PropertyDefinition(constants.ARCHIVE_PART_INDEX_ID, 
                                                      constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                                      property_type.NumberType(0, None, 0, 0),
                                                      constants.ARCHIVE_PART_INDEX_DISPLAYNAME,
                                                      constants.ARCHIVE_PART_INDEX_DESCRIPTION)
        self._systemProperties.append(archivePartIndexProperty)
        
        archivePartCount = PropertyDefinition(constants.ARCHIVE_PART_COUNT_ID, 
                                              constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                              property_type.NumberType(0, None, 0, 0),
                                              constants.ARCHIVE_PART_COUNT_DISPLAYNAME,
                                              constants.ARCHIVE_PART_COUNT_DESCRIPTION)
        self._systemProperties.append(archivePartCount)

        dataFormatProperty = PropertyDefinition(constants.DATA_FORMAT_ID, 
                                                constants.MANAGED_SYSTEM_PROPERTY_CATEGORY,
                                                property_type.StringType(),
                                                constants.DATA_FORMAT_DISPLAYNAME,
                                                constants.DATA_FORMAT_DESCRIPTION)
        self._systemProperties.append(dataFormatProperty)
        
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
        Registers property definitions. A registered definition can be updated by simply registering again.
        
        @param propertyDefinition: The property definitions to register.
        @type propertyDefinition: C{list} of L{PropertyDefinition}
        """
        
        self._lock.acquire()
        try:
            notRegisteredPropertyDefs = list()
            for propertyDef in propertyDefinitions:
                try:
                    registeredPropertyDef = self._registeredProperties[(propertyDef.namespace, propertyDef.identifier)]    
                except KeyError:
                    self._registeredProperties[(propertyDef.namespace, propertyDef.identifier)] = propertyDef
                else:
                    if registeredPropertyDef.category == constants.MANAGED_SYSTEM_PROPERTY_CATEGORY \
                       or registeredPropertyDef.category == constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY:
                        notRegisteredPropertyDefs.append(propertyDef)
                    else:
                        self._registeredProperties[(propertyDef.namespace, propertyDef.identifier)] = propertyDef
            if len(notRegisteredPropertyDefs) > 0:
                propertyNames = [propertyDef.identifier + " " for propertyDef in notRegisteredPropertyDefs]
                errorMessage = "The following properties were not registered because system specific " \
                               + "property definition already exist.\n '%s'" % propertyNames  
                raise ConfigurationError(errorMessage)
        finally:
            self._lock.release()
            
    def unregister(self, propertyDefinitions):
        """
        Removes the given property type definitions from the registration.
        
        @param propertyDefinitions: The property definition to unregister.
        @type propertyDefinitions: C{list} of L{PropertyDefinition}
        """
    
        self._lock.acquire()
        try:
            for propertyDefinition in propertyDefinitions:
                if (propertyDefinition.namespace, propertyDefinition.identifier) in self._registeredProperties:
                    del self._registeredProperties[(propertyDefinition.namespace, propertyDefinition.identifier)]
        finally:
            self._lock.release()
    
    def clear(self):
        """ Clears the list of registered property definitions. """
        
        self._lock.acquire()
        try:
            self._registeredProperties.clear()
        finally:
            self._lock.release()
    
    def existsSystemPropertyDefinition(self, identifier):
        """ 
        Checks whether a system-specific property exists for the given property identifier.
        
        @param identifier: Identifier of the property definition.
        @type identifier: C{unicode}
        
        @return: Flag indicating existence of a system-specfic property.
        @rtype: C{bool}
        """
    
        self._lock.acquire()
        try:
            return (None, identifier) in self._registeredProperties
        finally:
            self._lock.release()
            
    def isPropertyDefinitionRegistered(self, propertyDefinition):
        """ 
        Checks whether the given property is already registered. 
        
        @return: Flag indicating the existence of the property with the given identifier and name space.
        @rtype: C{bool}
        """
            
        self._lock.acquire()
        try:
            if (propertyDefinition.namespace, propertyDefinition.identifier) in self._registeredProperties:
                return True
            return False
        finally:
            self._lock.release()
        
    def getPropertyDefinition(self, propertyIdentifier, namespace=None):
        """
        Returns a property type definition for the given identifier.
        
        @param propertyIdentifier: Property identifier.
        @type propertyIdentifier: C{unicode}
        @param namespace: Name space of the property, i.e. the data type name it is registered for.
        @type namespace: C{unicode}
        
        @return: Matching property definition.
        @rtype: L{PropertyDefinition}
        """
        
        self._lock.acquire()
        try:
            registeredPropertyDefinition = None
            if (namespace, propertyIdentifier) in self._registeredProperties:
                registeredPropertyDefinition = copy(self._registeredProperties[(namespace, propertyIdentifier)])
            if (None, propertyIdentifier) in self._registeredProperties:
                registeredPropertyDefinition = copy(self._registeredProperties[(None, propertyIdentifier)])
            if registeredPropertyDefinition is None:
                registeredPropertyDefinition = self._propertyDefinitionFactory.createPropertyDefinition(propertyIdentifier, 
                                                                                                        constants.USER_PROPERTY_CATEGORY)
            return registeredPropertyDefinition
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
        
        @return: Mapping of property definition identifiers (namespace, property id) to property type definitions.
        @rtype: C{dict}; keys: C{unicode}, C{unicode}; values: C{PropertyDefinition}
        """
        
        self._lock.acquire()
        try:
            return copy(self._registeredProperties)
        finally:
            self._lock.release()
    
    @property
    def systemPropertyDefinitions(self):
        """
        Returns a list of system-specific property type definitions.
        
        @return: Mapping of property definition identifiers (namespace, property id) to property type definitions.
        @rtype: C{list} of C{PropertyDefinition}
        """
        
        self._lock.acquire()
        try:
            result = list()
            for propertyDefinition in self._registeredProperties.values():
                if propertyDefinition.category == constants.UNMANAGED_SYSTEM_PROPERTY_CATEGORY \
                   or propertyDefinition.category == constants.MANAGED_SYSTEM_PROPERTY_CATEGORY:
                    result.append(propertyDefinition)
            return result
        finally:
            self._lock.release()

    @property
    def propertyNameValidationFunction(self):
        """ Getter for the property identifier validation function. """
        
        def wrapperFunction(inputString):
            return self._propertyDefinitionFactory.isValidPropertyIdentifier(inputString) \
                   and not self.existsSystemPropertyDefinition(inputString)
        return wrapperFunction
