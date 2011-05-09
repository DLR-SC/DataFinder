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
Implements test cases for the meta data values.
"""


import decimal
import unittest

from datetime import datetime

from datafinder.persistence.metadata.value_mapping import MetadataValue, getPersistenceRepresentation


__version__ = "$Revision-Id$" 


class MetadataValueTestCase(unittest.TestCase):
    """ Test cases for the meta data value. """
    
    def testValue(self):
        """ Tests the behavior of the value property. """
        
        # Tests for a bool value.
        persistedValue = u"1"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, True)
 
        # Tests for an unicode value.
        persistedValue = u"test"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, u"test")
        
        # Tests for a decimal value.
        persistedValue = u"4.5"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, decimal.Decimal("4.5"))
        persistedValue = u"5"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, decimal.Decimal("5"))
        
        # Tests for a datetime.
        # From float.
        persistedValue = u"34794.57"
        metdataValue = MetadataValue(persistedValue, expectedType=datetime)
        self.assertEquals(metdataValue.value, datetime(1970, 1, 1, 10, 39, 54, 570000))
        # From RFC 822.
        persistedValue = u"Wed, 02 Oct 2002 13:00:00 GMT"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, datetime(2002, 10, 2, 15, 0))
        # From Iso8601.
        persistedValue = u"2006-10-16T08:19:39Z"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, datetime(2006, 10, 16, 10, 19, 39))
        
        # Tests for a list value.
        # Empty list.
        persistedValue = []
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, [])
        persistedValue = u"____EMPTY____LIST____"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, [])

        # Tests for a dict value.
        # Empty dict.
        persistedValue = {}
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.value, {})
        
    def testGuessRepresentation(self):
        """ Tests the behavior of the guessRepresentation method. """
        
        # Tests for a bool value.
        persistedValue = u"1"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [True, decimal.Decimal("1"), datetime(1970, 1, 1, 1, 0, 1), 1,  u"1"])
        persistedValue = u"0"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [False, decimal.Decimal("0"), datetime(1970, 1, 1, 1, 0), 0, u"0"])
      
      
    def testGetPersistenceRepresentation(self):
        """ Tests the behavior of the getPersistenceRepresentation method. """
        
        # Tests for a bool value.
        persistedValue = True
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"1")
        persistedValue = False
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"0")
        
        # Tests for an unicode value.
        persistedValue = u"test"
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"test")
        
        # Tests for a decimal value.
        persistedValue = decimal.Decimal("4.5")
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"4.5")
        persistedValue = decimal.Decimal("5")
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"5")
        
        # Tests for a datetime.
        persistedValue = datetime(2006, 10, 16, 10, 19, 39)
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"2006-10-16T08:19:39Z")
        
        # Tests for a list value.
        persistedValue = [decimal.Decimal("2006"), decimal.Decimal("10"), decimal.Decimal("16"), decimal.Decimal("10")]
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"2006;10;16;10;")
        persistedValue = []
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"____EMPTY____LIST____")

        # Tests for a dict value.
        persistedValue = {"a": decimal.Decimal("134"), "b": decimal.Decimal("45.32")}
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"{\"a\": \"134\", \"b\": \"45.32\"}")
        persistedValue = {}
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"{}")
        persistedValue = {"a": []}
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"{\"a\": []}")
        persistedValue = {"a": [decimal.Decimal("2006"), decimal.Decimal("10")]}
        self.assertEquals(getPersistenceRepresentation(persistedValue), u"{\"a\": [\"2006\", \"10\"]}")
