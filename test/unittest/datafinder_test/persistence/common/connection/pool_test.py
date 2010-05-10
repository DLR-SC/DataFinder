#
# Created: 16.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: pool_test.py 4333 2009-11-10 16:33:34Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements test cases for the generic connection pool."
"""


import unittest
import threading

from datafinder.persistence.common.connection.pool import ConnectionPool
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4333 $"


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
                connection = self._connectionPool.acquire()
                self._connectionPool.release(connection)
                self._connectionPool.reload()
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
