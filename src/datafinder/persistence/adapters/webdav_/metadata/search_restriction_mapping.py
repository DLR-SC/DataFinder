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
Implements WebDAV-specific restriction mapping.
"""


import time

from webdav import Condition

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants
from datafinder.persistence.adapters.webdav_.metadata.identifier_mapping import mapMetadataId


__version__ = "$Revision-Id:$" 


__daslLeafConditionMapping = {
    constants.EQUAL_OPERATOR: [Condition.MatchesTerm, Condition.IsEqualTerm, Condition.OnTerm],
    constants.LT_OPERATOR: [Condition.IsSmallerTerm, Condition.IsSmallerTerm, Condition.BeforeTerm],
    constants.GT_OPERATOR: [Condition.IsGreaterTerm, Condition.IsGreaterTerm, Condition.AfterTerm],
    constants.LTE_OPERATOR: [Condition.IsSmallerOrEqualTerm, Condition.IsSmallerOrEqualTerm, Condition.BeforeTerm],
    constants.GTE_OPERATOR: [Condition.IsGreaterOrEqualTerm, Condition.IsGreaterOrEqualTerm, Condition.AfterTerm],
    constants.LIKE_OPERATOR: [Condition.ContainsTerm],
    constants.EXISTS_OPERATOR: [Condition.ExistsTerm],
    constants.CONTENT_CONTAINS_OPERATOR: [Condition.ContentContainsTerm],
    constants.IS_COLLECTION_OPERATOR: [Condition.IsCollectionTerm]
}

__daslConjunctionOperatorMapping = {
    constants.AND_OPERATOR: Condition.AndTerm,
    constants.OR_OPERATOR: Condition.OrTerm,
    constants.NOT_OPERATOR: Condition.NotTerm
}
    
    
def mapSearchRestriction(restrictions):
    """ 
    Parses the given restrictions and transforms them into the 
    corresponding format used by the WebDAV library.
    
    @param restrictions: Search restrictions described as hierarchical organized list.
    @type restrictions: C{list}
    
    @return: Condition term instance.
    @rtype: L{ConditionTerm<webdav.Condition.ConditionTerm>}
    """
        
    conditionTerms = list()
    conjunctionTerms = list()
    rootConjunctionTerm = None
    for token in restrictions:
        if isinstance(token, list):
            result = mapSearchRestriction(token)
            conditionTerms.append(result)
        elif token in [constants.AND_OPERATOR, constants.OR_OPERATOR, constants.NOT_OPERATOR]:
            conjunctionTerms.append(token)
        else: # conditionTerm
            conditionTerms.append(__conditionTermParseAction(token))
    
    if len(conjunctionTerms) > 0:
        operator = conjunctionTerms[0]
        if operator == constants.NOT_OPERATOR:
            assert len(conditionTerms) == 1
            rootConjunctionTerm = __daslConjunctionOperatorMapping[operator](conditionTerms[0])
        else:
            assert len(conditionTerms) > 1
            rootConjunctionTerm = __daslConjunctionOperatorMapping[operator](conditionTerms)
    else:
        assert len(conditionTerms) == 1
        rootConjunctionTerm = conditionTerms[0]
    return rootConjunctionTerm

    
def __conditionTermParseAction(condition):
    """ Translates the operator, propertyName_, literal tuple to a WebDAV DASL restriction. """
    
    propertyName = condition[0]
    operator = condition[1]
    literal = condition[2]
    conditionTermClass = __getConditionTermClass(operator, literal)

    if propertyName is None and literal is None:
        conditionTermInstance = conditionTermClass()
    elif not propertyName is None and not literal is None:
        conditionTermInstance = conditionTermClass(mapMetadataId(propertyName), literal)
    elif propertyName is None:
        conditionTermInstance = conditionTermClass(literal)
    else: # literal is None:
        conditionTermInstance = conditionTermClass(mapMetadataId(propertyName))
    return conditionTermInstance

    
def __getConditionTermClass(operator, literal):
    """ Determines the condition term class. """
    
    try:
        conditionTermList = __daslLeafConditionMapping[operator]
    except KeyError:
        errorMessage = "Operator '%s' is not supported!" % operator
        raise PersistenceError(errorMessage)
    else:
        if len(conditionTermList) == 3:
            if isinstance(literal, basestring):
                conditionTermClass = conditionTermList[0]
            elif isinstance(literal, time.struct_time):
                conditionTermClass = conditionTermList[2]
            else:
                conditionTermClass = conditionTermList[1]
        else:
            conditionTermClass = conditionTermList[0]
        return conditionTermClass
