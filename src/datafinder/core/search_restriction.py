# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#
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
Implementation of commonly used search grammar.
"""


import time 
import unicodedata

from pyparsing import White, alphas, nums, QuotedString, Word, operatorPrecedence, \
                      opAssoc, Combine, Keyword, Group, StringEnd, Regex, ParserElement


__version__ = "$Revision-Id:$" 


EQUAL_OPERATOR = "="
LT_OPERATOR = "<"
GT_OPERATOR = ">"
LTE_OPERATOR = "<="
GTE_OPERATOR = ">="
LIKE_OPERATOR = "like"
EXISTS_OPERATOR = "exists"
CONTENT_CONTAINS_OPERATOR = "contains"
IS_COLLECTION_OPERATOR = "isCollection"

AND_OPERATOR = "AND"
OR_OPERATOR = "OR"
NOT_OPERATOR = "NOT"


ParserElement.enablePackrat() # Improves the performance of pyparsing

class SearchRestrictionParser(object):
    """ 
    Defines the grammar for a simple search restriction expressions. 
    
    The parsers of the different terms of these restriction expressions are provided by this class.
    """
    
    def __init__(self):
        """ Constructor. """
        
        self.__literalExpression = None
        self.__keywordExpression = None
        self.__propertyNameExpression = None
        self.__comparisonExpression = None
        self.__conditionExpression = None
        self.__conjunctionExpression = None
        self.__restrictionExpression = None
        self.__dateExpression = None
        self.__numberExpression = None
        self.__conjunctionTokens = None
        self.__comparisonTokens = None
        self.__andKeyword = None
        self.__orKeyword = None
        self.__notKeyword = None
        self.__quotedStringCharacters = ["\"", "'"]
        
        self.__initSearchRestrictionParser()
        
    def __initSearchRestrictionParser(self):
        """ Initializes and returns a parser for the search restrictions. """
        
        unicodeUmlaut = unicodedata.lookup("LATIN CAPITAL LETTER A WITH DIAERESIS") + \
                        unicodedata.lookup("LATIN SMALL LETTER A WITH DIAERESIS") + \
                        unicodedata.lookup("LATIN CAPITAL LETTER O WITH DIAERESIS") + \
                        unicodedata.lookup("LATIN SMALL LETTER O WITH DIAERESIS") + \
                        unicodedata.lookup("LATIN CAPITAL LETTER U WITH DIAERESIS") + \
                        unicodedata.lookup("LATIN SMALL LETTER U WITH DIAERESIS") + \
                        unicodedata.lookup("LATIN SMALL LETTER SHARP S")
        # define property name
        firstPropertyNameCharacter = alphas + unicodeUmlaut + "_" 
        propertyCharacter = firstPropertyNameCharacter + nums + ".-" 
        self.__propertyNameExpression = Word(firstPropertyNameCharacter, propertyCharacter)
              
        # define literal
        day = Regex("(0[1-9]|[12][0-9]|3[01])")
        month = Regex("(0[1-9]|1[012])")
        year = Regex("((?:19|20)\d\d)")
        hour = Regex("([01][0-9]|2[0-3])")
        minute = Regex("([0-5][0-9])")
        second = minute
        self.__dateExpression = Combine(day + "." + month + "." + year + White() + hour + ":"  + minute + ":"  + second)
        self.__numberExpression = Regex("[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?")
        self.__literalExpression = QuotedString(self.__quotedStringCharacters[0])
        for quotedStringCharacter in self.__quotedStringCharacters[1:]: 
            self.__literalExpression |= QuotedString(quotedStringCharacter)
        self.__literalExpression.setParseAction(self.__handleLiteral)
        
        # define keywords
        notKeyword = Keyword(NOT_OPERATOR, caseless=True)
        andKeyword = Keyword(AND_OPERATOR, caseless=True)
        orKeyword = Keyword(OR_OPERATOR, caseless=True)
        
        gteKeyword = Keyword(GTE_OPERATOR)
        lteKeyword = Keyword(LTE_OPERATOR)
        equalKeyword = Keyword(EQUAL_OPERATOR)
        gtKeyword = Keyword(GT_OPERATOR)
        ltKeyword = Keyword(LT_OPERATOR)
        likeKeyword = Keyword(LIKE_OPERATOR, caseless=True)
        comparisonKeyword = gteKeyword | lteKeyword | equalKeyword | gtKeyword | ltKeyword | likeKeyword
       
        existsKeyword = Keyword(EXISTS_OPERATOR, caseless=True)
        contentContainsKeyword = Keyword(CONTENT_CONTAINS_OPERATOR, caseless=True)
        isCollectionKeyword = Keyword(IS_COLLECTION_OPERATOR, caseless=True)
        
        self.__keywordExpression = notKeyword | andKeyword | orKeyword | comparisonKeyword | existsKeyword | \
                                   contentContainsKeyword | isCollectionKeyword | "(" | ")"
        
        # definition of condition terms
        comparisonCondition = Group(self.__propertyNameExpression + comparisonKeyword + self.__literalExpression)
        existsCondition = Group(existsKeyword + self.__propertyNameExpression)
        contentContainsCondition = Group(contentContainsKeyword + self.__literalExpression)
        isCollectionCondition = isCollectionKeyword  
        self.__conditionExpression = comparisonCondition | existsCondition | contentContainsCondition | isCollectionCondition
        self.__conditionExpression.setParseAction(self.__handleConditionTerm)
        
        
        # definition of restriction expressions (operators to combine the condition terms)
        self.__restrictionExpression = operatorPrecedence(
            self.__conditionExpression, [
                (notKeyword, 1, opAssoc.RIGHT), 
                (andKeyword, 2, opAssoc.LEFT),
                (orKeyword,  2, opAssoc.LEFT)
            ]
        ) + StringEnd()
        
        # definition of comparison expression
        self.__comparisonExpression = comparisonKeyword
        self.__andKeyword = andKeyword
        self.__orKeyword = orKeyword
        self.__notKeyword = notKeyword
        
        # definition of conjunction expression
        self.__conjunctionExpression = andKeyword | orKeyword
    
    def registerPropertyParseAction(self, parseAction):
        """ Appends a parsing action when matching a property expression. """
        
        self.__propertyNameExpression.setParseAction(parseAction)
    
    def registerLiteralParseAction(self, parseAction):
        """ Appends a parsing action when matching a literal. """
        
        self.__literalExpression.setParseAction(parseAction)
    
    def registerConjunctionParseAction(self, parseAction):
        """ Appends a parsing action when matching a conjunction keyword. """
        
        self.__andKeyword.setParseAction(parseAction)
        self.__orKeyword.setParseAction(parseAction)
        self.__notKeyword.setParseAction(parseAction)
    
    def registerComparisonParseAction(self, parseAction):
        """ Appends a parsing action when matching a comparison keyword. """
        
        self.__comparisonExpression.setParseAction(parseAction)
    
    def __handleLiteral(self, _, __, tokenList):
        """" Evaluates the content of the quoted string. """
       
        unquotedString = tokenList[0]
        result = list()
        for item in self.__dateExpression.scanString(unquotedString):
            result.append(item)
        if len(result) == 1:
            return time.strptime(str(result[0][0][0]), "%d.%m.%Y %H:%M:%S")
        else:
            for item in self.__numberExpression.scanString(unquotedString):
                result.append(item)
            if len(result) == 1:
                return eval(str(result[0][0][0]))

    def parseString(self, inputString):
        """ 
        Parses the string and returns the result. 
        
        @param inputString: String to parse.
        @type inputString: C{unicode}
        
        @raise ParseException: Signals an error parsing the given string.
        """
        
        return self.__restrictionExpression.parseString(inputString)
    
    @staticmethod
    def __handleConditionTerm(_, __, tokens):
        """ 
        Extracts operator, literal, property name from the parsed string
        and calls the given parse action function.
        """
        
        operator = propertyName = literal = None
        tokenList = list(list(tokens)[0])
        
        if len(tokenList) == 3:
            operator = tokenList[1]
            propertyName = tokenList[0]
            literal = tokenList[2]
        elif len(tokenList) == 2:
            operator = tokenList[0]
            if operator == EXISTS_OPERATOR:
                propertyName = tokenList[1]
            else:
                literal = tokenList[1]
        else:
            operator = tokens[0]
        return (propertyName, operator, literal)
        
    def matchKeyword(self, inputString):
        """ 
        Returns all matches of keywords. Keywords in literals are ignored.
        
        @param inputString: String to parse.
        @type inputString: C{unicode}
        
        @return: List of matched expression tuples that consist of matched expression, start index, end index.
        @rtype: C{list} of C{tuple} of C{unicode}, C{int}, C{int}
        """
        
        return self._matchWrapper(inputString, self.__keywordExpression)
            
    def matchPropertyName(self, inputString):
        """ 
        Returns all matches of property names. Keywords and property names in literals are ignored.
        
        @param inputString: String to parse.
        @type inputString: C{unicode}
        
        @return: List of matched expression tuples that consist of matched expression, start index, end index.
        @rtype: C{list} of C{tuple} of C{unicode}, C{int}, C{int}
        """
        
        return self._matchWrapper(inputString, self.__propertyNameExpression)
        
    def matchLiteral(self, inputString):
        """ 
        Returns all matches of literals.
        
        @param inputString: String to parse.
        @type inputString: C{unicode}
        
        @return: List of matched expression tuples that consist of matched expression, start index, end index.
        @rtype: C{list} of C{tuple} of (C{unicode} or C{time.struct_time} or C{int} or C{float}, C{int}, C{int})
        """
        
        return self._matchWrapper(inputString, self.__literalExpression)
    
    def matchComparison(self, inputString):
        """ 
        Returns all matches of comparison operators.
        
        @param inputString: String to parse.
        @type inputString: C{unicode}
        
        @return: List of matched expression tuples that consist of matched expression, start index, end index.
        @rtype: C{list} of C{tuple} of (C{unicode} or C{time.struct_time} or C{int} or C{float}, C{int}, C{int})
        """
        
        return self._matchWrapper(inputString, self.__comparisonExpression)
    
    def matchConjunction(self, inputString):
        """ 
        Returns all matches of conjunction operators.
        
        @param inputString: String to parse.
        @type inputString: C{unicode}
        
        @return: List of matched expression tuples that consist of matched expression, start index, end index.
        @rtype: C{list} of C{tuple} of (C{unicode} or C{time.struct_time} or C{int} or C{float}, C{int}, C{int})
        """
        
        return self._matchWrapper(inputString, self.__conjunctionExpression)
        
    def matchConditionTerm(self, inputString):
        """ 
        Returns all matches of condition terms. Condition terms in literals are ignored.
        
        @param inputString: String to parse.
        @type inputString: C{unicode}
        
        @return: List of matched expression tuples that consist of matched expression, start index, end index.
        @rtype: C{list} of C{tuple} of C{unicode}, C{int}, C{int}
        """
        
        return self._matchWrapper(inputString, self.__conditionExpression)
    
    @property    
    def comparisonTokens(self):
        """
        Returns a list of strings representing the comparison operators.
        """
       
        if self.__comparisonTokens is None:
            self.__comparisonTokens = self._walkKeywordTree(self.__comparisonExpression)
        return self.__comparisonTokens
    
    @property    
    def conjunctionTokens(self):
        """
        Returns a list of strings representing the conjunction keywords.
        """
        
        if self.__conjunctionTokens is None:
            self.__conjunctionTokens = self._walkKeywordTree(self.__conjunctionExpression)
        return self.__conjunctionTokens
    
    @property    
    def quotedStringCharacters(self):
        """
        Returns a list of strings representing the quoted string characters.
        """
        
        return self.__quotedStringCharacters
    
    def _walkKeywordTree(self, rootNode):
        """
        Walks through a MatchFirst object and returns possible matches as a string list
        """
        
        nextRoot = None
        try:
            nextRoot = rootNode.exprs[0]
        except AttributeError:
            return [rootNode.match]
        else:
            result = self._walkKeywordTree(nextRoot)
            result.append(rootNode.exprs[1].match)
            return result

    @staticmethod
    def _matchWrapper(inputString, expression):
        """ Calls scanString with given input, parse expression and returns the result. """
        
        result = list()
        for expression, startIndex, endIndex in expression.scanString(inputString):
            expressionString = expression[0]
            result.append((expressionString, startIndex, endIndex))
        return result
