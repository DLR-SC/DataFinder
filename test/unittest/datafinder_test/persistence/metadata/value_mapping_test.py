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

from datafinder.persistence.metadata.value_mapping import MetadataValue


__version__ = "$Revision-Id$" 


class MetadataValueTestCase(unittest.TestCase):
    """ Test cases for the meta data value. """
    
    def setUp(self):
        """ Set up for the test cases. """
        
        pass
    
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
        self.assertEquals(metdataValue.guessRepresentation(), [True, decimal.Decimal("1"), datetime(1970, 1, 1, 1, 0, 1), u"1"])
        persistedValue = u"0"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [False, decimal.Decimal("0"), datetime(1970, 1, 1, 1, 0), u"0"])
        
        # Tests for an unicode value.
        persistedValue = u"test"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [u"test"])
        
        # Tests for a decimal value.
        persistedValue = u"4.5"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [decimal.Decimal("4.5"), datetime(1970, 1, 1, 1, 0, 4, 500000), u"4.5"])
        persistedValue = u"5"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [decimal.Decimal("5"), datetime(1970, 1, 1, 1, 0, 5), u"5"])
        
        # Tests for a datetime.
        # From float.
        persistedValue = u"34794.57"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [decimal.Decimal("34794.57"), datetime(1970, 1, 1, 10, 39, 54, 570000), u"34794.57"])
        # From RFC 822.
        persistedValue = u"Wed, 02 Oct 2002 13:00:00 GMT"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [datetime(2002, 10, 2, 15, 0), u"Wed, 02 Oct 2002 13:00:00 GMT"])
        # From Iso8601.
        persistedValue = u"2006-10-16T08:19:39Z"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [datetime(2006, 10, 16, 10, 19, 39), u"2006-10-16T08:19:39Z"])
        
        # Tests for a list value.
        # Empty list.
        persistedValue = []
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [[]])
        persistedValue = u"____EMPTY____LIST____"
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [[], u"____EMPTY____LIST____"])
        # List with dict.
        persistedValue = [{}]
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [[{}]])
        # List with bools.
        persistedValue = [u"1", u"0"]
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [[True, False]])
        # List with decimals.
        persistedValue = [u"134", u"45.32"]
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [[decimal.Decimal("134"), decimal.Decimal("45.32")]])
        # List with unicodes.
        persistedValue = [u"test", u"test2"]
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [[u"test", u"test2"]])
        # List with datetimes.
        persistedValue = [u"Wed, 02 Oct 2002 13:00:00 GMT", u"2006-10-16T08:19:39Z"]
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [[datetime(2002, 10, 2, 15, 0), datetime(2006, 10, 16, 10, 19, 39)]])
        
        # Tests for a dict value.
        # Empty dict.
        persistedValue = {}
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [{}])
        # Dict with bools.
        persistedValue = {"a": u"1", "b": u"0"}
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [{"a": True, "b": False}])
        # Dict with decimals.
        persistedValue = {"a": u"134", "b": u"45.32"}
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [{"a": decimal.Decimal("134"), "b": decimal.Decimal("45.32")}])
        # Dict with unicodes.
        persistedValue = {"a": u"test", "b": u"test2"}
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [{"a": u"test", "b": u"test2"}])
        # Dict with datetimes.
        persistedValue = {"a": u"Wed, 02 Oct 2002 13:00:00 GMT", "b": u"2006-10-16T08:19:39Z"}
        metdataValue = MetadataValue(persistedValue)
        self.assertEquals(metdataValue.guessRepresentation(), [{"a": datetime(2002, 10, 2, 15, 0), "b": datetime(2006, 10, 16, 10, 19, 39)}])
