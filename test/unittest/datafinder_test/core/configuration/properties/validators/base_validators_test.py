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
Tests for the validators module.
"""


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
        self.assertRaises(validators.ValidationError, inRangeValidator, self.maxValue + 1)
        self.assertRaises(validators.ValidationError, inRangeValidator, self.minValue - 1)
        self.assertRaises(validators.ValidationError, inRangeValidator, 30009)
        self.assertRaises(validators.ValidationError, inRangeValidator, -110)
        
        # upper boundary
        inRangeValidator = validators.IsInRange(maxValue=self.maxValue)
        self.assertRaises(validators.ValidationError, inRangeValidator, self.maxValue + 1)
        self.assertRaises(validators.ValidationError, inRangeValidator, 30009)
        
        # lower boundary
        inRangeValidator = validators.IsInRange(minValue=self.minValue)
        self.assertRaises(validators.ValidationError, inRangeValidator, self.minValue - 1)
        self.assertRaises(validators.ValidationError, inRangeValidator, -110)        
            
            
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
        self.assertRaises(validators.ValidationError, lengthRangeValidator, self.valueLessMinLength)
        self.assertRaises(validators.ValidationError, lengthRangeValidator, self.valueMoreMaxLength)
        
        # upper boundary
        lengthRangeValidator = validators.IsLengthInRange(maxLength=self.maxValue)
        self.assertRaises(validators.ValidationError, lengthRangeValidator, self.valueMoreMaxLength)
        
        # lower boundary
        lengthRangeValidator = validators.IsLengthInRange(minLength=self.minValue)
        self.assertRaises(validators.ValidationError, lengthRangeValidator, self.valueLessMinLength)


class IsNumberOfDecimalPlacesInRangeTestCase(unittest.TestCase):
    """
    Tests cases for the IsNumberOfDecimalPlacesInRange class.
    """
        
    def setUp(self):
        """ Defines the range for the number of decimal places. """
        
        self.minValue = 2
        self.maxValue = 7
        self.valueWithExactMinDecimalPlaces = Decimal("-1234.45")
        self.valueWithExactMaxDecimalPlaces = Decimal("-1234.4556346")
        self.valueInBoundries = Decimal("-1234.4548")
        self.valueLessMinDecimalPlaces = Decimal("-1234.4")
        self.valueMoreMaxDecimalPlaces = Decimal("-1234.44567890")
        
    def testValidValues(self):
        """ Tests the behavior for decimal values with a number of decimal places in the defined range. """
        
        # upper and lower boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(self.minValue, self.maxValue)
        decimalPlacesInRangeValidator(self.valueWithExactMinDecimalPlaces)
        decimalPlacesInRangeValidator(self.valueInBoundries)
        decimalPlacesInRangeValidator(self.valueWithExactMaxDecimalPlaces)
        
        # upper boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(maxNumberOfDecimalPlaces=self.maxValue)
        decimalPlacesInRangeValidator(self.valueWithExactMinDecimalPlaces)
        decimalPlacesInRangeValidator(self.valueInBoundries)
        decimalPlacesInRangeValidator(self.valueWithExactMaxDecimalPlaces)
        
        # lower boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(minNumberOfDecimalPlaces=self.minValue)
        decimalPlacesInRangeValidator(self.valueWithExactMinDecimalPlaces)
        decimalPlacesInRangeValidator(self.valueInBoundries)
        decimalPlacesInRangeValidator(self.valueWithExactMaxDecimalPlaces)
        
        # no boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange()
        decimalPlacesInRangeValidator(self.valueWithExactMinDecimalPlaces)
        decimalPlacesInRangeValidator(self.valueInBoundries)
        decimalPlacesInRangeValidator(self.valueWithExactMaxDecimalPlaces)
         
    def testInvalidValues(self):
        """ Tests the behavior for decimal values with a number of decimal places outside the defined range. """
        
        # lower and upper boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(self.minValue, self.maxValue)
        self.assertRaises(validators.ValidationError, decimalPlacesInRangeValidator, self.valueLessMinDecimalPlaces)
        self.assertRaises(validators.ValidationError, decimalPlacesInRangeValidator, self.valueMoreMaxDecimalPlaces)
        
        # upper boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(maxNumberOfDecimalPlaces=self.maxValue)
        self.assertRaises(validators.ValidationError, decimalPlacesInRangeValidator, self.valueMoreMaxDecimalPlaces)
        
        # lower boundary
        decimalPlacesInRangeValidator = validators.IsNumberOfDecimalPlacesInRange(minNumberOfDecimalPlaces=self.minValue)
        self.assertRaises(validators.ValidationError, decimalPlacesInRangeValidator, self.valueLessMinDecimalPlaces)


class AreOptionsMatchedTestCase(unittest.TestCase):
    """ Defines some tests for the AreOptionsMatched class. """
    
    def setUp(self):
        """ Setups the instance of the class. """
        
        self.areOptionsMatchedValidator = validators.AreOptionsMatched(["hallo", True, 123])
        
    def testValidValues(self):
        """ Tests different values that are conforming to the defined options. """
        
        self.areOptionsMatchedValidator(True)
        self.areOptionsMatchedValidator(123)
        self.areOptionsMatchedValidator("hallo")
        
    def testInvalidValues(self):
        """ Tests different values that are non-conforming to the defined options. """
        
        self.assertRaises(validators.ValidationError, self.areOptionsMatchedValidator, [True])
        self.assertRaises(validators.ValidationError, self.areOptionsMatchedValidator, 1235)
        self.assertRaises(validators.ValidationError, self.areOptionsMatchedValidator, None)
        

class AreTypesMatchedTestCase(unittest.TestCase):
    """ Defines some tests for the AreTypesMatched class. """
    
    def setUp(self):
        """ Setups the instance of the class. """
        
        self.areTypeMatchedValidator = validators.AreTypesMatched([unicode])
        
    def testValidValues(self):
        """ Tests different values with suitable data type. """
        
        self.areTypeMatchedValidator(u"ahaha")
        self.areTypeMatchedValidator(u"9980")
        
    def testInvalidValues(self):
        """ Tests different values with unsuitable data type. """
        
        self.assertRaises(validators.ValidationError, self.areTypeMatchedValidator, [False])
        self.assertRaises(validators.ValidationError, self.areTypeMatchedValidator, 1235)
        self.assertRaises(validators.ValidationError, self.areTypeMatchedValidator, "halo")


class IsPatternMatchedTestCase(unittest.TestCase):
    """ Tests the class IsPatternMatched. """
    
    def setUp(self):
        """ Setups the instance of the class. """
        
        self.isPatternMatchedValidator = validators.IsPatternMatched("T..t")
        
    def testValidValues(self):
        """ Test some strings the are conforming to the defined regular expression pattern. """

        self.isPatternMatchedValidator("Test")
        self.isPatternMatchedValidator("Taat")
        
    def testInvalidValues(self):
        """ Test some strings the are not conforming to the defined regular expression pattern. """

        self.assertRaises(validators.ValidationError, self.isPatternMatchedValidator, "Hallo")
        self.assertRaises(validators.ValidationError, self.isPatternMatchedValidator, "est")
        
    def testInvalidPattern(self):
        """ Tests the behavior if an invalid regular expression pattern is used. """
        
        self.isPatternMatchedValidator.pattern = "?**???"
        self.assertRaises(validators.ValidationError, self.isPatternMatchedValidator, "Hallo")
        
        
class IsEachValueUniqueTestCase(unittest.TestCase):
    """ Test case for the validation function isEachValueUnique. """

    def setUp(self):
        """ Test case setup. """
        
        self.isEachValueUnique = validators.IsEachValueUnique()
        
    def testValidValues(self):
        """ Test some sequences containing no duplicated values. """
        
        self.assertEquals(self.isEachValueUnique([1, 2, 3, 4, 5]), None)
        self.assertEquals(self.isEachValueUnique(["a", "b", "c", "d"]), None)
        
    def testInvalidValues(self):
        """ Test some sequences containing duplicate values. """
        
        self.assertRaises(validators.ValidationError, self.isEachValueUnique, [1, 2, 3, 3, 5])
        self.assertRaises(validators.ValidationError, self.isEachValueUnique, ["b", "b", "c", "d"])


class ForEachTestCase(unittest.TestCase):
    """ Tests the class ForEach. """
    
    def setUp(self):
        """ Instantiates the class under test. """
        
        self.forEachValidator = validators.ForEach(validators.IsEachValueUnique())
        
    def testValidValues(self):
        """ Tests some valid values given to ForEach and isEachValueUnique combination. """
        
        self.forEachValidator(([1, 2, 3, 4], [1]))
        self.forEachValidator([[1, 2, 3, 4]])
        
    def testInvalidValues(self):
        """ Tests some invalid values given to ForEach and isEachValueUnique combination. """
        
        self.assertRaises(validators.ValidationError, self.forEachValidator, ([1, 3, 3, 4], [1]))
        self.assertRaises(validators.ValidationError, self.forEachValidator, [[1, 2, 1, 4]])
        