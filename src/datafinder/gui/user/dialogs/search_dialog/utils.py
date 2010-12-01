# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
This modules contains a converter to convert simple search queries to normal queries.
"""


from datetime import datetime
from threading import Lock

from pyparsing import ParseException
from PyQt4 import QtCore

from datafinder.core.error import PropertyError
from datafinder.core.configuration.properties import constants
from datafinder.core.item.search_restriction import OR_OPERATOR, LIKE_OPERATOR


__version__ = "$Revision-Id:$" 


class KeywordSearchQueryConverter(object):
    """
    KeywordSearchQueryConverter converts the given keywords into a search query.
    """
    
    def __init__(self, propertyDefinitions):
        """
        @param propertyDefinitions: Registered property definitions.
        @type propertyDefinitions: C{dict}; keys: C{unicode}, C{unicode}; values: C{PropertyDefinition}
        """
        
        self._propertyDefinitions = propertyDefinitions
        self._conversionFunctions = {constants.NUMBER_TYPE: float,
                                     constants.BOOLEAN_TYPE: self._convertBoolean,
                                     constants.DATETIME_TYPE: self._convertDate}
            
    def convert(self, keywords):
        """
        Converts the given keywords into a search query. It takes all keywords and tries to
        find properties that could fit. For example, a keyword 123 could be a string or a number. So this
        keyword will be checked for NumberType, StringType and AnyType properties. All possible combinations
        of property keyword pairs are or-wise connected in a search query.  
        
        @param keywords: String of keywords to convert.
        @type keywords: C{unicode}
        
        @return: A search string that could be used with the search method of a repository.
        @rtype: C{unicode}
        """
          
        keywords = keywords.split()
        query = ""
        
        for keyword in keywords:
            for propertyDefinition in self._propertyDefinitions.values():
                try:
                    convertedPhrase = self._conversionFunctions[propertyDefinition.type](keyword)
                except ValueError:
                    continue
                except KeyError:
                    convertedPhrase = unicode(keyword)
                try:   
                    propertyDefinition.validate(convertedPhrase)
                except PropertyError:
                    pass
                else:
                    if len(query) > 0:
                        query += " %s " % OR_OPERATOR
                    query += "%s %s '%s'" % (propertyDefinition.identifier, LIKE_OPERATOR, keyword)       
        return query
    
    @staticmethod
    def _convertBoolean(string):
        """
        Tries to convert a string to boolean. If the string is C{True} it returns the boolean value C{True},
        if it's C{False} it returns the boolean value False. In all other cases it raises a ValueError.
        """
        
        if string in ["True"]:
            return True
        elif string in ["False"]:
            return False
        else:
            raise ValueError()
        
    @staticmethod
    def _convertDate(string):
        """
        Tries to convert a string to a L{Datetime <datetime.datetime>} object.
        
        @rtype: L{datetime <datetime.datetime>}
        """
        
        return datetime.strptime(string, "%d.%m.%Y")


class SearchQueryAnalyzer(QtCore.QObject):
    """ Helper which analyzes a given search query. """
    
    VALIDATION_SIGNAL = "validationSignal" # signals validity of search query
    
    PROPERTY_TYPE = 0
    COMPARISON_TYPE = 1
    LITERAL_TYPE = 2
    CONJUNCTION_TYPE = 3
    
    def __init__(self, parser, propertyDefinitionToolTipMap, matchHook=None):
        """ Constructor. """

        QtCore.QObject.__init__(self)
        self._lock = Lock()
        self._parsingResults = dict()
        self._propertyDefinitionToolTipMap = propertyDefinitionToolTipMap
        self._matchHook = matchHook
        self._parser = parser
        self._matchFunctions = [(parser.matchLiteral, self.LITERAL_TYPE),
                                (parser.matchConjunction, self.CONJUNCTION_TYPE),
                                (parser.matchComparison, self.COMPARISON_TYPE),
                                (parser.matchPropertyName, self.PROPERTY_TYPE)]
        self._errorResult = None
        self._analyzedSearchQuery = ""
        self._tokenTypeTransitionMap = {self.CONJUNCTION_TYPE: self.PROPERTY_TYPE,
                                        self.COMPARISON_TYPE: self.LITERAL_TYPE,
                                        self.PROPERTY_TYPE: self.COMPARISON_TYPE,
                                        self.LITERAL_TYPE: self.CONJUNCTION_TYPE}
        
        self._parser.registerComparisonParseAction(self._parserActionWrapper(self.COMPARISON_TYPE))
        self._parser.registerPropertyParseAction(self._parserActionWrapper(self.PROPERTY_TYPE))
        self._parser.registerConjunctionParseAction(self._parserActionWrapper(self.CONJUNCTION_TYPE))
        self._parser.registerLiteralParseAction(self._parserActionWrapper(self.LITERAL_TYPE))

    def nextTokenType(self, tokenType):
        """
        Determines the next possible token type he given token type.
        
        @param tokenType: One of the following constants:
        @type tokenType: C{int}
        
        @return: The next valid token type.
        @rtype: C{int}
        """
        
        try:
            return self._tokenTypeTransitionMap[tokenType]
        except KeyError:
            return self.PROPERTY_TYPE
        
    def analyze(self, searchQuery):
        """ Analyzes the given text and produces the actual parsing result. """
        
        self._lock.acquire()
        try:
            self._analyzedSearchQuery = searchQuery
            self.clearParsingResults()
            try:
                self._parser.parseString(searchQuery)
                self._errorResult = None
            except ParseException, error:
                self._errorResult = error.loc, error.msg
                length = error.loc
                searchQuery = " " * length + searchQuery[error.loc:]
                for matchFunction, tokenType in self._matchFunctions: # Required to analyze tokens after error
                    for _, start, end in matchFunction(searchQuery):
                        length = end - start
                        token = searchQuery[start:end]
                        searchQuery = searchQuery[:start] + " " * length + searchQuery[end:]
                        self._analyzeToken(start, end, token, tokenType)
                self._emitValidationSignal(False)
            else:
                self._emitValidationSignal(True)
        finally:
            self._lock.release()
    
    def _emitValidationSignal(self, valid):
        """
        Signal is emitted when the validation of the syntax changed.

        @param valid: C{True} if the syntax is valid else False.
        @type valid: C{bool}
        """

        self.emit(QtCore.SIGNAL(self.VALIDATION_SIGNAL), valid)

    def clearParsingResults(self):
        """ Clears the parsing results. """
        
        self._parsingResults.clear()
        self._errorResult = 0, "" 
        self._emitValidationSignal(False)
        
    def _parserActionWrapper(self, tokenType):
        """ Returns a parseAction for the given token type. """
        
        def _parseAction(searchQuery, start, tokenList):
            token = tokenList[0]
            untrimmedLength = len(searchQuery[start:])
            leftTrimmedLength = len(searchQuery[start:].lstrip())
            start = start + (untrimmedLength - leftTrimmedLength) # Sometimes white spaces are not considered determining start
            end = start + len(token)
            if tokenType == self.LITERAL_TYPE: 
                end += 2
            token = searchQuery[start:end]
            self._analyzeToken(start, end, token, tokenType)
        return _parseAction
    
    def _analyzeToken(self, start, end, token, tokenType):
        """ Analyzes the specific token and adds a descriptor to the result. """
        
        toolTip = ""
        if tokenType == self.PROPERTY_TYPE:
            try:
                toolTip = self._propertyDefinitionToolTipMap[token]
            except KeyError:
                toolTip = token
        tokenDescriptor = TokenDescriptor(start, end, token, tokenType, toolTip)
        self._parsingResults[(start, end)] = tokenDescriptor
        if not self._matchHook is None:
            self._matchHook(tokenDescriptor)
    
    def token(self, position):
        """ 
        Determines the token at the given position. 
        
        @param position: Position in the last analyzed search query. 
        @type position: C{int}
        
        @return: The specific token.
        @rtype: C{TokenDescriptor}
        """
        
        return self.tokenAround(position)[0]
    
    def tokenAround(self, position):
        """ 
        Determines the tokens around the given position, i.e. the token 
        at the given position and the token before. 
        
        @param position: Position in the last analyzed search query. 
        @type position: C{int}
        
        @return: Token at position, token before the position.
        @rtype: C{tuple} of C{TokenDescriptor}, C{TokenDescriptor}
        """
             
        currentToken = None
        tokenBefore = None
        
        ranges = self._parsingResults.keys()
        ranges.sort()
        rangeBefore = None
        for range_ in ranges:
            start, end = range_
            token = self._parsingResults[range_]
            if position in range(start, end + 1):
                currentToken = token
                break
            elif position < end:
                break
            else:
                rangeBefore = range_
        if not rangeBefore is None:
            tokenBefore = self._parsingResults[rangeBefore]
        return currentToken, tokenBefore
        
    @property
    def errorResult(self):
        """ Returns occurred errors. """
        
        return self._errorResult
    
    @property
    def analyzedSearchQuery(self):
        """ Returns the analyzed search query. """
        
        return self._analyzedSearchQuery


class TokenDescriptor(object):
    """ Describes a search query token. """
    
    def __init__(self, start, end, token, type_, toolTip):
        """ Constructor. """
        
        self.start = start
        self.end = end
        self.token = token
        self.type = type_
        self.toolTip = toolTip
        
    def __str__(self):
        """ Returns a nice string representation. """
        
        return self.token + " at: " + str(self.start) + ", " + str(self.end)
