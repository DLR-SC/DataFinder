#
# Created: 30.07.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: utils_test.py 4314 2009-10-19 12:38:25Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Test for the datafinder.gui.user.common.simple_search module
"""


import unittest

from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.properties import property_type
from datafinder.gui.user.dialogs.search_dialog.utils import KeywordSearchQueryConverter


__version__ = "$LastChangedRevision: 4314 $"
 

class KeywordSearchQueryConverterTestCase(unittest.TestCase): 
    """ 
    Tests the KeywordSearchQueryConverter class.
    """
    
    def testConversionOneProperty(self):
        """ Tests the conversion with only one property and one keyword. """ 
        
        propDef = PropertyDefinition("animal_type", propertyType = property_type.StringType())
        propertyDefinitions = {("SYSTEM","__animal_type__"): propDef}
        
        converter = KeywordSearchQueryConverter(propertyDefinitions)
        result = converter.convert("penguin")
        self.assertEquals(result, "animal_type like 'penguin'")
        
    def testConversionMultipleProperties(self):
        """ Tests the conversion with multiple properties and one keyword. """
        
        propertyDefinitions = {("SYSTEM" ,"__animal_type__"): \
                                 PropertyDefinition("animal_type", displayName = "animal_type",
                                                    propertyType = property_type.StringType()),
                               ("SYSTEM", "__skin_color__"):\
                                 PropertyDefinition("skin_color", propertyType = property_type.AnyType())}
        
        converter = KeywordSearchQueryConverter(propertyDefinitions)
        result = converter.convert("penguin")
        self.assertEquals(result, "skin_color like 'penguin' OR animal_type like 'penguin'")
        
    def testConversionOnePropertyMultipleKeywords(self):
        """ Tests the conversion with only one property and multiple keywords. """
        
        propDef = PropertyDefinition("animal_type", propertyType = property_type.StringType())
        propertyDefinitions = {("SYSTEM","__animal_type__"): propDef}
        
        converter = KeywordSearchQueryConverter(propertyDefinitions)
        result = converter.convert("penguin dolphin")
        self.assertEquals(result, "animal_type like 'penguin' OR animal_type like 'dolphin'")
        
    def testConversionMultiplePropertiesMultipleKeywords(self):
        """ Tests the conversion with multiple properties and multiple keywords. """
        
        repository = {("SYSTEM" ,"__animal_type__"): \
                        PropertyDefinition("animal_type", propertyType = property_type.StringType()),
                      ("SYSTEM", "__skin_color__"):\
                        PropertyDefinition("skin_color", propertyType = property_type.AnyType()) }
        
        converter = KeywordSearchQueryConverter(repository)
        result = converter.convert("penguin dolphin")
        self.assertEquals(result, "skin_color like 'penguin' OR animal_type like 'penguin' " \
                          "OR skin_color like 'dolphin' OR animal_type like 'dolphin'")
        
    def testConversionOnePropertyMultipleKeywordsInvalidTypes(self):
        """ Tests the conversion with only one property, multiple keywords and invalid types. """ 

        propertyDefinitions = {("SYSTEM","__team_member__"):\
                                PropertyDefinition("team_member", propertyType = property_type.NumberType())}
        
        converter = KeywordSearchQueryConverter(propertyDefinitions)
        
        result = converter.convert("12 14.04 True penguin")
        self.assertEquals(result, "team_member like '12' OR team_member like '14.04'")    
        
        propertyDefinitions = {("SYSTEM","__team_member__"):\
                                 PropertyDefinition("team_member", propertyType = property_type.BooleanType())}
        converter._propertyDefinitions = propertyDefinitions
        result = converter.convert("12 14.04 True penguin")
        self.assertEquals(result, "team_member like 'True'")  
        
        propertyDefinitions = {("SYSTEM","__team_member__"):\
                                PropertyDefinition("team_member", propertyType = property_type.DatetimeType())}
        converter._propertyDefinitions = propertyDefinitions
        result = converter.convert("12 14.04 True penguin 19.12.2000 11:54:56")
        self.assertEquals(result, "team_member like '19.12.2000'")
        
    def testProvokeExceptions(self):
        """ Provokes exceptions. """
        
        # No matching keyword
        propertyDefinitions = {("SYSTEM","__team_member__"):\
                                PropertyDefinition("team_member", propertyType = property_type.DatetimeType())}
        converter = KeywordSearchQueryConverter(propertyDefinitions)    
        result = converter.convert("12 True penguin")
        self.assertEquals(result, "")
        
        #Empty property map
        propertyDefinitions = dict()
        converter = KeywordSearchQueryConverter(propertyDefinitions)    
        result = converter.convert("12 True penguin")
        self.assertEquals(result, "")
        
        #Keyword with correct type but out of range of property
        propertyDefinitions = {("SYSTEM","team_member"):\
                                PropertyDefinition("team_member", propertyType = property_type.NumberType(minimum = 15))}
        converter = KeywordSearchQueryConverter(propertyDefinitions)    
        result = converter.convert("12 True penguin")
        self.assertEquals(result, "")
