# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#
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
Implements test cases for the custom meta data persistence format.
"""


from datetime import datetime
import decimal
import sys
import unicodedata
import unittest

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata.value_mapping import\
    MetadataValue, getPersistenceRepresentation


__version__ = "$Revision-Id$" 


_AE = unicodedata.lookup("LATIN SMALL LETTER A WITH DIAERESIS")


class MetadataValueTestCase(unittest.TestCase):
    def testInvalidPersistenceValue(self):
        self.assertRaises(PersistenceError, MetadataValue, None)
        
    def testComparison(self):
        self.assertEquals(MetadataValue("a"), MetadataValue("a"))
        self.assertEquals(hash(MetadataValue("a")), 
                          hash(MetadataValue("a")))
        
        self.assertNotEquals(MetadataValue("a"), MetadataValue("b"))
        self.assertNotEquals(hash(MetadataValue("a")), 
                             hash(MetadataValue("b")))
        
        self.assertNotEquals(MetadataValue("a"), None)
        self.assertNotEquals(hash(MetadataValue("a")), hash(None))
        
    def testRepresentation(self):
        self.assertEquals(str(MetadataValue("a")), "'a'")

    def testBoolValue(self):
        self.assertTrue(MetadataValue("1").value)
        self.assertFalse(MetadataValue("0").value)
 
    def testStringValue(self):
        self.assertEquals(MetadataValue(u"test").value, u"test")
        self.assertEquals(MetadataValue("test").value, "test")
        # Special escaped sequences
        self.assertEquals(MetadataValue("\\____EMPTY____LIST____").value, 
                          "____EMPTY____LIST____")
        self.assertEquals(MetadataValue("\\;").value, ";")
        
    def testNumericValue(self):
        self.assertEquals(MetadataValue(u"4.5").value, decimal.Decimal("4.5"))
        self.assertEquals(MetadataValue(u"5").value, decimal.Decimal("5"))
        
    def testDatetimeValue(self):
        # From time stamp
        metdataValue = MetadataValue("0", expectedType=datetime)
        self.assertEquals(metdataValue.value, datetime(1970, 1, 1, 1, 0))
        # From RFC 822.
        persistedValue = u"Wed, 02 Oct 2002 13:00:00 GMT"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, datetime(2002, 10, 2, 15, 0))
        # From Iso8601.
        persistedValue = u"2006-10-16T08:19:39Z"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, datetime(2006, 10, 16, 10, 19, 39))
        
    def testListValue(self):
        # Success
        self.assertEquals(MetadataValue("a;b;1").value, 
                          ["a", "b", decimal.Decimal(1)])
        # Special cases
        persistedValue = u"____EMPTY____LIST____"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, list())
        
        self.assertEquals(MetadataValue(";").value, ";")
        
        self.assertEquals(MetadataValue("a\\;b;c").value, ["a;b", "c"])
        
    def testDictValues(self):
        metdataValue = MetadataValue("{}")
        self.assertEquals(metdataValue.value, dict())
        
    def testGuessRepresentation(self):
        # Success
        self.assertEquals(MetadataValue("").guessRepresentation(), [None])
        self.assertEquals(MetadataValue("1").guessRepresentation(), 
                          [True, decimal.Decimal("1"), 
                           datetime(1970, 1, 1, 1, 0, 1), u"1"])

      
class GetPersistenceRepresentationTestCase(unittest.TestCase):
    def testBoolValue(self):
        self.assertEquals(getPersistenceRepresentation(True), "1")
        self.assertEquals(getPersistenceRepresentation(False), "0")
        
    def testNoneValue(self):
        self.assertEquals(getPersistenceRepresentation(None), "")
        self.assertRaises(PersistenceError, getPersistenceRepresentation, tuple())
        
    def testStringValue(self):
        self.assertEquals(getPersistenceRepresentation(u"test"), u"test")
        self.assertEquals(getPersistenceRepresentation("test"), u"test")
        # Special escaped sequences
        self.assertEquals(getPersistenceRepresentation(";"), "\\;")
        self.assertEquals(getPersistenceRepresentation("____EMPTY____LIST____"),
                          "\\____EMPTY____LIST____")
        # Invalid raw string
        orignalFunction = sys.getdefaultencoding
        sys.getdefaultencoding = lambda: None # Mock encoding determination
        try:
            self.assertRaises(
                PersistenceError, getPersistenceRepresentation, _AE.encode("Latin-1)"))
        finally:
            sys.getdefaultencoding = orignalFunction
        
    def testNumericValue(self):
        # Decimals
        persistedValue = decimal.Decimal("4.5")
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"4.5")
        persistedValue = decimal.Decimal("5")
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"5")
        # Raw integer
        self.assertEquals(getPersistenceRepresentation(5), u"5")
        #Raw float
        self.assertEquals(getPersistenceRepresentation(4.5), u"4.5")
        
    def testDatetimeValue(self):
        persistedValue = datetime(2006, 10, 16, 10, 19, 39)
        self.assertEquals(getPersistenceRepresentation(persistedValue), 
                          u"2006-10-16T08:19:39Z")
        
    def testListValue(self):
        persistedValue = [decimal.Decimal("2006"), decimal.Decimal("10"), 
                          decimal.Decimal("16"), decimal.Decimal("10")]
        self.assertEquals(getPersistenceRepresentation(persistedValue), 
                          u"2006;10;16;10;")
        persistedValue = list()
        self.assertEquals(getPersistenceRepresentation(persistedValue), 
                          u"____EMPTY____LIST____")

    def testDictValue(self):
        self.assertEquals(getPersistenceRepresentation(dict()), u"{}")
