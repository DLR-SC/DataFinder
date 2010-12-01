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
Implements tests for search restriction mapping.
"""


import time
import unittest

from webdav import Condition

from datafinder.persistence.adapters.webdav_.metadata.search_restriction_mapping import mapSearchRestriction


__version__ = "$Revision-Id:$" 


class SearchRestrictionDaslTransformerTestCase(unittest.TestCase):
    """
    Defines test cases for the transformation of identified tokens to
    instances used by the WebDAV library to represent search queries.
    """
    
    def testTransform(self):
        """ Tests the transforming from a search restriction to a WebDAV library specific expression. """
        
        daslRestrictions = mapSearchRestriction([[('SITe', '=', 'ggg'), 'OR', [('SITe', '=', 'ggg'), 'AND', ('SITe', '=', 'ggg')]]])
        self.failUnless(isinstance(daslRestrictions, Condition.OrTerm), "The result is not an or term.")
        
        daslRestrictions = mapSearchRestriction([(None, "isCollection", None)])
        self.failUnless(isinstance(daslRestrictions, Condition.IsCollectionTerm), "The result is not a isCollection term.")
        
        daslRestrictions = mapSearchRestriction([("PeterProp", "exists", None)])
        self.failUnless(isinstance(daslRestrictions, Condition.ExistsTerm), "The result is not an exists term.")
        
        daslRestrictions = mapSearchRestriction([("SITe98", "=", "g")])
        self.failUnless(isinstance(daslRestrictions, Condition.MatchesTerm), "The result is not a match term.")
        
        daslRestrictions = mapSearchRestriction([("SITe98", "=", 100)])
        self.failUnless(isinstance(daslRestrictions, Condition.IsEqualTerm), "The result is not an equal term.")
        
        daslRestrictions = mapSearchRestriction([("SITe98", "=", time.localtime())])
        self.failUnless(isinstance(daslRestrictions, Condition.OnTerm), "The result is not an on term.")
