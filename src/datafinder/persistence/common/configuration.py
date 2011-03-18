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
Module provides class defining basic configuration parameters.
"""


from urlparse import urlsplit


__version__ = "$Revision-Id:$" 


class BaseConfiguration(object):
    """
    Contains the basic configuration parameters for accessing a generic file system.
    Additional configuration parameters can be specified using keyword arguments.
    """
    
    baseWorkingDirectory = None
    
    def __init__(self, baseUri=None, **kwargs):
        """ 
        Constructor.
        
        @param baseUri: URI of an item in the file system the other items are addressed relative to.
        @type baseUri: C{unicode}
        """
        
        self._baseUri = None
        self.uriScheme = None
        self.uriNetloc = None
        self.uriHostname = None
        self.uriPort = None
        self.uriPath = None
    
        self.baseUri = baseUri
        
        self.__dict__.update(kwargs)
        
    def __getBaseUri(self):
        """ Simple getter. """
        
        return self._baseUri
        
    def __setBaseUri(self, baseUri):
        """ Sets the base URI. """
        # pylint: disable=E1103
        # E1103: urlsplit produces the required results but Pylint
        # cannot correctly determine it.

        if not baseUri is None:
            parsedUri = urlsplit(baseUri)
            self._baseUri = parsedUri.geturl()
            self.uriScheme = parsedUri.scheme
            self.uriNetloc = parsedUri.netloc
            self.uriHostname = parsedUri.hostname
            try:
                self.uriPort = parsedUri.port
            except ValueError:
                self.uriPort = None
            self.uriPath = parsedUri.path
        
    baseUri = property(__getBaseUri, __setBaseUri)
        
    def __getattr__(self, _):
        """ 
        Returns C{None} for unknown attributes instead of raising an C{AttributeError}. 
        This is provided for convenience to avoid boiler-plate exception handling code.
        """
        
        return None
