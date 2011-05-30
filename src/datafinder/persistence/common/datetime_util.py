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
Helper functions for date time conversion.
"""


__version__ = "$Revision-Id:$" 


import datetime
import rfc822
import time


_ISO8601_DATETIME_FORMAT = r"%Y-%m-%dT%H:%M:%SZ"


def convertToDatetime(datetimeString):
    """ If all conversion tries fail C{None} is returned.
    Supported formats are: 
        Time ticks since 1970 (e.g., 0.0)
        ISO8601 (e.g., 2000-01-01T10:10:10Z)
        RFC822 (e.g., Wed, 02 Oct 2002 13:00:00 GMT)        
    @note: Date and time is represented in local time zone. """
    
    dtConversionFuncs = [convertFromTimeStamp,
                         convertFromIso8601,
                         convertFromRfc822]
    for dtConversionFunc in dtConversionFuncs:
        try:
            return dtConversionFunc(datetimeString)
        except ValueError:
            datetimeValue = None
    return datetimeValue


def convertFromTimeStamp(timeStamp):
    """ Converts the time stamp to a C{datetime.datetime} object.
    @note: Date and time is represented in local time zone.
    @raise ValueError: To indicate failed conversion. """
    
    try:
        timeStamp = float(timeStamp)
    except TypeError:
        raise ValueError()
    dt = datetime.datetime.fromtimestamp(timeStamp)
    return _convertToLocaltime(dt, _LocalTimezone())


def _convertToLocaltime(dt, srcTimeZone):
    dt = dt.replace(tzinfo=srcTimeZone)
    dt = dt.astimezone(_LocalTimezone())
    return dt.replace(tzinfo=None)


def convertFromRfc822(rfc822Format):
    """ Converts the RFC822 formatted date time string
    to a C{datetime.datetime} object.
    @note: Date and time is represented in local time zone.
    @raise ValueError: To indicate failed conversion. """
    
    timeStruct = rfc822.parsedate(rfc822Format)
    if not timeStruct is None:
        dt = datetime.datetime(*(timeStruct[0:6]))
        return _convertToLocaltime(dt, _UtcTimezone())
    else:
        raise ValueError()


def convertFromIso8601(iso8601Format):
    """ Converts the ISO8601 formatted date time string
    to a C{datetime.datetime} object.
    @note: Date and time is represented in local time zone.
    @raise ValueError: To indicate failed conversion. """
    
    try:
        timeStruct = time.strptime(iso8601Format, _ISO8601_DATETIME_FORMAT)
    except TypeError:
        raise ValueError()
    dt = datetime.datetime(*(timeStruct)[0:6])
    return _convertToLocaltime(dt, _UtcTimezone())


def convertToIso8601(dt):
    """ Converts a C{datetime.datetime} object to 
    an ISO8601 formatted date time string. 
    @note: Date and time is represented in UTC time zone.
    @raise ValueError: To indicate failed conversion. """

    try:
        dt = dt.replace(tzinfo=_LocalTimezone())
        dt = dt.astimezone(_UtcTimezone())
        return dt.strftime(_ISO8601_DATETIME_FORMAT)
    except AttributeError:
        raise ValueError()


class _UtcTimezone(datetime.tzinfo):

    def utcoffset(self, _):
        return datetime.timedelta(0)

    def dst(self, _):
        return datetime.timedelta(0)
    

class _LocalTimezone(datetime.tzinfo):

    def __init__(self):
        datetime.tzinfo.__init__(self)
        self._standardOffset = datetime.timedelta(seconds=-time.timezone)
        self._dstOffset = self._standardOffset
        if time.daylight:
            self._dstOffset = datetime.timedelta(seconds=-time.altzone)
        self._destDifference = self._dstOffset - self._standardOffset

    def utcoffset(self, dt):
        if self._isDst(dt):
            return self._dstOffset
        else:
            return self._standardOffset

    def dst(self, dt):
        if self._isDst(dt):
            return self._destDifference
        else:
            return datetime.timedelta(0)

    @staticmethod
    def _isDst(dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        try:
            stamp = time.mktime(tt)
            tt = time.localtime(stamp)
            return tt.tm_isdst > 0
        except (ValueError, OverflowError):
            return False
