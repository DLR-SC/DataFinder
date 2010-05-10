#
# Created: 09.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: icon_test.py 4430 2010-02-03 15:38:57Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests for the icon module.
"""


import unittest

from datafinder.core.configuration.icons import icon
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4430 $"


class IconTestCase(unittest.TestCase):
    """ Tests the parsing of a specific directory for suitable icon files. """
    
    def setUp(self):
        """ Creates test setup. """
        
        self._directoryFileStorer = SimpleMock(identifier="/test")
    
    def testParsingSuccess(self):
        """  Tests the successful parsing of a directory for icon files. """
        
        self._directoryFileStorer.value = [SimpleMock(name="a16.png"), SimpleMock(name="a24.png"),
                                           SimpleMock(name="b16.png"), SimpleMock(name="b24.png")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 2)
        
        self._directoryFileStorer.value = [SimpleMock(name="a6.png"), SimpleMock(name="a24.png"),
                                           SimpleMock(name="b16.png"), SimpleMock(name="b24.png")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 1)
        
        self._directoryFileStorer.value = [SimpleMock(name="a6.png"), SimpleMock(name="a24.png"),
                                           SimpleMock(name="b16.png"), SimpleMock(name="b24.ng")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 1)
        
        self._directoryFileStorer.value = [SimpleMock(name="a6.png"), SimpleMock(name="a24.png"),
                                           SimpleMock(name="b6.png"), SimpleMock(name="b24.ng")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 0)
        
    def testErrorHandling(self):
        """ Tests the error handling when parsing a directory for icon files. """
        
        self._directoryFileStorer.value = [SimpleMock(name=""), SimpleMock(name="a24.png")]
        self.assertEquals(len(icon.parseIconDirectory(self._directoryFileStorer)), 0)
        
        self._directoryFileStorer.error = PersistenceError("")
        self.assertRaises(ConfigurationError, icon.parseIconDirectory, self._directoryFileStorer)
        
    def testIconComparison(self):
        """ Tests the comparison of icons. """
        
        anIcon = icon.Icon("a", "b", "c", "d")
        self.assertEquals(anIcon, anIcon)
        
        anotherIcon = icon.Icon("a", "b", "c", "d")
        self.assertEquals(anIcon, anotherIcon)
        
        anotherIcon.baseName = "d"
        self.assertNotEquals(anIcon, anotherIcon)
        
        self.assertNotEquals(anIcon, None)
    