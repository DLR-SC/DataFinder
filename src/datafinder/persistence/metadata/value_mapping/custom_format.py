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
Handles encoding/decoding of Python objects to a custom string format.
This module is intended to be replaced. Make sure to use L{JSON Format
<datafinder.persistence.metadata.value_mapping.json_format>} for new
implementations.

This module can handle the following data types:
- Numerics (float, int C{decimal.Decimal}
- Booleans
- Strings (unicode, str)
- Date time (C{datetime.datetime}, Decoding works from: ISO8601, 
RFC822, time stamp. Encoding works from local time to UTC and decoding vice versa.
- Lists (CANNOT not be nested)
- Dictionaries (Already uses the new JSON format)
"""


import datetime
import decimal
import re
import sys

from datafinder.persistence.common import datetime_util
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata.value_mapping import json_format


__version__ = "$Revision-Id$" 


_LIST_SEPARATOR = ";"
_ESCAPED_LIST_SEPARATOR = "\\" + _LIST_SEPARATOR
_NONE_PERSISTENCE_REPRESENTATION = ""
_EMPTY_LIST_REPRESENTATION = "____EMPTY____LIST____"
_ESCAPED_EMPTY_LIST = "\\" + _EMPTY_LIST_REPRESENTATION


class MetadataValue(object):
    """ Wrapper around a meta data value which represents a restored value. """

    def __init__(self, persistedValue, expectedType=None):
        """ 
        @param persistedValue: The persistence representation of a property value.
        @type persistedValue: C{basestring}
        @param expectedType: Type to which the value should be converted. Type 
            comparison is performed using built-in C{type} function.
        @type expectedType: C{object}
        
        @raise PersistenceError: The persistence value is no string.
        """
        
        if not isinstance(persistedValue, basestring):
            raise PersistenceError("No valid persistence string has been provided. %s" % str(persistedValue))
        self._expectedType = expectedType
        self._persistedValue = persistedValue
        self._conversionFunctions = list()
        self._conversionFunctions.append(self._convertToBool)
        self._conversionFunctions.append(self._convertToDecimal)
        self._conversionFunctions.append(self._convertToDatetime)
        self._conversionFunctions.append(self._convertToList)
        self._conversionFunctions.append(self._convertToDict)
        self._conversionFunctions.append(self._convertToUnicode)
        
    @property
    def persistedValue(self):
        return self._persistedValue
    
    @property
    def value(self):
        """ Returns the most probable value. """
        
        representations = self.guessRepresentation()
        if not self._expectedType is None:
            for representation in representations:
                if type(representation) == self._expectedType:
                    return representation
        return representations[0]
        
    def guessRepresentation(self):
        """ 
        Tries to convert the retrieved value to the expected type.
        If the conversion fails an empty list is returned.
        
        @return: List of possible value representations.
        @rtype: C{list} of C{object}
        """
        
        result = list()
        if _NONE_PERSISTENCE_REPRESENTATION == self._persistedValue:
            result.append(None)
        else:
            convertedValue = None
            for conversionFunction in self._conversionFunctions:
                convertedValue = conversionFunction(self._persistedValue)
                if not convertedValue is None:
                    result.append(convertedValue)
        return result
        
    def _convertToList(self, value):
        result = None
        stringList = re.split("(?<!\\\\);", value) # does not split at: \;
        if len(stringList) > 0 and stringList[0] != value:
            typedList = list()
            for item in stringList:
                if item == _NONE_PERSISTENCE_REPRESENTATION:
                    convertedValue = None
                else:
                    for conversionFunction in self._conversionFunctions:
                        convertedValue = conversionFunction(item)
                        if not convertedValue is None:
                            break
                    typedList.append(convertedValue)
                    result = typedList
        elif value == _EMPTY_LIST_REPRESENTATION:
            result = list()
        return result
    
    @staticmethod
    def _convertToDict(value):
        try:
            dictValue = json_format.convertFromPersistenceFormat(value)
        except PersistenceError:
            dictValue = None
        else:
            if not isinstance(dictValue, dict):
                dictValue = None
        return dictValue

    @staticmethod
    def _convertToUnicode(value):
        if _ESCAPED_LIST_SEPARATOR in value:
            value = value.replace(_ESCAPED_LIST_SEPARATOR, _LIST_SEPARATOR)
        elif value == _ESCAPED_EMPTY_LIST:
            value = _EMPTY_LIST_REPRESENTATION
        return value
    
    @staticmethod
    def _convertToBool(value):
        try:
            intValue = int(value)
        except (ValueError, TypeError):
            return None
        else:
            if intValue in [0, 1]:
                return bool(intValue)
    
    @staticmethod
    def _convertToDecimal(value):
        try:
            value = decimal.Decimal(value)
        except (decimal.InvalidOperation, ValueError, TypeError):
            value = None
        return value
        
    @staticmethod
    def _convertToDatetime(value):
        return datetime_util.convertToDatetime(value)
    
    def __cmp__(self, other):
        return cmp(self.persistedValue, other)
        
    def __hash__(self):
        return hash(self.persistedValue)
    
    def __repr__(self):
        return repr(self.value)

    
def getPersistenceRepresentation(value):
    """ 
    Converts the given value to the persistence string format.
    
    @param value: Value to persist.
    @type value: C{object}

    @return: Persistence representation.
    @rtype: C{basestring}
    
    @raise PersistenceError: Indicating unsupported value type or
        problems during conversion.
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
                                     datetime.datetime: _convertFromDatetime,
                                     dict: _convertFromDict} 
        valueType = type(value)
        if valueType in typeConversionFunctionMap:
            return typeConversionFunctionMap[valueType](value)
        else:
            raise PersistenceError("Persistence support for values of type " \
                                   + "'%s' is not available." % str(valueType))


def _convertFromDatetime(value):
    return datetime_util.convertToIso8601(value)


def _convertFromDecimal(value):
    return unicode(value)
    
    
def _convertFromBool(value):
    return unicode(int(value))


def _convertFromList(value):
    listAsString = ""
    for item in value:
        convertedItem = getPersistenceRepresentation(item)
        listAsString += convertedItem + _LIST_SEPARATOR
    if len(listAsString) == 0:
        listAsString = _EMPTY_LIST_REPRESENTATION
    return listAsString


def _convertFromDict(value):
    return json_format.convertToPersistenceFormat(value)


def _convertFromUnicode(value):
    if not isinstance(value, unicode):
        encoding = sys.getdefaultencoding() or "ascii"
        try:
            value = unicode(value, encoding)
        except UnicodeError, error:
            errorMessage = "Problem during string conversion: '%s'" \
                           % str(error)
            raise PersistenceError(errorMessage)
    value = _escapeSpecialSequence(value)
    return value


def _escapeSpecialSequence(value):
    if _LIST_SEPARATOR in value:
        value = value.replace(_LIST_SEPARATOR, _ESCAPED_LIST_SEPARATOR)
    elif value == _EMPTY_LIST_REPRESENTATION:
        value = _ESCAPED_EMPTY_LIST
    return value
