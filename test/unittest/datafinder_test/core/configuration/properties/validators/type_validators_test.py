#
# Created: 01.09.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: type_validators_test.py 3884 2009-03-26 17:07:42Z schlauch $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" 
Provides tests for the type-specific validation functionalities.
"""


import unittest
from datetime import datetime
from decimal import Decimal

from datafinder.core.configuration.properties.validators import type_validators, error


__version__ = "$LastChangedRevision: 3884 $"


class StringValidatorTestCase(unittest.TestCase):
    """ Tests of the class StringProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        self.__validator = type_validators.StringValidator()

    def testValidate(self):
        """ Tests the validation method for the StringProperty. """
        
        self.__validator(u"value")
        self.__validator("binaryString")
        self.assertRaises(error.ValidationError, self.__validator, 1234)
    
    
class BooleanValidatorTestCase(unittest.TestCase):
    """ Tests of the class BooleanProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        self.__validator = type_validators.BooleanValidator()

    def testValidate(self):
        """ Tests the validation method for the BooleanProperty. """
        
        self.__validator(True)
        self.__validator(False)
        self.assertRaises(error.ValidationError, self.__validator, "binaryString")
        self.assertRaises(error.ValidationError, self.__validator, 1234)
        
        
class DecimalValidatorTestCase(unittest.TestCase):
    """ Tests of the class DecimalProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        self.__validator = type_validators.NumberValidator()

    def testValidate(self):
        """ Tests the validation method for the DecimalProperty. """
        
        self.__validator(Decimal("1234"))
        self.__validator(Decimal(1234))
        self.__validator(1234.897)
        self.__validator(123)
        self.assertRaises(error.ValidationError, self.__validator, "binaryString")
        self.assertRaises(error.ValidationError, self.__validator, True)
        
        
class DatetimeValidatorTestCase(unittest.TestCase):
    """ Tests of the class DatetimeProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        self.__validator = type_validators.DatetimeValidator()

    def testValidate(self):
        """ Tests the validation method for the DatetimeProperty. """
        
        self.__validator(datetime(2008, 10, 19))
        self.assertRaises(error.ValidationError, self.__validator, 1234)
        self.assertRaises(error.ValidationError, self.__validator, "20.03.2009")
        
        
class ListValidatorTestCase(unittest.TestCase):
    """ Tests of the class ListProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        self.__validator = type_validators.ListValidator()    

    def testValidate(self):
        """ Tests the validation method for the ListProperty. """
        
        self.__validator([])
        self.__validator([["peter", False], False, "hhh", 324234, 123.89, Decimal("12.4"), datetime(2008, 9, 9), u"ttz"])
        self.assertRaises(error.ValidationError, self.__validator, "binaryString")
        self.assertRaises(error.ValidationError, self.__validator, dict())


class ArbitaryValidatorTestCase(unittest.TestCase):
    """ Tests of the class ArbitaryValidatorTest. """
    
    def setUp(self):
        """ Creates the test environment. """

        self.__validator = type_validators.ArbitaryValidator()    
       
    def testValidate(self):
        """ Tests the validation method for the ArbitaryProperty. """
        
        testValues = [False, "hhh", 324234, 123.89, Decimal("12.4"), 
                      datetime(2008, 9, 9), u"ttz", [1, u"344", True]]
        for testValue in testValues:
            self.__validator(testValue)
        self.assertRaises(error.ValidationError, self.__validator, dict())
        self.assertRaises(error.ValidationError, self.__validator, [[123], 34])
