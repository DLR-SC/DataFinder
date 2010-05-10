#
# Created: 09.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: property.py 4117 2009-05-27 11:12:39Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Represents a property, i.e. property definition and value.
"""


from datafinder.core.error import PropertyError


__version__ = "$LastChangedRevision: 4117 $"


class Property(object):
    """
    Represents a property, i.e. property definition and value.
    """

    def __init__(self, propertyDefinition, value):
        """
        Constructor.

        @param propertyDefinition: Describes the property by name, identifier, restrictions, etc.
        @type propertyDefinition: L{PropertyDefinition<datafinder.core.configuration.properties.property_definition.PropertyDefinition>}
        @param value: Value of the property.
        @type value: C{object}
        """
        
        self._propertyDefinition = propertyDefinition
        self._additionalValueRepresentations = list()
        self._value = None
        self.value = value
        
    def __getPropertyIdentifier(self):
        """ Getter of the property identifier. """
        
        return self._propertyDefinition.identifier
    
    identifier = property(__getPropertyIdentifier)
        
    def __getPropertyDefinition(self):
        """ Getter for the property definition. """
        
        return self._propertyDefinition
    
    propertyDefinition = property(__getPropertyDefinition)
        
    def __getValue(self):
        """ Getter of the value attribute. """
        
        return self._value
        
    def __setValue(self, value):
        """ Setter of the value attribute. """        

        self.propertyDefinition.validate(value)
        self._additionalValueRepresentations = list()
        self._value = value
    
    value = property(__getValue, __setValue)

    def __getAdditionalValueRepresentations(self):
        """ Returns the additional supported value representations. """
        
        return self._additionalValueRepresentations[:]

    additionalValueRepresentations = property(__getAdditionalValueRepresentations)

    def __repr__(self):
        """ Returns the representation. """
        
        return repr(self.propertyDefinition) + ": " + repr(self.value)
    
    def __cmp__(self, other):
        """ Implements comparison of two instances. """
        
        try:
            return cmp(self.propertyDefinition.identifier, other.propertyDefinition.identifier)
        except AttributeError:
            return 1
        
    @staticmethod
    def create(propertyDefinition, persistedValue):
        """ 
        Creates a property from persistence format.
        
        @param propertyDefinition: Describes the property by name, identifier, restrictions, etc.
        @type propertyDefinition: L{PropertyDefinition<datafinder.core.configuration.properties.property_definition.PropertyDefinition>}
        @param persistedValue: Value of the property in persistence format.
        @type persistedValue: L{MetadataValue<datafinder.persistence.metadata.value_mapping.MetadataValue>}
        """
    
        additionalValueRepresentations = list()
        foundValidRepresentation = False
        valueRepresentations = persistedValue.guessRepresentation()
        for valueRepresentation in valueRepresentations:
            try:
                propertyDefinition.validate(valueRepresentation)
                if not foundValidRepresentation:
                    value = valueRepresentation
                    foundValidRepresentation = True
                else:
                    additionalValueRepresentations.append(valueRepresentation)
            except PropertyError:
                continue
        if not foundValidRepresentation:
            value = propertyDefinition.defaultValue
        result = Property(propertyDefinition, value)
        result._additionalValueRepresentations = additionalValueRepresentations
        return result
