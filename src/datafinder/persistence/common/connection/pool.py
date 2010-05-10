#
# Created: 29.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: pool.py 4333 2009-11-10 16:33:34Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements the connection pool for WebDAV connections.
"""


from threading import Condition

from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4333 $"


class ConnectionPool(object):
    """ Implements a generic connection pool for shared resources. """
    
    def __init__(self, maxConnectionNumber=10, timeout=None):
        """ 
        Constructor. 
        
        @param maxConnectionNumber: Maximum number of parallel connections. Default: 10.
        @type maxConnectionNumber: C{int}
        @param timeout: Time out in seconds or C{None} specifying not time out (default).
        @type timeout: C{int}
        """
        
        self._maxConnectionNumber = maxConnectionNumber
        self._timeout = timeout
        self._connections = dict()
        self._lock = Condition()
        self.reload()
        
    def reload(self):
        """ Reloads the connection pool. """
        
        self._lock.acquire()
        try:
            for connection, _ in self._connections.values():
                self._releaseConnection(connection)
            self._connections = dict()
        finally:
            self._lock.release()
            
    def acquire(self):
        """ 
        Acquires a connection. 
        
        @return: Usable connection.
        @rtype: C{object} 
        
        @raise PersistenceError: Indicating time when acquiring a connection object.
        """

        self._lock.acquire()
        try:
            connection = self._determineUnunsedConnection()
            if connection is None:
                if self._availableConnections < self._maxConnectionNumber:
                    connection = self._createConnection()
                else:
                    self._lock.wait(self._timeout)
                    connection = self._determineUnunsedConnection()
                    if connection is None:
                        raise PersistenceError("Time out occurred before a new connection was available.")
            self._connections[id(connection)] = connection, True
            return connection
        finally:
            self._lock.release()

    def _determineUnunsedConnection(self):
        """ Returns an unused connection or C{None}. """
        
        for connection, used in self._connections.values():
            if not used:
                return connection
            
    def release(self, connection):
        """ 
        Releases the given connection. 
        
        @param connection: Connection to release.
        @type connection: C{object} 
        """

        self._lock.acquire()
        try:
            if not id(connection) in self._connections:
                raise PersistenceError("The release connection was not managed by this connection pool.")
            self._connections[id(connection)] = connection, False
            self._lock.notify()
        finally:
            self._lock.release()
            
    @property
    def _availableConnections(self):
        """ Calculates the number of produced connections. """
        
        return len(self._connections)
            
    def _createConnection(self):
        """ Template method implementing connection creation. """

        pass
    
    def _releaseConnection(self, connection):
        """ Template method implementing connection specific releasing behavior. """
        
        pass
