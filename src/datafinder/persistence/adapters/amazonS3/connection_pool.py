# pylint: disable-msg=W0511
# Created: 04.12.2009 ney <Miriam.Ney@dlr.de>
# Changed: $Id: connection_pool.py 4388 2010-01-14 10:27:33Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements Amazon S3-specific connection pool.
"""


from boto.s3.connection import S3Connection

from datafinder.persistence.common.connection.pool import ConnectionPool
from datafinder.persistence.adapters.amazonS3.constants import MAX_CONNECTION_NUMBER


__version__ = "$LastChangedRevision: 4388 $"


class S3ConnectionPool(ConnectionPool):
    """ Implements a Amazon S3-specific connection pool. """
    
    def __init__(self, configuration):
        """ 
        Constructor. 
        
        @param configurationContext: S3 connection parameters.
        @type configurationContext: L{Configuration<datafinder.persistence.
        amazonS3.configuration.Configuration>}
        """
        
        self._configuration = configuration
        ConnectionPool.__init__(self, MAX_CONNECTION_NUMBER)
        
    def _createConnection(self):
        """ Overwrites template method for connection creation. """
        
        
        secretAccessKey = self._configuration.awsSecretAccesKey
        accessKey = self._configuration.awsAccessKey
        
        connection = S3Connection(accessKey, secretAccessKey) 
         
        return connection
