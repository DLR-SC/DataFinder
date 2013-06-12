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
    """ Utility class to simplify different operations on logical
    and persistence IDs. """

    def __init__(self, basePath):
        """
        @param basePath: Base path on the SFTP server.
        @type basePath: C{unicode}
        """
        
        self._basePath = basePath
    
    def determinePeristenceId(self, identifier):
        """ Transforms the logical identifier to the persistence identifier. 
        
        @param identifier: The logical ID of an item.
        @type identifier: C{unicode}
        
        @return: Path on the SFTP server. 
                 It is already correctly encoded to use it with the library.
        @rtype: C{str}
        """
        
        if self._basePath.endswith("/"):
            persistenceId = self._basePath[:-1] + identifier
        else:
            persistenceId = self._basePath + identifier
        persistenceId = persistenceId.encode(
            constants.FILE_NAME_ENCODING, errors="replace")
        return persistenceId
    
    @staticmethod
    def determineParentId(identifier):
        """ Determines the logical ID of the parent item.
        @param identifier: The logical ID of an item.
        @type identifier: C{unicode}
        
        @return: The logical ID of the parent item.
        @rtype: C{unicode}
        """
        
        if identifier.endswith("/"):
            identifier = identifier[:-1]
        parentId = "/".join(identifier.rsplit("/")[:-1])
        if parentId == "" and identifier.startswith("/") and identifier != "/":
            parentId = "/"
        return parentId
    
    @staticmethod
    def determineChildId(identifier, name):
        """
        Creates the child ID for the given identifier and the child name.
        
        @note: Both parameters can be C{str} or C{unicode}. 
               However, make sure that both have the same type/
               are encoded the same way.
        """
        
        if not identifier and not name:
            return ""
        if identifier.endswith("/"):
            child_id = identifier + name
        else:
            child_id = identifier + "/" + name
        return child_id
    
    @staticmethod
    def determinePersistenceChildId(persistenceIdentifier, name):
        """
        Creates the child ID for the given persistence identifier and the child name.
        @note: It is just an alias definition for persistence IDs which implies that you 
               use already encoded string.
        """
        
        return ItemIdentifierMapper.determineChildId(persistenceIdentifier, name)
