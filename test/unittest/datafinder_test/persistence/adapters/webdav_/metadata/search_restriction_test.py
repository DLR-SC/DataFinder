#
# Created: 29.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: search_restriction_test.py 3803 2009-02-20 16:26:50Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements tests for search restriction mapping.
"""


import time
import unittest

from webdav import Condition

from datafinder.persistence.adapters.webdav_.metadata.search_restriction_mapping import mapSearchRestriction


__version__ = "$LastChangedRevision: 3803 $"


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
