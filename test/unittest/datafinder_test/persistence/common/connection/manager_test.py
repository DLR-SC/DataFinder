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
Implements the test cases of the connection pool manager.
"""


import threading
import random
import unittest

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.common.connection.manager import ConnectionPoolManager


__version__ = "$Revision-Id:$" 


class ConnectionPoolManagerTestCase(unittest.TestCase):
    """ Implements test cases for the connection pool manager. """
    
    def setUp(self):
        """ Creates the instance under test. """
        
        self._connectionPoolManager = ConnectionPoolManager(1)
        self._connectionPool = "POOL"
        self._configuration = "configuration"
        
    def testSuccessfulUsage(self):
        """ Demonstrates the base interface of the connection manager. """
        
        for _ in range(30):
            self._connectionPoolManager.add(self._configuration, self._connectionPool)
            self.assertEquals(len(self._connectionPoolManager), 1)
            self.assertEquals(self._connectionPoolManager.get(self._configuration), self._connectionPool)
            self._connectionPoolManager.remove(self._configuration)
            self.assertEquals(self._connectionPoolManager.get(self._configuration), None)
            self.assertEquals(len(self._connectionPoolManager), 0)
    
    def testFull(self):
        """ Tests the behavior when no more connection pools can be added. """
        
        self._connectionPoolManager.add(self._configuration, self._connectionPool)
        self.assertRaises(PersistenceError, self._connectionPoolManager.add, "self._configuration", "self._connectionPool")
        
    def testConcurrentAccess(self):
        """ Tests the concurrent access to the connection pool manager. """
        
        def testFunction():
            try:
                for _ in range(100):
                    configuration = "" + str(random.random())
                    connectionPool = "connectionPool"
                    self._connectionPoolManager.add(configuration, connectionPool)
                    self._connectionPoolManager.get(configuration)
                    self._connectionPoolManager.remove(configuration)
            except PersistenceError:
                return
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
