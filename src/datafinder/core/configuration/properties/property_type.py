# pylint: disable=W0142
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
from types import ObjectType


""" 
Implements different property types.
"""


from datetime import datetime
from decimal import Decimal

from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.validators import type_validators
from datafinder.core.error import ConfigurationError


__version__ = "$Revision-Id:$" 


class StringType(object):
    """ Represents string values. """

    NAME = constants.STRING_TYPE

    def __init__(self, minimum=None, maximum=None, pattern=None, options=None, optionsMandatory=None):
        """
        Constructor.
        
        @param minimum: Minimum length of the string.
        @type minimum: C{int}
        @param maximum: Maximum length of the string.
        @type maximum: C{int}
        @param pattern: Regular expression pattern.
        @type pattern: C{str}
        @param options: List of options the value has to be taken from.
        @type options: C{list} of C{unicode}
        """
        
        self.restrictions = dict()
        self.restrictions[constants.MINIMUM_LENGTH] = minimum
        self.restrictions[constants.MAXIMUM_LENGTH] = maximum
        self.restrictions[constants.PATTERN] = pattern
        self.restrictions[constants.OPTIONS] = options
        self.restrictions[constants.OPTIONS_MANDATORY] = optionsMandatory
        self.validator = type_validators.StringValidator(minimum, maximum, pattern, options, optionsMandatory)


class BooleanType(object):
    """ Represents a boolean values. """

    NAME = constants.BOOLEAN_TYPE

    def __init__(self):
        """
        Constructor.
        
        @param minimum: Minimum value. 
        @type minimum: C{decimal.Decimal}
        @param maximum: Maximum value.
        @type maximum: C{decimal.Decimal}
        @param options: List of options the value has to be taken from.
        @type options: C{list} of C{decimal.Decimal}
        """
        
        self.restrictions = dict()
        self.validator = type_validators.BooleanValidator()


class NumberType(object):
    """ Represents numeric values. """
    
    NAME = constants.NUMBER_TYPE

    def __init__(self, minimum=None, maximum=None, minDecimalPlaces=None, 
                 maxDecimalPlaces=None, options=None, optionsMandatory=None):
        """
        Constructor.
        
        @param minimum: Minimum value. 
        @type minimum: C{decimal.Decimal}
        @param maximum: Maximum value.
        @type maximum: C{decimal.Decimal}
        @param options: List of options the value has to be taken from.
        @type options: C{list} of C{decimal.Decimal}
        """
        
        self.restrictions = dict()
        self.restrictions[constants.MINIMUM_VALUE] = minimum
        self.restrictions[constants.MAXIMUM_VALUE] = maximum
        self.restrictions[constants.MINIMUM_NUMBER_OF_DECIMAL_PLACES] = minDecimalPlaces
        self.restrictions[constants.MAXIMUM_NUMBER_OF_DECIMAL_PLACES] = maxDecimalPlaces
        self.restrictions[constants.OPTIONS] = options
        self.restrictions[constants.OPTIONS_MANDATORY] = optionsMandatory
        self.validator = type_validators.NumberValidator(minimum, maximum, minDecimalPlaces, maxDecimalPlaces, options, optionsMandatory)


class DatetimeType(object):
    """ Represents date and time values. """
    
    NAME = constants.DATETIME_TYPE

    def __init__(self, minimum=None, maximum=None, options=None, optionsMandatory=None):
        """
        Constructor.
        
        @param minimum: Minimum length of the list.
        @type minimum: C{int}
        @param maximum: Maximum length of the list.
        @type maximum: C{int}
        @param options: List of options the value has to be taken from.
        @type options: C{list} of C{datetime}
        """
        
        self.restrictions = dict()
        self.restrictions[constants.MINIMUM_VALUE] = minimum
        self.restrictions[constants.MAXIMUM_VALUE] = maximum
        self.restrictions[constants.OPTIONS] = options
        self.restrictions[constants.OPTIONS_MANDATORY] = optionsMandatory
        self.validator = type_validators.DatetimeValidator(minimum, maximum, options, optionsMandatory)


class ListType(object):
    """ Represents list of primitive values. """
    
    NAME = constants.LIST_TYPE

    def __init__(self, minimum=None, maximum=None):
        """
        Constructor.
        
        @param minimum: Minimum length of the list.
        @type minimum: C{int}
        @param maximum: Maximum length of the list.
        @type maximum: C{int}
        @type allowed: Optional list of sub 
        """
        
        self.restrictions = dict()
        self.restrictions[constants.MINIMUM_VALUE] = minimum
        self.restrictions[constants.MAXIMUM_VALUE] = maximum
        self._allowedSubtypes = list()
        self._allowedSubtypes.append(StringType())
        self._allowedSubtypes.append(NumberType())
        self._allowedSubtypes.append(BooleanType())
        self._allowedSubtypes.append(DatetimeType())
        subValidators = list()
        for subtype in self._allowedSubtypes:
            subValidators.append(subtype.validator)
        self.validator = type_validators.ListValidator(minimum, maximum, subValidators)


