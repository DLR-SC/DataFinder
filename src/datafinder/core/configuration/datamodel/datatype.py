#
# Created: 06.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: datatype.py 4376 2009-12-07 16:12:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the data type representation.
"""


from datafinder.core.configuration.datamodel.constants import DEFAULT_DATATYPE_ICONNAME
from datafinder.core.configuration.properties.constants import DATAMODEL_PROPERTY_CATEGORY
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.gen import datamodel


__version__ = "$LastChangedRevision: 4376 $"


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
