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
Implements the data type representation.
"""


from datafinder.core.configuration.datamodel.constants import DEFAULT_DATATYPE_ICONNAME
from datafinder.core.configuration.properties.constants import DATAMODEL_PROPERTY_CATEGORY
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.gen import datamodel


__version__ = "$Revision-Id:$" 


class DataType(object):
    """ Represents a data type. """
    
    def __init__(self, name, iconName=DEFAULT_DATATYPE_ICONNAME, propertyDefinitions=None):
        """ 
        Constructor. 
        
        @param name: Name of data type.
        @type name: C{unicode}
        @param iconName: Symbolic name of an associated icon.
        @type iconName: C{unicode}
        @param propertyDefinitions: List of property definitions.
        @type propertyDefinitions: C{list} of L{PropertyDefinition<datafinder.core.
        configuration.properties.property_definition.PropertyDefinition>} 
        """
        
        self.name = name
        self.iconName = iconName
        self._propertyDefinitions = dict()
        if not propertyDefinitions is None:
            self.propertyDefinitions = propertyDefinitions
            
    def _getPropertyDefinitions(self):
        """ Getter for the property definitions. """
        
        return self._propertyDefinitions.values()

    def _setPropertyDefinitions(self, propertyDefinitions):
        """ 
        Sets the property definitions.
        
        @param propertyDefinitions: List of new property definitions.
        @type propertyDefinitions: C{list} of L{PropertyDefinition<datafinder.core.
        configuration.properties.property_definition.PropertyDefinition>}
        """
        
        self._propertyDefinitions.clear()
        for propertyDefiniton in propertyDefinitions:
            self.addPropertyDefinition(propertyDefiniton)

    propertyDefinitions = property(_getPropertyDefinitions, _setPropertyDefinitions)
    
    def addPropertyDefinition(self, propertyDefinition):
        """ 
        Adds / updates a property definition to the data type. 
        
        @param propertyDefinition: A property definition.
        @type propertyDefinition: L{PropertyDefinition<datafinder.core.
        configuration.properties.property_definition.PropertyDefinition>}
        """
        
        self._propertyDefinitions[propertyDefinition.identifier] = propertyDefinition
        
    def removePropertyType(self, propertyIdentifier):
        """ 
        Removes a property definition from the data type. 
        
        @param propertyIdentifier: Identifier of the property.
        @type propertyIdentifier: L{PropertyDefinition<datafinder.core.
        configuration.properties.property_definition.PropertyDefinition>}
        """
        
        if propertyIdentifier in self._propertyDefinitions:
            del self._propertyDefinitions[propertyIdentifier]
        
    def __cmp__(self, other):
        """ Makes the data types comparable. """
        
        try:
            return cmp(self.name, other.name)
        except AttributeError:
            return 1
        
    @staticmethod
    def load(persistedDataType):
        """ 
        Initializes a data type from the persisted data type representation. 
        
        @return: Initialized data type. 
        @rtype: C{DataType}
        """

        propertyDefinitions = list()
        for peristedPropertyDefinition in persistedDataType.properties:
            propertyDef = PropertyDefinition.load(peristedPropertyDefinition)
            propertyDef.category = DATAMODEL_PROPERTY_CATEGORY
            propertyDef.namespace = persistedDataType.name
            propertyDefinitions.append(propertyDef)
        return DataType(persistedDataType.name, persistedDataType.iconName, propertyDefinitions)

    def toPersistenceRepresentation(self):
        """ 
        Converts the data type instance to its XML-data-binding representation. 
        
        @return: Data type in XML-binding representation.
        @rtype: C{datamodel.datatype}
        """
        
        properties = list()
        for propertyDefinition in self._propertyDefinitions.values():
            properties.append(propertyDefinition.toPersistenceRepresentation())
        return datamodel.datatype(self.name, self.iconName, properties)
