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
Tests the mapping of the lucene scheme within the configuration.
"""


import unittest


from datafinder.persistence.adapters.lucene.configuration import Configuration
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.common.configuration import BaseConfiguration


__version__ = "$Revision-Id$"


class ConfigurationTest(unittest.TestCase):
    """ Test the validation / mapping of the artificially created "lucene+" scheme. """
    # Boring error causes by the unittest framework pylint:disable=R0904
    
    def testLuceneHttpsUri(self):
        baseConfig = BaseConfiguration("lucene+https://server.com/path/index.idx")
        config = Configuration(baseConfig, None)
        
        self.assertEquals(config.luceneIndexUri, "https://server.com/path/index.idx")
        
    def testLuceneHttpUri(self):
        baseConfig = BaseConfiguration("lucene+http://server.com/path/index.idx")
        config = Configuration(baseConfig, None)
        
        self.assertEquals(config.luceneIndexUri, "http://server.com/path/index.idx")
        
    def testLuceneWinFileUri(self):
        baseConfig = BaseConfiguration("lucene+file:///c:/path/index.idx")
        config = Configuration(baseConfig, None)
        
        self.assertEquals(config.luceneIndexUri, "file:///c:/path/index.idx")
        
    def testLuceneFileUri(self):
        baseConfig = BaseConfiguration("lucene+file:///path/index.idx")
        config = Configuration(baseConfig, None)
        
        self.assertEquals(config.luceneIndexUri, "file:///path/index.idx")
        
    def testEmptyLuceneFileUri(self):
        baseConfig = BaseConfiguration("")
        self.assertRaises(PersistenceError, Configuration, baseConfig, None)
        
    def testNone(self):
        baseConfig = BaseConfiguration(None)
        self.assertRaises(PersistenceError, Configuration, baseConfig, None)
        
    def testWithoutLuceneScheme(self):
        baseConfig = BaseConfiguration("https://server.com/path/index.idx")
        config = Configuration(baseConfig, None)
        
        self.assertEquals(config.luceneIndexUri, "https://server.com/path/index.idx")
