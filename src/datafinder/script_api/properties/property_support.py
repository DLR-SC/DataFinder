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
This module contains the script API functionalities for property access.
@note: System-specific properties are set via dedicated methods, e.g. during file import. 
The support package is developed for the user who should not directly set system properties.
"""


from datafinder.core.configuration.properties import constants as const
from datafinder.core.error import PropertyError, ItemError, ConfigurationError
from datafinder.core.repository_manager import repositoryManagerInstance
from datafinder.script_api.error import PropertySupportError, ItemSupportError
from datafinder.script_api.properties.property_description import PropertyDescription


__version__ = "$Revision-Id:$" 


def validate(properties, path=None):
    """ 
    Validates the given properties.
        
    @param properties: Mapping of property identifiers to values.
    @type properties: C{dict}
    @param path: Optional item path which ensures that the validation is performed 
        in the correct context.
    @type path: C{unicode}
        
    @raise PropertySupportError: Raised when a value does not conform to 
        the defined property restrictions. 
    """

    reqPropDefs = dict()
    if not path is None:
        try:    
            item = repositoryManagerInstance.workingRepository.getItem(path)
        except ItemError:
            raise ItemSupportError("Item '%s' cannot be found." % path)
        else:
            reqPropDefs = item.requiredPropertyDefinitions 

    registry = _getPropertyDefinitionRegistry()
    for propId, value in properties.iteritems():
        if propId in reqPropDefs:
            propDef = reqPropDefs[propId]
        else:
            propDef = registry.getPropertyDefinition(propId)
        try:
            propDef.validate(value)
        except PropertyError:
            raise PropertySupportError(
                "Value '%s' for property '%s' is not valid." \
                % (str(value), propDef.displayName))


def _getPropertyDefinitionRegistry():
    return repositoryManagerInstance.workingRepository.\
        configuration.propertyDefinitionRegistry


def _getPropertyDefinitionFactory():
    return repositoryManagerInstance.workingRepository.\
        configuration.propertyDefinitionFactory


def propertyDescription(propertyIdentifier):
    """ 
    Returns the property description for the given property identifier.
        
    @param propertyIdentifier: property identifier.
    @type propertyIdentifier: C{unicode}
        
    @return: property description instance.
    @rtype: L{PropertyDescription<datafinder.script_api.configuration.properties.
        property_description.PropertyDescription>}
    """
    
    registry = _getPropertyDefinitionRegistry() 
    propDef = registry.getPropertyDefinition(propertyIdentifier)
    propDesc = PropertyDescription(propDef)
    return propDesc


def availableProperties():
    """ 
    Returns all defined properties, i.e. system specific or data model specific 
    properties.
        
    @return: List of property descriptions.
    @rtype: C{dict} of L{PropertyDescription<PropertyDescription>}
    """
        
    registry = _getPropertyDefinitionRegistry()
    regPropDef = registry.registeredPropertyDefinitions
    propertyDescriptions = dict()
    for propId, propDef in regPropDef.iteritems():
        propertyDescriptions[propId[1]] = PropertyDescription(propDef)
    return propertyDescriptions


def retrieveProperties(path):
    """
    Retrieves the properties and maps them to the correct representation.
    
    @param path: path of the item whose properties should be retrieved.
    @type path: C{unicode}
    
    @return properties: Mapping of property identifiers to values.
    @rtype properties: C{dict} of C{unicode}, C{object}
        
    @raise ItemSupportError: Raised when problems during the property retrieval occur.
    """
    
    try:    
        item = repositoryManagerInstance.workingRepository.getItem(path)
    except ItemError:
        raise ItemSupportError("Item '%s' cannot be found." % path)
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
        
    @raise ItemSupportError: Raised when difficulties with the item access occur.
    @raise PropertySupportError: Raised when values do not conform to the specified restrictions,
        values of system-specific properties are changed.
    """
    
    cwr = repositoryManagerInstance.workingRepository
    try:
        item = cwr.getItem(path)
    except ItemError:
        raise ItemSupportError("Cannot find item '%s'." % path)
    else:
        mappedProperties = list()
        for propId, value in properties.iteritems():
            if propId in item.properties:
                prop = item.properties[propId]
                prop.value = value
            else:
                prop = cwr.createProperty(propId, value)
            if (prop.propertyDefinition.category != const.MANAGED_SYSTEM_PROPERTY_CATEGORY
               and prop.propertyDefinition.category != const.UNMANAGED_SYSTEM_PROPERTY_CATEGORY):
                mappedProperties.append(prop)
            else:
                errorMessage = "You cannot change system-specific property values."
                raise PropertySupportError(errorMessage)
        try:
            item.updateProperties(mappedProperties)
        except ItemError, error:
            raise ItemSupportError("Cannot update properties.\nReason: '%s'" % str(error.args))


def deleteProperties(path, propertyIdentifiers):
    """ 
    Deletes the given properties from the item properties.
    
    @param path: The item where the properties should be deleted.
    @type path: C{unicode}  
    @param propertyIdentifiers: List of property identifiers.
    @type propertyIdentifiers: C{list} of C{unicode}
    
    @raise ItemSupportError: Raised when difficulties with the item access occur.
    @raise PropertySupportError: Raised when system specific or data model specific properties
        should be removed.
    """
    
    cwr = repositoryManagerInstance.workingRepository
    try:
        item = cwr.getItem(path)
    except ItemError:
        raise ItemSupportError("Cannot find item '%s'." % path)
    else:
        registry = _getPropertyDefinitionRegistry()
        propertiesForDeletion = list()
        for propId in propertyIdentifiers:
            if propId in item.requiredPropertyDefinitions:
                propDef = item.requiredPropertyDefinitions[propId]
            else:
                propDef = registry.getPropertyDefinition(propId)
            if propDef.category == const.USER_PROPERTY_CATEGORY:
                propertiesForDeletion.append(propId)
            else:
                raise PropertySupportError("Unable to delete property '%s' because it is not user-defined. " \
                                           % propDef.displayName + \
                                           "Only user-defined properties can be deleted." )
        try:
            item.deleteProperties(propertiesForDeletion)
        except ItemError, error:
            raise ItemSupportError("Cannot delete item properties.\nReason: '%s'" % str(error.args))


def registerPropertyDefinition(identifier, type_, displayName=None, description=None):
    """
    Creates a user-specific property and registers it.
    
    @param identifier: Unique name.
    @type identifier: C{unicode}
    @param type_: Type of the property.
    @type type_: C{BasePropertyType} @see {properties<datafinder.script_api.properties.__init__>}
    @param displayName: A user-readable name.
    @type displayName: C{unicode}
    @param description: A short help test.
    @type description: C{unicode}
    
    @raises PropertySupportError: Invalid identifier 
        / Overwrites read-only property.
    """
    
    registry = _getPropertyDefinitionRegistry()
    factory = _getPropertyDefinitionFactory()
    try:
        propDef = factory.createPropertyDefinition(
            identifier, const.USER_PROPERTY_CATEGORY, type_, displayName, description) 
        registry.register([propDef])
    except ConfigurationError, error:
        raise PropertySupportError(str(error.args))
