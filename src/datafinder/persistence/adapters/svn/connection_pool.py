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
Implements SVN-specific connection pool.
"""


from datafinder.persistence.adapters.svn.constants import MAX_CONNECTION_NUMBER
from datafinder.persistence.common.connection.pool import ConnectionPool
from datafinder.persistence.adapters.svn.util import util


__version__ = "$Revision-Id:$" 


class SubversionConnectionPool(ConnectionPool):
    """ Implements a SVN-specific connection pool. """
    
    def __init__(self, configuration):
        """ 
        Constructor. 
        
        @param configurationContext: SVN connection parameters.
        @type configurationContext: L{Configuration<datafinder.persistence.
        svn.configuration.Configuration>}
        """
        
        self._configuration = configuration
        ConnectionPool.__init__(self, MAX_CONNECTION_NUMBER)
        
    def _createConnection(self):
        """ Overwrites template method for connection creation. """
        
        repoPath = self._configuration.baseUrl
        workingCopyPath = self._configuration.workingCopyPath
        username = self._configuration.username
        password = self._configuration.password
        
        connection = util.createSubversionConnection(repoPath, workingCopyPath, username, password)
        
        return connection
    