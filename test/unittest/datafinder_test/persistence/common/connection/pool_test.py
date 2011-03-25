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
Implements test cases for the generic connection pool."
"""


import unittest
import threading

from datafinder.persistence.common.connection.pool import ConnectionPool
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


class ConnectionPoolTestCase(unittest.TestCase):
    """ Implements the test cases. """
    
    def setUp(self):
        """ Creates test setup. """
        
        ConnectionPool._createConnection = lambda _: "connection"
        self._connectionPool = ConnectionPool(1)
        
    def testSuccessfulUsage(self):
        """ Tests the standard acquire/release/reload behavior. """
        
        for _ in range(30):
            connection = self._connectionPool.acquire()
            self._connectionPool.release(connection)
        self._connectionPool.reload()
            
    def testEmptyConnectionPool(self):
        """ Test behavior when no connection is available. """
        
        self._connectionPool.acquire()
        self._connectionPool._timeout = 1
        self.assertRaises(PersistenceError, self._connectionPool.acquire)
        
    def testFullConnectionPool(self):
        """ Test behavior when connection pool is already full. """
        
        self.assertRaises(PersistenceError, self._connectionPool.release, None)
        
    def testConcurrentAccess(self):
        """ Tests the concurrent access to the connection pool. """
        
        def testFunction():
            try:
                try:
                    self._connectionPool.reload()
                    connection = self._connectionPool.acquire()
                finally:
                    self._connectionPool.release(connection)
            except PersistenceError:
                return False
        
        threads = list()
        for _ in range(100):
            thread = threading.Thread(target=testFunction)
            threads.append(thread)
        for thread in threads:
            thread.start()
        alive = True
        while alive:
            alive_ = False
            for thread in threads:
                alive_ = alive_ | thread.isAlive()
            alive = alive_
