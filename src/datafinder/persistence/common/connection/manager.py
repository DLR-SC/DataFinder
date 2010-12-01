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
Implements a manager for connection pools which providing
connections bound to a specific configuration.
"""


from threading import RLock

from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


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
