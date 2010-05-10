# pylint: disable-msg=R0901
# R0901: Tells you that you have to much ancestors in your class hierarchy.
#        But this is required here to build a error hierarchy.
#
# Created: 06.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: error.py 4117 2009-05-27 11:12:39Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
Error classes of the core level.
"""


__version__ = "$LastChangedRevision: 4117 $"


class CoreError(Exception):
    """
    Error class for the application level.
    Other error classes on the application level
    should be subclassed from this one.
    """
    
    pass


class ItemError(CoreError):
    """
    Error class that occurs during item handling.
    """
    
    pass


class PrivilegeError(CoreError):
    """
    Error class that occurs during privilege handling.
    """
    
    pass


class ConfigurationError(CoreError):
    """
    Error class that occurs during configuration loading.
    """
    
    pass


class PropertyError(CoreError):
    """ Representing errors concerning property definitions. """
    
    def __init__(self, propertyIdentifier, errorMessage):
        """ 
        Constructor.

        @param propertyIdentifier: The identifier of the property.
        @type propertyIdentifier: C{unicode}
        @param errorMessage: The message describing the occurred error.
        @type errorMessage: C{unicode}
        """
        
        CoreError.__init__(self, errorMessage)
        self.propertyIdentifier = propertyIdentifier


class AuthenticationError(CoreError):
    """ Representing errors focusing missing or invalid authentication information. """
    
    def __init__(self, errorMessage, datastore, updateCredentialsCallback):
        """ 
        Constructor.

        @param errorMessage: The message describing the occurred error.
        @type errorMessage: C{unicode}
        @param datastore: Data store configuration of the accessed file system.
        @type datastore: L{DefaultDataStore<datafinder.core.configuration.datastores.datastore.DefaultDataStore>}
        @param updateCredentialsCallback: Function which allows specification of authentication information
                                          via a parameter dictionary.
        @type updateCredentialsCallback: C{Callable}
        """
        
        CoreError.__init__(self, errorMessage)
        self.updateCredentialsCallback = updateCredentialsCallback
        self.datastore = datastore

