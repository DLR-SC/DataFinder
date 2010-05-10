#
# Created: 24.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: util_test.py 4070 2009-05-18 15:20:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests utility functionality.
"""


__version__ = "$LastChangedRevision: 4070 $"


import unittest

from datafinder.persistence.adapters.webdav_ import util


_PERSISTENCE_ID = "http://test.de:80/hhh/j/c:/lll/"
_INTERFACE_ID = "/c:/lll"


class ItemIdentifierMapperTestCase(unittest.TestCase):
    """ Tests the identifier mapping. """
    
    def testMapIdentifier(self):
        """ Tests the normal behavior of the identifier mapping. """
        
        mapper = util.ItemIdentifierMapper("http://test.de:80/hhh/j")
        self.assertEquals(mapper.mapIdentifier("/c:/lll/"), _PERSISTENCE_ID)
        self.assertEquals(mapper.mapIdentifier("c:/lll/"), _PERSISTENCE_ID)
        mapper = util.ItemIdentifierMapper("http://test.de:80/hhh/j/")
        self.assertEquals(mapper.mapIdentifier("/c:/lll/"), _PERSISTENCE_ID)
        self.assertEquals(mapper.mapIdentifier("c:/lll/"), _PERSISTENCE_ID)
        
    def testMapPersistenceIdentifier(self):
        """ Tests the normal behavior of the persistence ID mapping. """
        
        mapper = util.ItemIdentifierMapper("http://test.de:80/hhh/j")
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test.de:80/hhh/j/c:/lll/"), _INTERFACE_ID)
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test.de:80/hhh/j/c:/lll"), _INTERFACE_ID)
        mapper = util.ItemIdentifierMapper("http://test.de:80/hhh/j/")
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test.de:80/hhh/j/c:/lll/"), _INTERFACE_ID)
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test.de:80/hhh/j/c:/lll"), _INTERFACE_ID)
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test:80/kkk/j/c:/lll"), "/kkk/j/c:/lll")
        self.assertEquals(mapper.mapPersistenceIdentifier("http://test:80/kkk/j/c:/lll/"), "/kkk/j/c:/lll")

    def testDetermineBaseName(self):
        """ Tests the determine base name functionality. """
        
        self.assertEquals(util.ItemIdentifierMapper.determineBaseName("/kkjh/aa/hh"), "hh")
        self.assertEquals(util.ItemIdentifierMapper.determineBaseName("/"), "")
        self.assertEquals(util.ItemIdentifierMapper.determineBaseName("jjj"), "jjj")
        self.assertEquals(util.ItemIdentifierMapper.determineBaseName(""), "")
        self.assertRaises(AttributeError, util.ItemIdentifierMapper.determineBaseName, None)
        
    def testDetermineParentPath(self):
        """ Tests the determine parent functionality. """
        
        self.assertEquals(util.ItemIdentifierMapper.determineParentPath("/kkjh/aa/hh"), "/kkjh/aa")
        self.assertEquals(util.ItemIdentifierMapper.determineParentPath("/"), "")
        self.assertEquals(util.ItemIdentifierMapper.determineParentPath("jjj"), "")
        self.assertEquals(util.ItemIdentifierMapper.determineParentPath(""), "")
        self.assertRaises(AttributeError, util.ItemIdentifierMapper.determineBaseName, None)
    
    def testInvalidUrl(self):
        """ Tests invalid base URL. """
        
        self.assertRaises(AttributeError, util.ItemIdentifierMapper, None)
        util.ItemIdentifierMapper("invalidURL")
