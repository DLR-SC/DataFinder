#
# Created: 29.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id$ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements a manager for connection pools which providing
connections bound to a specific configuration.
"""


from threading import RLock

from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision$"


class ConnectionPoolManager(object):
    """ Manages the connection pool for different configurations. """
    
    def __init__(self, maxConnectionPoolNumber=10):
        """ 
        Constructor.
        
        @param maxConnectionPoolNumber: Maximum number of allowed connection pools. Default:10.
        @type maxConnectionPoolNumber: C{int}
        """

        self._maxConnectionPoolNumber = maxConnectionPoolNumber
        self._connectionPools = dict()
        self._lock = RLock()
    
    def get(self, configuration):
        """ 
        Returns a connection pool for the specific configuration or C{None}. 
        
        @param configuration: Configuration identifying the connection pool.
        @type configuration: C{object}
        
        @return: Connection pool.
        @rtype: L{ConnectionPool<datafinder.persistence.common.
        connection_handling.connection_pool.ConnectionPool>} 
        """
        
        self._lock.acquire()
        try:
            connectionPool = None
            if configuration in self._connectionPools:
                connectionPool = self._connectionPools[configuration]
            return connectionPool
        finally:
            self._lock.release()
            
    def add(self, configuration, connectionPool):
        """ 
        Adds a connection and the associated connection pool.
        
        @param configuration: Configuration identifying the connection pool.
        @type configuration: C{object}
        @param connectionPool: Connection pool.
        @type connectionPool: L{ConnectionPool<datafinder.persistence.common.
        connection_handling.connection_pool.ConnectionPool>} 
        
        @raise PersistenceError: Indicating that no additional connection pool can be added.
        """
        
        self._lock.acquire()
        try:
            if not configuration in self._connectionPools:
                if len(self._connectionPools) < self._maxConnectionPoolNumber:
                    self._connectionPools[configuration] = connectionPool
                else:
                    raise PersistenceError("No more connection pools can be created.")
        finally:
            self._lock.release()
                
    def remove(self, configuration):
        """ 
        Removes the configuration and the associated connection pool. 
        
        @param configuration: Configuration.
        @type configuration: C{object} 
        """
        
        self._lock.acquire()
        try:
            if configuration in self._connectionPools:
                del self._connectionPools[configuration]
        finally:
            self._lock.release()
            
    def __len__(self):
        """ Returns the number of connection pools. """
        
        return len(self._connectionPools)
