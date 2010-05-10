# pylint: disable-msg=W0142
# W0142: *,** magic is used to simplify creation of PropertyType in factory method.
#
# Created: 09.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: property_type.py 4419 2010-01-28 16:08:09Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements different property types.
"""


from datetime import datetime
from decimal import Decimal

from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.validators import type_validators
from datafinder.core.error import ConfigurationError


__version__ = "$LastChangedRevision: 4419 $"


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


_propertyNameClassMap = {StringType.NAME: StringType,
                         BooleanType.NAME: BooleanType,
                         NumberType.NAME: NumberType,
                         DatetimeType.NAME: DatetimeType,
                         ListType.NAME: ListType,
                         AnyType.NAME: AnyType}
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
                               constants.STRING_TYPE: unicode}
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
