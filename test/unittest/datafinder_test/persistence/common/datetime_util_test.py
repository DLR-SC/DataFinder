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
Provides tests for the date and time utility helper functions.
"""


import datetime
import decimal
import unittest

from datafinder.persistence.common import datetime_util as dt_util


__version__ = "$Revision-Id:$" 


class DatetimeUtilTestCase(unittest.TestCase):

    def testConvertToDatetime(self):
        # Success
        self.assertEquals(dt_util.convertToDatetime("1"),
                           datetime.datetime(1970, 1, 1, 1, 0, 1))
        
        # error handling
        self.assertEquals(dt_util.convertToDatetime(None), None)
        self.assertEquals(dt_util.convertToDatetime(""), None)
        
    def testConvertFromTimeStamp(self):
        # Success
        self.assertEquals(dt_util.convertFromTimeStamp("1"),
                          datetime.datetime(1970, 1, 1, 1, 0, 1))
        self.assertEquals(dt_util.convertFromTimeStamp(1),
                          datetime.datetime(1970, 1, 1, 1, 0, 1))
        self.assertEquals(dt_util.convertFromTimeStamp(decimal.Decimal("1.0")),
                          datetime.datetime(1970, 1, 1, 1, 0, 1))

        # Error
        self.assertRaises(ValueError, dt_util.convertFromTimeStamp, None)
        self.assertRaises(ValueError, dt_util.convertFromTimeStamp, -10.0)

    def testConvertFromRfc822(self):
        # Success
        self.assertEquals(
            dt_util.convertFromRfc822("Wed, 02 Oct 2002 13:06:07 GMT"),
            datetime.datetime(2002, 10, 2, 15, 6, 7))

        # Error
        self.assertRaises(ValueError, dt_util.convertFromRfc822, None)
        self.assertRaises(ValueError, dt_util.convertFromRfc822, "10")
        self.assertRaises(ValueError, dt_util.convertFromRfc822, "")

    def testConvertFromIso8601(self):
        # Success
        self.assertEquals(
            dt_util.convertFromIso8601("2006-10-16T08:19:39Z"),
            datetime.datetime(2006, 10, 16, 10, 19, 39))

        # Error
        self.assertRaises(ValueError, dt_util.convertFromIso8601, None)
        self.assertRaises(ValueError, dt_util.convertFromIso8601, "")

    def testConvertToIso8601(self):
        # Success
        self.assertEquals(
            dt_util.convertToIso8601(datetime.datetime(2006, 10, 16, 10, 19)), 
            "2006-10-16T08:19:00Z")
        
        # Error
        self.assertRaises(ValueError, dt_util.convertToIso8601, None)
