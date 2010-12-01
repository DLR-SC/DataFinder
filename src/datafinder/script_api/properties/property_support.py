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
This module contains the script API functionalities for property data access.
@note: System specific properties are set via dedicated methods, e.g. during file import. 
       The support package is developed for the user who should not directly set system properties.
"""


from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.property_definition import PropertyDefinitionFactory
from datafinder.core.configuration.properties.registry import PropertyDefinitionRegistry
from datafinder.core.error import PropertyError, ItemError
from datafinder.core.repository_manager import repositoryManagerInstance
from datafinder.script_api.error import PropertiesSupportError, ItemSupportError
from datafinder.script_api.properties.property_description import PropertyDescription


__version__ = "$Revision-Id:$" 


def validate(properties):
    """ 
    Validates the given properties.
        
    @param properties: Mapping of property identifiers to values.
    @type properties: C{dict}
        
    @raise PropertiesSupportError: Raised when a value does not conform to 
                                 the defined property restrictions. 
    """
    
    propertyRegistry = PropertyDefinitionRegistry(PropertyDefinitionFactory(), repositoryManagerInstance.workingRepository)
    
    for propertyIdentifier, value in properties.iteritems():
        propertyDefinition = propertyRegistry.getPropertyDefinition(propertyIdentifier)
        try:
            propertyDefinition.validate(value)
        except PropertyError:
            raise PropertiesSupportError("Value for property '%s' is not valid." % 
                                         propertyDefinition.displayName)


def propertyDescription(propertyIdentifier):
    """ 
    Returns the property description for the given property identifier.
        
    @param propertyIdentifier: property identifier.
    @type propertyIdentifier: C{unicode}
        
    @return: property description instance.
    @rtype: L{PropertyDescription<datafinder.script_api.configuration.properties.
                property_description.PropertyDescription>}
    """
    
    propertyRegistry = PropertyDefinitionRegistry(PropertyDefinitionFactory(), repositoryManagerInstance.workingRepository)    
     
    propertyDefinition = propertyRegistry.getPropertyDefinition(propertyIdentifier)
    propertyDescription_ = PropertyDescription(propertyDefinition)
    return propertyDescription_


def availableProperties():
    """ 
    Returns all defined properties, i.e. system specific or data model specific 
    properties.
        
    @return: List of property descriptions.
    @rtype: C{dict} of L{PropertyDescription<PropertyDescription>}
    """
        
    propertyRegistry = PropertyDefinitionRegistry(PropertyDefinitionFactory(), 
                                                  repositoryManagerInstance.workingRepository.configuration.isManagedRepository)    
    registeredPropertyDefinitions = propertyRegistry.registeredPropertyDefinitions
    propertyDescriptions = dict()
    for propertyIdentifier, propertyDefinition in registeredPropertyDefinitions.iteritems():
        propertyDescriptions[propertyIdentifier[1]] = PropertyDescription(propertyDefinition)
    return propertyDescriptions


def retrieveProperties(path):
    """
    Retrieves the properties and maps them to the correct representation.
    
    @param path: path of the item whose properties should be retrieved.
    @type path: C{unicode}
    
    @return properties: Mapping of property identifiers to values.
    @rtype properties: C{dict} of C{unicode}, C{object}
        
    @raise ItemSupportError: Raised when problems during the property retrieval occurs.
    """
    
    try:    
        item = repositoryManagerInstance.workingRepository.getItem(path)
    except ItemError:
        raise ItemSupportError("Item cannot be found.")
    else:
        properties = item.properties
        result = dict()
        for key, value in properties.iteritems():
            result[key] = value.value
        return result
        

def storeProperties(path, properties):
    """ 
    Adds/Updates the given properties of the item.
    
    @param path: The item whose properties should be updated.
    @type path: C{unicode}  
    @param properties: Mapping of property identifiers to values.
    @type properties: C{dict} of C{unicode}, C{object}
        
    @raise ItemSupportError: Raised when values do not conform to the specified restrictions,
                             values of system specific properties are tried to change or
                             other difficulties occur during property storage. 
    """
    
    cwr = repositoryManagerInstance.workingRepository
    try:
        item = cwr.getItem(path)
    except ItemError:
        raise ItemSupportError("Item cannot be found.")
    else:
        mappedProperties = list()
        for propertyIdentifier, value in properties.iteritems():
            try:
                if propertyIdentifier in item.properties:
                    property_ = cwr.createPropertyFromDefinition(item.properties[propertyIdentifier].propertyDefinition, value)
                else:
                    property_ = cwr.createProperty(propertyIdentifier, value)
                if not property_.propertyDefinition.category == constants.MANAGED_SYSTEM_PROPERTY_CATEGORY:
                    mappedProperties.append(property_)
            except PropertyError, error:
                errorMessage = u"The property '%s' is an invalid value assigned." % error.propertyIdentifier \
                               + "The validation failed for the following reason:\n '%s'." % error.message
                raise ItemSupportError(errorMessage)
        try:
            item.updateProperties(mappedProperties)
        except ItemError, error:
            raise ItemSupportError("Cannot update properties.\nReason: '%s'" % error.message)


def deleteProperties(path, propertyIdentifiers):
    """ 
    Deletes the given properties from the item properties.
    
    @param path: The item where the properties should be deleted.
    @type path: C{unicode}  
    @param propertyIdentifiers: List of property identifiers.
    @type propertyIdentifiers: C{list} of C{unicode}
    
    @raise ItemSupportError: Raised when system specific or data model specific properties
                             should be removed or other difficulties during the deletion
                             process occur.
    """
    
    cwr = repositoryManagerInstance.workingRepository
    try:
        item = cwr.getItem(path)
    except ItemError:
        raise ItemSupportError("Problem during retrieval of the item.")
    else:
        propertyRegistry = PropertyDefinitionRegistry(PropertyDefinitionFactory(), cwr)    
        propertiesForDeletion = list()
        for propertyIdentifier in propertyIdentifiers:
            propertyDefinition = propertyRegistry.getPropertyDefinition(propertyIdentifier)
            if propertyDefinition.category == constants.USER_PROPERTY_CATEGORY:
                propertiesForDeletion.append(propertyIdentifier)
            else:
                raise ItemSupportError("Unable to delete property '%s' because it is not user-defined. " \
                                       % propertyDefinition.displayName + \
                                       "Only user-defined properties can be deleted." )
        try:
            item.deleteProperties(propertiesForDeletion)
        except ItemError, error:
            raise ItemSupportError("Cannot delete item properties.\nReason: '%s'" % error.message)
