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
Provides tests for the type-specific validation functionalities.
"""


import unittest
from datetime import datetime
from decimal import Decimal

from datafinder.core.configuration.properties.validators import type_validators


__version__ = "$Revision-Id:$" 


class StringValidatorTestCase(unittest.TestCase):
    """ Tests of the class StringProperty. """
    
    def setUp(self):
        """ Creates the test environment. """

        pattern = "."        
        options = [u"value", u"binaryString"]
        self.__validator = type_validators.StringValidator(pattern=pattern, 
                                                           options=options)

    def testValidate(self):
        """ Tests the validation method for the StringProperty. """
        
        self.__validator(u"value")
        self.__validator("binaryString")
        self.assertRaises(ValueError, self.__validator, 1234)
    
    
class BooleanValidatorTestCase(unittest.TestCase):
    """ Tests of the class BooleanProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        self.__validator = type_validators.BooleanValidator()

    def testValidate(self):
        """ Tests the validation method for the BooleanProperty. """
        
        self.__validator(True)
        self.__validator(False)
        self.assertRaises(ValueError, self.__validator, "binaryString")
        self.assertRaises(ValueError, self.__validator, 1234)
        
        
class NumberValidatorTestCase(unittest.TestCase):
    """ Tests of the class DecimalProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        options = [Decimal("1234")]
        self.__validator = type_validators.NumberValidator(options=options)

    def testValidate(self):
        """ Tests the validation method for the DecimalProperty. """
        
        self.__validator(Decimal("1234.0"))
        self.__validator(Decimal(1234))
        self.__validator(1234)
        self.assertRaises(ValueError, self.__validator, 1234.0)
        self.assertRaises(ValueError, self.__validator, 123) # not an allowed option
        self.assertRaises(ValueError, self.__validator, "binaryString")
        self.assertRaises(ValueError, self.__validator, True)
        
        
class DatetimeValidatorTestCase(unittest.TestCase):
    """ Tests of the class DatetimeProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        options = [datetime(2008, 10, 19), datetime(2008, 10, 20)]
        self.__validator = type_validators.DatetimeValidator(options=options)

    def testValidate(self):
        """ Tests the validation method for the DatetimeProperty. """
        
        self.__validator(datetime(2008, 10, 19))
        self.__validator(datetime(2008, 10, 20))
        self.assertRaises(ValueError, self.__validator, datetime(2008, 10, 21))
        self.assertRaises(ValueError, self.__validator, 1234)
        self.assertRaises(ValueError, self.__validator, "20.03.2009")
        
        
class ListValidatorTestCase(unittest.TestCase):
    """ Tests of the class ListProperty. """
    
    def setUp(self):
        """ Creates the test environment. """
        
        self.__validator = type_validators.ListValidator()    

    def testValidate(self):
        """ Tests the validation method for the ListProperty. """
        
        self.__validator([])
        self.__validator([["peter", False], False, "hhh", 324234, 123.89, Decimal("12.4"), datetime(2008, 9, 9), u"ttz"])
        self.assertRaises(ValueError, self.__validator, "binaryString")
        self.assertRaises(ValueError, self.__validator, dict())
