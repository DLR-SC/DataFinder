# $Filename$$
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
Tests the base configuration.
"""


import unittest

from datafinder.persistence.common.configuration import BaseConfiguration


__version__ = "$Revision-Id:$" 


class BaseConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self._baseConfig = BaseConfiguration("http://test.dlr.de/myPath",
                                             user="me", password="secret")
        

    def testConfigurationHandling(self):
        """ Demonstrates use cases of the base configuration. """
        
        # Access URI parameters
        self.assertEquals(self._baseConfig.uriScheme, "http")
        self.assertEquals(self._baseConfig.uriNetloc, "test.dlr.de")
        self.assertEquals(self._baseConfig.uriHostname, "test.dlr.de")
        self.assertEquals(self._baseConfig.uriPort, None)
        self.assertEquals(self._baseConfig.uriPath, "/myPath")
        self.assertEquals(self._baseConfig.baseUri, "http://test.dlr.de/myPath")
        
        # Access additional parameters
        self.assertEquals(self._baseConfig.user, "me")
        self.assertEquals(self._baseConfig.password, "secret")

        # Access not defined parameters
        self.assertEquals(self._baseConfig.unknown1, None)
        self.assertEquals(self._baseConfig.unknown2, None)

        # Testing None -> everything stays the same
        self._baseConfig.baseUri = None
        self.assertEquals(self._baseConfig.baseUri, "http://test.dlr.de/myPath")
        
        # Testing unknown scheme
        self._baseConfig.baseUri = ""
        self.assertEquals(self._baseConfig.uriScheme, "")
        self.assertEquals(self._baseConfig.uriNetloc, "")
        self.assertEquals(self._baseConfig.uriHostname, None)
        self.assertEquals(self._baseConfig.uriPort, None)
        self.assertEquals(self._baseConfig.uriPath, "")
        self.assertEquals(self._baseConfig.baseUri, "")
