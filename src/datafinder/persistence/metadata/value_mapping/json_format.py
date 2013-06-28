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
Handles encoding/decoding of Python objects to the JSON format.
This module is intended to replace the L{Custom Format
<datafinder.persistence.metadata.value_mapping.custom_format>}.

It encodes just like the standard JSON decoder. In addition it handles:
- L{Decimal<decimal.Decimal>} objects => float string
- L{datetime<datetime.datetime>} => ISO8601 formatted date time string.
The datetime object should be given in local time and is converted to UTC time.

It decodes just like the standard JSON decoder with two exceptions:
- Encoded C{float}, C{int} values => L{Decimal<decimal.Decimal>}
- Date time strings in ISO8601 format => L{datetime<datetime.datetime>} 
The date time string should be in UTC time and is converted to local time.
    
@see: L{json.dump<json.dump>} and @see: L{json.load<json.load>} for handling
of standard Python types/objects.
"""


import datetime
import decimal
import json

from datafinder.persistence.common import datetime_util
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


class MetadataValue(object):
    """ Just a very small wrapper to keep the interface. 
    If the custom format is removed, the class gets obsolete.
    """
    
    def __init__(self, value):
        self.persistedValue = value
        self.value = value
    
    def guessRepresentation(self):
        """ Here we always have the right representation. """
        
        return [self.value]
    
    def __cmp__(self, other):
        try:
            return cmp(self.value, other.value)
        except AttributeError:
            return -1
    
    def __hash__(self):
        return hash(self.value)
    
    def __repr__(self):
        return repr(self.value)


def convertToPersistenceFormat(obj):
    """ Encodes Python objects in a JSON string.
    
    @raise PersistenceError: If encoding fails.
    """
    try:
        return json.dumps(obj, default=_jsonEncoder)
    except ValueError, error:
        raise PersistenceError(str(error))


def _jsonEncoder(obj):
    """ Encodes C{decimal.Decimal} and C{datetime.datetime} objects. """
    
    if isinstance(obj, datetime.datetime):
        obj = datetime_util.convertToIso8601(obj)
    elif isinstance(obj, decimal.Decimal):
        decimalTuple = obj.as_tuple()
        if decimalTuple.exponent == 0:
            obj = int(obj)
        else:
            obj = float(obj)
    return obj

 
def convertFromPersistenceFormat(jsonString):
    """ Decodes a JSON string to the corresponding Python object.
    
    @raise PersistenceError: If decoding fails.
    """
    
    try:
        return json.loads(jsonString, parse_float=decimal.Decimal, 
                          parse_int=decimal.Decimal, 
                          cls=_DatetimeJsonDecoder)
    except (ValueError, TypeError), error:
        raise PersistenceError(str(error))


class _DatetimeObjectHook(object):
    """ Object hook for JSON decoders. It ensures that date time strings 
    (ISO8601 format) are decoded to C{datetime.datetime} instances in 
    local time. It also handles strings in nested C{list} and C{dict}. """

    def __call__(self, value, handleDict=True):
        newValue = value
        if isinstance(value, basestring):
            newValue = self._handleString(value)
        elif isinstance(value, list):
            newValue = self._handleList(value)
        elif isinstance(value, dict) and handleDict:
            newValue = self._handleDict(value)
        return newValue
    
    def _handleDict(self, dct):
        for key, value in dct.iteritems():
            dct[key] = self.__call__(value)
        return dct
    
    def _handleList(self, values):
        result = list()
        for value in values:
            result.append(self.__call__(value))
        return result
            
    @staticmethod
    def _handleString(datetimeString):
        try:
            return datetime_util.convertFromIso8601(datetimeString)
        except ValueError:
            return datetimeString


class _DatetimeJsonDecoder(json.JSONDecoder):
    """ Custom JSON decoder which ensures that date time strings 
    (ISO8601 format) are decoded to C{datetime.datetime} instances in 
    local time. It also handles nested strings within C{list} and C{dict}. """
    
    # Handles date time string decoding
    _datetimeDecoder = _DatetimeObjectHook()
        
    def decode(self, s, _w=None):
        # pylint: disable=C0103
        # Just an assignment to an attribute of the inherited class.
        # Other coding style.
        
        self.object_hook = self._datetimeDecoder
        result = json.JSONDecoder.decode(self, s)
        return self._datetimeDecoder(result, False)
