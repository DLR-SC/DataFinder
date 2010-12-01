# $Filename$ 
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
Implements tests for the search restriction parser.
"""


import unittest

from datafinder.core.item.search_restriction import SearchRestrictionParser


__version__ = "$Revision-Id:$" 


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
