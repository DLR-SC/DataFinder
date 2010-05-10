#
# Created: 31.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: registry_test.py 4430 2010-02-03 15:38:57Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Test cases concerning the icon handling.
"""


import unittest

from datafinder.core.configuration.constants import LOCAL_INSTALLED_ICONS_DIRECTORY_PATH
from datafinder.core.configuration.icons import Icon
from datafinder.core.configuration.icons import registry
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4430 $"


class IconRegistryTest(unittest.TestCase):
    """ Test cases for the icon registry. """
    
    _DEFAULT_LOCATION = "location"
    
    def setUp(self):
        """ Creates the object under test. """
        
        self._fileStorerMock = SimpleMock(list(), identifier="/test")
        registry.createFileStorer = SimpleMock(self._fileStorerMock)
        self._iconRegistry = registry.IconRegistry()

    def testLoad(self):
        """ Tests the initialization. """

        self._iconRegistry.load()
        
        self._fileStorerMock.value = [SimpleMock(name="a16.png"), SimpleMock(name="a24.png"),
                                      SimpleMock(name="b16.png"), SimpleMock(name="b24.png")]
        self._iconRegistry.load()
        self.assertEquals(len(self._iconRegistry.icons), 2)
        self.assertEquals(len(self._iconRegistry.getIcons(LOCAL_INSTALLED_ICONS_DIRECTORY_PATH)), 2)

        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._iconRegistry.load)

    def testRegister(self):
        """ Tests the registration of an icon. """
        
        self._iconRegistry.register(self._DEFAULT_LOCATION, [Icon("a", "b", "c", "d")])
        self.assertTrue(self._iconRegistry.hasIcon("a", self._DEFAULT_LOCATION))
        
        self._iconRegistry.register(self._DEFAULT_LOCATION, [])
        self.assertTrue(self._iconRegistry.hasIcon("a", self._DEFAULT_LOCATION))
        self.assertEquals(self._iconRegistry.getIcon("a", self._DEFAULT_LOCATION), Icon("a", "b", "c", "d"))
        self.assertEquals(len(self._iconRegistry.getIcons(self._DEFAULT_LOCATION)), 1)
        self.assertEquals(len(self._iconRegistry.icons), 1)
        
        self.assertRaises(TypeError, self._iconRegistry.register, self._DEFAULT_LOCATION, None)
        
        self.assertRaises(AttributeError, self._iconRegistry.register, self._DEFAULT_LOCATION, [None])
        
    def testUnregister(self):
        """ Tests the unregistration of an icon. """
        
        self._iconRegistry.unregister(self._DEFAULT_LOCATION, Icon("a", "b", "c", "d"))
        
        self._iconRegistry.register(self._DEFAULT_LOCATION, [Icon("a", "b", "c", "d")])
        self._iconRegistry.unregister("anotherloc", Icon("a", "b", "c", "d"))
        self.assertTrue(self._iconRegistry.hasIcon("a", self._DEFAULT_LOCATION))
        self._iconRegistry.unregister(self._DEFAULT_LOCATION, Icon("a", "b", "c", "d"))
        self.assertFalse(self._iconRegistry.hasIcon("a", self._DEFAULT_LOCATION))
        
        self._iconRegistry.unregister(None, None)
