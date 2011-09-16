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
Implements Lucene-specific restriction mapping.
"""


import time

from datetime import datetime

from datafinder.persistence.adapters.lucene import constants as lucene_constants 
from datafinder.persistence.search import constants


__version__ = "$Revision-Id:$" 

    
__daslLeafConditionMapping = {
    constants.EQUAL_OPERATOR: ["%s:\"%s\""],
    constants.LT_OPERATOR: ["%s:[* TO %s]"],
    constants.GT_OPERATOR: ["%s:[%s TO *]"],
    constants.LTE_OPERATOR: ["%s:[* TO %s]"],
    constants.GTE_OPERATOR: ["%s:[%s TO *]"],
    constants.LIKE_OPERATOR: ["%s:\"%s\""],
    constants.EXISTS_OPERATOR: [""],
    constants.CONTENT_CONTAINS_OPERATOR: [""],
    constants.IS_COLLECTION_OPERATOR: [""]
}
    
__daslConjunctionOperatorMapping = {
    constants.AND_OPERATOR: "AND",
    constants.OR_OPERATOR: "OR",
    constants.NOT_OPERATOR: "NOT"
}
    
def mapSearchRestriction(restrictions):
    """ 
    Parses the given restrictions and transforms them into the 
    corresponding format used by the Lucene library.
    
    @param restrictions: Search restrictions described as hierarchical organized list.
    @type restrictions: C{list}
    
    @return: Lucene query string.
    @rtype: C{unicode}
    """
    
    conditionTerms = list()
    conjunctionTerms = list()
    queryString = ""
    for token in restrictions:
        if isinstance(token, list):
            result = "(%s)" % mapSearchRestriction(token)
            conditionTerms.append(result)
        elif token in [constants.AND_OPERATOR, constants.OR_OPERATOR, constants.NOT_OPERATOR]:
            conjunctionTerms.append(token)
        else: # conditionTerm
            conditionTerms.append(__conditionTermParseAction(token))
    if len(conjunctionTerms) > 0:
        i = 0
        for conditionTerm in conditionTerms:
            if i < len(conjunctionTerms):
                queryString += conditionTerm + " " + conjunctionTerms[i] + " "
            else:
                queryString += conditionTerm
            i += 1
    else:
        for conditionTerm in conditionTerms:
            queryString += conditionTerm
    if queryString.startswith("(") and queryString.endswith(")") and (queryString.find("AND") == -1):
        queryString = queryString.replace(")", " OR %s:\"%s\" OR %s:\"%s\")" % (lucene_constants.CONTENT_FIELD, restrictions[0][0][2], 
                                                                                lucene_constants.FILEPATH_FIELD, restrictions[0][0][2]))
    return queryString

def __conditionTermParseAction(condition):
    """ Translates the operator, propertyName_, literal tuple to a WebDAV DASL restriction. """
    
    propertyName = condition[0]
    if propertyName is None:
        propertyName = ""
    operator = condition[1]
    literal = condition[2]   
    if literal is None:
        literal = ""
    if (operator == constants.LT_OPERATOR) or (operator == constants.LTE_OPERATOR) or \
        (operator == constants.GT_OPERATOR) or (operator == constants.GTE_OPERATOR):
        if isinstance(literal, time.struct_time):
            conditionTerm = __daslLeafConditionMapping[operator][0] % (propertyName, datetime.fromtimestamp(time.mktime(literal)))
        else:
            conditionTerm = __daslLeafConditionMapping[operator][0] % (propertyName, literal)
    else:
        if (operator == constants.EXISTS_OPERATOR) or (operator == constants.CONTENT_CONTAINS_OPERATOR) or \
            (operator == constants.IS_COLLECTION_OPERATOR):
            conditionTerm = __daslLeafConditionMapping[operator][0]
        else:
            if isinstance(literal, time.struct_time):
                conditionTerm = __daslLeafConditionMapping[operator][0] % (propertyName, datetime.fromtimestamp(time.mktime(literal)))
            else:
                conditionTerm = __daslLeafConditionMapping[operator][0] % (propertyName, literal)
    return conditionTerm
        
