#
# Created: 06.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: property_description.py 4556 2010-03-21 14:48:01Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Contains wrapper class around the property representation used in the core package.
"""
 

from datafinder.core.configuration.properties.validators import base_validators
from datafinder.script_api.properties import constants


__version__ = "$LastChangedRevision: 4556 $"


# definition of supported restriction parameters
_restrictionParameterValidatorMapping = {constants.MINIMUM_VALUE: (base_validators.IsInRange, "minValue"),
                                         constants.MAXIMUM_VALUE: (base_validators.IsInRange, "maxValue"),
                                         constants.MINIMUM_LENGTH: (base_validators.IsLengthInRange, "minLength"),
                                         constants.MAXIMUM_LENGTH: (base_validators.IsLengthInRange, "maxLength"),
                                         constants.MINIMUM_NUMBER_OF_DECIMAL_PLACES: (base_validators.IsNumberOfDecimalPlacesInRange, 
                                                                                      "minNumberOfDecimalPlaces"),
                                         constants.MAXIMUM_NUMBER_OF_DECIMAL_PLACES: (base_validators.IsNumberOfDecimalPlacesInRange, 
                                                                                      "maxNumberOfDecimalPlaces"),
                                         constants.OPTIONS: (base_validators.AreOptionsMatched, "options"),
                                         constants.OPTIONS_MANDATORY: (base_validators.AreOptionsMatched, "optionsMandatory"),
                                         constants.PATTERN: (base_validators.IsPatternMatched, "pattern")}
 

class PropertyDescription(object):
    """ 
    Wrapper around the internal property representation giving restricted access to
    the relevant parameters.
    All instance variables are read-only.
    
    @ivar identifier: This is the logical identifier of the property. 
    @type identifier: C{unicode}
    @ivar category: This holds the category of the property, i.e. if the property is 
                    system, data model or user specific.
                    System specific: property can NOT be deleted from resource, values are read-only
                    Data model specific: property can NOT be deleted from resource, values changeable
                    User specific: property can be deleted from resource, values changeable
    @type category: C{unicode}, possible values are: 
                    L{systemPropertyCategory<systemPropertyCategory>},
                    L{datamodelPropertyCategory<systemPropertyCategory>}, 
                    L{userPropertyCategory<systemPropertyCategory>}
    @ivar displayName: A readable name that can be presented in a user interface.
    @type displayName: C{unicode}
    @ivar description: Describes the purpose of the property.
    @type description: C{unicode}
    @ivar notNull: Flag indicating if C{None} is a allowed property value or not.
    @type notNull: C{bool}
    @ivar defaultValue: A default value for the property that is used for creation of the property on a resource.
    @type defaultValue: The type of the default value depends on the property definition.
    @ivar representationTypes: Read-only property restricting the type of the property values.
    @type representationTypes: C{list} of class objects
    @ivar restrictions: This parameter holds the defined property restrictions that are
                        represented by  parameters. The returned mapping can contain the following keys:
                        minimumValue: Defining the lower boundary of a value range.
                        maximumValue: Defining the upper boundary of a value range.
                        minimumLength: Defining the lower boundary of a length range.
                        maximumLength: Defining the upper boundary of a length range.
                        minimumNumberOfDecimalPlaces: Defining the minimum number of decimal places.
                        maximumNumberOfDecimalPlaces: Defining the maximum number of decimal places. 
                        options: A list of options the value can be chosen from.
                        pattern: Regular expression pattern that restricts a string value.
                        The possible restrictions depend on the supported representation types.
    @type restrictions: C{dict}
    """
    
    
    def __init__(self, propertyDefinition):
        """ 
        Constructor. 
        
        @param propertyRepresentation: The property definition.
        @type propertyRepresentation: L{PropertyTemplate<datafinder.application.metadata.property_types.PropertyBase>}
        """
        
        self.__propertyDefinition = propertyDefinition
    
    
    def __getIdentifier(self):
        """ 
        Returns the identifier of the property.
        """
        
        return self.__propertyDefinition.identifier
    
    identifier = property(__getIdentifier)
    
    
    def __getType(self):
        """ Returns the propertyType. """
        
        return self.__propertyDefinition.type
    
    type = property(__getType)
    
    
    def __getDisplayName(self):
        """ 
        Returns the display name of the property. 
        """
        
        return self.__propertyDefinition.displayName
    
    displayName = property(__getDisplayName)
    
    
    def __getCategory(self):
        """ 
        Returns the property category. 
        """
        
        return self.__propertyDefinition.category
    
    category = property(__getCategory)
    
    
    def __getDescription(self):
        """ 
        Returns the property description. 
        """
        
        return self.__propertyDefinition.description
    
    description = property(__getDescription)
    
    
    def __getDefaultValue(self):
        """ 
        Returns the specific default value. 
        """
        
        return self.__propertyDefinition.defaultValue
    
    defaultValue = property(__getDefaultValue)
    
    
    def __getNotNull(self):
        """ 
        Returns whether the value can be C{None} or not. 
        """
        
        return self.__propertyDefinition.notNull
    
    notNull = property(__getNotNull)
    
    
    def __getNamespace(self):
        """ 
        Returns the namespace.
        """
        
        return self.__propertyDefinition.namespace
        
    namespace = property(__getNamespace)
    
    
    def __getRestrictions(self):
        """
        Returns the defined restrictions of the property.
        """
        
        return self.__propertyDefinition.restrictions
    
    restrictions = property(__getRestrictions)

    def __str__(self):
        """ Returns a readable representation. """
        
        return self.identifier + " Type: " + self.type \
               + " Category: " + self.category
