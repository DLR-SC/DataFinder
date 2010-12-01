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
Tests the relation representation.
"""


import unittest

from datafinder.core.configuration.datamodel import relation
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class RelationTestCase(unittest.TestCase):
    """ Tests the relation representation. """

    def setUp(self):
        """ Creates object under test. """
        
        self._relation = relation.Relation("name")
    
    def testSourceDataTypeHandling(self):
        """ Tests the handling of source data type names. """
        
        self._relation.addSourceDataTypeName("name")
        self._relation.addSourceDataTypeName("name2")
        self.assertEquals(len(self._relation.sourceDataTypeNames), 2)
        
        self._relation.addSourceDataTypeName("name2")
        self.assertEquals(len(self._relation.sourceDataTypeNames), 2)
        
        self._relation.removeSourceDataTypeName("name")
        self._relation.removeSourceDataTypeName("name2")
        self.assertEquals(len(self._relation.sourceDataTypeNames), 0)
        
        self._relation.sourceDataTypeNames = ["name", "name2"] 
        self.assertEquals(len(self._relation.sourceDataTypeNames), 2)
        
    def testTargetDataTypeHandling(self):
        """ Tests the handling of target data type names. """
        
        self._relation.addTargetDataTypeName("name")
        self._relation.addTargetDataTypeName("name2")
        self.assertEquals(len(self._relation.targetDataTypeNames), 2)
        
        self._relation.addTargetDataTypeName("name2")
        self.assertEquals(len(self._relation.targetDataTypeNames), 2)
        
        self._relation.removeTargetDataTypeName("name")
        self._relation.removeTargetDataTypeName("name2")
        self.assertEquals(len(self._relation.targetDataTypeNames), 0)
        
    def testLoad(self):
        """ Tests the creation of a relation from the persistence format. """
        
        newRelation = relation.Relation.load(SimpleMock(name="name", iconName="iconName",
                                                        sourceDataTypeNames=["a", "b"],
                                                        targetDataTypeNames=["c", "d"]))
        self.assertEquals(newRelation.name, "name")
        self.assertEquals(newRelation.iconName, "iconName")
        self.assertEquals(newRelation.sourceDataTypeNames, ["a", "b"])
        self.assertEquals(newRelation.targetDataTypeNames, ["c", "d"])
        
    def testToPersistenceRepresentation(self):
        """ Tests the transformation to the persistence format. """
        
        self._relation.sourceDataTypeNames = ["a"]
        self._relation.targetDataTypeNames = ["a"]
        
        persistedDataType = self._relation.toPersistenceRepresentation()
        self.assertEquals(persistedDataType.name, "name")
        self.assertEquals(persistedDataType.iconName, "relationType")
        self.assertEquals(persistedDataType.sourceDataTypeNames, ["a"])
        self.assertEquals(persistedDataType.targetDataTypeNames, ["a"])
