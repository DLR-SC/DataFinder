# pylint: disable-msg=R0201
# R0201 is disabled in order to correctly implement the interface.
#
# Created: 18.08.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: connection_pool.py 4524 2010-03-05 14:09:59Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements a connection pool for TSM adapter.
"""


import socket

from paramiko import Transport, SSHException

from datafinder.persistence.adapters.tsm.constants import DEFAULT_SSH_PORT
from datafinder.persistence.common.connection.pool import ConnectionPool
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4524 $"


class TsmConnectionPool(ConnectionPool):
    """ Implements the connection pool. """

    def __init__(self, configuration):
        """ 
        Constructor. 
        
        @param configurationContext: TSM connection parameters.
        @type configurationContext: L{Configuration<datafinder.persistence.tsm.configuration.Configuration>}
        """
        
        self._configuration = configuration
        ConnectionPool.__init__(self, 5)

    def _createConnection(self):
        """
        @see: L{_createConnection<datafinder.persistence.common.connection.pool.ConnectionPool._createConnection>}
        """

        try:
            connection = Transport((self._configuration.hostname, DEFAULT_SSH_PORT))
            connection.connect(username=self._configuration.username, password=self._configuration.password)
            return connection
        except (SSHException, socket.error, socket.gaierror), error:
            errorMessage = u"Unable to establish SSH connection to TSM host '%s'! " \
                           % (self._configuration.hostname) + "\nReason: '%s'" % str(error)
            raise PersistenceError(errorMessage)

    def _releaseConnection(self, connection): #R0201
        """
        @see: L{_releaseConnection<datafinder.persistence.common.connection.pool.ConnectionPool._releaseConnection>}
        """
        
        return connection.close()
