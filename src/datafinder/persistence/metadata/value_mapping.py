#
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
Implements conversion of meta data values from 
Python types to the persistence format and vice versa.
"""


import json
import time
from datetime import datetime, timedelta, tzinfo
import rfc822
import decimal


__version__ = "$Revision-Id$" 


_LIST_SEPARATOR = ";"
_ISO8601_DATETIME_FORMAT = r"%Y-%m-%dT%H:%M:%SZ"
_NONE_PERSISTENCE_REPRESENTATION = ""
_EMPTY_LIST_REPRESENTATION = "____EMPTY____LIST____"


class MetadataValue(object):
    """ Wrapper around a meta data value in persistence format. """

    def __init__(self, persistedValue, expectedType=None):
        """ 
        Constructor. 
        
        @param persistedValue: The persistence representation of a property value.
        @type persistedValue: C{unicode}
        """
        
        self._expectedType = expectedType
        self.__persistedValue = persistedValue
        self.__conversionFunctions = list()
        self.__conversionFunctions.append(self._convertToBool)
        self.__conversionFunctions.append(self._convertToDecimal)
        self.__conversionFunctions.append(self._convertToDatetime)
        self.__conversionFunctions.append(self._convertToList)
        self.__conversionFunctions.append(self._convertToUnicode)
        self.__conversionFunctions.append(self._convertToDict)
        
    def __getPersistedValue(self):
        """ Simple getter. """
        
        return self.__persistedValue
    persistedValue = property(__getPersistedValue)
    
    def __getValue(self):
        """ Getter for the most probable value. """
        
        representations = self.guessRepresentation()
        if not self._expectedType is None:
            for representation in representations:
                if type(representation) == self._expectedType:
                    return representation
        try:
            return representations[0]
        except IndexError:
            return None
    value = property(__getValue)
        
    def guessRepresentation(self):
        """ 
        Tries to convert the retrieved value to the expected type.
        If the conversion fails an empty list is returned.
        
        @return: List of possible value representations.
        @rtype: C{list} of C{object}
        """
        
        result = list()
        if _NONE_PERSISTENCE_REPRESENTATION == self.__persistedValue:
            result.append(None)
        else:
            convertedValue = None
            for conversionFunction in self.__conversionFunctions:
                convertedValue = conversionFunction(self.__persistedValue)
                if not convertedValue is None:
                    result.append(convertedValue)
        return result
        
    def _convertToList(self, value):
        """ Converts value to a list. """
        
        try:
            if isinstance(value, type(list())):
                typedList = list()
                for item in value:
                    for conversionFunction in self.__conversionFunctions:
                        convertedValue = conversionFunction(item)
                        if not convertedValue is None:
                            break
                    typedList.append(convertedValue)
                return typedList
            elif _LIST_SEPARATOR in value:
                stringList = value.split(_LIST_SEPARATOR)[:-1]
                typedList = list()
                for item in stringList:
                    if item == _NONE_PERSISTENCE_REPRESENTATION:
                        convertedValue = None
                    else:
                        for conversionFunction in self.__conversionFunctions:
                            print conversionFunction
                            convertedValue = conversionFunction(item)
                            if not convertedValue is None:
                                break
                        typedList.append(convertedValue)
                        return typedList
            elif value == _EMPTY_LIST_REPRESENTATION:
                return  list()
        except TypeError:
            return None
        
    def _convertToDict(self, value):
        """ 
        Converts value to a dict. 
        
        Dicts and strings are supported. Dirty hack!
        """
        
        if isinstance(value, type(dict())):
            typedDict = dict()
            for key in value:
                for conversionFunction in self.__conversionFunctions:
                    convertedValue = conversionFunction(value[key])
                    if not convertedValue is None:
                        break
                typedDict[key] = convertedValue
            return typedDict
        else:
            try:
                return json.loads(value)
            except ValueError:
                return None
            except TypeError:
                return None

    @staticmethod
    def _convertToUnicode(value):
        """ Converts to a unicode value. """
        
        if not (isinstance(value, type(dict())) or isinstance(value, type(list()))):
            return value
    
    @staticmethod
    def _convertToBool(value):
        """ Converts the given unicode value to boolean. """
        
        try:
            intValue = int(value)
        except ValueError:
            return None
        except TypeError:
            return  None
        else:
            if intValue in [0, 1]:
                return bool(intValue)
    
    @staticmethod
    def _convertToDecimal(value):
        """ Converts value to decimal. """
        
        try:
            value =  decimal.Decimal(value)
        except (decimal.InvalidOperation, ValueError, TypeError):
            value = None
        return value
        
    def _convertToDatetime(self, value):
        """ Converts value to date time. """
        
        datetimeInstance = None
        datetimeConversionFunctions = [self._convertToDatetimeFromIso8601,
                                       self._convertToDatetimeFromRfc822,
                                       self._convertToDatetimeFromFloat]
        try:
            for datetimeConversionFunction in datetimeConversionFunctions:
                datetimeInstance = datetimeConversionFunction(value)
                if not datetimeInstance is None:
                    return datetimeInstance.replace(tzinfo=None)
        except TypeError:
            return None
    
    @staticmethod
    def _convertToDatetimeFromFloat(value):
        """ 
        Converts to datetime instance from float 
        value representing time ticks since 1970.
        """
        
        try:
            floatValue = float(value)
            dt = datetime.fromtimestamp(floatValue)
            dt = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, _LocalTimezone())
        except ValueError:
            return None
        return dt
    
    @staticmethod
    def _convertToDatetimeFromRfc822(value):
        """
        Converts to datetime instance from string
        representing date and time in format defined by RFC 822.
        """
        
        try:
            structTime = rfc822.parsedate(value)
        except IndexError:
            return None
        if not structTime is None:
            dt = datetime(*(structTime[0:6]))
            dt = dt.replace(tzinfo=_Utc())
            return dt.astimezone(_LocalTimezone())
        else:
            return None
    
    @staticmethod
    def _convertToDatetimeFromIso8601(value):
        """ 
        Converts to datetime from string 
        representing date and time in format defined by ISO 8601.
        """
        
        try:
            dt = datetime(*(time.strptime(value, _ISO8601_DATETIME_FORMAT)[0:6]))
            dt = dt.replace(tzinfo=_Utc())
            return dt.astimezone(_LocalTimezone())
        except ValueError:
            return None
    
    def __cmp__(self, instance):
        """ Compares to instances. """
        
        if self.persistedValue == instance.persistedValue:
            return 0
        else:
            return 1
        
        
    def __repr__(self):
        """returns the representation of the value"""
        
        return repr(self.value)

    
def getPersistenceRepresentation(value):
    """ 
    Tries to convert the given value to the persistence string format.
    
    @param value: Value to persist.
    @type value: C{object}

    @return: String representation.
    @rtype: C{string}
    """
    
    if value is None:
        return _NONE_PERSISTENCE_REPRESENTATION
    else:
        typeConversionFunctionMap = {str: _convertFromUnicode,
                                     unicode: _convertFromUnicode,
                                     int: _convertFromDecimal,
                                     float: _convertFromDecimal,
                                     bool: _convertFromBool,
                                     decimal.Decimal: _convertFromDecimal,
                                     list: _convertFromList,
                                     datetime: _convertFromDatetime,
                                     dict: _convertFromDict} 
        valueType = type(value)
        if valueType in typeConversionFunctionMap:
            return typeConversionFunctionMap[valueType](value)
        else:
            raise ValueError("Persistence support for values of type '%s' is not available." % str(valueType))


def _convertFromDatetime(value):
    """ Converts an datetime instance to a string. """

    value = value.replace(tzinfo=_LocalTimezone())
    value = value.astimezone(_Utc())
    return value.strftime(_ISO8601_DATETIME_FORMAT)
    

def _convertFromDecimal(value):
    """ Converts a Decimal instance to a string. """
    
    return unicode(value)
    
    
def _convertFromBool(value):
    """ Converts a boolean value to a string. """
    
    return unicode(int(value))


def _convertFromList(value):
    """ Converts a list to a string. """
    
    listAsString = ""
    for item in value:
        convertedItem = getPersistenceRepresentation(item)
        listAsString += convertedItem + _LIST_SEPARATOR
    if len(listAsString) == 0:
        listAsString = _EMPTY_LIST_REPRESENTATION
    return listAsString


def _convertFromListToJson(value):
    """ Converts a list to a json list. """
    
    listJson = []
    for item in value:
        convertedItem = getPersistenceRepresentation(item)
        listJson.append(convertedItem)
    return listJson


def _convertFromDict(value):
    """ Converts a dict to a json string. """
    
    convertedDict = {}
    for key in value:
        if isinstance(value[key], type(list())):
            convertedDict[key] = _convertFromListToJson(value[key])
        else:
            convertedDict[key] = getPersistenceRepresentation(value[key])
    return unicode(json.dumps(convertedDict))


def _convertFromUnicode(value):
    """ Converts an unicode. """
    
    if not isinstance(value, unicode):
        value = unicode(value)
    return value
    
    
class _Utc(tzinfo):
    """ Representation of UTC time. """

    def utcoffset(self, _):
        """ @see: L{datetime.tzinfo.utcoffset} """
        
        return timedelta(0)

    def tzname(self, _):
        """ @see: L{datetime.tzinfo.tzname} """
        
        return "UTC"

    def dst(self, _):
        """ @see: L{datetime.tzinfo.dst} """
        
        return timedelta(0)
    

class _LocalTimezone(tzinfo):
    """ Representation of the local time. """

    def __init__(self):
        """ Constructor. """
        
        tzinfo.__init__(self)
        self.__standardOffset = timedelta(seconds=-time.timezone)
        self.__dstOffset = self.__standardOffset
        if time.daylight:
            self.__dstOffset = timedelta(seconds=-time.altzone)
        self.__destDifference = self.__dstOffset - self.__standardOffset

    def utcoffset(self, dt):
        """ @see: L{datetime.tzinfo.utcoffset} """
        
        if self.__isdst(dt):
            return self.__dstOffset
        else:
            return self.__standardOffset

    def dst(self, dt):
        """ @see: L{datetime.tzinfo.dst} """
        
        if self.__isdst(dt):
            return self.__destDifference
        else:
            return timedelta(0)

    def tzname(self, dt):
        """ @see: L{datetime.tzinfo.tzname} """
        
        return time.tzname[self.__isdst(dt)]

    @staticmethod
    def __isdst(dt):
        """ 
        Helper method determining datetime
        instance in daylight saving time or not.
        """
        
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        try:
            stamp = time.mktime(tt)
            tt = time.localtime(stamp)
            return tt.tm_isdst > 0
        except (ValueError, OverflowError):
            return False
