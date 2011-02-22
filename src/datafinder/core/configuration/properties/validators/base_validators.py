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


""" 
This module defines a basic set of validation functions / classes for value verification.
"""


import re
from decimal import Decimal

from datafinder.core.configuration.properties.validators.error import ValidationError


__version__ = "$Revision-Id:$" 

    
class IsInRange(object):
    """ 
    Checks whether a given value is in a specific range. 
    The requirement is that minimum, maximum and the value are comparable (<, > support).
    """
    
    def __init__(self, minValue=None, maxValue=None):
        """ 
        Constructor. 
        
        @param minValue: The lower bound.
        @type minValue: C{object}
        @param maxValue: The upper bound.
        @type minValue: C{object}
        """
        
        self.minValue = minValue
        self.maxValue = maxValue
              
    def __call__(self, value):
        """ 
        Implements the validation.
        
        @param value: The value to check.
        @type value: C{object}
        """
        
        if not self.minValue is None and value < self.minValue:
            raise ValidationError("The provided value is < than the defined minimum.")
        if not self.maxValue is None and value > self.maxValue:
            raise ValidationError("The provided value is > then the defined maximum.")


class IsDecimalInRange(object):
    """ 
    Class for checking boundaries of decimal values.
    """
    
    def __init__(self, minValue, maxValue):
        """ 
        Constructor. 
        
        @param minValue: The lower bound.
        @type minValue: C{decimal.Decimal}
        @param maxValue: The upper bound.
        @type maxValue: C{decimal.Decimal}
        """
        
        self.minValue = minValue
        self.maxValue = maxValue
        self.__inRangeValidator = IsInRange()
        
    def __call__(self, value):
        """ 
        Implements validation of the value.
        The value is converted to C{decimal.Decimal} before performing the range check.
        """
        
        if isinstance(value, float):
            value = Decimal(str(value))
        self.__inRangeValidator.minValue = self.minValue
        self.__inRangeValidator.maxValue = self.maxValue
        self.__inRangeValidator(value)
        
        
class IsLengthInRange(object):
    """ 
    Checks whether the length of a given value is in a specific range. 
    The values that can be checked with this validation class have to support
    the "len" function.
    """
    
    def __init__(self, minLength=None, maxLength=None):
        """ 
        Constructor. 
        
        @param minLength: The lower bound.
        @type minLength: C{int}
        @param maxLength: The upper bound.
        @type maxLength: C{int}
        """
        
        self.minLength = minLength
        self.maxLength = maxLength
        self.__inRangeValidator = IsInRange()
        
    def __call__(self, value):
        """ 
        Implements the validation.
        
        @param value: The value to check.
        @type value: C{object}
        """
        
        self.__inRangeValidator.minValue = self.minLength
        self.__inRangeValidator.maxValue = self.maxLength
        self.__inRangeValidator(len(value))


class IsNumberOfDecimalPlacesInRange(object):
    """ 
    Checks whether the number of decimal places which was specified 
    is in a specific range. 
    """
    
    def __init__(self, minNumberOfDecimalPlaces=None, maxNumberOfDecimalPlaces=None):
        """ 
        Constructor. 
        
        @param minNumberOfDecimalPlaces: The lower bound.
        @type minNumberOfDecimalPlaces: C{int}
        @param maxNumberOfDecimalPlaces: The upper bound.
        @type maxNumberOfDecimalPlaces: C{int}
        """
        
        self.minNumberOfDecimalPlaces = minNumberOfDecimalPlaces
        self.maxNumberOfDecimalPlaces = maxNumberOfDecimalPlaces
        self.__inRangeValidator = IsInRange()
        
    def __call__(self, value):
        """ 
        Implements the validation.
        
        @param value: The value to check.
        @type value: L{Decimal<decimal.Decimal>}, C{float}, C{int}
        """
        
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        # calculate specified number of decimal places
        tupleRepr = value.as_tuple() # represents the numeric value as (sign, given digits, exponent)
        if tupleRepr[2] >= 0: # positive or zero exponent indicates zero decimal places
            decimalPlaces = 0
        else: # negative exponent indicates a numeric value with decimal places
            absolutExponent = abs(tupleRepr[2])
            possibleNumberOfDecimalPlaces = len(tupleRepr[1])
            if possibleNumberOfDecimalPlaces > absolutExponent:
                decimalPlaces = absolutExponent
            else:
                decimalPlaces = possibleNumberOfDecimalPlaces
                
        # check the calculate number of specified decimal places
        self.__inRangeValidator.minValue = self.minNumberOfDecimalPlaces
        self.__inRangeValidator.maxValue = self.maxNumberOfDecimalPlaces
        self.__inRangeValidator(decimalPlaces)
        

class AreOptionsMatched(object):
    """ 
    Checks whether a value is taken from a certain list of options.
    The check is performed with the comparison operator.
    """
    
    def __init__(self, options, optionsMandatory=True):
        """
        Constructor.
        
        @param options: List of options that the checked value have to be taken from.
        @type options: C{list}
        """
        
        self.options = options
        self.optionsMandatory = optionsMandatory
        
    def __call__(self, value):
        """
        Implements the validation.
        
        @param value: Value to check.
        @type value: Depends on the concrete use case.
        """
        
        if self.optionsMandatory:
            if not value in self.options:
                raise ValidationError("The item is not taken from the specified options.") 


