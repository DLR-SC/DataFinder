#
# Handler for the generated datamodel stuff.
#
# Created: Heinrich Wendel (heinrich.wendel@dlr.de)
#
# Version: $Id: handler.py 4598 2010-04-12 11:28:59Z schlauch $
#
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
#
#
# http://www.dlr.de/datafinder
#


""" Handler for the data model. """


import codecs
from copy import deepcopy
from StringIO import StringIO
from xml.parsers.expat import ExpatError

from datafinder.core.configuration.gen import datamodel
from datafinder.core.configuration.datamodel.constants import ROOT_RELATION_NAME
from datafinder.core.configuration.datamodel.datatype import DataType
from datafinder.core.configuration.datamodel.relation import Relation
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import createFileStorer


__version__ = "$LastChangedRevision: 4598 $"    


_DEFAULT_ENCODING = "UTF-8"
datamodel.ExternalEncoding = _DEFAULT_ENCODING 


class DataModelHandler(object):
    """ Allows access to the defined data model. """
    
    _streamWriterClass = codecs.getwriter(_DEFAULT_ENCODING)
    
    _NEW_BASE_RELATION_NAME = "New Relation"
    _NEW_BASE_DATATYPE_NAME = "New Data Type"
    
    def __init__(self, fileStorer, propertyDefinitionRegistry):
        """ 
        Constructor.
        
        @param fileStorer: Handles retrieval of the data model file.
        @type fileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        @param propertyDefinitionRegistry: Registration for property definitons.
        @type propertyDefinitionRegistry: L{PropertyDefinitionRegistry<datafinder.core.configuration.properties.
        registry.PropertyDefinitionRegistry>} 
        """
        
        self._fileStorer = fileStorer
        self._propertyDefinitionRegistry = propertyDefinitionRegistry
        
        self._dataTypes = dict()
        self._relations = dict()
        self.relations = list()
        
    def create(self):
        """ 
        Creates a new data model. 
        
        @raise ConfigurationError: Indicating problems on creation.
        """
        
        try:
            self._fileStorer.createResource()
            self.store()
        except PersistenceError, error:
            raise ConfigurationError("Cannot create the data model. Reason: '%s'" % error.message)
        
    def load(self):
        """ 
        Loads the data model. 
        
        @raise ConfigurationError: Indicating problems on data model loading.
        """
        
        try:
            if self._fileStorer.exists():
                stream = self._fileStorer.readData()
            else:
                raise ConfigurationError("The data model does not exists.")
        except PersistenceError, error:
            raise ConfigurationError("Cannot load data model. Reason: '%s'" % error.message)
        else:
            try:
                persistedDatamodel = datamodel.parseString(unicode(stream.read(), _DEFAULT_ENCODING))
            except (ValueError, ExpatError, UnicodeDecodeError), error:
                raise ConfigurationError("Cannot load data model. Reason:'%s'" % error.message)
            else:
                self._loadPersistenceState(persistedDatamodel)
            finally:
                stream.close()
        
    def _loadPersistenceState(self, persistedDatamodel):
        """ Loads the internal state from the persistence format. """
        
        self._dataTypes.clear()
        self._relations.clear()
        for persistedDataType in persistedDatamodel.datatypes:
            dataType = DataType.load(persistedDataType)
            self.addDataType(dataType)
            self._propertyDefinitionRegistry.register(dataType.propertyDefinitions)
        for persistedRelation in persistedDatamodel.relations:
            relation = Relation.load(persistedRelation)
            self.addRelation(relation)
        if len(self._relations) == 0:
            self.addRelation(self.createRelation(ROOT_RELATION_NAME))
            
    def store(self):
        """ 
        Stores the current data model state. 
        
        @raise ConfigurationError: Indicating problems on data model storage.
        """
        
        persistedDatamodel = self._createPersistedDatamodel()
        stream = self._streamWriterClass(StringIO())
        persistedDatamodel.export(stream, 0)
        stream.seek(0)
        try:
            self._fileStorer.writeData(stream)
        except PersistenceError, error:
            raise ConfigurationError("Cannot store the data model.\nReason: '%s'" % error.message)
        
    def _createPersistedDatamodel(self):
        """ Transforms internal state to the persistence format. """
        
        persistedDataTypes = list()
        for dataType in self._dataTypes.values():
            persistedDataTypes.append(dataType.toPersistenceRepresentation())
        persistedRelations = list()
        for relation in self._relations.values():
            persistedRelations.append(relation.toPersistenceRepresentation())
        return datamodel.datamodel(persistedDataTypes, persistedRelations)
            
    def importDatamodel(self, localFilePath):
        """ 
        Imports a data model. 
        
        @param localFilePath: Path to file on the local file system.
        @type localFilePath: C{unicode}
        
        @raise ConfigurationError: Indicating problems on data model storing.
        """
        
        try:
            localFileStorer = createFileStorer("file:///" + localFilePath)
            binaryStream = localFileStorer.readData()
            try:
                persistedDatamodel = datamodel.parseString(binaryStream.read())
            finally:
                binaryStream.close()
        except PersistenceError, error:
            raise ConfigurationError("Cannot import data model. Reason: '%s'" % error.message)
        else:
            self._loadPersistenceState(persistedDatamodel)
            
    def exportDatamodel(self, localFilePath):
        """ 
        Exports the data model. 
        
        @param localFilePath: Path to file on the local file system.
        @type localFilePath: C{unicode}

        @raise ConfigurationError: Indicating problems on data model storage.
        """

        persistedDatamodel = self._createPersistedDatamodel()
        stream = self._streamWriterClass(StringIO())
        persistedDatamodel.export(stream, 0)
        stream.seek(0)
        try:
            localFileStorer = createFileStorer("file:///" + localFilePath)
            localFileStorer.writeData(stream)
        except PersistenceError, error:
            raise ConfigurationError("Cannot export data model. Reason: '%s'" % error.message)
 
    def createRelation(self, name=None, iconName="relationType", sourceDataTypeNames=None, targetDataTypeNames=None):
        """ 
        Creates a unique relation. 
        
        @param name: Proposed name of the relation.
        @type name: C{unicode}@param iconName: Symbolic name of an associated icon.
        @type iconName: C{unicode}
        @param sourceDataTypeNames: List of source data type names.
        @type sourceDataTypeNames: C{list} of C{unicode}
        @param targetDataTypeNames: List of source data type names.
        @type targetDataTypeNames: C{list} of C{unicode}
        
        @return: A new unique relation.
        @rtype: C{Relation}
        """
        
        if name is None:
            relationName = self._NEW_BASE_RELATION_NAME
        else:
            relationName = name
        if relationName in self._relations:
            counter = 0
            tmpName = relationName
            while tmpName in self._relations:
                counter = counter + 1
                tmpName = relationName + (" (%i)" % counter)
            relationName = tmpName
        return Relation(relationName, iconName, sourceDataTypeNames, targetDataTypeNames)

    def _getRelations(self):
        """ 
        Returns list of all defined relations. 
        
        @return: Defined data model relations.
        @rtype: C{list} of C{Relation}
        """
        
        result = list()
        for relation in self._relations.values():
            result.append(deepcopy(relation))
        return result
    
    def _setRelations(self, relations):
        """
        Replaces current relation set with the given.
        
        @param relations: Set of new data model relations.
        @type relations: C{list} of C{Relation}
        """
        
        self._relations.clear()
        self._relations[ROOT_RELATION_NAME] = self.createRelation(ROOT_RELATION_NAME)
        for relation in relations:
            self.addRelation(relation)

    relations = property(_getRelations, _setRelations)
            
    def addRelation(self, relation):
        """ 
        Adds / Updates the given relation. 
        
        @param relation: New/updated relation.
        @type relation: C{Relation}
        
        @note: Not registered data types referenced in the relation are removed.
        """
        
        relation = deepcopy(relation)
        for name in relation.sourceDataTypeNames:
            if not name in self._dataTypes:
                relation.removeSourceDataTypeName(name)
        for name in relation.targetDataTypeNames:
            if not name in self._dataTypes:
                relation.removeTargetDataTypeName(name)
        self._relations[relation.name] = relation
    
    def removeRelation(self, name):
        """ 
        Removes the relation. 
        
        @param name: Name of the relation.
        @type name: C{unicode}
        """
        
        if name == ROOT_RELATION_NAME:
            raise ConfigurationError("The removal of the root relation is not allowed.")
        if name in self._relations:
            del self._relations[name]

    def getRelation(self, name):
        """
        Returns the corresponding relation for the given name.
        
        @param name: Identifies the relation.
        @type name: C{unicode}
        
        @return: The corresponding relation.
        @rtype: C{Relation}
        """
        
        result = None
        if name in self._relations:
            result = deepcopy(self._relations[name])
        return result

    def hasRelation(self, relationName):
        """ 
        Determines whether the specific data type exists. 
        
        @param relationName: Name of the data type.
        @type relationName: C{unicode}
        
        @return: Flag indicating existence of the relation.
        @rtype: C{bool}
        """
        
        return relationName in self._relations

    def createDataType(self, name=None, iconName="dataType", propertyDefinitions=None):
        """ 
        Creates a unique data type. 
        
        @param name: Proposed name of the data type.
        @type name: C{unicode}
        @param iconName: Symbolic name of an associated icon.
        @type iconName: C{unicode}
        @param propertyDefinitions: List of property definitions.
        @type propertyDefinitions: C{list} of L{PropertyDefinition<datafinder.core.
        configuration.properties.property_definition.PropertyDefinition>} 
        
        @return: A new unique data type.
        @rtype: C{DataType}
        """

        if name is None:
            datatypeName = self._NEW_BASE_DATATYPE_NAME
        else:
            datatypeName = name
        if datatypeName in self._dataTypes:
            counter = 0
            tmpName = datatypeName
            while tmpName in self._dataTypes:
                counter = counter + 1
                tmpName = datatypeName + (" (%i)" % counter)
            datatypeName = tmpName
        return DataType(datatypeName, iconName, propertyDefinitions)

    def _getDataTypes(self):
        """ 
        Returns list of all defined data types. 
        
        @return: Defined data types.
        @rtype: C{list} of C{DataType}
        """
        
        result = list()
        for dataType in self._dataTypes.values():
            result.append(deepcopy(dataType))
        return result
 
    def _setDataTypes(self, datatypes):
        """
        Replaces current data type set with the given.
        
        @param datatypes: Set of new data model relations.
        @type datatypes: C{list} of C{Relation}
        """
        
        self._dataTypes.clear()
        for dataType in datatypes:
            self.addDataType(dataType)

    datatypes = property(_getDataTypes, _setDataTypes)
    
    def addDataType(self, dataType):
        """ 
        Adds / Updates the given data type. 
        
        @param dataType: The new/updated data type.
        @type dataType: C{DataType}
        """
        
        self._dataTypes[dataType.name] = deepcopy(dataType)
    
    def removeDataType(self, name):
        """ 
        Removes the data type. 
        
        @param name: Name of the data type.
        @type name: C{unicode}
        """
        
        if name in self._dataTypes:
            del self._dataTypes[name]
            for relation in self._relations.values():
                relation.removeSourceDataTypeName(name)
                relation.removeTargetDataTypeName(name)
                
    def getDataType(self, name):
        """
        Returns the corresponding data type for the given name.
        
        @param name: Identifies the data type.
        @type name: C{unicode}
        
        @return: The corresponding relation.
        @rtype: C{DataType}
        """
        
        result = None
        if name in self._dataTypes:
            result = deepcopy(self._dataTypes[name])
        return result

    def hasDataType(self, dataTypeName):
        """ 
        Determines whether the specific data type exists. 
        
        @param dataTypeName: Name of the data type.
        @type dataTypeName: C{unicode}
        
        @return: Flag indicating existence of the data type.
        @rtype: C{bool}
        """
        
        return dataTypeName in self._dataTypes

    def existsConnection(self, sourceDataTypeName, targetDataTypeName):
        """ 
        Checks whether a directed connection between the data type referenced
        by C{sourceDataTypeName} and the data type referenced by 
        C{targetDataTypeName} exists.
        
        @param sourceDataTypeName: Name of the source data type.
        @type sourceDataTypeName: C{unicode}
        @param targetDataTypeName: Name of the target data type.
        @type targetDataTypeName: C{unicode}
        
        @return: Flag indicating connection existence.
        @rtype: C{bool}
        """
        
        dataTypeNames = list()
        if sourceDataTypeName is None:
            dataTypeNames = self._relations[ROOT_RELATION_NAME].targetDataTypeNames
        else:
            for relation in self._relations.values():
                if sourceDataTypeName in relation.sourceDataTypeNames:
                    dataTypeNames.extend(relation.targetDataTypeNames)
        return targetDataTypeName in dataTypeNames
            
    def getTargetDataTypes(self, sourceDataTypeName):
        """ 
        Returns all target data types for the data type referenced by
        C{sourceDataTypeName}.
        
        @param sourceDataTypeName: Name of the data type.
        @type sourceDataTypeName: C{unicode}
        
        @return: List of all sub data types.
        @rtype: C{list} of C{DataType}
        """
        
        result = list()
        if sourceDataTypeName is None:
            for dataTypeName in self._relations[ROOT_RELATION_NAME].targetDataTypeNames:
                dataType = deepcopy(self._dataTypes[dataTypeName])
                result.append(dataType)
        else:
            for relation in self._relations.values():
                if sourceDataTypeName in relation.sourceDataTypeNames:
                    for dataTypeName in relation.targetDataTypeNames:
                        dataType = deepcopy(self._dataTypes[dataTypeName])
                        if not dataType in result:
                            result.append(dataType)
        return result
