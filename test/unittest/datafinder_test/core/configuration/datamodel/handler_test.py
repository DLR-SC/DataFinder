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
Test cases for the data model handling.
"""


import unittest
from xml.parsers.expat import ExpatError

from datafinder.core.configuration.datamodel import handler, constants
from datafinder.core.configuration.gen import datamodel as gen_datamodel
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class DataModelHandlerTest(unittest.TestCase):
    """ Tests of the data model handler. """
    
    def setUp(self):
        """ Creates the object under test. """
        
        self._parseStringMock = SimpleMock()
        handler.datamodel.parseString = self._parseStringMock
        self._createFileStorerMock = SimpleMock(SimpleMock())
        handler.createFileStorer = self._createFileStorerMock
        self._fileStorerMock = SimpleMock()
        self._dataModelHandler = handler.DataModelHandler(self._fileStorerMock, SimpleMock())
        self._persistedDataModel = self._initPersistedDataModel()
        self._dataTypes, self._relations = self._initDataModel() 
         
    @staticmethod
    def _initPersistedDataModel():
        """ Creates persisted data model. """
        
        dataTypeA = gen_datamodel.datatype("a")
        dataTypeB = gen_datamodel.datatype("b")
        relation = gen_datamodel.relation("relation", "", ["a"], ["a", "b"])
        return gen_datamodel.datamodel([dataTypeA, dataTypeB], [relation])
        
    def _initDataModel(self):
        """ Initializes corresponding data model. """
        
        dataTypes = [self._dataModelHandler.createDataType("a"), self._dataModelHandler.createDataType("b")]
        relations = [self._dataModelHandler.createRelation("relation", "", ["a"], ["a", "b"])]
        return dataTypes, relations
         
    def testCreate(self):
        """ Tests initial data model persistence. """
        
        self._dataModelHandler.create()
        
        self._fileStorerMock.error = PersistenceError()
        self.assertRaises(ConfigurationError, self._dataModelHandler.create)
        
    def testLoad(self):
        """ Tests the loading of the persisted data model. """
        
        self._fileStorerMock.methodNameResultMap = {"exists": (True, None), 
                                                    "readData": (SimpleMock(""), None)}
        self._parseStringMock.value = self._persistedDataModel
        self._dataModelHandler.load()
        self.assertEquals(self._dataModelHandler.datatypes, self._dataTypes)
        self.assertEquals(self._dataModelHandler.relations, self._relations)

        self._fileStorerMock.methodNameResultMap = None
        self._fileStorerMock.value = False
        self.assertRaises(ConfigurationError, self._dataModelHandler.load)
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._dataModelHandler.load)
        
        self._parseStringMock.error = ExpatError("")
        self.assertRaises(ConfigurationError, self._dataModelHandler.load)
        
        self._parseStringMock.error = ValueError("")
        self.assertRaises(ConfigurationError, self._dataModelHandler.load)
        
    def testStore(self):
        """ Tests the persistence of the data model. """
        
        self._dataModelHandler.store()
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._dataModelHandler.store)
        
    def testExportDataModel(self):
        """ Tests the data model export. """
        
        self._dataModelHandler.exportDatamodel("/target/file/path.xml")
        
        self._createFileStorerMock.value.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._dataModelHandler.exportDatamodel, "/target/file/path.xml")
        
        self._createFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._dataModelHandler.exportDatamodel, "/target/file/path.xml")
         
    def testImportDataModel(self):
        """ Tests the data model import. """
        
        self._createFileStorerMock.value = SimpleMock(SimpleMock())
        self._parseStringMock.value = self._persistedDataModel
        self._dataModelHandler.importDatamodel("")
        self.assertEquals(self._dataModelHandler.datatypes, self._dataTypes)
        self.assertEquals(self._dataModelHandler.relations, self._relations)

        self._createFileStorerMock.value.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._dataModelHandler.importDatamodel, "")
        
        self._createFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._dataModelHandler.importDatamodel, "")

    def testCreateRelation(self):
        """ Tests the factory method for creation of relations. """
        
        relation = self._dataModelHandler.createRelation("name", "iconName", 
                                                         ["sourceDataTypeNames"], ["targetDataTypeNames"])
        self.assertEquals(relation.name, "name")
        self.assertEquals(relation.iconName, "iconName")
        self.assertEquals(relation.sourceDataTypeNames, ["sourceDataTypeNames"])
        self.assertEquals(relation.targetDataTypeNames, ["targetDataTypeNames"])
        
        self._dataModelHandler.addRelation(relation)
        anotherRelation = self._dataModelHandler.createRelation(relation.name)
        self.assertNotEquals(relation.name, anotherRelation.name)
        
    def testRelationHandling(self):
        """ Tests the handling of relations. """
        
        relation = self._dataModelHandler.createRelation("name")
        self.assertFalse(self._dataModelHandler.hasRelation(relation.name))
        anotherRelation = self._dataModelHandler.createRelation()
        self._dataModelHandler.relations = [relation, anotherRelation]
        self.assertEquals(len(self._dataModelHandler.relations), 3)
        self.assertTrue(self._dataModelHandler.hasRelation(relation.name))
        self.assertTrue(self._dataModelHandler.hasRelation(anotherRelation.name))
        self.assertTrue(self._dataModelHandler.hasRelation(constants.ROOT_RELATION_NAME))
        
        relation.iconName = "anotherName"
        self.assertNotEquals(self._dataModelHandler.getRelation("name").iconName, relation.iconName)
        relation.addSourceDataTypeName("unknown")
        relation.addTargetDataTypeName("unknown")
        self._dataModelHandler.addRelation(relation)
        self.assertEquals(len(self._dataModelHandler.relations), 3)
        self.assertEquals(self._dataModelHandler.getRelation(relation.name).iconName, relation.iconName)
        self.assertEquals(self._dataModelHandler.getRelation(relation.name).sourceDataTypeNames, list())
        self.assertEquals(self._dataModelHandler.getRelation(relation.name).targetDataTypeNames, list())
        
        self._dataModelHandler.removeRelation("name")
        self._dataModelHandler.removeRelation("name")
        self.assertEquals(len(self._dataModelHandler.relations), 2)
        
        self.assertRaises(ConfigurationError, self._dataModelHandler.removeRelation, constants.ROOT_RELATION_NAME)
        
    def testCreateDataType(self):
        """ Tests the factory method for creation of data types. """
        
        propertyDefinitions = list()
        dataType = self._dataModelHandler.createDataType("name", "iconName", propertyDefinitions)
        self.assertEquals(dataType.name, "name")
        self.assertEquals(dataType.iconName, "iconName")
        self.assertEquals(dataType.propertyDefinitions, propertyDefinitions)
        
        self._dataModelHandler.addDataType(dataType)
        anotherDataType = self._dataModelHandler.createDataType(dataType.name)
        self.assertNotEquals(dataType.name, anotherDataType.name)
        
    def testDataTypeHandling(self):
        """ Tests the handling of data types. """
        
        dataType = self._dataModelHandler.createDataType("name")
        self.assertFalse(self._dataModelHandler.hasDataType(dataType.name))
        anotherDataType = self._dataModelHandler.createDataType()
        self._dataModelHandler.datatypes = [dataType, anotherDataType]
        self.assertEquals(len(self._dataModelHandler.datatypes), 2)
        self.assertTrue(self._dataModelHandler.hasDataType(dataType.name))
        self.assertTrue(self._dataModelHandler.hasDataType(anotherDataType.name))
        
        dataType.iconName = "anotherName"
        self.assertNotEquals(self._dataModelHandler.getDataType("name").iconName, dataType.iconName)
        self._dataModelHandler.addDataType(dataType)
        self.assertEquals(len(self._dataModelHandler.datatypes), 2)
        self.assertEquals(self._dataModelHandler.getDataType("name").iconName, dataType.iconName)

        rootRelation = self._dataModelHandler.getRelation(constants.ROOT_RELATION_NAME)
        rootRelation.addSourceDataTypeName(dataType.name)
        rootRelation.addTargetDataTypeName(dataType.name)
        self._dataModelHandler.addRelation(rootRelation)
        rootRelation = self._dataModelHandler.getRelation(constants.ROOT_RELATION_NAME)
        self.assertEquals(len(rootRelation.sourceDataTypeNames), 1)
        self.assertEquals(len(rootRelation.targetDataTypeNames), 1)
        self._dataModelHandler.removeDataType(dataType.name)
        rootRelation = self._dataModelHandler.getRelation(constants.ROOT_RELATION_NAME)
        self.assertEquals(len(rootRelation.sourceDataTypeNames), 0)
        self.assertEquals(len(rootRelation.targetDataTypeNames), 0)
        
        self._dataModelHandler.removeDataType(dataType.name)
        self.assertEquals(len(self._dataModelHandler.datatypes), 1)
        
    def testConnectionHandling(self):
        """ Tests the existence check for data type connections. """
        
        dataType = self._dataModelHandler.createDataType()
        anotherDataType = self._dataModelHandler.createDataType("anoterName")
        
        rootRelation = self._dataModelHandler.getRelation(constants.ROOT_RELATION_NAME)
        rootRelation.addSourceDataTypeName(dataType.name)
        rootRelation.addTargetDataTypeName(anotherDataType.name)
        anotherRelation = self._dataModelHandler.createRelation(sourceDataTypeNames=[anotherDataType.name],
                                                                targetDataTypeNames=[dataType.name])

        self.assertFalse(self._dataModelHandler.existsConnection(None, anotherDataType.name))
        self.assertFalse(self._dataModelHandler.existsConnection(None, dataType.name))
        self.assertFalse(self._dataModelHandler.existsConnection(dataType.name, anotherDataType.name))
        self.assertFalse(self._dataModelHandler.existsConnection(anotherDataType.name, dataType.name))
        self.assertEquals(self._dataModelHandler.getTargetDataTypes(dataType.name), list())
        self.assertEquals(self._dataModelHandler.getTargetDataTypes(anotherDataType.name), list())
        
        self._dataModelHandler.addDataType(dataType)
        self._dataModelHandler.addDataType(anotherDataType)
        self._dataModelHandler.addRelation(rootRelation)
        self._dataModelHandler.addRelation(anotherRelation)

        self.assertTrue(self._dataModelHandler.existsConnection(None, anotherDataType.name))
        self.assertFalse(self._dataModelHandler.existsConnection(None, dataType.name))
        self.assertTrue(self._dataModelHandler.existsConnection(dataType.name, anotherDataType.name))
        self.assertTrue(self._dataModelHandler.existsConnection(anotherDataType.name, dataType.name))
        self.assertEquals(self._dataModelHandler.getTargetDataTypes(dataType.name), [anotherDataType])
        self.assertEquals(self._dataModelHandler.getTargetDataTypes(anotherDataType.name), [dataType])
