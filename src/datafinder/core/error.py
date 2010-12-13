# pylint: disable=R0901
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#
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
Error classes of the core level.
"""


__version__ = "$Revision-Id:$" 


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

class PrincipalError(CoreError):
    """
    Error class that occurs during principal handling.
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

