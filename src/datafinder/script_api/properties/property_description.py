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
Contains wrapper class around the property representation used in the core package.
"""
 

__version__ = "$Revision-Id:$" 


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
    @type category: C{unicode}, for possible values see: 
                    L{constants<datafinder.script_api.properties.constants>}
    @ivar displayName: A readable name that can be presented in a user interface.
    @type displayName: C{unicode}
    @ivar description: Describes the purpose of the property.
    @type description: C{unicode}
    @ivar notNull: Flag indicating if C{None} is a allowed property value or not.
    @type notNull: C{bool}
    @ivar defaultValue: A default value for the property that is used for creation of the property on a resource.
    @type defaultValue: The type of the default value depends on the property definition.
    @ivar restrictions: This parameter holds the defined property restrictions that are
                        represented by  parameters. The returned mapping can contain the following keys:
                        minimumValue: Defining the lower boundary of a value range.
                        maximumValue: Defining the upper boundary of a value range.
                        minimumLength: Defining the lower boundary of a length range.
                        maximumLength: Defining the upper boundary of a length range.
                        minimumNumberOfDecimalPlaces: Defining the minimum number of decimal places.
                        maximumNumberOfDecimalPlaces: Defining the maximum number of decimal places. 
                        pattern: Regular expression pattern that restricts a string value.
                        options: A list of options the value can be chosen from.
                        optionsMandatory: Boolean indicating whether the value MUST be from the list of options.
                        subTypes: List of strings identifying supported types.
                        The possible restrictions depend on the type.
    @type restrictions: C{dict}
    @ivar namespace: Name space in which the property is valid, e.g. used to distinguish
                     different C{name} properties of different data types.
    @type namespace: C{unicode}
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

    def __repr__(self):
        """ Returns a readable representation. """
        
        return self.identifier + " Type: " + self.type \
               + " Category: " + self.category
