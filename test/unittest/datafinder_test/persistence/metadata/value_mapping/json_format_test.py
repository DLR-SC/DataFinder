# $Filename$$
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
Tests for the JSON encoder / decoder.
"""


import datetime
import decimal
import sys
import unicodedata
import unittest

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata.value_mapping import json_format


__version__ = "$Revision-Id:$" 


_AE = unicodedata.lookup("LATIN SMALL LETTER A WITH DIAERESIS")


class MetadataValueTestCase(unittest.TestCase):
    
    def setUp(self):
        self._value = json_format.MetadataValue("None")
        
    def testComparison(self):
        self.assertEquals(self._value, self._value)
        self.assertEquals(hash(self._value), hash(self._value))
        
        self.assertNotEquals(self._value, json_format.MetadataValue(12))
        self.assertNotEquals(hash(self._value), hash(json_format.MetadataValue(12)))
        
        self.assertNotEquals(self._value, None)
        self.assertNotEquals(hash(self._value), hash(None))
        
    def testRepresentation(self):
        self.assertEquals(str(self._value), "'None'")
    
    def testGuessRepresentation(self):
        self.assertEquals(self._value.guessRepresentation(), ["None"])
    
    def testValue(self):
        self.assertEquals(self._value.value, "None")
    

class ConvertFromPersistenceFormatTestCase(unittest.TestCase):
    
    def testError(self):
        # Invalid JSON
        self.assertRaises(PersistenceError, 
                          json_format.convertFromPersistenceFormat, "as")
        # No string
        self.assertRaises(PersistenceError, 
                          json_format.convertFromPersistenceFormat, None)
        
    def testBoolValue(self):
        self.assertTrue(json_format.convertFromPersistenceFormat("true"))
        self.assertFalse(json_format.convertFromPersistenceFormat("false"))
 
    def testStringValue(self):
        self.assertEquals(json_format.convertFromPersistenceFormat(u'"test"'), u"test")
        self.assertEquals(json_format.convertFromPersistenceFormat('"test"'), "test")
        
    def testNumericValue(self):
        self.assertEquals(json_format.convertFromPersistenceFormat("4.5"), 
                          decimal.Decimal("4.5"))
        self.assertEquals(json_format.convertFromPersistenceFormat("5"), 
                          decimal.Decimal("5"))
        
    def testDatetimeValue(self):
        # From Iso8601.
        persistedValue = u'"2006-10-16T08:19:39Z"'
        metdataValue = json_format.convertFromPersistenceFormat(persistedValue)
        self.assertEquals(metdataValue, datetime.datetime(2006, 10, 16, 10, 19, 39))
        
    def testListValue(self):
        # Empty list
        metdataValue = json_format.convertFromPersistenceFormat("[]")
        self.assertEquals(metdataValue, list())
        # Mixed list
        self.assertEquals(
            json_format.convertFromPersistenceFormat('["a", "b", 1, "2006-10-16T08:19:39Z"]'), 
            ["a", "b", decimal.Decimal(1), datetime.datetime(2006, 10, 16, 10, 19, 39)])
        # Nested list
        jsonString = '[[["2006-10-16T08:19:39Z"]]]'
        self.assertEquals(
            json_format.convertFromPersistenceFormat(jsonString),
            [[[datetime.datetime(2006, 10, 16, 10, 19, 39)]]])
        
    def testDictValues(self):
        # Empty dict
        metdataValue = json_format.convertFromPersistenceFormat("{}")
        self.assertEquals(metdataValue, dict())
        # Mixed and nested dict
        jsonString = '{"name": "me", "age": 30, ' \
                   + '"address":{"street": "there", "number": 1, ' \
                   + '"city": {"name": "there", "build": ["2006-10-16T08:19:39Z"]}}}'
                   
        expectedResult = {"name": "me", "age": decimal.Decimal(30), 
                          "address":{"street": "there", "number": decimal.Decimal(1),
                          "city": {"name": "there", 
                                   "build": [datetime.datetime(2006, 10, 16, 10, 19, 39)]}}}
        self.assertEquals(json_format.convertFromPersistenceFormat(jsonString),
                          expectedResult)
      
class GetPersistenceRepresentationTestCase(unittest.TestCase):
    
    def testError(self):
        # Unsupported type
        self.assertRaises(
            PersistenceError, 
            json_format.convertToPersistenceFormat, json_format.MetadataValue(""))
        
    def testBoolValue(self):
        self.assertEquals(json_format.convertToPersistenceFormat(True), "true")
        self.assertEquals(json_format.convertToPersistenceFormat(False), "false")
        
    def testNoneValue(self):
        self.assertEquals(json_format.convertToPersistenceFormat(None), "null")
        
    def testStringValue(self):
        self.assertEquals(json_format.convertToPersistenceFormat(u"test"), '"test"')
        self.assertEquals(json_format.convertToPersistenceFormat("test"), '"test"')

        # Invalid raw string
        orignalFunction = sys.getdefaultencoding
        sys.getdefaultencoding = lambda: None # Mock encoding determination
        try:
            self.assertRaises(
                PersistenceError, json_format.convertToPersistenceFormat, _AE.encode("Latin-1)"))
        finally:
            sys.getdefaultencoding = orignalFunction
        
    def testNumericValue(self):
        # Decimals
        persistedValue = decimal.Decimal("4.5")
        self.assertEquals(json_format.convertToPersistenceFormat(persistedValue), u"4.5")
        persistedValue = decimal.Decimal("5")
        self.assertEquals(json_format.convertToPersistenceFormat(persistedValue), u"5")
        # Raw integer
        self.assertEquals(json_format.convertToPersistenceFormat(5), u"5")
        # Raw float
        self.assertEquals(json_format.convertToPersistenceFormat(4.5), u"4.5")
        
    def testDatetimeValue(self):
        persistedValue = datetime.datetime(2006, 10, 16, 10, 19, 39)
        self.assertEquals(json_format.convertToPersistenceFormat(persistedValue), 
                          '"2006-10-16T08:19:39Z"')
        
    def testListValue(self):
        persistedValue = [decimal.Decimal("2006"), decimal.Decimal("10.0"), 
                          decimal.Decimal("16"), decimal.Decimal("10.01")]
        self.assertEquals(json_format.convertToPersistenceFormat(persistedValue), 
                          u"[2006, 10.0, 16, 10.01]")
        persistedValue = list()
        self.assertEquals(json_format.convertToPersistenceFormat(persistedValue), 
                          u"[]")

    def testDictValue(self):
        self.assertEquals(json_format.convertToPersistenceFormat(dict()), u"{}")
