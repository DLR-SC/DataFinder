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
Implements mapping of logical identifiers to SVN-specific identifiers.
"""


import platform

from datafinder.persistence.adapters.svn.util.cpython import CPythonSVNDataWrapper
#from datafinder.persistence.adapters.svn.util.jython import JythonSVNDataWrapper


__version__ = "$Revision-Id:$" 


def createSVNConnection(repoPath, workingCopyPath, username, password):
    if platform.platform().lower().find("java") == -1:
        connection = CPythonSVNDataWrapper(repoPath, workingCopyPath, username, password)
    else:
        #connection= JythonSVNDataWrapper(repoPath, workingCopyPath, username, password)
        pass
    return connection

def determineBaseName(identifier):
    """ 
    Determines the last component of the logical path - the base name. 
        
    @param identifier: The interface identifier.
    @type identifier: C{unicode}
        
    @return: Last part of the identifier.
    @rtype: C{unicode}
    """
        
    return identifier.rsplit("/")[-1]

def mapIdentifier(identifier):
    """ 
    Maps the logical identifier to the persistence representation.
        
    @param identifier: Path relative to the configured base URL.
                       Base URL is implicitly represented by '/'.
    @type identifier: C{unicode}
        
    @return: URL identifying the resource.
    @rtype: C{unicode}
    """
        
    if identifier.startswith("/"):
        persistenceId = identifier
    else:
        persistenceId = "/" + identifier
    return persistenceId
