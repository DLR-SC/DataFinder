# pylint: disable-msg=W0511
#
# Created: 28.11.2009 ney <Miriam.Ney@dlr.de>
# Changed: $Id: configuration.py 4559 2010-03-23 15:20:18Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines S3-specific connection parameters. 
"""


__version__ = "$LastChangedRevision: 4559 $"

class Configuration(object):
    """ Defines a set of configuration parameters of the WebDAV protocol. """
    
    def __init__(self, baseConfiguration):
        """ 
        Constructor.
        
        @param baseConfiguration: General basic configuration.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """
  
        self.baseUrl = baseConfiguration.baseUri
        self.protocol = baseConfiguration.uriScheme

        self.username = baseConfiguration.username
        self.password = baseConfiguration.password
        
        self.awsAccessKey = baseConfiguration.awsAccessKey
        self.awsSecretAccessKey = baseConfiguration.awsSecretAccessKey
        
        bucketName, keyName = self._determineBucketAndKey(baseConfiguration.uriPath or "")
               
        self.bucketName = bucketName
        self.keyName = keyName
        
    @staticmethod   
    def _determineBucketAndKey(bucketAndKey):   
        
        splitUrl = bucketAndKey.split("/")
        return splitUrl[1], splitUrl[2]
       
