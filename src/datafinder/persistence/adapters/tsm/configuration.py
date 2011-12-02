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
Implements a configuration holder object.
"""


from urlparse import urlsplit


__version__ = "$Revision-Id:$" 


class Configuration(object):
    """ Defines a set of configuration parameters for TSdM access. """
    
    def __init__(self, baseConfiguration):
        """ 
        Constructor.
        
        @param baseConfiguration: General basic configuration.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """
        
        self.baseUri = baseConfiguration.baseUri
        hostname, path = self._determineHostAndPath(baseConfiguration.uriPath or "")
        self.hostname = hostname or ""
        self.basePath = path
        self.username = baseConfiguration.username
        self.password = baseConfiguration.password
        self.serverNodeName = baseConfiguration.serverNodeName
        
    @staticmethod
    def _determineHostAndPath(hostAndPath):
        """ 
        Need to do a little trick because C{tsm} is no standard 
        URI scheme and thus host name and path are not correctly split.
        Just changing the scheme to a supported one.
        """
        # pylint: disable=E1103
        # E1103: urlsplit produces the required results but Pylint
        # cannot correctly determine it.

        splitUrl = urlsplit("http:" + hostAndPath, allow_fragments=False)
        return splitUrl.hostname, splitUrl.path
