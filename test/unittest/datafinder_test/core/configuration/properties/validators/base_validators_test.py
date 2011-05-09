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
from datafinder_test.mocks import SimpleMock


""" 
Tests for the validators module.
"""


import unicodedata
import unittest
from decimal import Decimal
        
from datafinder.core.configuration.properties.validators import base_validators as validators


__version__ = "$Revision-Id:$" 


class IsInRangeTestCase(unittest.TestCase):
    """
    Tests cases for the IsInRange class.
    """
        
    def setUp(self):
        """ Defines the range for this test case. """
        
        self.minValue = 12
        self.maxValue = 2009
        
    def testValidValues(self):
        """ Tests the behavior for values in the defined range. """
        
        # upper and lower boundary
        inRangeValidator = validators.IsInRange(self.minValue, self.maxValue)
        inRangeValidator(300)
        inRangeValidator(self.minValue)
        inRangeValidator(self.maxValue)
        
        # upper boundary
        inRangeValidator = validators.IsInRange(maxValue=self.maxValue)
        inRangeValidator(300)
        inRangeValidator(self.minValue)
        inRangeValidator(self.maxValue)
        
        # lower boundary
        inRangeValidator = validators.IsInRange(minValue=self.minValue)
        inRangeValidator(300)
        inRangeValidator(self.minValue)
        inRangeValidator(self.maxValue)
        
        # no boundary
        inRangeValidator = validators.IsInRange()
        inRangeValidator(300)
        inRangeValidator(self.minValue)
        inRangeValidator(self.maxValue)
         
    def testInvalidValues(self):
        """ Tests the behavior for values outside the defined range. """
        
        # lower and upper boundary
        inRangeValidator = validators.IsInRange(self.minValue, self.maxValue)
        self.assertRaises(ValueError, inRangeValidator, self.maxValue + 1)
        self.assertRaises(ValueError, inRangeValidator, self.minValue - 1)
        self.assertRaises(ValueError, inRangeValidator, 30009)
        self.assertRaises(ValueError, inRangeValidator, -110)
        
        # upper boundary
        inRangeValidator = validators.IsInRange(maxValue=self.maxValue)
        self.assertRaises(ValueError, inRangeValidator, self.maxValue + 1)
        self.assertRaises(ValueError, inRangeValidator, 30009)
        
        # lower boundary
        inRangeValidator = validators.IsInRange(minValue=self.minValue)
        self.assertRaises(ValueError, inRangeValidator, self.minValue - 1)
        self.assertRaises(ValueError, inRangeValidator, -110)        
            
            
class IsLengthInRangeTestCase(unittest.TestCase):
    """
    Tests cases for the IsLengthInRange class.
    """
        
    def setUp(self):
        """ Defines the range for this test case. """
        
        self.minValue = 2
        self.maxValue = 7
        self.valueWithExactMinLength = "aa"
        self.valueWithExactMaxLength = "aaaaaaa"
        self.valueInBoundries = "aaaaa"
        self.valueLessMinLength = "a"
        self.valueMoreMaxLength = "aaaaaaaa"
        
    def testValidValues(self):
        """ Tests the behavior for values with a length in the defined range. """
        
        # upper and lower boundary
        lengthRangeValidator = validators.IsLengthInRange(self.minValue, self.maxValue)
        lengthRangeValidator(self.valueWithExactMinLength)
        lengthRangeValidator(self.valueInBoundries)
        lengthRangeValidator(self.valueWithExactMaxLength)
        
        # upper boundary
        lengthRangeValidator = validators.IsLengthInRange(maxLength=self.maxValue)
        lengthRangeValidator(self.valueWithExactMinLength)
        lengthRangeValidator(self.valueInBoundries)
        lengthRangeValidator(self.valueWithExactMaxLength)
        
        # lower boundary
        lengthRangeValidator = validators.IsLengthInRange(minLength=self.minValue)
        lengthRangeValidator(self.valueWithExactMinLength)
        lengthRangeValidator(self.valueInBoundries)
        lengthRangeValidator(self.valueWithExactMaxLength)
        
        # no boundary
        lengthRangeValidator = validators.IsLengthInRange()
        lengthRangeValidator(self.valueWithExactMinLength)
        lengthRangeValidator(self.valueInBoundries)
        lengthRangeValidator(self.valueWithExactMaxLength)
         
    def testInvalidValues(self):
        """ Tests the behavior for values with a length outside the defined range. """
        
        # lower and upper boundary
        lengthRangeValidator = validators.IsLengthInRange(self.minValue, self.maxValue)
        self.assertRaises(ValueError, lengthRangeValidator, self.valueLessMinLength)
        self.assertRaises(ValueError, lengthRangeValidator, self.valueMoreMaxLength)
        
        # upper boundary
        lengthRangeValidator = validators.IsLengthInRange(maxLength=self.maxValue)
        self.assertRaises(ValueError, lengthRangeValidator, self.valueMoreMaxLength)
        
        # lower boundary
        lengthRangeValidator = validators.IsLengthInRange(minLength=self.minValue)
        self.assertRaises(ValueError, lengthRangeValidator, self.valueLessMinLength)


