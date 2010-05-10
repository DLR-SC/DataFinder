#
# Created: 24.09.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: connection_pool_test.py 4283 2009-09-30 13:34:32Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests for the TSM specific connection pool.
"""


from paramiko import SSHException
import socket
import unittest

from datafinder.persistence.adapters.tsm import connection_pool
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4283 $"


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


class TsmConnectionTestCase(unittest.TestCase):
    """ Implements test cases for the TSM specific connection pool. """

    def setUp(self):
        """ Creates the test setup."""
        
        _TransportMock.error = None
        connection_pool.Transport = _TransportMock
        self._connectionPool = connection_pool.TsmConnectionPool(SimpleMock())
        
    def testAquireSuccess(self):
        """ Tests the successful acquire of a TSM connection. """
        
        self.assertNotEquals(self._connectionPool.acquire(), None)
        
    def testAcquireError(self):
        """ Tests error handling when acquiring a TSM connection. """

        _TransportMock.error = SSHException("")
        self.assertRaises(PersistenceError, self._connectionPool.acquire)
        
        _TransportMock.error = socket.error("")
        self.assertRaises(PersistenceError, self._connectionPool.acquire)

        _TransportMock.error = socket.gaierror("")
        self.assertRaises(PersistenceError, self._connectionPool.acquire)