class AreTypesMatched(object):
    """
    Checks whether the value is from one of the allowed types.
    
    @note: The type checking is performed with the help of C{isinstance}.
    """
    
    def __init__(self, valueTypes, exactMatch=True):
        """
        Constructor.
        
        @param valueTypes: List of class object.
        @type valueTypes: C{list} of class objects.
        @param exactMatch: If C{True} type checking is performed by using C{type}
                           otherwise C{isinstance} is used.
        @type exactMatch: C{bool}
        """
        
        self.valueTypes = valueTypes
        self.exactMatch = exactMatch
        
    def __call__(self, value):
        """ 
        Implements the check. 
        
        @param value: Class object.
        """
        
        representationTypeFound = False
        for valueType in self.valueTypes:
            if self.exactMatch:
                if type(value) == valueType:
                    representationTypeFound = True
                    break
            else:
                if isinstance(value, valueType):
                    representationTypeFound = True
                    break
        if not representationTypeFound:
            raise ValidationError("The given value has not the required type.")


class IsPatternMatched(object):
    """
    Checks whether the value conforms to specified string pattern.
    """
    
    def __init__(self, pattern):
        """
        Constructor.
        
        @param regularExpression: Convenient regular expression pattern.
        @type regularExpression: C{unicode}
        """
        
        self.pattern = pattern
        
    def __call__(self, value):
        """ Implements the check. """
        
        try:
            result = re.match(self.pattern, value)
        except (re.error, TypeError):
            raise ValidationError("The pattern %s is not a valid regular expression." % self.pattern)
        if result is None:
            raise ValidationError("The given value does not match the defined pattern.")


class IsEachValueUnique(object):
    """ Checks whether every value of a given list appears only once. """
    
    @staticmethod
    def __call__(value):
        """ 
        Checks whether every value of a given list appears only once.
        The check is performed with the comparison operator ("==").
        
        @param value: List of items to check.
        @type value: C{list}
        """
        
        tmpDict = dict.fromkeys(value) # Removes duplicated entries
        if len(tmpDict) != len(value):
            raise ValidationError("The values in the given list are not unique.")
        
        
class IsBinaryStringDecodable(object):
    """
    Checks whether the given string can be converted to unicode by 
    using the default encoding.
    """
        
    @staticmethod
    def __call__(value):
        """
        Checks whether the given string can be converted to unicode by 
        using the default encoding.
        
        @param value: String to check.
        @type value: C{basestring}
        """
        
        if isinstance(value, basestring):
            if isinstance(value, str):
                try:
                    unicode(value)
                except UnicodeEncodeError:
                    errorMessage = "The given binary string cannot be converted to unicode using the default encoding." + \
                                   "Please convert the string to unicode before."
                    raise ValidationError(errorMessage)

            
class ForEach(object):
    """
    This class performs a given check for each value in a sequence.
    """
    
    def __init__(self, validator):
        """
        Constructor.
        
        @param validator: A callable which takes a certain value as input.
                          Valid callables are defined in this module.
        @type: C{callable}
        """
        
        self.validator = validator
        
    def __call__(self, value):
        """
        Calls the validator for each item of the given sequence.
        
        @param value: A sequence.
        """
        
        for item in value:
            self.validator(item)


class OrValidator(object):
    """
    This class performs given checks on a value until one of the checks succeeds.
    """
    
    def __init__(self, validators):
        """
        Constructor.
        
        @param validator: A list callable which takes a certain value as input.
                          Valid callables are defined in this module.
        @type: C{list} of C{callable}
        """
        
        self.validators = validators
        
    def __call__(self, value):
        """
        Calls every check until a one of them succeeds.
        
        @param value: Any value.
        """
        
        if value == 1:
            pass
        for validator in self.validators:
            try:
                validator(value)
                allValidatorsFailed = False
                break
            except ValidationError:
                allValidatorsFailed = True
        if allValidatorsFailed:
            raise ValidationError("Every defined validation rule failed for the given value.")


class AndValidator(object):
    """
    Succeeds when all configured checks succeed as well.
    """
    
    def __init__(self, validators):
        """
        Constructor.
        
        @param validator: A list of callables which takes a certain value as input.
                          Valid callables are defined in this module.
        @type: C{list} of C{callable}
        """
        
        self.validators = validators
        
    def __call__(self, value):
        """
        Calls all checks on the given value.
        
        @param value: Any value.
        """
        
        for validator in self.validators:
            validator(value)
      
        
class ObjectTypeValidator(object):
    """ 
    Checks whether a given value is a representation of a predefined object.
    """ 

    def __call__(self, value):
        """ 
        Calls all checks on the given value.
        
        @param value: A dict representing an object. 
        """

        if len(self.__dict__) == len(value):
            try:
                for key in self.__dict__:
                    if isinstance(self.__dict__[key], type(ObjectTypeValidator())) and isinstance(value[key], type(dict())):
                        self.__dict__[key](value[key])
                    elif type(self.__dict__[key]) == type(value[key]):
                        pass
                    else:
                        raise ValidationError("The given object does not match the defined object.")
            except KeyError:
                raise ValidationError("The given object does not match the defined object.")
            except TypeError:
                raise ValidationError("The given object does not match the defined object.")
        else:
            raise ValidationError("The given object does not match the defined object.")
