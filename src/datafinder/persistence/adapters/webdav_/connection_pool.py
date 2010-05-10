#
# Created: 30.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: connection_pool.py 3803 2009-02-20 16:26:50Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements WebDAV-specific connection pool.
"""


from webdav.Connection import Connection

from datafinder.persistence.common.connection.pool import ConnectionPool
from datafinder.persistence.adapters.webdav_.constants import MAX_CONNECTION_NUMBER


__version__ = "$LastChangedRevision: 3803 $"


class WebdavConnectionPool(ConnectionPool):
    """ Implements a WebDAV-specific connection pool. """
    
    def __init__(self, configuration):
        """ 
        Constructor. 
        
        @param configurationContext: WebDAV connection parameters.
        @type configurationContext: L{Configuration<datafinder.persistence.
        webdav.configuration.Configuration>}
        """
        
        self._configuration = configuration
        ConnectionPool.__init__(self, MAX_CONNECTION_NUMBER)
        
    def _createConnection(self):
        """ Overwrites template method for connection creation. """
        
        protocol = self._configuration.protocol
        hostname = self._configuration.hostname
        port = self._configuration.port
        connection = Connection(hostname, port, protocol=protocol)
        username = self._configuration.username
        password = self._configuration.password
        if not username is None or password is None:
            connection.addBasicAuthorization(username, password)
        return connection
