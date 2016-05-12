# pylint: disable=W0511, W0201
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
Implements test cases for the AmazonS3-specific file system factory.
"""


from unittest import TestCase
from boto.s3.connection import S3Connection

from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.adapters.amazonS3 import factory
from datafinder.persistence.adapters.amazonS3.data.adapter import DataS3Adapter
from datafinder.persistence.adapters.amazonS3.connection_pool import S3ConnectionPool
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id$" 


class FileSystemTestCase(TestCase):
    """ Test cases for Amazon S3 file system factory."""
    
    def setUp(self):
        """ Mocks an utility functionality. """
        
        factory.FileSystem._getConnectionPool = SimpleMock(SimpleMock(SimpleMock()))
        self._factory = factory.FileSystem(BaseConfiguration("http://s3.amazonaws.de/bucketname/keyname"))
      
    def testCreateDataStorer(self):
        """ Tests the creation of a AmazonS3 specific data storer. """
        
        self.assertTrue(isinstance(self._factory.createDataStorer("identifier"), DataS3Adapter))
  
    def testUpdateCredentials(self):
        """ Tests to update the credentials """
        
        credentials = dict()
        credentials["username"] = ""
        credentials["password"] = ""
        self._factory.updateCredentials(credentials)
        

class ConnectionPool(TestCase):
    """Test case for the connection Pool"""
    
    def setUp(self):
        """ Mocks an utility functionality. """
    
    def testGetConnectionPool(self):
        """getting a connection"""
        
        self._factory = factory.FileSystem(BaseConfiguration("http://s3.amazonaws.de/bucketname/keyname"))
        connectionPool = self._factory._getConnectionPool()
        self.assertTrue(isinstance(connectionPool, S3ConnectionPool))
        
