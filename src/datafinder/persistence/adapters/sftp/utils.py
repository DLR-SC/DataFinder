#
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
Implements some utility functionality.
"""


from datafinder.persistence.adapters.sftp import constants


__version__ = "$Revision-Id:$" 


class ItemIdentifierMapper(object):
    
    def __init__(self, basePath):
        self._basePath = basePath
    
    def determinePeristenceIdentifier(self, identifier):
        """ Transforms the logical identifier to the persistence identifier. """
        
        if self._basePath.endswith("/"):
            persistenceId = self._basePath[:-1] + identifier
        else:
            persistenceId = self._basePath + identifier
        persistenceId = persistenceId.encode(
            constants.FILE_NAME_ENCODING, errors="replace")
        return persistenceId
    
    @staticmethod
    def determineParentId(identifier):
        parentId = "/".join(identifier.rsplit("/")[:-1])
        if parentId == "" and identifier.startswith("/") and identifier != "/":
            parentId = "/"
        return parentId
    
    @staticmethod
    def determineChildId(identifier, name):
        if identifier.endswith("/"):
            child_id = identifier + name
        else:
            child_id = identifier + "/" + name
        return child_id
    
    @staticmethod
    def determinePersistenceChildId(persistenceIdentifier, name):
        return ItemIdentifierMapper.determineChildId(persistenceIdentifier, name)
