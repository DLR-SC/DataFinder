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
Test cases concerning the icon handling.
"""


import unittest

from datafinder.core.configuration.constants import LOCAL_INSTALLED_ICONS_DIRECTORY_PATH
from datafinder.core.configuration.icons import Icon
from datafinder.core.configuration.icons import registry
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


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
