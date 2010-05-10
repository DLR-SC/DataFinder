#
# Created: 29.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: search_restriction_test.py 4314 2009-10-19 12:38:25Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements tests for the search restriction parser.
"""


import unittest

from datafinder.core.item.search_restriction import SearchRestrictionParser


__version__ = "$LastChangedRevision: 4314 $"


class SearchSupportTestCase(unittest.TestCase):
    """
    Defines test cases for the basic parser of search restrictions. In particular these tests demonstrate 
    the available basic syntax for search restrictions. 
    """
    
    def setUp(self):
        """ Creates the parser. """
        
        self.__searchRestrictionParser = SearchRestrictionParser()
        
    def testMatch(self):
        """ Simple test function for the match interface of SearchRestrictionParser. """
        
        myParser = self.__searchRestrictionParser
        
        testData = "SIorTe = '-8990.89' or (SITe = 'ggg') and (SITe = 'ggg')"
        
        literalResult = myParser.matchLiteral(testData)
        self.assertEqual(len(literalResult), 3)
        
        keywordResult = myParser.matchKeyword(testData)
        self.assertEqual(len(keywordResult), 9)
        
        propertyResult = myParser.matchPropertyName(testData)
        self.assertEqual(len(propertyResult), 7) # Does also find keywords that conform to the property name definition
        
        result = myParser.matchConditionTerm(testData)
        self.assertEqual(len(result), 3)
           
    def testBasicSyntax(self):
        """ Tests and demonstrates the basic syntax of the search restrictions. """
        
        myParser = self.__searchRestrictionParser
        
        self.assertEqual(myParser.parseString("isCollection").asList(), [(None, "isCollection", None)]) 
        
        self.assertEqual(myParser.parseString("not IsCollection").asList(), [["NOT", (None, "isCollection", None)]])
        
        self.assertEqual(myParser.parseString("SITe98 > 'g'").asList(), [("SITe98", ">", "g")])
        
        self.assertEqual(myParser.parseString("SITe = 'ggg' or (SITe = 'ggg') and (SITe = 'ggg')").asList(),
                         [[('SITe', '=', 'ggg'), 'OR', [('SITe', '=', 'ggg'), 'AND', ('SITe', '=', 'ggg')]]])
        
        self.assertEqual(myParser.parseString("not (Description = 'sdf')").asList(), [['NOT', ('Description', '=', 'sdf')]])
        
        self.assertEqual(myParser.parseString(u"not SITe = 'ggg'").asList(), [['NOT', ('SITe', '=', u'ggg')]])
        
        self.assertEqual(myParser.parseString("SITe < 'g'").asList(), [('SITe', '<', 'g')])
        
        self.assertEqual(myParser.parseString("SITe_.T >= 'g'").asList(), [('SITe_.T', '>=', 'g')])
        
        self.assertEqual(myParser.parseString("(_S9ITe <= 'g')").asList(), [('_S9ITe', '<=', 'g')])
        
        self.assertEqual(myParser.parseString("_S9ITe <= '19.12.2000 11:54:56'").asList(), 
                         [('_S9ITe', '<=', (2000, 12, 19, 11, 54, 56, 1, 354, -1))])
        
        self.assertEqual(myParser.parseString("(containS 'g')").asList(), [(None, 'contains', 'g')])
        
        self.assertEqual(myParser.parseString("SITe liKe \"glk\"").asList(), [('SITe', 'like', 'glk')])
        
        self.assertEqual(myParser.parseString("not exists g").asList(), [['NOT', ('g', 'exists', None)]])
        
        self.assertEqual(myParser.parseString("IsCollecTion or (IsCollecTion) and not(iscollection)").asList(), 
                    [[(None, 'isCollection', None), 'OR', [(None, 'isCollection', None), 'AND', ['NOT', (None, 'isCollection', None)]]]])
        
        self.assertEqual(myParser.parseString("SITe = 'g_&/%$!\' or SITe = 'g'").asList(),
                         [[('SITe', '=', 'g_&/%$!'), 'OR', ('SITe', '=', 'g')]])        
                   
        self.assertEqual(myParser.parseString("SITe = 'g' and not SITe = 'g'").asList(),
                         [[('SITe', '=', 'g'), 'AND', ['NOT', ('SITe', '=', 'g')]]])
        
        self.assertEqual(myParser.parseString("(SITe = '1' And nOt (not(ITe >= '-2.0' or SITe < '19.12.2000 11:54:07'))) " \
                                              "and (exists Perter) or (b > '9')").asList(),
                         [[[[('SITe', '=', 1), 'AND', ['NOT', ['NOT', [('ITe', '>=', -2.0), 'OR', 
                         ('SITe', '<', (2000, 12, 19, 11, 54, 7, 1, 354, -1))]]]],'AND', ('Perter', 'exists', None)], 'OR', ('b', '>', 9)]])
        
        self.assertEqual(myParser.parseString("not(SITe = 'g' and SITe = 'g') and (exists b)").asList(),
                         [[['NOT', [('SITe', '=', 'g'), 'AND', ('SITe', '=', 'g')]], 'AND', ('b', 'exists', None)]])
        
        self.assertEqual(myParser.parseString("a_. > '978.89' and b > 'qewe' and c = 'zzu'").asList(),
                         [[('a_.', '>', 978.88999999999999), 'AND', ('b', '>', 'qewe'), 'AND', ('c', '=', 'zzu')]])
        
        self.assertEqual(myParser.parseString("a_. > '978.89' and b > 'qewe' or c = 'zzu' or c = 'zzu' " \
                                              "and c = 'zzu' or c = 'zzu' and c = 'zzu'").asList(),
                         [[[('a_.', '>', 978.88999999999999), 'AND', ('b', '>', 'qewe')], 'OR', ('c', '=', 'zzu'), 'OR', 
                           [('c', '=', 'zzu'), 'AND', ('c', '=', 'zzu')], 'OR', [('c', '=', 'zzu'), 'AND', ('c', '=', 'zzu')]]])
        
        self.assertEqual(myParser.parseString("a_. > '978.89' or b > 'qewe' and c = 'zzu'").asList(),
                         [[('a_.', '>', 978.88999999999999), 'OR', [('b', '>', 'qewe'), 'AND', ('c', '=', 'zzu')]]])
        
        self.assertEqual(myParser.parseString("a_. > '978.89' and (b > 'qewe' and c = 'zzu')").asList(),
                         [[('a_.', '>', 978.88999999999999), 'AND', [('b', '>', 'qewe'), 'AND', ('c', '=', 'zzu')]]])
        
        self.assertEqual(myParser.parseString("a_. > '978.89' and (b > 'qewe' or c = 'zzu')").asList(),
                         [[('a_.', '>', 978.88999999999999), 'AND', [('b', '>', 'qewe'), 'OR', ('c', '=', 'zzu')]]])
        
        self.assertEqual(myParser.parseString("a_. > '978.89' or (b > 'qewe' and c = 'zzu')").asList(),
                         [[('a_.', '>', 978.88999999999999), 'OR', [('b', '>', 'qewe'), 'AND', ('c', '=', 'zzu')]]])


    def testComparisonTokens(self):
        """ Tests the available comparison tokens. """
        
        self.assertEquals(self.__searchRestrictionParser.comparisonTokens, [">=", "<=", "=", ">", "<", "like"])
        
    def testConjunctionTokens(self):
        """ Tests the available conjunction tokens. """
        
        self.assertEquals(self.__searchRestrictionParser.conjunctionTokens, ["AND", "OR"]) 

    def testQuotedStringCharacters(self):
        """ Tests the available quoted string characters. """
        
        self.assertEquals(self.__searchRestrictionParser.quotedStringCharacters, ["\"", "'"])
