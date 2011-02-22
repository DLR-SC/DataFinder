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
This module provides the definition of a property representations. 
"""


from datafinder.core.configuration.gen.datamodel import property as property_
from datafinder.core.configuration.properties import constants, property_type
from datafinder.core.configuration.properties.validators import error
from datafinder.core.error import ConfigurationError, PropertyError


__version__ = "$Revision-Id:$" 


class PropertyDefinition(object):
    """ 
    This the base class for property definitions.
    
    @ivar identifier: This is the logical identifier of the property which has to be unique on
                      a specific resource. This identifier is mapped on a persistence identifier 
                      when the property value is stored. 
    @type identifier: C{unicode}
    @ivar type: Indicates the type of the property, i.e. the format of associated values.
    @type type: C{string}, for constant definition see L{constants<datafinder.core.item.metadata.constants>}.
    @ivar category: This holds the category of the property, i.e. if the property is 
                    system-, data model- or user-specific. In accordance to the category
                    depends whether a property can be changed or deleted by the user. 
    @type category: C{string}, for constant definitions see L{constants<datafinder.core.item.metadata.constants>}
    @ivar displayName: A readable name that can be presented in a user interface.
    @type displayName: C{unicode}
    @ivar description: Describes the purpose of the property.
    @type description: C{unicode}
    @ivar notNull: Flag indicating if C{None} is a allowed property value or not.
                   This restrictions is also checked on property value validation.
    @type notNull: C{bool}
    @ivar defaultValue: A default value for the property. The default value is not checked
                        against the the existing restrictions when set.
    @type defaultValue: The type of the default value depends on the property definition.
    """
    
    def __init__(self, identifier, category=constants.USER_PROPERTY_CATEGORY, propertyType=property_type.AnyType(), 
                 displayName=None, description=None, namespace=None):
        """ 
        Constructor. 
        
        @param identifier: This is the logical identifier of the property which has to be 
                           unique on a specific resource. 
        @type identifier: C{unicode}
        @param category: Determines the category of the property.
        @type category: C{unicode}
        @param propertyType: Type/ restrictions for property values.
        @type propertyType: C{object}
        @param displayName: Descriptive name of the property.
        @type displayName: C{unicode}
        @param description: Description of the property.
        @type description: C{unicode}
        """
        
        self._identifier = identifier
        self.namespace = namespace
        self.category = category
        self.displayName = displayName or identifier
        self.description = description
        self._propertyType = propertyType
        self.defaultValue = None
        self.notNull = False
        
    @property
    def identifier(self):
        """ Getter for the attribute C{self.__identifier}. """
        
        return self._identifier

    @property
    def type(self):
        """ Returns the type constant of the property. """
        
        return self._propertyType.NAME
    
    @property
    def propertyType(self):
        """ Returns the type of the property. """
        
        return self._propertyType

    @property
    def restrictions(self):
        """ Returns the defined restrictions of the property. """
        
        result = dict()
        for restriction, value in self._propertyType.restrictions.iteritems():
            if not value is None:
                result[restriction] = value
        return result

    def validate(self, value):
        """ 
        Checks whether the given value conforms to the given restrictions. 
        
        @param value: The value to check against the restrictions.
        @type value: C{object}
        
        @raise PropertyError: Indicating that the value does not conform
                              to the defined restrictions.
        """
        
        if not value is None:
            try:
                self._propertyType.validator(value)
            except error.ValidationError, error_:
                raise PropertyError(self.identifier, error_.errorMessage)
        else:
            if self.notNull:
                raise PropertyError(self.identifier, "Property value for %s must not be None." % self.displayName)
            
    def __cmp__(self, other):
        """ Comparison of two instances. """
        
        if self.identifier ==  other.identifier \
           and self.namespace == other.namespace:
            return 0
        return 1
        
    def __repr__(self):
        """ Returns a readable representation. """
        
        return self.displayName

    @staticmethod
    def load(peristedPropertyDefinition):
        """ Loads the property form persistence format. """
        
        propertyType = property_type.createPropertyType(peristedPropertyDefinition.valueType)
        propertyDef = PropertyDefinition(peristedPropertyDefinition.name, propertyType=propertyType)
        propertyDef.defaultValue = peristedPropertyDefinition.defaultValue
        propertyDef.notNull = peristedPropertyDefinition.mandatory
        return propertyDef
    
    def toPersistenceRepresentation(self):
        """ Returns a property in persistence format. """
        
        return property_(self.identifier, self._propertyType.NAME, 
                         self.notNull, self.defaultValue)


class PropertyDefinitionFactory(object):
    """ Factory for creation of property definitions. """
    
    PROPERTY_TYPE_NAMES = property_type.PROPERTY_TYPE_NAMES
    
    def __init__(self, propertyIdValidator=None):
        """ 
        Constructor.
        
        @param propertyIdValidator: Function taking the property  identifier as argument and checks whether it is valid.
        @type propertyIdValidator: Function object.
        """
        
        self.propertyIdValidator = propertyIdValidator
        
    def isValidPropertyIdentifier(self, identifier):
        """ 
        Checks whether the given identifier is valid. 
        
        @param identifier: Identifier of a property definition.
        @type identifier: C{unicode}
        """

        isValid = True
        if not self.propertyIdValidator is None:
            isValid = self.propertyIdValidator(identifier)[0]
        return isValid
   
    def createPropertyDefinition(self, identifier, category, propertyType=property_type.AnyType(), 
                                 displayName=None, description=None, namespace=None):
        """ 
        Returns a property definition. 
        
        @raise ConfigurationError: Indicating problems with identifier.
        """
        
        if not self.isValidPropertyIdentifier(identifier):
            raise ConfigurationError("Identifier '%s' does not match property identifier pattern.")
        else:
            return PropertyDefinition(identifier, category, propertyType, 
                                      displayName, description, namespace)

    @staticmethod
    def createPropertyType(propertyTypeName, restrictions=dict()):
        """ 
        Provided for convenience.
        @see: L{createPropertyType<datafinder.core.configuration.properties.property_type.createPropertyType>}
        """

        return property_type.createPropertyType(propertyTypeName, restrictions)
