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
Tests for the TSM specific connection pool.
"""


from paramiko import SSHException
import socket
import unittest

from datafinder.persistence.adapters.tsm import connection_pool
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class _TransportMock(object):
    """ Mocks the paramiko Transport class. """
    
    error = SSHException("")
    
    def __init__(self, _):
        """ Mocks constructor. """
        
        self.username = None
        self.password = None
    
    def connect(self, username=None, password=None):
        """ Mocks connect method. """
        
        self.username = username
        self.password = password
        if not self.error is None:
            raise self.error
        
    def close(self):
        pass


class TsmConnectionTestCase(unittest.TestCase):
    """ Implements test cases for the TSM specific connection pool. """

    def setUp(self):
        """ Creates the test setup."""
        
        _TransportMock.error = None
        connection_pool.Transport = _TransportMock
        self._connectionPool = connection_pool.TsmConnectionPool(SimpleMock())
        
    def tearDown(self):
        self._connectionPool.reload()
    
    def testAquireSuccess(self):
        """ Tests the successful acquire of a TSM connection. """
        
        connection = self._connectionPool.acquire()
        self.assertNotEquals(connection, None)
        
    def testAcquireError(self):
        """ Tests error handling when acquiring a TSM connection. """

        _TransportMock.error = SSHException("")
        self.assertRaises(PersistenceError, self._connectionPool.acquire)
        
        _TransportMock.error = socket.error("")
        self.assertRaises(PersistenceError, self._connectionPool.acquire)

        _TransportMock.error = socket.gaierror("")
        self.assertRaises(PersistenceError, self._connectionPool.acquire)