class IsNumberOfDecimalPlacesInRangeTestCase(unittest.TestCase):
        
    def setUp(self):
        """ Setups the validator and defines some comparison values. """
        
        self.minValue = 0
        self.maxValue = 7
        self.valueWithExactMinDecimalPlaces = Decimal("-1234")
        self.valueWithExactMaxDecimalPlaces = Decimal("-1234.4556346")
        self.valueInBoundries = Decimal("-1.23e-04")
        self.valueLessMinDecimalPlaces = Decimal("-1234.4")
        self.valueMoreMaxDecimalPlaces = Decimal("-1234.44567890")
        
    def testValidValues(self):
        # upper and lower boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(
            self.minValue, self.maxValue)
        decimalPlacesInRangeValidator(self.valueWithExactMinDecimalPlaces)
        decimalPlacesInRangeValidator(self.valueInBoundries)
        decimalPlacesInRangeValidator(self.valueWithExactMaxDecimalPlaces)
        
        # upper boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(
            maxNumberOfDecimalPlaces=self.maxValue)
        decimalPlacesInRangeValidator(self.valueWithExactMinDecimalPlaces)
        decimalPlacesInRangeValidator(self.valueInBoundries)
        decimalPlacesInRangeValidator(self.valueWithExactMaxDecimalPlaces)
        
        # lower boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(
            minNumberOfDecimalPlaces=self.minValue)
        decimalPlacesInRangeValidator(self.valueWithExactMinDecimalPlaces)
        decimalPlacesInRangeValidator(self.valueInBoundries)
        decimalPlacesInRangeValidator(self.valueWithExactMaxDecimalPlaces)
        
        # no boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange()
        decimalPlacesInRangeValidator(self.valueWithExactMinDecimalPlaces)
        decimalPlacesInRangeValidator(self.valueInBoundries)
        decimalPlacesInRangeValidator(self.valueWithExactMaxDecimalPlaces)
        
    def testInvalidValues(self):
        # lower and upper boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(
            self.minValue, self.maxValue)
        self.assertRaises(ValueError, decimalPlacesInRangeValidator, self.valueMoreMaxDecimalPlaces)
        
        # upper boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(
            maxNumberOfDecimalPlaces=self.maxValue)
        self.assertRaises(ValueError, decimalPlacesInRangeValidator, self.valueMoreMaxDecimalPlaces)


class IsDecimalInRangeTestCase(unittest.TestCase):
    
    def setUp(self):
        self._validator = validators.IsDecimalInRange(2.0, 4)
        
    def testValidValues(self):
        self._validator(3)
        self._validator(2)
        self._validator(4)
        
        self._validator(3.2)
        self._validator(Decimal(3))
        
    def testInvalidValues(self):
        self.assertRaises(ValueError, self._validator, 1.2)
        self.assertRaises(ValueError, self._validator, Decimal(0))
        self.assertRaises(ValueError, self._validator, 5)
        
        # non-numerics
        self.assertRaises(ValueError, self._validator, None)
        self.assertRaises(ValueError, self._validator, "")
        

class AreOptionsMatchedTestCase(unittest.TestCase):
    
    def setUp(self):
        self.areOptionsMatchedValidator = validators.AreOptionsMatched(["hallo", True, 123])
        
    def testValidValues(self):
        self.areOptionsMatchedValidator(True)
        self.areOptionsMatchedValidator(123)
        self.areOptionsMatchedValidator("hallo")
        
    def testInvalidValues(self):
        self.assertRaises(ValueError, self.areOptionsMatchedValidator, [True])
        self.assertRaises(ValueError, self.areOptionsMatchedValidator, 1235)
        self.assertRaises(ValueError, self.areOptionsMatchedValidator, None)
        

