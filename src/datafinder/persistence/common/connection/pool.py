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
Implements the connection pool for WebDAV connections.
"""


from threading import Condition

from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


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
