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
Implements the relation representation.
"""


from datafinder.core.configuration.datamodel.constants import DEFAULT_RELATION_ICONNAME
from datafinder.core.configuration.gen import datamodel


__version__ = "$Revision-Id:$" 


class Relation(object):
    """ 
    Represents a data model relation. 
    A relation represents directed connections between the defined data types.
    The connections are established from the source data types to the target data types
    of the relation. In a relation the data types are referenced by the data type name.
    """
    
    def __init__(self, name, iconName=DEFAULT_RELATION_ICONNAME, sourceDataTypeNames=None, targetDataTypeNames=None):
        """ 
        Constructor. 
        
        @param name: Name of the relation.
        @type name: C{unicode}
        @param iconName: Symbolic name of an associated icon.
        @type iconName: C{unicode}
        @param sourceDataTypeNames: List of source data type names.
        @type sourceDataTypeNames: C{list} of C{unicode}
        @param targetDataTypeNames: List of target data type names.
        @type targetDataTypeNames: C{list} of C{unicode}
        """
        
        self.name = name
        self.iconName = iconName
        self._sourceDataTypeNames = set()
        self._targetDataTypeNames = set()
        
        if not sourceDataTypeNames is None:
            self.sourceDataTypeNames = sourceDataTypeNames
        if not targetDataTypeNames is None:
            self.targetDataTypeNames = targetDataTypeNames

    def _getSourceDataTypeNames(self):
        """ Getter for the source data type names. """
        
        return list(self._sourceDataTypeNames.copy())

    def _setSourceDataTypeNames(self, dataTypeNames):
        """ 
        Sets the source data type names.
        
        @param dataTypeNames: List of of data type names.
        @type dataTypeNames: C{unicode}
        """
        
        self._sourceDataTypeNames.clear()
        for dataTypeName in dataTypeNames:
            self.addSourceDataTypeName(dataTypeName)
    sourceDataTypeNames = property(_getSourceDataTypeNames, _setSourceDataTypeNames)
    
    def addSourceDataTypeName(self, dataTypeName):
        """ 
        Adds the given data type name to the source types of the relation. 
        @note: The source data types are organized as set.
        
        @param dataTypeName: Name of the data type.
        @type dataTypeName: C{unicode}
        """
        
        self._sourceDataTypeNames.add(dataTypeName)
    
    def removeSourceDataTypeName(self, dataTypeName):
        """ 
        Removes the given data type name from the source types of the relation. 
        
        @param dataTypeName: Name of the data type.
        @type dataTypeName: C{unicode}
        """
        
        if dataTypeName in self._sourceDataTypeNames:
            self._sourceDataTypeNames.remove(dataTypeName)

    def _getTargetDataTypeNames(self):
        """ Getter for the target data type names. """
        
        return list(self._targetDataTypeNames.copy())
    
    def _setTargetDataTypeNames(self, dataTypeNames):
        """ 
        Sets the target data type names.
        
        @param dataTypeNames: List of of data type names.
        @type dataTypeNames: C{unicode}
        """
        
        self._targetDataTypeNames.clear()
        for dataTypeName in dataTypeNames:
            self.addTargetDataTypeName(dataTypeName)
    targetDataTypeNames = property(_getTargetDataTypeNames, _setTargetDataTypeNames)
    
    def addTargetDataTypeName(self, dataTypeName):
        """ 
        Adds the given data type name to target types of the relation.
        @note: The target data types are organized as set.
        
        @param dataTypeName: Name of the data type.
        @type dataTypeName: C{unicode}
        """
        
        self._targetDataTypeNames.add(dataTypeName)
    
    def removeTargetDataTypeName(self, dataTypeName):
        """ 
        Removes the given data type name from the target types of the relation. 
        
        @param dataTypeName: Name of the data type.
        @type dataTypeName: C{unicode}
        """
        
        if dataTypeName in self._targetDataTypeNames:
            self._targetDataTypeNames.remove(dataTypeName)

    def __cmp__(self, other):
        """ Makes the relations comparable. """
        
        try:
            return cmp(self.name, other.name)
        except AttributeError:
            return 1
        
    @staticmethod
    def load(persistedRelation):
        """ 
        Loads a relation form persistence format. 
        
        @return: Initialized relation.
        @rtype: C{Relation}
        """
        
        return Relation(persistedRelation.name, persistedRelation.iconName,
                        persistedRelation.sourceDataTypeNames, persistedRelation.targetDataTypeNames)
        
    def toPersistenceRepresentation(self):
        """ 
        Converts the relation type instance to its XML-data-binding representation. 
        
        @return: Relation in XML-binding format.
        @rtype: C{datamodel.relation}
        """
        
        return datamodel.relation(self.name, self.iconName, self.sourceDataTypeNames, self.targetDataTypeNames)