class AreTypesMatchedTestCase(unittest.TestCase):
    
    def setUp(self):
        self.exactValidator = validators.AreTypesMatched([unicode])
        self.isinstanceValidator = validators.AreTypesMatched([basestring], 
                                                              exactMatch=False)
        
    def testValues(self):
        """ Shows valid and invalid values for exact / inexact type matching. """
        
        self.exactValidator(u"ahaha")
        self.exactValidator(u"9980")
        self.assertRaises(ValueError, self.exactValidator, [False])
        self.assertRaises(ValueError, self.exactValidator, 1235)
        self.assertRaises(ValueError, self.exactValidator, "halo")

        self.isinstanceValidator(u"ahaha")
        self.isinstanceValidator("9980")
        self.assertRaises(ValueError, self.isinstanceValidator, [False])
        self.assertRaises(ValueError, self.isinstanceValidator, 1235)


class IsPatternMatchedTestCase(unittest.TestCase):
    
    def setUp(self):
        self.isPatternMatchedValidator = validators.IsPatternMatched("T..t")
        
    def testValidValues(self):
        self.isPatternMatchedValidator("Test")
        self.isPatternMatchedValidator("Taat")
        
    def testInvalidValues(self):
        self.assertRaises(ValueError, self.isPatternMatchedValidator, "Hallo")
        self.assertRaises(ValueError, self.isPatternMatchedValidator, "est")
        
    def testInvalidPattern(self):
        self.isPatternMatchedValidator.pattern = "?**???"
        self.assertRaises(ValueError, self.isPatternMatchedValidator, "Hallo")
        
        
class IsEachValueUniqueTestCase(unittest.TestCase):

    def setUp(self):
        self.isEachValueUnique = validators.IsEachValueUnique()
        
    def testValidValues(self):
        self.isEachValueUnique([1, 2, 3, 4, 5])
        self.isEachValueUnique(["a", "b", "c", "d"])
        
    def testInvalidValues(self):
        self.assertRaises(ValueError, self.isEachValueUnique, [1, 2, 3, 3, 5])
        self.assertRaises(ValueError, self.isEachValueUnique, ["b", "b", "c", "d"])


class ForEachTestCase(unittest.TestCase):
    
    def setUp(self):
        self.forEachValidator = validators.ForEach(validators.IsEachValueUnique())
        
    def testValidValues(self):
        self.forEachValidator(([1, 2, 3, 4], [1]))
        self.forEachValidator([[1, 2, 3, 4]])
        
    def testInvalidValues(self):
        self.assertRaises(ValueError, self.forEachValidator, ([1, 3, 3, 4], [1]))
        self.assertRaises(ValueError, self.forEachValidator, [[1, 2, 1, 4]])


class IsBinaryStringDecodableTestCase(unittest.TestCase):
    
    def setUp(self):
        self.validator = validators.IsBinaryStringDecodable()
        
    def testValidValues(self):
        self.validator("asdsd")
        self.validator(u"asfdfer")
        
    def testInvalidValues(self):
        smallAe = unicodedata.lookup("LATIN SMALL LETTER A WITH DIAERESIS")
        smallAe = smallAe.encode("utf-8") # Make it an UTF-8 encoded binary string
        self.validator._encoding = "ascii" # Make default decoding with ASCII codec
        self.assertRaises(ValueError, self.validator, smallAe)
        
        # Non-strings
        self.assertRaises(ValueError, self.validator, None)
        self.assertRaises(ValueError, self.validator, list())


class OrTestCase(unittest.TestCase):
    
    def setUp(self):
        self.validator = validators.OrValidator(list())
        
    def testSuccessfullValidation(self):
        successValidators = [SimpleMock(), SimpleMock()]
        self.validator.validators = successValidators
        self.validator("testValue")

        validatorsWithOneError = [SimpleMock(error=ValueError), SimpleMock()]
        self.validator.validators = validatorsWithOneError
        self.validator("testValue")

    def testValidationError(self):
        validatorsWithError = [SimpleMock(error=ValueError), 
                               SimpleMock(error=ValueError)]
        self.validator.validators = validatorsWithError
        self.assertRaises(ValueError, self.validator, "testValue")


class AndTestCase(unittest.TestCase):
    
    def setUp(self):
        self.validator = validators.AndValidator(list())
        
    def testSuccessfullValidation(self):
        successValidators = [SimpleMock(), SimpleMock()]
        self.validator.validators = successValidators
        self.validator("testValue")
        
    def testValidationError(self):
        validatorWithOneError = [SimpleMock(error=ValueError), SimpleMock()]
        self.validator.validators = validatorWithOneError
        self.assertRaises(ValueError, self.validator, "testValue")

        validatorWithError = [SimpleMock(error=ValueError), 
                              SimpleMock(error=ValueError)]
        self.validator.validators = validatorWithError
        self.assertRaises(ValueError, self.validator, "testValue")
    