class AnyType(object):
    """ Represents an unspecific property type. """
    
    NAME = constants.ANY_TYPE
    
    def __init__(self):
        """ Constructor. """
        
        self.restrictions = dict()
        self.validator = type_validators.ArbitaryValidator()
        
        
class ObjectType(object):
    """ Represents a object values. """

    NAME = constants.OBJECT_TYPE

    def __init__(self, modelIdentifier):
        """
        Constructor.
        
        @param restrictions: Dict of restrictions the object has to be taken from.
        @type restrictions: C{dict}
        """
        
        self.restrictions = dict()
        
        self._modulIdentifier = modelIdentifier[:modelIdentifier.rfind(".")]
        self._classIdentifier = modelIdentifier[modelIdentifier.rfind(".")+1:]
        self._model = self._importModel(self._modulIdentifier, self._classIdentifier)
        self.validator = self._model()
        
    def _importModel(self, fromName, fromList=None, globals={}, locals={}):
        """
        An easy wrapper around ``__import__``.

        >>> import sys
        >>> sys2 = _importModel("sys")
        >>> sys is sys2
        True

        >>> import os.path
        >>> ospath2 = _importModel("os.path")
        >>> os.path is ospath2
        True

        >>> from time import time
        >>> time2 = _importModel("time", "time")
        >>> time is time2
        True

        >>> from os.path import sep
        >>> sep2 = _importModel("os.path", "sep")
        >>> sep is sep2
        True

        >>> from os import sep, pathsep
        >>> sep2, pathsep2 = _importModel("os", ["sep", "pathsep"])
        >>> sep is sep2; pathsep is pathsep2
        True
        True

        >>> _importModel("existiertnicht")
        Traceback (most recent call last):
        ...
        ImportError: No module named existiertnicht

        >>> _importModel("os", "gibtsnicht")
        Traceback (most recent call last):
        ...
        ImportError: cannot import name gibtsnicht
        """

        oneonly = False
        if isinstance(fromList, basestring):
            oneonly = True
            fromList = [fromList]

        obj = __import__(fromName, globals, locals, ["foo"])
        if fromList is None:
            return obj

        result = []
        for objectName in fromList:
            try:
                result.append(getattr(obj, objectName))
            except AttributeError:
                raise ImportError("cannot import name " + objectName)

        if oneonly:
            return result[0]
        return result


_propertyNameClassMap = {StringType.NAME: StringType,
                         BooleanType.NAME: BooleanType,
                         NumberType.NAME: NumberType,
                         DatetimeType.NAME: DatetimeType,
                         ListType.NAME: ListType,
                         AnyType.NAME: AnyType,
                         ObjectType.NAME: ObjectType}
PROPERTY_TYPE_NAMES = _propertyNameClassMap.keys()[:]


def createPropertyType(propertyTypeName, restrictions=dict()):
    """ 
    Factory method for property type creation.
    
    @param propertyTypeName: Name of the property type.
    @type propertyTypeName: C{unicode}
    @param restrictions: Map of restriction parameters and corresponding values.
    @type restrictions: C{dict} keys: C{unicode}, C{object}
    """

    if propertyTypeName in _propertyNameClassMap:
        try:
            return _propertyNameClassMap[propertyTypeName](**restrictions)
        except TypeError:
            raise ConfigurationError("Restrictions for property type '%s' are invalid." % propertyTypeName)
    else:
        raise ConfigurationError("The property type name '%s' is not supported." % propertyTypeName)


_typeConstantsPythonTypeMap = {constants.BOOLEAN_TYPE: bool,
                               constants.DATETIME_TYPE: datetime,
                               constants.LIST_TYPE: list,
                               constants.NUMBER_TYPE: Decimal,
                               constants.STRING_TYPE: unicode,
                               constants.OBJECT_TYPE: object}
_pythonTypeTypeConstantsMap = dict((value, key) for key, value in _typeConstantsPythonTypeMap.items())


def determinePropertyTypeConstant(value):
    """ 
    Helper function to determine the property type constant of the given value. 
    @see: L{constants<datafinder.core.configuration.properties.constants>} for property type constants.
    
    @param value: Python object.
    @type value: C{object}
    
    @return: Property type constant.
    @rtype: C{unicode}
    
    @raise ValueError: Indicates non-matching value.
    """
    
    try:
        displayPropertyTypeName = _pythonTypeTypeConstantsMap[type(value)]
    except KeyError:
        raise ValueError("Property value is unsupported.")
    return displayPropertyTypeName
