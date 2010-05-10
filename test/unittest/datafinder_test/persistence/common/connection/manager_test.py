#
# Created: 17.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: manager_test.py 4597 2010-04-12 08:25:34Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the test cases of the connection pool manager.
"""


import threading
import random
import unittest

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.common.connection.manager import ConnectionPoolManager


__version__ = "$LastChangedRevision: 4597 $"


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
